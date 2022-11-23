import os, sys
sys.path.append("../")

import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup as bs
from AccountServices import *

LiviMenuURL = ('Livingston', 'http://menuportal.dining.rutgers.edu/FoodPro/pickmenu.asp?sName=Rutgers+University+Dining&locationNum=03&locationName=Livingston+Dining+Commons&naFlag=1')
BuschMenuURL = ('Busch', 'http://menuportal.dining.rutgers.edu/foodpro/pickmenu.asp?sName=Rutgers+University+Dining&locationNum=04&locationName=Busch+Dining+Hall&naFlag=1')
CAMenuURL = ('Brower', 'http://menuportal.dining.rutgers.edu/FoodPro/pickmenu.asp?sName=Rutgers+University+Dining&locationNum=01&locationName=Brower+Commons&naFlag=1')
CDMenuURL = ('Nielson', 'http://menuportal.dining.rutgers.edu/FoodPro/pickmenu.asp?sName=Rutgers+University+Dining&locationNum=05&locationName=Neilson+Dining+Hall&naFlag=1')
CampusMenuURLs = [LiviMenuURL, BuschMenuURL, CAMenuURL, CDMenuURL]

'''
Collects the weekly menu for the specified dining hall
'''
def getDiningHallInfo(URLprefix: str = 'http://menuportal.dining.rutgers.edu/FoodPro/') -> None:
    diningHallNames = {'Livingston':'2', 'Busch':'3', 'Nielson':'4', 'Brower':'1'}

	# iterates through each campus food site
    for campus in CampusMenuURLs:
        req = requests.get(campus[1])
        soup = bs(req.text, 'html.parser')

        # iterates through each day menu and collects them
        menuDicts = dict()
        dayURLs = soup.find("select").findAll("option")
        for date in dayURLs:
            dateStr = _dateToString(date.getText())
            dateMenuDict = _getDateMenus(URLprefix + date['value'])
            menuDicts[dateStr] = dateMenuDict

        # adds the dishes with all the information needed
        _addCampusDishes(int(diningHallNames[campus[0]]), menuDicts)

'''
Updates dishes and menuItems tables
'''
def _addCampusDishes(diningHallInt:int, menuDicts:dict):
    cursor, write_conn = setup_cursor("write")

    for day in menuDicts:
        menuDict = menuDicts[day]
        dishes, meal = menuDict['Dishes'], menuDict['Meal']

        for i, dish in enumerate(dishes):
            # check if the item already exists
            # if it doesn't exist, add it into dishes
            cursor.execute("SELECT name FROM dishes WHERE name=?", (dish,))
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO dishes (name) VALUES (%s)", (dish,))
                write_conn.commit()

            # gets the index of current dish
            cursor.execute("SELECT id FROM dishes WHERE name=?", (dish,))
            res = cursor.fetchone()
            id = res[0]

            # add dish and date into menuItems table
            cursor.execute("INSERT INTO menuItems (dish_id, restaurant_id, date, meal_time) VALUES (%d, %d, %s, %s)", (id, diningHallInt, day, meal[i]))
            write_conn.commit()


'''
Returns the date in YYYY-MM-DD form
'''
def _dateToString(fullDate:str):
    # removes the day of the week (will not store this)
    fullDate = fullDate[fullDate.index(' ')+1:]

    # gets the month integer
    spaceInd = fullDate.index(' ')
    monthInt = datetime.strptime(fullDate[:spaceInd], '%B').month
    monthStr = '0'+str(monthInt) if monthInt < 10 else str(monthInt)	# pads beginning zero if needed

    # gets the day
    commaInd = fullDate.index(',')
    dayStr = fullDate[spaceInd+1:commaInd]
    dayStr = '0'+dayStr if int(dayStr) < 10 else dayStr		# pads beginning zero if needed

    # gets the year
    yearStr = fullDate[commaInd+2:]

    return yearStr + '-' + monthStr + '-' + dayStr

'''
Scrapes through each tab to retrieve all information
'''
def _getDateMenus(URL: str, URLprefix: str = 'http://menuportal.dining.rutgers.edu/FoodPro/') -> pd.DataFrame:
    req = requests.get(URL)
    soup = bs(req.text, 'html.parser')

    # collects all meal time URLs
    mealURLs = dict()
    for t in soup.find_all('div', 'tab'):
        if 'active' in t['class']:
            mealURLs[t.getText()] = None
            continue
        mealURLs[t.getText()] = t.find('a')['href']

    # collects each day's menu
    prevLen = 0
    menuItems, mealType = list(), list()
    for t in mealURLs:
        currURL = URLprefix + mealURLs[t] if mealURLs[t] else URL
        req = requests.get(currURL)
        soup = bs(req.text, 'html.parser')

        # collecting menu items and type
        menuItems += [i.getText() for i in soup.find_all('div', 'col-1')]
        mealType += [t for _ in range(len(menuItems) - prevLen)]

    menuData = {
            'Dishes': menuItems,
            'Meal': mealType
            }

    return menuData

'''
Deletes all items from menuItems table
'''
def clearMenuItemsTable():
    cursor, write_conn = setup_cursor("write")
    cursor.execute("DELETE FROM menuItems")
    write_conn.commit()

def main():
    clearMenuItemsTable()
    getDiningHallInfo()

if __name__ == "__main__":
    main()
