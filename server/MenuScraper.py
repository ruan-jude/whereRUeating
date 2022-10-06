import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from tabulate import tabulate

LiviMenuURL = ('Livingston', 'http://menuportal.dining.rutgers.edu/FoodPro/pickmenu.asp?sName=Rutgers+University+Dining&locationNum=03&locationName=Livingston+Dining+Commons&naFlag=1')
BuschMenuURL = ('Busch', 'http://menuportal.dining.rutgers.edu/foodpro/pickmenu.asp?sName=Rutgers+University+Dining&locationNum=04&locationName=Busch+Dining+Hall&naFlag=1')
CAMenuURL = ('Brower', 'http://menuportal.dining.rutgers.edu/FoodPro/pickmenu.asp?sName=Rutgers+University+Dining&locationNum=01&locationName=Brower+Commons&naFlag=1')
CDMenuURL = ('Nielson', 'http://menuportal.dining.rutgers.edu/FoodPro/pickmenu.asp?sName=Rutgers+University+Dining&locationNum=05&locationName=Neilson+Dining+Hall&naFlag=1')
CampusMenuURLs = [LiviMenuURL, BuschMenuURL, CAMenuURL, CDMenuURL]

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
            dateMenu = getDateMenus(URLprefix + date['value'], campus[0])
            results[date.getText()] = pd.concat([results[date.getText()], dateMenu]) if date.getText() in results else dateMenu

    for date in results:
        print('===== ' + date + ' =====')
        print(tabulate(results[date], headers = 'keys', tablefmt = 'psql'))

'''
Scrapes through each tab to retrieve all information
'''
def getDateMenus(URL: str, campus: str, URLprefix: str = 'http://menuportal.dining.rutgers.edu/FoodPro/') -> pd.DataFrame:
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

    df = pd.DataFrame({
        'Menu Item': menuItems,
        'Serving Size' : servingSize,
        'Meal Type': mealType,
        'Campus': campus
    })  

    return df

getDiningHallInfo(CAMenuURL)


