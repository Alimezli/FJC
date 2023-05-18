from datetime import datetime, timedelta
from fastapi import Body
from app.model import UserEmailLoginSchema, UserSchema, EmailForgetSchema, ChangePasswordSchema
from app.auth.jwt_handler import signJWT, get_username_from_jwt
from app.auth.jwt_bearer import jwtBearer
from pymongo import MongoClient
import json
import secrets

client = MongoClient('localhost', 27017)
UserDB = client['User']
CreditDB = client['Credit']
USRCLN = UserDB['USRCollection']  # collection
EditorCLN = UserDB['EditorCollection']
resetsCLN = UserDB["ResetsCollection"]
CreditCLN = CreditDB['CreditCollection']


def user_signup(user: UserSchema = Body(default=None)):
    ValidEmail = USRCLN.find_one({"email": user.email})
    if ValidEmail:
        return {"ERR": "this email aleardy exist"}
    elif user.access == "admin":
        return {"ERR": "You don't have premission to do this."}
    user.userID = int(USRCLN.count_documents({})) + 1
    userJson = json.loads(user.json())
    USRCLN.insert_one(userJson)
    signJWT(user.userID, user.access)
    print(f"signup:{user}")
    return {"msg": "user added!!"}


def check_email(data: UserEmailLoginSchema):
    user = USRCLN.find_one({"email": data.email})
    if user:
        if user['email'] == data.email and user['password'] == data.password:
            return True
    return False


def User_EmailLogin(user: UserEmailLoginSchema = Body(default=None)):
    if check_email(user):
        usr = USRCLN.find_one({"email": user.email})
        access = usr['access']
        return signJWT(usr["userID"], access)
    else:
        return {"ERR": "email or password invalid!!"}


def User_Forget(email):
    usr = USRCLN.find_one({"email": email})
    if usr:
        expires = datetime.now() + timedelta(hours=1)
        Token = secrets.token_hex(16)
        reset_data = resetsCLN.find_one({"userID": usr['userID']})
        if reset_data:
            resetsCLN.update_one({"userID": usr['userID']}, {"$set": {"Token": Token, "expires": expires}})
        else:
            resetsCLN.insert_one({"userID": usr['userID'], "Token": Token, "expires": expires})
        print(Token)
        return {"msg": "reset link sent"}
    else:
        return {"ERR": "user not found"}


def Reset_Password(Token, New_Password, re_enter):
    usrTKN = resetsCLN.find_one({"Token": Token})
    if usrTKN:
        if usrTKN['expires'] > datetime.now():
            usr = USRCLN.find_one({"userID": usrTKN["userID"]})
            if New_Password == re_enter:
                if len(New_Password) >= 8:
                    USRCLN.update_one({"userID": usr['userID']}, {"$set": {"password": New_Password}})
                    resetsCLN.delete_one({"Token": Token})
                    return {"msg": "password successfuly changed."}
                else:
                    return {"ERR": "password must be longer than 8 character."}
            else:
                return {"ERR": "your re_entered password incorrect."}
        else:
            return {"ERR": "token expired"}
    else:
        return {"ERR": "invalid token"}


def Change_Password(CurrentPassword, NewPassword, userID):
    usr = USRCLN.find_one({"userID": userID})
    if CurrentPassword == usr['password']:
        if CurrentPassword == NewPassword:
            return {'ERR': "you can't change password to your current password."}
        elif len(NewPassword) >= 8:
            USRCLN.update_one({"userID": usr['userID']}, {"$set": {"password": NewPassword}})
            return {"msg": "password successfuly changed."}
        else:
            return {"ERR": "password must be longer than 8 character."}
    else:
        return {"ERR": "your current password incorrect."}
