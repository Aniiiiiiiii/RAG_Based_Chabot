from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ScrapedParagraph(Base):
    __tablename__ = "scraped_paragraphs"

    id = Column(Integer, primary_key=True, index=True)
    question_hash = Column(String, index=True)
    paragraph = Column(Text)
    keywords = Column(ARRAY(String))