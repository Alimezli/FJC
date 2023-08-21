import datetime

import uvicorn

from app.auth.jwt_bearer import jwtBearer
from app.auth.jwt_handler import get_username_from_jwt
from app.model import UserEmailLoginSchema, UserSchema, ChangePasswordSchema, EmailForgetSchema, NewsSchema, \
    GetNewSchema, AutoDetectSchema, SetStatusSchema, CheckNewsSchema
from fastapi import FastAPI, Body, Depends, HTTPException
from pymongo import MongoClient
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from FJC import ReturnNews, Auth, Editor, NLP

client = MongoClient('mongodb://localhost:27017/')
UserDB = client['User']
NewsDB = client['News']
CreditDB = client['Credit']
USRCLN = UserDB['USRCollection']
EditorCLN = UserDB['EditorCollection']
NewsCLN = NewsDB['NewsCollection']
CreditCLN = CreditDB['CreditCollection']

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount('/Data/Pictures', StaticFiles(directory="Data/Pictures"), name="static")

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


@app.get('/News/search/{query}')
async def search(query: str):
    return ReturnNews.search(query)


@app.post('/News/AddNew', dependencies=[Depends(jwtBearer()), ], tags=["News"])
async def AddNews(new: NewsSchema, token: str = Depends(jwtBearer())):
    return ReturnNews.AddNew(token, new)

@app.post('/News/DelNew', dependencies=[Depends(jwtBearer()), ], tags=["News"])
async def DelNews(New: GetNewSchema, token: str = Depends(jwtBearer())):
    return ReturnNews.DelNew( New.NewID)

@app.post('/News/GetNew', tags=["News"])
async def GetNews(New: GetNewSchema):
    return ReturnNews.GetNew(New.NewID)


@app.post('/News/AutoDetect', dependencies=[Depends(jwtBearer()), ], tags=["News"])
async def AutoDetect(text: AutoDetectSchema):
    return {'Title': NLP.TopicModeling(text.Text), 'Tags': str(NLP.ReturnTags(text.Text)).replace('[','').replace(']','')}


@app.post('/News/SetStatus', dependencies=[Depends(jwtBearer()), ], tags=["News", "Admin", "Editor"])
async def SetStatus(New: SetStatusSchema, token: str = Depends(jwtBearer())):
    ReturnNews.SetVerified(token, int(New.NewID), New.Visibility)
    return ReturnNews.SetVisibility(token, int(New.NewID), New.Visibility)


@app.get('/News/ReturnNews', dependencies=[Depends(jwtBearer()), ], tags=["Admin"])
async def Allnews(token: str = Depends(jwtBearer())):
    return ReturnNews.ReturnNews(token)


@app.get('/Admin/Class/1', dependencies=[Depends(jwtBearer()), ], tags=["Admin"])
async def AdminStatus(token: str = Depends(jwtBearer())):
    user = get_username_from_jwt(token)
    userAccess = user['access']
    if userAccess == 'Admin':
        Reporter = USRCLN.count_documents({'access': 'Reporter'})
        News = NewsCLN.count_documents({})
        View = 10
        return {'ReporterCount': Reporter, 'NewsCount': News, 'Veiw': View}
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")
        #return {"ERR": "Access Denied"}


@app.get('/Admin/Class/2', dependencies=[Depends(jwtBearer()), ], tags=["Admin"])
async def AdminStatus(token: str = Depends(jwtBearer())):
    user = get_username_from_jwt(token)
    userAccess = user['access']
    if userAccess == 'Admin':
        Cultur = ReturnNews.CountCategories('Cultur')
        Economy = ReturnNews.CountCategories('Economy')
        Education = ReturnNews.CountCategories('Education')
        Politic = ReturnNews.CountCategories('Politic')
        Sport = ReturnNews.CountCategories('sport')  # Sport
        CulturEditor = Editor.EditorCount('Cultur')
        EconomyEditor = Editor.EditorCount('Economy')
        EducationEditor = Editor.EditorCount('Education')
        PoliticEditor = Editor.EditorCount('Politic')
        SportEditor = Editor.EditorCount('sport')  # Sport
        Reporter = USRCLN.count_documents({'access': 'Reporter'})

        return {'CulturNews': Cultur, "EconomyNews": Economy, "EducationNews": Education, 'PoliticNews': Politic,
                "SportNews": Sport, "CulturEditor": CulturEditor, 'EconomyEditor': EconomyEditor,
                'EducationEditor': EducationEditor, 'PoliticEditor': PoliticEditor, 'SportEditor': SportEditor,
                'Reporter': Reporter}
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")
        #return {"ERR": "Access Denied"}


@app.get('/Editor/Class/1', dependencies=[Depends(jwtBearer()), ], tags=["Editor"])
async def EditorStatus(token: str = Depends(jwtBearer())):
    user = get_username_from_jwt(token)
    userID = user['userID']
    Reporter = USRCLN.count_documents({'access': 'Reporter'})
    News = NewsCLN.count_documents({})
    View = 10
    return {'ReporterCount': Reporter, 'NewsCount': News, 'Veiw': View}


@app.get('/Editor/Class/2', dependencies=[Depends(jwtBearer()), ], tags=["Editor"])
async def EditorStatus(token: str = Depends(jwtBearer())):
    user = get_username_from_jwt(token)
    userID = user['userID']
    
    return Editor.EditorStatus(userID)


@app.post('/News/Check', dependencies=[Depends(jwtBearer()), ], tags=["Editor"])
async def CheckNews(param: CheckNewsSchema, token: str = Depends(jwtBearer())):
    UserID = get_username_from_jwt(token)['userID']
    Visibility = param.Visibility
    print(UserID,Visibility)
    return ReturnNews.CheckNews(UserID, Visibility)


if __name__ == "__main__":
    uvicorn.run(app, host="65.21.93.30", port=8000)
