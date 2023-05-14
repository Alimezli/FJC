#import json
from pymongo import MongoClient , DESCENDING

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

        jsn[i] = {'title' : new['Title'], 'subject': new['Subject'],'date': new['Date'], 'picture':new['Picture'],'text':new['Text']}
        i += 1
    return jsn