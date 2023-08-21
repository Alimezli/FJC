# import json
from fastapi import Body, HTTPException
from pymongo import MongoClient, DESCENDING
from datetime import datetime, timedelta
from app.model import NewsSchema
from app.auth.jwt_handler import get_username_from_jwt
# import NLP

from . import NLP

client = MongoClient('mongodb://localhost:27017/')
UserDB = client['User']
NewsDB = client['News']
CreditDB = client['Credit']
USRCLN = UserDB['USRCollection']
EditorCLN = UserDB['EditorCollection']
NewsCLN = NewsDB['NewsCollection']
CreditCLN = CreditDB['CreditCollection']

ip = ""#"65.21.93.30:8000/"
def FirstPage():
    jsn = {}
    filter_query = {'Visibility': True}
    top_10_news = NewsCLN.find(filter_query).sort("Date", DESCENDING).limit(10)
    i = 0
    for new in top_10_news:
        jsn[i] = {'newsID': new["NewsID"],'title': new['Title'], 'subject': new['Subject'], 'date': new['Date'], 'picture': ip + new['Picture'],
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
        jsn[i] = {'newsID': new["NewsID"],'title': new['Title'], 'subject': new['Subject'], 'date': new['Date'], 'picture': ip + new['Picture'],
                  'text': new['Text']}
        i += 1
    if jsn:
        return jsn
    else:
        return {"msg": "Not Found"}


def ReturnNews(Token):
    userID = get_username_from_jwt(Token)
    userID = userID['userID']
    user = USRCLN.find_one({"userID": userID})
    jsn = {}
    i = 0
    if user['access'] == 'Admin':
        results = NewsCLN.find().sort('Date', DESCENDING).limit(10)
        for new in results:
            status = NewsStatus(new)
            reporter = USRCLN.find_one({'userID': new['ReporterID']})
            reporter = reporter['name']
            jsn[i] = {'newsID': new["NewsID"],'title': new['Title'], 'reporter': reporter, 'subject': new['Subject'], 'date': new['Date'],
                      'status': status}
            i += 1
        return jsn
    elif user['access'] == 'Editor':
        results = NewsCLN.find({'EditorID': userID}).sort('Date', DESCENDING).limit(10)
        for new in results:
            status = NewsStatus(new)
            reporter = USRCLN.find_one({'userID': new['ReporterID']})
            reporter = reporter['name']
            jsn[i] = {'newsID': new["NewsID"],'title': new['Title'], 'reporter': reporter, 'subject': new['Subject'], 'date': new['Date'],
                      'status': status}
            i += 1
        return jsn
    elif user['access'] == 'Reporter':
        results = NewsCLN.find({'ReporterID': userID}).sort('Date', DESCENDING).limit(10)
        for new in results:
            status = NewsStatus(new)
            reporter = USRCLN.find_one({'userID': new['ReporterID']})
            reporter = reporter['name']
            jsn[i] = {'newsID': new["NewsID"],'title': new['Title'], 'reporter': reporter, 'subject': new['Subject'], 'date': new['Date'],
                      'status': status}
            i += 1
        return jsn
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")
        #return {"ERR": "Access denied"}


def AddNew(Token, new: NewsSchema = Body(default=None)):
    NewID = int(NewsCLN.count_documents({})) + 1
    userID = get_username_from_jwt(Token)
    userID = userID['userID']
    Topic = NLP.TopicModeling(new.Text)
    Topics = {'cultur': 'Cultur', 'economy': 'Economy', 'education': 'Education', 'politics': 'Politic',
              'sport': 'Sport'}
    Topic = Topics[Topic]
    Tags = NLP.ReturnTags(new.Text)
    Editor = EditorCLN.find_one({'Title': Topic})
    NewsCLN.insert_one({'NewsID': NewID, 'ReporterID': userID, 'EditorID': Editor["UserID"], 'Date': datetime.now(),
                        'Subject': new.Subject, 'Text': new.Text, 'Title': Topic, 'Picture': new.PicPath, 'Tags': Tags,
                        'Verified': False, 'Visibility': False})
    return {"msg": "add new successful!!", "topic": Topic, "Tags": Tags}

def DelNew(NewID):
    new = NewsCLN.delete_one({"NewsID": NewID})
    return {"msg":"successful"}

def GetNew(NewID):
    new = NewsCLN.find_one({"NewsID": NewID})
    if new:
        return {'NewsID': new['NewsID'], 'ReporterID': new['ReporterID'], 'EditorID': new['EditorID'],
                'Date': new['Date'],
                'Subject': new['Subject'], 'Text': new['Text'], 'Title': new["Title"], 'Picture': ip + new['Picture'],
                'Tags': new['Tags'], 'Verified': new['Verified'], 'Visibility': new['Visibility']}
    else:
        return {}


def SetVisibility(Token, NewID, visibility):
    userID = get_username_from_jwt(Token)
    userID = userID['userID']
    user = USRCLN.find_one({"userID": userID})
    Editor = EditorCLN.find_one({'UserID': userID})
    new = NewsCLN.find_one({"NewsID": NewID})
    if user['access'] == 'Admin' or new['EditorID'] == userID:
        NewsCLN.update_one({"NewID": NewID}, {"$set": {"Visibility": visibility}})
        return {'msg': 'message visibility set'}
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")
        #return {'ERR': 'Access Denied!!'}


def SetVerified(Token, NewID, verified):
    user = get_username_from_jwt(Token)
    userID = user['userID']
    user = USRCLN.find_one({"userID": userID})
    new = NewsCLN.find_one({"NewsID": NewID})
    if user['access'] == 'Admin' or new['EditorID'] == userID:
        NewsCLN.update_one({"NewID": NewID}, {"$set": {"Verified": verified}})
        Reporter = USRCLN.find_one({'userID': new['ReporterID']})
        return {'msg': 'message set verified'}
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")
        #return {'ERR': 'Access denied!!'}


def NewsStatus(new):
    if new['Verified'] and new['Visibility']:
        return 'active'
    elif not new['Verified']:
        return 'verifying'
    else:
        return 'inactive'


def CheckNews(UserID, Visibility):
    Result = []
    print(UserID)
    News = NewsCLN.find({"$or": [{"EditorID": UserID}, {"ReporterID": UserID}], "Visibility": Visibility}).sort("Date", DESCENDING).limit(10)
    user = USRCLN.find_one({"userID": UserID})
    if user['access'] == 'Admin':
        News = NewsCLN.find({"Visibility": Visibility}).sort("Date", DESCENDING).limit(10)
    for New in News:
        n = {
            "newsID": New['NewsID'], "reporter": New["ReporterID"], "editorID": New["EditorID"], "date": New['Date'],
            "subject": New["Subject"],
            "text": New['Text'], "title": New['Title'], "picture": ip + New["Picture"], "tags": New["Tags"],
            "Verified": New["Verified"], "status": New['Visibility']
        }
        Result.append(n)

    return Result


def CountCategories(Category):
    return NewsCLN.count_documents({"Title": Category})
