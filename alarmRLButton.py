# Non RL Learning Alarm
##Author: Prakhar Mehrotra

import datetime
from datetime import datetime as dt
import os
import tensorflow as tf
import numpy as np

import RPi.GPIO as GPIO

timeFormat = '%H:%M'
numMinutes = 7

GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.IN, pull_up_down=GPIO.PUD_UP)
buttonInput = GPIO.input(18)

def timeConverter(td):
    return td.seconds//3600, (td.seconds//60)%60,td.seconds%60

def timeComparer(t1,t2):
    result = ' '
    if (t1.hour == t2.hour) and (t1.minute == t2.minute) and (t1.second == t2.second):
        result = 'equal'
    elif t1 > t2:
        result = 'greater'
    elif t1 < t2:
        result = 'less'
    else:
        result = 'none'
        
    return result

class contextualAlarm:

    def __init__(self, _time):
        self.inputTime = _time
        self.updateTime(updatedTime=self.inputTime)
        self.alarmMinute = 0
        self.now = dt.now()
        self.prevSec = 0
        self.running = False
        self.sessionEnded = False
        self.wakeTime = self.endTime
       
        
    def updateTime(self, updatedTime = None):
        inputTime = updatedTime or self.inputTime
        self.targetTime = dt.strptime(inputTime, timeFormat).time()
        self.target = dt.combine(dt.today(),self.targetTime)           
        self.startTime = self.target - datetime.timedelta(minutes = (numMinutes - 1)) #How many minutes before target to start the program
        self.endTime = self.target + datetime.timedelta(minutes = 5) #How many minutes after target to run the program

        if self.startTime < dt.now():
            self.target += datetime.timedelta(days =1) 
            self.startTime += datetime.timedelta(days =1)
            self.endTime += datetime.timedelta(days =1) 
            print("added a day")  
            
        print ("Target time: " + '{0}'.format(self.target))
        print ("Start time: " + '{0}'.format(self.startTime))
        print ("End time: " + '{0}'.format(self.endTime)) 
    
    def startAlarm(self):
        played = False
        alarmTime = self.startTime +datetime.timedelta(minutes=self.alarmMinute)
        print ("Alarm time: {0}".format(alarmTime))

        while self.running:
            self.now = dt.now()
            buttonInput = GPIO.input(18)
            if buttonInput == False:
            	print("button")
                self.running = False
                self.sessionEnded = True
                self.wakeTime = self.now
                print("button end")
                break
            	
            #else:
        		#print("noButton")
     
            if (self.now.second != self.prevSec):
                self.prevSec = self.now.second
                difference = self.endTime - self.now
                dHours, dMinutes, dSeconds = timeConverter(difference)
                print("Time to program end: "+'{0}:{1:02d}:{2:02d}'.format(dHours,dMinutes,dSeconds))

                if timeComparer(self.now,self.endTime)=='equal':
                    self.running = False
                    self.sessionEnded = True
                    print("end")
                    break

                elif (timeComparer(alarmTime,self.now) == 'equal') and (played == False):
                    print("Playing Alarm")
                    os.system('mpg123 -q '+'1.mp4')
                    played = True



    def calculateReward(self):
        tDiff = self.wakeTime - self.target
        tDiffSeconds= tDiff.total_seconds()
        tDiffMinutes = tDiffSeconds
        print(tDiffMinutes)

        reward = tDiffMinutes

        if (self.wakeTime > self.target):
            reward * 2
        print ("Reward: {0}".format(reward))
        return reward

        
    def run(self,minute):

        self.alarmMinute = minute
        self.now = dt.now()
        
        if (timeComparer(self.now,self.startTime) == 'equal') and (self.running == False):
            self.running = True
            print("Start")
            
        elif (self.now.second != self.prevSec) and (self.running == False):
                self.prevSec = self.now.second
                difference = self.startTime - self.now
                dHours, dMinutes, dSeconds = timeConverter(difference)
                print("Time to program start: "+'{0}:{1:02d}:{2:02d}'.format(dHours,dMinutes,dSeconds))

        elif self.running == True:
            print("running")
            self.startAlarm()

tf.reset_default_graph()

weights = tf.Variable(tf.ones([numMinutes]))
chosen_action = tf.argmax(weights,0)

reward_holder = tf.placeholder(shape=[1],dtype=tf.float32) #maybe creates temp reward
action_holder = tf.placeholder(shape=[1],dtype=tf.int32) #int because list index = int
responsible_weight = tf.slice(weights,action_holder,[1]) #identify weight responsible for reward??
loss = -(tf.log(responsible_weight)*reward_holder) ##Loss = Log(policy)* Advantage (how much better an action was than the baseline, which in this case is 0)
optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.01) #improve policy based on Loss??
update = optimizer.minimize(loss) #act greedily

#alarmTime = input("Enter alarm time ('HH:MM') ")
targetMinutes = dt.now() + datetime.timedelta(minutes = numMinutes)
targetTime = "{0}:{1}".format(targetMinutes.hour,targetMinutes.minute)
cAlarm = contextualAlarm(targetTime)

total_episodes = 10
total_reward = np.zeros(numMinutes)
e = 0.5
init = tf.initialize_all_variables()

with tf.Session() as sess:
    sess.run(init)
    i = 0
    while i <total_episodes:
        cAlarm.sessionEnded = False
        
        if np.random.rand(1) < e:
            action = np.random.randint(numMinutes)
            print("Random Minute {0}".format(action))
        else:
            action = sess.run(chosen_action)
            print("Calculated Minute {0}".format(action))

        while cAlarm.sessionEnded == False:
            cAlarm.run(action)

        reward = cAlarm.calculateReward()
        
        print("Rewarded") 

        feed_dict={reward_holder:[reward],action_holder:[action]}
        _,resp,ww = sess.run([update,responsible_weight,weights],feed_dict={reward_holder:[reward],action_holder:[action]})

        total_reward[action] += reward
        bestTime = cAlarm.startTime+datetime.timedelta(minutes = (sess.run(chosen_action)).item()) 
        print "The best time to play the alarm right now is {0}".format(bestTime)

        i +=1
        cAlarm.updateTime()
      
            

#cAlarm.run()



