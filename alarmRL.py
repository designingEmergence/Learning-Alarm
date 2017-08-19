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
buttonInput == GPIO.input(18)

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

    def __init__(self,_time):
        self.targetTime = dt.strptime(_time,timeFormat) 
        self.startTime = self.targetTime - datetime.timedelta(minutes = (numMinutes-2))
        self.endTime = self.startTime + datetime.timedelta(minutes = numMinutes)
        self.alarmMinute = 0
        self.now = dt.now()
        self.prevSec = 0
        self.running = False
        self.sessionEnded = False
        self.wakeTime = self.endTime
        print ("Target time: " + '{0}'.format(self.targetTime))
        print ("Start time: " + '{0}'.format(self.startTime))
        print ("End time: " + '{0}'.format(self.endTime))        

    def startAlarm(self):
        played = False
        alarmTime = self.startTime +datetime.timedelta(minutes=self.alarmMinute)
        print ("Alarm time: {0}".format(alarmTime))

        while self.running:
            self.now = dt.now()
            
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
        tDiff = self.wakeTime - self.targetTime
        tDiffMinutes = tdiff.minutes
        print(tDiffMinutes)

        reward = -tDiffMinutes

        if (wakeTime > self.targetTime):
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
            
class agent():

    def __init__ (self, lr, numActions):
        
        self.weights = tf.Variable(tf.ones([numActions]))
        self.chosen_action = tf.argmax(self.weights,0)
        
        self.reward_holder = tf.placeholder(shape=[1],dtype=tf.float32)
        self.action_holder = tf.placeholder(shape=[1],dtype=tf.int32)
        self.responsible_weight = tf.slice(self.weights,self.action_holder,[1])
        self.loss = -(tf.log(self.responsible_weight)*self.reward_holder)
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=lr)
        self.update = optimizer.minimize(self.loss)

tf.reset_default_graph()

#alarmTime = input("Enter alarm time ('HH:MM') ")
sixMinutes = dt.now() + datetime.timedelta(minutes = 6)
startTime = "{0}:{1}".format(sixMinutes.hour,sixMinutes.minute)
cAlarm = contextualAlarm(startTime)
myAgent = agent(lr=0.02,numActions=numMinutes)
weights = tf.trainable_variables()[0]

total_episodes = 10
total_reward = np.zeros(numMinutes)
e = 0.2
init = tf.initialize_all_variables()

with tf.Session() as sess:
    sess.run(init)
    i = 0
    while i <total_episodes:
        cAlarm.sessionEnded = False
        if np.random.rand(1) < e:
            action = np.random.randint(numMinutes)
            print(action)
        else:
            action = sess.run(myAgent.chosen_action)
            print(action)

        while cAlarm.sessionEnded == False:
            cAlarm.run(action.item())

        reward = cAlarm.calculateReward
        
        print("Rewarded") 

        feed_dict={myAgent.reward_holder:[reward],myAgent.action_holder:[action]}
        _,resp,ww = sess.run([myAgent.update,myAgent.responsible_weight,weights],feed_dict=feed_dict)

        total_reward[action] += reward
        bestTime = cAlarm.startTime+datetime.timedelta(minutes = (sess.run(myAgent.chosen_action)).item()) 
        print "The best time to play the alarm right now is {0}".format(bestTime)

        i +=1
      
            

#cAlarm.run()



