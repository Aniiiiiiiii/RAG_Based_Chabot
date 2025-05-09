import pandas as pd
from datasets import load_dataset, Dataset, concatenate_datasets, load_from_disk
import evaluate
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer, TrainingArguments, default_data_collator, EarlyStoppingCallback, TrainerCallback, AutoModelForCausalLM, pipeline
from torch.utils.data import DataLoader
import numpy as np
import torch
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from bs4 import BeautifulSoup
import requests

pipe = pipeline("text2text-generation", model="google/flan-t5-large")

# OR load model and tokenizer directly (more control)
# tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
# model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")

def generate_search_query(question, use_pipeline=True):
    """
    Generates a Google search query from a user's question using FLAN-T5.

    Args:
        question: The user's question (string).
        use_pipeline: Whether to use the pipeline (True) or model/tokenizer directly (False).

    Returns:
        A search query string.
    """
    prompt = f"Give a search query to look up for this context : {question}"

    if use_pipeline:
        result = pipe(prompt, max_length=30, num_return_sequences=1)
        search_query = result[0]['generated_text']
    # else:
    #     inputs = tokenizer(prompt, return_tensors="pt")
    #     outputs = model.generate(**inputs, max_length=30, num_return_sequences=1)
    #     search_query = tokenizer.decode(outputs[0], skip_special_tokens=True)


    return search_query

def extract_keywords(question):

    words = word_tokenize(question)
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.lower() not in stop_words]
    pos_tags = pos_tag(filtered_words)
    keywords = [word for word, pos in pos_tags if pos.startswith('NN') or pos.startswith('VB') or pos.startswith('JJ')]
    
    return keywords

def google_search(query):
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': 'AIzaSyB2mI5jz49lA9rC6RPVTTzm6PnSccSpwX0',
        'cx': 'd79c9bf76a5ca451a',
    }

    response = requests.get(url, params=params)
    results = response.json()
    links = [item['link'] for item in results.get('items', [])[:5]]
    return links

def scrape_content(urls, keywords, target_word_count=1000):
    """
    Scrapes content from a list of URLs, accumulating relevant paragraphs based on keywords,
    until the target word count is reached or all URLs are processed.

    Args:
        urls: A list of URLs to scrape.
        keywords: A list of keywords to filter relevant paragraphs.
        target_word_count: The target word count to reach (approximately).

    Returns:
        A string containing the combined text from all scraped URLs.
    """
    combined_text = ""
    current_word_count = 0

    for url in urls:
        try:
            response = requests.get(url)
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
            combined_text += f"An error occurred with URL {url}: {e}\n\n"
            continue

    return combined_text

if __name__ == "__main__":
    question = "What is Donald Trump's panama canal dispute?"
    # custom_text = """
    # """

    query_question = generate_search_query(question)

    urls = google_search(query_question)
    keywords = extract_keywords(query_question)

    text = scrape_content(urls, keywords)

    # 1. Load Model and Tokenizer
    model_path = "./best_model"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    # Combine question and text into a single input string
    prompt = f"Answer the following question based on the provided text:\n\nQuestion: {question} \n\nText: {text}"

    # 3. Tokenize the Input
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=1024).to(device)

    # 4. Generate and Decode the Answer
    with torch.no_grad():
        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=512,
            num_beams=4,
        )
    generated_answer = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

    # 5. Print the Generated Answer
    print("Generated Answer:")
    print(generated_answer)
