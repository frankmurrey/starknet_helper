from pydantic import BaseModel


class DmailProfileSchema(BaseModel):
    email: str
    theme: str