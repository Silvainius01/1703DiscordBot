import asyncio
import discord
import sys
import time
import datetime
from discord.ext.commands import Bot

timezoneDict = {
    'EST': datetime.timezone(datetime.timedelta(hours=-5), "Eastern"),
    'CST': datetime.timezone(datetime.timedelta(hours=-6), "Central"),
    'MST': datetime.timezone(datetime.timedelta(hours=-7), "Mountain"),
    'PST': datetime.timezone(datetime.timedelta(hours=-8), "Pacific"),
    }


def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
    return False

class CalenderEvent:
   name = "EventName"
   date = None
   dateTime = None

   def __init__(self, name, dt: datetime.datetime):
       self.name = name
       self.date = dt.date()
       self.dateTime = dt

class UserSettings:
    format = 'mdy'
    timezone = None
    
    def __init__(self, format: str, timezone: datetime.tzinfo):
        self.format = format
        self.timezone = timezone
        return

class BotCalender:
    client = discord.Client()

    eventDict = {
        }
    reminderDict = {
        }

    today = None
    closestEventDate = None
    farthestEventDate = None
    defaultSettings = UserSettings('mdy', timezoneDict['EST'])

    def __init__(self, client: discord.Client, currDate: datetime.date):
        self.client = client
        return

    def event_date_exists(self, date: datetime.date):
        return self.eventDict.get(date)

    def set_event(self, event: CalenderEvent):
        if self.event_date_exists(event.date):
            self.eventDict[event.date].append(event)
        else:
            eventArray = [event]
            self.eventDict[event.date] = eventArray

        if self.closestEventDate == None or event.date.toordinal() < self.closestEventDate.toordinal():
            self.closestEventDate = event.date;
        if self.farthestEventDate == None or event.date.toordinal() > self.farthestEventDate.tooridinal():
            self.farthestEventDate = event.date
        return

    def get_events_on_date(self, date: datetime.date):
        if self.eventDict.get(date):
            return self.eventDict[date];
        return None

    def send_event_reminder(self):
        return

    def send_event_announcement(self):
        return

    def start_event_routines(self):
        noword = datetime.datetime.utcnow().toordinal()
        eventsToRemove = []
        for k in self.eventDict.fromkeys():
            if k.toordinal() < noword:
                eventsToRemove.append(k)
            else:
                for event in self.eventDict[k]:
                    asyncio.ensure_future(self.__event_message_routine(event))
        for k in eventsToRemove:
            self.eventDict.popitem(k)
        return

    async def __event_message_routine(self, event: CalenderEvent):
        timeUntil = event.dateTime - datetime.datetime.utcnow()
        await asyncio.sleep(timeUntil.total_seconds())
        await client.say(event.name + " is starting now!");
        return

    def load_events(self):
        return

    def save_events(self):
        return

    # 1/5/2019
    # 1/5/19
    # Jan 1, 2019
    # Janurary 1, 2019
    # 1 Janurary 2019