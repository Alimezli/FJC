from pydantic import BaseModel, Field, EmailStr


class UserSchema(BaseModel):
    userID: int = Field(default=None)
    access: str = Field(default=None)
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)
    fullname: str = Field(default=None)
    number: str = Field(default=None)
    credit: int = Field(default=None)

    class config:
        this_schema = {
            "userID": 123,
            "access": "child=2|parent = 1|admin = 0",
            "email": "example@exam.ple",
            "password": "123456",
            "fullname": "name",
            "number": "09120000000",
            "credit": 520000
        }


class UserEmailLoginSchema(BaseModel):
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)

    class config:
        the_schema = {
            "email": "example@exam.ple",
            "password": "123456",
        }


class EmailForgetSchema(BaseModel):
    email: str = Field(default=None)

    class config:
        this_schema = {
            "email": "email@gr.im",
        }


class ChangePasswordSchema(BaseModel):
    CurrentPassword: str = Field(default=None)
    NewPassword: str = Field(default=None)

    class config:
        this_schema = {
            "CurrentPassword ": "123456",
            "NewPassword": "654321"
        }


class NewsSchema(BaseModel):
    Subject: str = Field(default=None)
    Abstract: str = Field(default=None)
    Text: str = Field(default=None)
    PicPath: str = Field(default=None)


class GetNewSchema(BaseModel):
    NewID: int


class AutoDetectSchema(BaseModel):
    Text: str


class SetStatusSchema(BaseModel):
    NewID: int
    Visibility: bool
