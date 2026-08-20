from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.note import Note


class NoteRepository:
    def get(self, db: Session, user_id: str, note_id: str) -> Note | None:
        return db.scalar(select(Note).where(Note.id == note_id, Note.user_id == user_id))

    def list(self, db: Session, user_id: str, search: str | None = None, limit: int | None = None) -> list[Note]:
        query = select(Note).where(Note.user_id == user_id).order_by(Note.updated_at.desc())
        if search:
            term = f"%{search}%"
            query = query.where(or_(Note.title.ilike(term), Note.content.ilike(term)))
        if limit:
            query = query.limit(limit)
        return list(db.scalars(query))

