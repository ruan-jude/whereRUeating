import datetime

busy_class_end_times = [datetime.time(11,40,0), datetime.time(13,20, 0), datetime.time(15,20,0)]

def check_dining_halls_busy():
    current_minute = datetime.datetime.now().minute
    current_hour = datetime.datetime.now().hour
    
    for end_time in busy_class_end_times:
        if current_hour >= end_time.hour and current_minute >= end_time.minute and (current_hour - end_time.hour) == 0:
            return "Classes just ended at " + str(end_time) + ", so the dining halls might get busy now."
        elif end_time.hour >= current_hour and end_time.hour - current_hour <= 1: #and (current_minute >= 30) :
            return "Classes will end soon at " + str(end_time) + ", and the dining halls will get busier." 
            
def check_for_events():
    print("doing something now")

if __name__ == '__main__':
    # sometime = datetime.time(15,20,0)
    # currentTime = datetime.datetime.now()
    # print(sometime.hour)
    # print(currentTime.hour)
    # print(currentTime > sometime)
    print(check_dining_halls_busy())
    
    

