import datetime

busy_class_end_times = [datetime.time(11,40,0), datetime.time(13,20, 0), datetime.time(15,20,0), datetime.time(18,0,0)]

def check_dining_halls_busy():
    current_time = datetime.datetime.now()
    current_minute = current_time.minute
    current_hour = current_time.hour

    for end_time in busy_class_end_times:

        if (current_hour - end_time.hour) == 0 and current_minute >= end_time.minute:
            return "Classes just ended at " + datetime.datetime.strptime(str(end_time),'%H:%M:%S').strftime('%I:%M %p') + ", so the dining halls might get/be busy now."

        elif current_hour - end_time.hour == 1 and current_minute < end_time.minute:
            return "Classes just ended at " + datetime.datetime.strptime(str(end_time),'%H:%M:%S').strftime('%I:%M %p') + ", so the dining halls might get/be busy now."
        
        elif end_time.hour >= current_hour and end_time.hour - current_hour <= 1 and (current_minute >= 30):
            return "Classes will end soon at " + datetime.datetime.strptime(str(end_time),'%H:%M:%S').strftime('%I:%M %p') + ", and the dining halls will get busier."
     
    return "Probably not busy at this time."

def get_off_campus_restaurants():
    print("doing something")
    

def check_for_events():
    print("doing something now")

if __name__ == '__main__':
    print(check_dining_halls_busy())
    
    

