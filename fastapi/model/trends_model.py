from pydantic import BaseModel
from typing import Any, List, Tuple

class trends_model(BaseModel):
    month: str
    year: str
    trends: List[Tuple[str, str, Any]]
    last: str
    next: str
    type: str
    class Config:        
        arbitrary_types_allowed = True

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)