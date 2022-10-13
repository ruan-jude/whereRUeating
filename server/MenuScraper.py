import mariadb
import requests
import pandas as pd
from tabulate import tabulate
from bs4 import BeautifulSoup as bs

LiviMenuURL = ('Livingston', 'http://menuportal.dining.rutgers.edu/FoodPro/pickmenu.asp?sName=Rutgers+University+Dining&locationNum=03&locationName=Livingston+Dining+Commons&naFlag=1')
BuschMenuURL = ('Busch', 'http://menuportal.dining.rutgers.edu/foodpro/pickmenu.asp?sName=Rutgers+University+Dining&locationNum=04&locationName=Busch+Dining+Hall&naFlag=1')
CAMenuURL = ('Brower', 'http://menuportal.dining.rutgers.edu/FoodPro/pickmenu.asp?sName=Rutgers+University+Dining&locationNum=01&locationName=Brower+Commons&naFlag=1')
CDMenuURL = ('Nielson', 'http://menuportal.dining.rutgers.edu/FoodPro/pickmenu.asp?sName=Rutgers+University+Dining&locationNum=05&locationName=Neilson+Dining+Hall&naFlag=1')
CampusMenuURLs = [LiviMenuURL, BuschMenuURL, CAMenuURL, CDMenuURL]

'''
Sets up connection to database
'''
def setupCursor():
    db_user = "root"
    db_pwd = "VARRC"

    # attempts connection to MariaDB through the root user
    try:
        conn = mariadb.connect(
                user = db_user,
                password = db_pwd,
                port = 3306,
                database = "whereRUeating"
                )
        conn.autocommit = False
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")

    cursor = conn.cursor()
    return cursor, conn

'''
Collects the weekly menu for the specified dining hall
'''
def getDiningHallInfo(diningHallURL: str, URLprefix: str = 'http://menuportal.dining.rutgers.edu/FoodPro/') -> None:
    results = dict()

    for campus in CampusMenuURLs:
        req = requests.get(campus[1])
        soup = bs(req.text, 'html.parser')

        # collecting date and URLs of the weekly menu
        dateURL = soup.find("select").findAll("option")
        for date in dateURL:
            dateMenuDict = _getDateMenus(URLprefix + date['value'], campus[0])
            dateMenuDF = pd.DataFrame(dateMenuDict)
            results[date.getText()] = pd.concat([results[date.getText()], dateMenuDF]) if date.getText() in results else dateMenuDF

    return dateMenuDict
'''
    for date in results:
        print('===== ' + date + ' =====')
        print(tabulate(results[date], headers = 'keys', tablefmt = 'psql'))
    '''

'''
Scrapes through each tab to retrieve all information
'''
def _getDateMenus(URL: str, campus: str, URLprefix: str = 'http://menuportal.dining.rutgers.edu/FoodPro/') -> pd.DataFrame:
    req = requests.get(URL)
    soup = bs(req.text, 'html.parser')

    # collects all other tabs URLS
    tabURLs = dict()
    for t in soup.find_all('div', 'tab'):
        if 'active' in t['class']:
            tabURLs[t.getText()] = None
            continue
        tabURLs[t.getText()] = t.find('a')['href']

    # prints each meal's menu
    prevLen = 0
    menuItems, servingSize, mealType = list(), list(), list()
    for t in tabURLs:
        currURL = URLprefix + tabURLs[t] if tabURLs[t] else URL
        req = requests.get(currURL)
        soup = bs(req.text, 'html.parser')

        # collecting menu items and serving size
        menuItems += [i.getText() for i in soup.find_all('div', 'col-1')]
        servingSize += [s.getText() for s in soup.find_all('div', 'col-2')]
        mealType += [t for _ in range(len(menuItems) - prevLen)]
        prevLen = len(menuItems)

    campus = [campus for _ in range(prevLen)]

    menuData = {
            'Menu Item': menuItems,
            'Serving Size' : servingSize,
            'Meal Type': mealType,
            'Campus': campus
            }

    df = pd.DataFrame(menuData)

    return menuData

'''
Adds dishes into the dishes table through MariaDB
'''
def addDishes(itemList):
    cursor, write_conn = setupCursor()

    for item in itemList:
        # check if the item already exists
        cursor.execute("SELECT name FROM dishes WHERE name=?", (item,))
        if cursor.rowcount != 0:
            print('ERROR: Dish already exists')
            continue

        # adds item into the table
        cursor.execute("INSERT INTO dishes (name) VALUES (%s)", (item,))
        write_conn.commit()

        # gets the id of the item
        #cursor.execute()



def main():
    #for ()

    menuData = getDiningHallInfo(CAMenuURL)
    #print(menuData['Campus'])
    addDishes(menuData['Menu Item'])


if __name__ == "__main__":
    main()
