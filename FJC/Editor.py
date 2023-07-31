from pymongo import MongoClient

client = MongoClient('localhost', 27017)
UserDB = client['User']
NewsDB = client['News']
CreditDB = client['Credit']
USRCLN = UserDB['USRCollection']
EditorCLN = UserDB['EditorCollection']
NewsCLN = NewsDB['NewsCollection']
CreditCLN = CreditDB['CreditCollection']


def EditorStatus(userID):
    Editor = EditorCLN.find_one({'UserID': int(userID)})
    if Editor:
        Unvarified = int(NewsCLN.count_documents({"EditorID": int(userID), "Verified": False}))
        InVisible = int(NewsCLN.count_documents({"EditorID": int(userID), "Visibility": False}))
        Visible = int(NewsCLN.count_documents({"EditorID": int(userID), "Visibility": True}))
        return {"Unvarified": Unvarified, "InVisible": InVisible, "Visible":Visible }
    else:
        return {"ERR": "You are Not Editor."}

def EditorCount(Title):
    return EditorCLN.count_documents({'Title': Title})
