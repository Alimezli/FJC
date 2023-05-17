import datetime
from app.auth.jwt_bearer import jwtBearer
from app.auth.jwt_handler import get_username_from_jwt
from app.model import UserEmailLoginSchema, UserSchema, ChangePasswordSchema, EmailForgetSchema
from fastapi import FastAPI, Body, Depends
from pymongo import MongoClient
from starlette.middleware.cors import CORSMiddleware
from FJC import ReturnNews, Auth

client = MongoClient('mongodb://localhost:27017/')
UserDB = client['User']
NewsDB = client['News']
CreditDB = client['Credit']
USRCLN = UserDB['USRCollection']
EditorCLN = UserDB['EditorCollection']
NewsCLN = NewsDB['NewsCollection']
CreditCLN = CreditDB['CreditCollection']

# USRCLN.insert_one({'userID':2,'name':'ali','access':'Editor','email':'mmd@mmd.ir','password':'123456','credit':555})
# collection.insert_one({'CreditID':2, 'NewsID':3 ,'date':datetime.datetime.now(),'from':'economic','to':12,'Info':'dash karet ali bood!'})
# collection.insert_one({'NewsID':2,'Title':'hi','date':datetime.datetime.now(),'Subject':'economic','PicUrl':'pics/2.jpg','Text':'hi bro','tags':['economic','blah blah']})

# NewsCLN.insert_one({'NewsID': i,'ReporteID': 10 ,'EditorID': 2 ,'Date':datetime.datetime.now(),'Subject':'President','Text':'President is alive.','Picture':'data/pic1.jpg','Verified':False,'Visibility':False})
# EditorCLN.insert_one({'UserID':2,'Title':'economic'})

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# this funtion will return the index of top 10 newest news.
@app.get("/")
async def index():
    return ReturnNews.FirstPage()


@app.get('/daily')
async def msgOfDay():
    return ReturnNews.DayMessage()


@app.post("/user/signup", tags=["user"])
def user_signup(user: UserSchema = Body(default=None)):
    return Auth.user_signup(user)


@app.post('/user/EmailLogin', tags=["user"])
def user_login(user: UserEmailLoginSchema = Body(default=None)):
    return Auth.User_EmailLogin(user)


@app.post('/user/forget', tags=["user"])
def reset_pass(email: EmailForgetSchema = Body(default=None)):
    return Auth.User_Forget(email.email)


@app.post('/user/reset/', tags=["user"])
def reset_pass(Token: str = Body(default=None), password: str = Body(default=None)):
    print(Token)
    return Auth.Reset_Password(Token, password, password)

@app.post('/user/ChangePassword', dependencies=[Depends(jwtBearer()), ], tags=["user"])
def change_password(Password: ChangePasswordSchema, token: str = Depends(jwtBearer())):
    user = get_username_from_jwt(token)
    if user:
        userID = user['userID']
        print(userID, type(userID))
        return Auth.Change_Password(Password.CurrentPassword, Password.NewPassword, userID)
    else:
        return {"ERR": "Token Not valid."}

@app.get('/search/{query}')
async def search(query:str):
    return ReturnNews.search(query)