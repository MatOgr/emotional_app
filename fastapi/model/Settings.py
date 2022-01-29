from typing import Any
from pydantic import BaseModel

class Settings(BaseModel):
    send_pictures = True
    send_voice = True
    allow_reactions = True
    location = 'Poznan,PL'
    
    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)