import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from sqlalchemy.orm import Session
from app.database.models import ScrapedParagraph
from app.core.utils import hash_question
from typing import List
from sqlalchemy import and_
import time
import random

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
]

def scrape_content(urls, keywords, target_word_count=1000):
    """
    Scrapes content from a list of URLs, accumulating relevant paragraphs based on keywords,
    until the target word count is reached or all URLs are processed.
    """
    combined_text = ""
    current_word_count = 0

    for url in urls:
        try:
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.google.com/"
            }

            # time.sleep(random.uniform(2, 5))
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')

            for para in paragraphs:
                para_text = para.get_text()
                if any(keyword.lower() in para_text.lower() for keyword in keywords):
                    words = word_tokenize(para_text)
                    para_word_count = len(words)

                    if current_word_count + para_word_count <= target_word_count:
                        combined_text += para_text + "\n\n"
                        current_word_count += para_word_count
                    else:
                        return combined_text

            if current_word_count >= target_word_count:
                return combined_text

        except requests.exceptions.RequestException as e:
            print(f"An error occurred with URL {url}: {e}")
            continue

    return combined_text

def get_scraped_paragraphs(db: Session, question: str, keywords: List[str]) -> List[str]:
    """Retrieves scraped paragraphs from the database based on the question and keywords."""
    question_hash = hash_question(question)

    # Build the query using ORM methods
    query = db.query(ScrapedParagraph.paragraph).filter(
        ScrapedParagraph.question_hash == question_hash
    )

    # Add a filter for each keyword
    keyword_filters = [ScrapedParagraph.keywords.contains([keyword]) for keyword in keywords]
    query = query.filter(and_(*keyword_filters))

    paragraphs = query.all()
    return [para[0] for para in paragraphs]

def insert_scraped_paragraph(db: Session, question: str, paragraph: str, keywords: List[str]):
    """Inserts a scraped paragraph into the database."""
    question_hash = hash_question(question)
    db_paragraph = ScrapedParagraph(question_hash=question_hash, paragraph=paragraph, keywords=keywords)
    try:
        db.add(db_paragraph)
        db.commit()
        db.refresh(db_paragraph)
    except Exception as e:
        db.rollback()
        print(f"Error inserting paragraph: {e}")