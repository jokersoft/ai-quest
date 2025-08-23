from sqlalchemy import asc

from app.entities.chapter import Chapter


class ChapterRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def add(self, chapter: Chapter):
        self.db_session.add(chapter)
        self.db_session.commit()
        return chapter.id

    def get_chapter(self, story_id_bytes: bytes, chapter_number: int) -> Chapter:
        return self.db_session.query(Chapter).filter(Chapter.story_id == story_id_bytes).filter(
            Chapter.number == chapter_number).first()

    def get_chapters_by_story_id(self, story_id_bytes: bytes) -> list[Chapter]:
        return self.db_session.query(Chapter).filter(Chapter.story_id == story_id_bytes).order_by(
            asc(Chapter.number)).all()

    def get_last_chapter(self, story_id_bytes: bytes) -> Chapter:
        return self.db_session.query(Chapter).filter(Chapter.story_id == story_id_bytes).order_by(
            Chapter.number.desc()).first()

    def get_max_chapter_number(self, story_id_bytes: bytes) -> int:
        max_chapter = self.db_session.query(Chapter).filter(Chapter.story_id == story_id_bytes).order_by(
            Chapter.number.desc()).first()
        return max_chapter.number if max_chapter else 0

    def update(self, chapter: Chapter) -> Chapter:
        self.db_session.merge(chapter)
        self.db_session.commit()
        return chapter
