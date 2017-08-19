# Non RL Learning Alarm
##Author: Prakhar Mehrotra

import datetime
from datetime import datetime as dt
import os

timeFormat = '%H:%M'

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

    #print("{0} vs {1} = {2}").format(t1,t2,result)
        
    return result

class contextualAlarm:

    def __init__(self,_time):
        self.targetTime = dt.strptime(_time,timeFormat) 
        self.files = ['0.mp3','1.mp3','2.mp3','3.mp3'] #number and path for sound files
        self.numTimesSound = 3 #1-10 How many times to play alarms
        self.volumes = [0.3,0.4,0.9]
        self.times = [10,30,59]
        self.fileToPlay=[2,3,1]
        self.startTime = self.targetTime - datetime.timedelta(hours = 1)
        self.endTime = self.targetTime + datetime.timedelta(minutes = 5)
        self.now = dt.now()
        self.prevSec = 0
        self.running = False
        print ("Target time: " + '{0}'.format(self.targetTime))
        print ("Start time: " + '{0}'.format(self.startTime))
        print ("End time: " + '{0}'.format(self.endTime))

    def startAlarm(self):
        alarmTimes = []
        played = [False]*self.numTimesSound
        
        
        print('{0}'.format(self.numTimesSound) + " alarms will sound")
        for i in range(0,self.numTimesSound):
            alarmTimes.append(self.startTime + datetime.timedelta(minutes=self.times[i]))
            print("Alarm {0}: time = {1} | volume = {2} | file = 0.mp3").format(i+1,alarmTimes[i],self.volumes[i],self.files[self.fileToPlay[i]]) 

        while self.running:
            self.now = dt.now()
            
            if (self.now.second != self.prevSec):
                self.prevSec = self.now.second
                difference = self.endTime - self.now
                dHours, dMinutes, dSeconds = timeConverter(difference)
                print("Time to program end: "+'{0}:{1:02d}:{2:02d}'.format(dHours,dMinutes,dSeconds))

                if timeComparer(self.now,self.endTime)=='equal':
                    self.running = False
                    print("end")
                    break

                for i in range(0,self.numTimesSound):
                    if (timeComparer(alarmTimes[i],self.now) == 'equal') and (played[i] == False):
                        print("Playing Alarm {0}: time = {1} | volume = {2} | file = 0.mp3").format(i+1,alarmTimes[i],self.volumes[i],self.files[self.fileToPlay[i]]) 
                        os.system('mpg123 -q '+'{0}'.format(self.files[self.fileToPlay[i]]))
                        played[i] = True

            
##        if (counter <= self.numTimesSound) and (self.now.hour == alarmTime.hour) and (self.now.minute == alarmTime.minute) and (self.now.second ==alarmTime.second):
##            print ("Alarm " + '{0}'.format(counter))
##            os.system('mpg123 -q '+'{0}'.format(self.files[self.fileToPlay[counter]]))
##            counter  += 1

    def run(self):
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
            


alarmTime = input("Enter alarm time ('HH:MM') ")

alarm1 = contextualAlarm(alarmTime)

while True:
    alarm1.run()



