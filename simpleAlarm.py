##Simple Alarm##
##Author: Prakhar Mehrotra
##This is a simple alarm clock that sounds an alarm.mp4 file (located in
## the same directory) at a time specified by the user
## ex. Enter "22:03" (using quotes) to have alarm go off at 10:03 pm

from datetime import datetime
import os

alarmTime = input("Enter alarm time ('HH:MM') ")
timeFormat = '%H:%M'
prevSec = 0

print("Alarm set for " + alarmTime)

def hoursMinutesSeconds(td):
    return td.seconds//3600, (td.seconds//60)%60, td.seconds%60

while True:
    now = datetime.now()
    alarmTP = datetime.strptime(alarmTime,timeFormat)
    #print(alarmTP.hour + 1)
    
    if (now.hour == alarmTP.hour) and (now.minute == alarmTP.minute) and (now.second == alarmTP.second):
        print("ALARM")
        os.system('mpg123 -q alarm.mp3')
        #break

    elif now.second != prevSec:
        difference = alarmTP-now
        dHours, dMinutes, dSeconds = hoursMinutesSeconds(difference)
        print("Time to alarm: "+'{0}:{1:02d}:{2:02d}'.format(dHours,dMinutes,dSeconds))
        prevSec = now.second

    

