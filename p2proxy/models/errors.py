from typing import Union

from pydantic import BaseModel


class P2ProxyError(BaseModel):
    error: str
    message: Union[list, str]
