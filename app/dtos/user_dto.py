from pydantic import BaseModel
from typing import Optional
from ..models import UserModel

class UserDTO(BaseModel):
    id: Optional[int] = None
    email: str
    full_name: Optional[str] = None
    hashed_password: str
    is_active: Optional[bool] = None

    def to_model(self) -> UserModel:
        return UserModel(**self.model_dump(exclude_unset=True))