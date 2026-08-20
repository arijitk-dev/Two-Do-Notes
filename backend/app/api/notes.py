from fastapi import APIRouter, Response, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.note import Note
from app.repositories.note_repository import NoteRepository
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


def get_note(user: CurrentUser, db: DbSession, note_id: str) -> Note:
    note = NoteRepository().get(db, user.id, note_id)
    if not note:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("", response_model=list[NoteResponse])
def list_notes(user: CurrentUser, db: DbSession, search: str | None = None):
    return NoteRepository().list(db, user.id, search)


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, user: CurrentUser, db: DbSession):
    note = Note(user_id=user.id, **payload.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{note_id}", response_model=NoteResponse)
def get_note_endpoint(note_id: str, user: CurrentUser, db: DbSession):
    return get_note(user, db, note_id)


@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(note_id: str, payload: NoteUpdate, user: CurrentUser, db: DbSession):
    note = get_note(user, db, note_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, key, value.strip() if isinstance(value, str) else value)
    if not note.title.strip() or not note.content.strip():
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Note title and content cannot be empty")
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str, user: CurrentUser, db: DbSession):
    note = get_note(user, db, note_id)
    db.delete(note)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
