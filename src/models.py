from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    activity_name: str = Field(foreign_key="activity.name")
    activity: Optional["Activity"] = Relationship(back_populates="participants")


class Activity(SQLModel, table=True):
    name: str = Field(primary_key=True)
    description: str
    schedule: str
    max_participants: int
    participants: List[Participant] = Relationship(back_populates="activity")
