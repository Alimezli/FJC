# import json
from pymongo import MongoClient, DESCENDING
from datetime import datetime, timedelta

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
        return {"msg":"متاسفانه چیری یافت نشد."}


def ReturnAllNews():
    jsn = {}
    results = NewsCLN.find()
    i = 0
    for new in results:
        status = ''
        if new['Verify'] == True and new['Visibility'] == True:
            status = 'active'
        elif new['Verify'] == False:
            status = 'verifying'
        else:
            status = 'disable'
        reporter = USRCLN.find({'UserID':new['ReporteID']})['name']
        jsn[i] = {'title': new['Title'],'reporter' : reporter, 'subject': new['Subject'], 'date': new['Date']}
        i += 1