import requests
from app.core.config import GOOGLE_API_KEY, GOOGLE_CX_ID
from transformers import pipeline

pipe = pipeline("text2text-generation", model="google/flan-t5-large")

def google_search(query):
    """Performs a Google Custom Search and returns a list of the top 5 URLs."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CX_ID,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json()
    links = [item['link'] for item in results.get('items', [])[:5]]
    return links

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

    return search_query

def generate_answer(question, text, model_path="./best_model"):
    """Generates an answer based on the question and provided text."""
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    prompt = f"Answer the following question based on the provided text:\n\nQuestion: {question} \n\nText: {text}"
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=1024).to(device)

    with torch.no_grad():
        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=512,
            num_beams=4,
        )
    generated_answer = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    return generated_answer