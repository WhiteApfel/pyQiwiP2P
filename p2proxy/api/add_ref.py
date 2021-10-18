from models import (
    Referer,
    RequestReferer,
    P2ProxyError,
    ResponseReferer,
    RequestGetByUid,
    ResponseReferers,
)
from app import app
from uuid import uuid4, UUID
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@app.post("/api/v1/add_referer", response_model=ResponseReferer)
async def api_add_referer(data: RequestReferer):
    referer = Referer.get_or_none(Referer.referer == data.referer)
    if not referer:
        referer = Referer(uid=uuid4(), referer=data.referer, is_public=data.is_public)
        referer.save()
    return referer.__data__


@app.get("/api/v1/get_by_uid", response_model=ResponseReferer)
async def api_get_by_uid(data: RequestGetByUid):
    referer = Referer.get_or_none(Referer.uid == data.uid)
    if not referer:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(
                P2ProxyError(error="UUID_NOT_FOUND", message="UUID NOT FOUND")
            ),
        )
    return referer.__data__


@app.get("/api/v1/get_public", response_model=ResponseReferers)
async def api_get_public():
    referers = Referer.select().where(Referer.is_public == True)
    return {"referers": [r.__data__ for r in referers]}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            P2ProxyError(error="INVALID_DATA", message=exc.errors())
        ),
    )
