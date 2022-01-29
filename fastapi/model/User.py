from typing import Any
from pydantic import BaseModel

class User(BaseModel):
    name: str
    family_name: str
    preferred_username: str
    email: str
    birthdate: str
    zoneinfo: str
    user_id: str
    
    class Config:
        validate_assignment = True

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)