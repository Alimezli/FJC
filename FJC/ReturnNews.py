# import json
from fastapi import Body
from pymongo import MongoClient, DESCENDING
from datetime import datetime, timedelta
from app.model import NewsSchema
from app.auth.jwt_handler import get_username_from_jwt

# from . import NLP

client = MongoClient('mongodb://localhost:27017/')
UserDB = client['User']
NewsDB = client['News']
CreditDB = client['Credit']
USRCLN = UserDB['USRCollection']
EditorCLN = UserDB['EditorCollection']
NewsCLN = NewsDB['NewsCollection']
CreditCLN = CreditDB['CreditCollection']


def FirstPage():
    jsn = {}
    filter_query = {'Visibility': True}
    top_10_news = NewsCLN.find(filter_query).sort("Date", DESCENDING).limit(10)
    i = 0
    for new in top_10_news:
        jsn[i] = {'title': new['Title'], 'subject': new['Subject'], 'date': new['Date'], 'picture': new['Picture'],
                  'text': new['Text']}
        i += 1
    return jsn


def DayMessage():
    today = datetime.utcnow()
    start_of_day = datetime(today.year, today.month, today.day)
    end_of_day = start_of_day + timedelta(days=1)
    filter_query = {'visibility': True, 'Date': {'$gte': start_of_day, '$lt': end_of_day}}
    results = NewsCLN.find(filter_query)
    if results:
        return results
    else:
        return {"msg": "هیچ رویدادی وجود ندارد."}


def search(query):
    jsn = {}
    filter_query = {'Visibility': True, 'Text': {'$regex': query}}
    results = NewsCLN.find(filter_query).sort('Date', DESCENDING).limit(5)
    i = 0
    for new in results:
        jsn[i] = {'title': new['Title'], 'subject': new['Subject'], 'date': new['Date'], 'picture': new['Picture'],
                  'text': new['Text']}
        i += 1
    if jsn:
        return jsn
    else:
        return {"msg": "متاسفانه چیری یافت نشد."}


def ReturnNews(Token):
    userID = get_username_from_jwt(Token)
    userID = userID['userID']
    user = USRCLN.find_one({"userID": userID})
    jsn = {}
    i = 0
    if user['access'] == 'Admin':
        results = NewsCLN.find()
        for new in results:
            status = NewsStatus(new)
            reporter = USRCLN.find_one({'userID': new['ReporterID']})
            reporter = reporter['name']
            jsn[i] = {'title': new['Title'], 'reporter': reporter, 'subject': new['Subject'], 'date': new['Date'],
                      'status': status}
            i += 1
        return jsn
    elif user['access'] == 'Editor':
        results = NewsCLN.find({'EditorID': userID})
        for new in results:
            status = NewsStatus(new)
            reporter = USRCLN.find_one({'userID': new['ReporterID']})
            reporter = reporter['name']
            jsn[i] = {'title': new['Title'], 'reporter': reporter, 'subject': new['Subject'], 'date': new['Date'],
                      'status': status}
            i += 1
        return jsn
    else:
        return {"ERR": "Access denied"}


def AddNew(Token, new: NewsSchema = Body(default=None)):
    NewID = int(USRCLN.count_documents({})) + 1
    userID = get_username_from_jwt(Token)
    userID = userID['userID']
    Topic = 'NLP.TopicModeling(new.Text)'
    Topics = {'cultur': 'Cultur', 'economy': 'Economy', 'education': 'Education', 'politics': 'Politic',
              'sport': 'Sport'}
    Topic = Topics[Topic]
    EditorID = EditorCLN.find_one({'Title': Topic})
    NewsCLN.insert_one({'NewsID': NewID, 'ReporterID': userID, 'EditorID': EditorID, 'Date': datetime.datetime.now(),
                        'Subject': new.Subject, 'Text': new.Text, 'Title': Topic, 'Picture': new.PicPath, 'Tags': [''],
                        'Verified': False, 'Visibility': False})


def SetVisibility(Token, NewID, visibility):
    userID = get_username_from_jwt(Token)
    userID = userID['userID']
    user = USRCLN.find_one({"userID": userID})
    Editor = EditorCLN.find_one({'UserID': userID})
    new = NewsCLN.find_one({"NewID": NewID})
    if user['access'] == 'Admin' or (user['access'] == 'Editor' and new['Title'] == Editor['Title']):
        NewsCLN.update_one({"NewID": NewID}, {"$set": {"Visibility": visibility}})
        return {'msg': 'message set visible'}
    else:
        return {'ERR': 'Access Denied!!'}


def SetVerified(Token, NewID, verified):
    userID = get_username_from_jwt(Token)
    userID = userID['userID']
    user = USRCLN.find_one({"userID": userID})
    Editor = EditorCLN.find_one({'UserID': userID})
    new = NewsCLN.find_one({"NewID": NewID})
    if user['access'] == 'Admin' or (user['access'] == 'Editor' and new['Title'] == Editor['Title']):
        NewsCLN.update_one({"NewID": NewID}, {"$set": {"Verified": verified}})
        Reporter = USRCLN.find_one({'userID': new['ReporterID']})
        return {'msg': 'message set verifieed'}
    else:
        return {'ERR': 'Access denied!!'}


def NewsStatus(new):
    if new['Verified'] and new['Visibility']:
        return 'active'
    elif not new['Verified']:
        return 'verifying'
    else:
        return 'inactive'
