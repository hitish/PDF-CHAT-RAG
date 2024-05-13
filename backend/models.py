from pydantic import BaseModel

class Message(BaseModel):
  message: str

class Response(BaseModel):
  response: str