CUISINE_TAGS = ['chinese', 'indian', 'mexican', 'italian', 'japanese', 'cafe', 'dessert', 'mediterranean', 'middle_eastern']
MEAT_TAGS = ['chicken', 'pork', 'beef', 'seafood', 'dairy', 'nuts']
DB_DH_STR = {"Livingston":"Livingston DH", "Busch":"Busch DH", "Brower":"Brower DH", "Neilson":"Neilson DH"}
MEAL_TIMES = ['breakfast', 'lunch', 'dinner']
DB_DH_IDS = {1:"Brower DH", 2:"Livingston DH", 3:"Busch DH", 4:"Neilson DH"}

'''
Extracts only the first values from a tuple
FUNCTIONING
'''
def isolateFirstValueFromTuple(resultSet):
    return [tup[0] for tup in resultSet]

'''
Isolates tags from all other information
FUNCTIONING
'''
def isolateTagNames(whitelistResultSet, blacklistResultSet):
    return isolateFirstValueFromTuple(whitelistResultSet), isolateFirstValueFromTuple(blacklistResultSet)

'''
User preferences for include and diet are obtained directly from HTML and combined
FUNCTIONING
'''
def synthesizeWhitelist(includeList, dietList):
    fullIncludeList = includeList + dietList
    return fullIncludeList