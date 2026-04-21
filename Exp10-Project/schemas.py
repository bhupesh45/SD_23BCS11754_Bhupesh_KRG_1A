from typing import List

from pydantic import BaseModel


class OptionCreate(BaseModel):
    text: str


class PollCreate(BaseModel):
    question: str
    options: List[OptionCreate]


class Vote(BaseModel):
    option_id: int
    previous_option_id: int | None = None


class OptionBase(BaseModel):
    id: int
    text: str
    votes: int

    class Config:
        orm_mode = True


class PollBase(BaseModel):
    id: int
    question: str
    options: List[OptionBase]

    class Config:
        orm_mode = True
