from pydantic import BaseModel
from typing import Union


class P2ProxyError(BaseModel):
    error: str
    message: Union[list, str]
