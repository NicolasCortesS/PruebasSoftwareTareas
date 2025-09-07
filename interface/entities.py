from typing import Optional
from pydantic import BaseModel


class ResponseLogin(BaseModel):
    success: bool
    userData: Optional['UserData'] = None

class UserData(BaseModel):
    username: str
    role: str