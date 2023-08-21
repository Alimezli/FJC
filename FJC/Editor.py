from fastapi import HTTPException
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
    admin = USRCLN.find_one({'userID': int(userID),'access':"Admin"})
    user = USRCLN.find_one({'userID': int(userID)})
    if admin:
        Unvarified = int(NewsCLN.count_documents({ "Verified": False}))
        InVisible = int(NewsCLN.count_documents({ "Visibility": False}))
        Visible = int(NewsCLN.count_documents({"Visibility": True}))
        return {"Unvarified": Unvarified, "InVisible": InVisible, "Visible":Visible }
    elif Editor:
        Unvarified = int(NewsCLN.count_documents({"EditorID": int(userID), "Verified": False}))
        InVisible = int(NewsCLN.count_documents({"EditorID": int(userID), "Visibility": False}))
        Visible = int(NewsCLN.count_documents({"EditorID": int(userID), "Visibility": True}))
        return {"Unvarified": Unvarified, "InVisible": InVisible, "Visible":Visible }
    elif user:
        Unvarified = int(NewsCLN.count_documents({"ReporterID": int(userID), "Verified": False}))
        InVisible = int(NewsCLN.count_documents({"ReporterID": int(userID), "Visibility": False}))
        Visible = int(NewsCLN.count_documents({"ReporterID": int(userID), "Visibility": True}))
        return {"Unvarified": Unvarified, "InVisible": InVisible, "Visible":Visible }
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")
        #return {"ERR": "You are Not Editor."}

def EditorCount(Title):
    return EditorCLN.count_documents({'Title': Title})
