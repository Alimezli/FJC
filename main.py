import datetime

from fastapi import FastAPI
from pymongo import MongoClient
from starlette.middleware.cors import CORSMiddleware
from FJC import ReturnNews
client = MongoClient('mongodb://localhost:27017/')
UserDB = client['User']
NewsDB = client['News']
CreditDB = client['Credit']
USRCLN = UserDB['USRCollection']
EditorCLN = UserDB['EditorCollection']
NewsCLN = NewsDB['NewsCollection']
CreditCLN = CreditDB['CreditCollection']

#USRCLN.insert_one({'userID':2,'name':'ali','access':'Editor','email':'mmd@mmd.ir','password':'123456','credit':555})
#collection.insert_one({'CreditID':2, 'NewsID':3 ,'date':datetime.datetime.now(),'from':'economic','to':12,'Info':'dash karet ali bood!'})
#collection.insert_one({'NewsID':2,'Title':'hi','date':datetime.datetime.now(),'Subject':'economic','PicUrl':'pics/2.jpg','Text':'hi bro','tags':['economic','blah blah']})

#NewsCLN.insert_one({'NewsID': i,'ReporteID': 10 ,'EditorID': 2 ,'Date':datetime.datetime.now(),'Subject':'President','Text':'President is alive.','Picture':'data/pic1.jpg','Verified':False,'Visibility':False})
#EditorCLN.insert_one({'UserID':2,'Title':'economic'})

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#this funtion will return the index of top 10 newest news.
@app.get("/")
async def index():
    return ReturnNews.FirstPage()


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
