from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    content: str = Field(min_length=1, max_length=20000)

    @model_validator(mode="after")
    def clean(self):
        self.title = self.title.strip()
        self.content = self.content.strip()
        if not self.title or not self.content:
            raise ValueError("Note title and content cannot be empty")
        return self


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    content: str | None = Field(default=None, min_length=1, max_length=20000)


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

