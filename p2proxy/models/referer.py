from peewee import *
import peewee_async
from pydantic import BaseModel, validator
import validators
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import os


# db = SqliteDatabase('db.sqlite')
db = peewee_async.PostgresqlDatabase(
    database="qiwip2proxy",
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PSSWD"),
    host=os.environ.get("DB_HOST"),
    port=int(os.environ.get("DB_PORT")),
)


class Referer(Model):
    uid = UUIDField()
    referer = CharField(max_length=256)
    is_public = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now, formats="'%Y-%m-%d %H:%M:%S")

    class Meta:
        database = db


class RequestReferer(BaseModel):
    referer: str
    is_public: Optional[bool] = False

    @validator("referer")
    def referer_must_be_url(cls, url):
        if validators.url(url):
            return url
        raise ValueError("referer must be url")


class RequestGetByUid(BaseModel):
    uid: str

    @validator("uid")
    def referer_must_be_url(cls, uid):
        if validators.uuid(uid):
            return uid
        raise ValueError("uid must be in UUID-like format")


class ResponseReferer(BaseModel):
    referer: str
    uid: UUID
    is_public: bool


class ResponseReferers(BaseModel):
    referers: List[ResponseReferer]
