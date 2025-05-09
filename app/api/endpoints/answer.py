from fastapi import APIRouter, HTTPException, Depends
from app.schemas.answer import QuestionRequest
from app.services.scraping import scrape_content, get_scraped_paragraphs, insert_scraped_paragraph
from app.services.search import google_search, generate_search_query, generate_answer
from app.core.utils import extract_keywords
from app.database.connection import get_db
from sqlalchemy.orm import Session
from nltk.tokenize import word_tokenize

router = APIRouter()

@router.post("/answer")
async def answer_question(request: QuestionRequest, db: Session = Depends(get_db)):
    question = request.question
    keywords = extract_keywords(question)
    # scraped_paragraphs = get_scraped_paragraphs(db, question, keywords)
    # combined_text = "\n\n".join(scraped_paragraphs)
    # combined_word_count = len(word_tokenize(combined_text))

    # if combined_word_count < 900:
    print("Scraping content from the web...")
    query_question = generate_search_query(question)
    urls = google_search(query_question)
    text = scrape_content(urls, keywords)
    for para in text.split("\n\n"):
        if para.strip():
            insert_scraped_paragraph(db, question, para, keywords)

    answer = generate_answer(question, text)
    return {"answer": answer}