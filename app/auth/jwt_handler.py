# this file is responsible  fo signing, encoding,decoding and returning jwts
import time
import jwt
from pydantic import BaseModel,Field,EmailStr
from decouple import config

JWT_SECRET = config('secret')
JWT_ALGORITHM = config('algorithm')

#return generated token (Jwts)
def token_responces(token:str):
    return {
        "access token": token
    }

def signJWT(userID:int,access:str):
    payload = {
        "userID": userID,
        "access": access,
        "expiry": time.time() + 600
    }
    token = jwt.encode(payload,JWT_SECRET,algorithm = JWT_ALGORITHM)
    return token_responces(token)

def decodeJWT(token:str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decode_token if decode_token['expires'] >= time.time() else None
    except:
        return {}

def get_username_from_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET,algorithms=JWT_ALGORITHM)
        print(payload)

    except:
        payload = ''


    return payload