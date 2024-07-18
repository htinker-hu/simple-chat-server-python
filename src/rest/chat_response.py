from pydantic import BaseModel
from typing import Optional, Any


class ChatResponse(BaseModel):
    value: Optional[Any] = None
    success: bool = True
    cause: Optional[str] = None

    @staticmethod
    def from_value(value: str) -> 'ChatResponse':
        return ChatResponse(value=value, success=True)

    @staticmethod
    def from_cause(cause: str) -> 'ChatResponse':
        return ChatResponse(cause=cause, success=False)
