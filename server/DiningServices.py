import time

global busy_class_end_times = []

def check_dining_halls_busy():
    current_time = time.localtime()
    
    busy_threshold = 1
    
    for end_time in busy_class_end_times:
        if current_time >= end_time and (current_time - end_time) < busy_threshold:
            return "Classes just ended at " + str(end_time) + ", so the dining halls might get busy now."
            
            
            
def check_for_events():
    print("doing something now")
    
    

