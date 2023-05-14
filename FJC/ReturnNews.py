from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
UserDB = client['User']
NewsDB = client['News']
CreditDB = client['Credit']
USRCLN = UserDB['USRCollection']
EditorCLN = UserDB['EditorCollection']
NewsCLN = NewsDB['NewsCollection']
CreditCLN = CreditDB['CreditCollection']

def FirstPage():
    count = NewsCLN.count_documents({'NewsID':''})
    print(count)
FirstPage()