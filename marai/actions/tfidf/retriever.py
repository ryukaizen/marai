import os
import re
import requests
import string
import numpy as np

from inltk.inltk import setup, tokenize, remove_foreign_languages
from .marathi_stopwords import marathi_stopwords
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from googlesearch import search
from lxml import html

setup('mr')

current_dir = os.path.dirname(os.path.abspath(__file__))
corpora_dir = os.path.join(current_dir, 'corpora')

def load_documents(folder_path):
    documents = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
                documents[filename] = file.read()
    return documents

def preprocess(text, remove_stops=False):
    text = remove_foreign_languages(text, 'mr')
    tokens = tokenize(text, 'mr')
    tokens = [item for sublist in tokens for item in sublist] if any(isinstance(i, list) for i in tokens) else tokens
    if remove_stops:
        tokens = [token for token in tokens if token not in marathi_stopwords]
    return ' '.join(tokens)

def truncate_text(text, max_chars=1000):
    sentences = re.split(r'[।॥।|!?\.]', text)
    truncated_sentences = []
    char_count = 0
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence: 
            continue
        if char_count + len(sentence) > max_chars:
            break
        truncated_sentences.append(sentence)
        char_count += len(sentence) + 1  
    
    result = '।'.join(truncated_sentences)
    return result

def get_response(query):
    print(f"VACCUME CLEANER")
    global X, vectorizer, documents

    # reload
    documents = load_documents(corpora_dir)
    vectorizer = TfidfVectorizer()
    vectorizer.fit([preprocess(doc, remove_stops=True) for doc in documents.values()])
    X = vectorizer.transform([preprocess(doc, remove_stops=True) for doc in documents.values()])

    local_result, relevance_score, best_doc_name = search_local_corpora(query, documents, vectorizer, X)

    if is_result_relevant(query, local_result, relevance_score, best_doc_name):
        print(f"Using result from corpora txt: {best_doc_name}\n")
        return local_result
    
    print("Local result insufficient or irrelevant. Querying online sources...\n")
    web_result = chatbot_query(query)
    
    if web_result != 'माफ करा मला या विषयाबद्दल माहिती नाही':
        print("Saving new information to corpora\n")
        file_name = f"{query.replace(' ', '_')}.txt"
        file_path = os.path.join(corpora_dir, file_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(web_result)
        
        return web_result
    else:
        return 'माफ करा मला या विषयाबद्दल माहिती नाही.'

def is_result_relevant(query, result, relevance_score, doc_name):
    if not result or len(result.strip()) < 50:
        return False
    
    query_terms = set(preprocess(query, remove_stops=True).lower().split())
    result_terms = set(preprocess(result, remove_stops=True).lower().split())
    
    term_match_percentage = len(query_terms.intersection(result_terms)) / len(query_terms)
    name_similarity = fuzz.partial_ratio(query.lower(), doc_name.lower()) / 100

    print(f"Relevance score: {relevance_score:.4f}, Term match percentage: {term_match_percentage:.4f}, Name similarity: {name_similarity:.4f}")
    return (relevance_score > 0.2 and term_match_percentage > 0.3) or (name_similarity > 0.8 and term_match_percentage > 0.3)

def search_local_corpora(query, documents, vectorizer, X):
    processed_query = preprocess(query, remove_stops=False)
    vectorized_query = vectorizer.transform([processed_query])
    similarities = cosine_similarity(vectorized_query, X)
    
    top_indices = similarities.argsort()[0][-5:][::-1]
    top_similarities = similarities[0][top_indices]
    
    print(f"Top 5 similar documents:")
    for i, idx in enumerate(top_indices):
        print(f"{i+1}. {list(documents.keys())[idx]} (Similarity: {top_similarities[i]:.4f})")
    
    best_doc = None
    best_score = 0
    best_doc_name = ""
    
    for idx in top_indices:
        doc = list(documents.values())[idx]
        doc_name = list(documents.keys())[idx]
        
        query_terms = set(processed_query.lower().split())
        doc_terms = set(preprocess(doc, remove_stops=False).lower().split())
        match_count = len(query_terms.intersection(doc_terms))
        
        name_similarity = fuzz.partial_ratio(query.lower(), doc_name.lower()) / 100
        score = similarities[0][idx] * (match_count + 1) * (name_similarity + 1)
        
        print(f"Document: {doc_name}, Score: {score:.4f}, Matches: {match_count}, Name Similarity: {name_similarity:.4f}")
        
        if score > best_score:
            best_score = score
            best_doc = doc
            best_doc_name = doc_name
    
    if best_doc:
        result = truncate_text(best_doc, 1000)
        return result, best_score, best_doc_name
    
    return None, 0, ""

def clean_wiki_text(text):
    text = re.sub(r'\[\d+\]', '', text) # citations [1], [2], etc.
    return text

def chatbot_query(query, index=0):
    fallback = 'माफ करा, मला या प्रश्नाचे उत्तर सापडले नाही.'
    
    search_query = f"{query} site:mr.wikipedia.org"
    search_results = list(search(search_query, tld="co.in", num=10, stop=3, pause=1))
    
    if not search_results:
        return None
    
    try:
        page = requests.get(search_results[0])
        soup = BeautifulSoup(page.content, "lxml")
        
        article_text = ''
        for paragraph in soup.find_all('p'):
            article_text += paragraph.get_text()
        

        cleaned_text = clean_wiki_text(article_text)
        truncated_text = truncate_text(cleaned_text, 1000)
        
        return truncated_text
    except Exception as e:
        print(f"Error: {e}")
        return fallback

documents = load_documents(corpora_dir)

vectorizer = TfidfVectorizer()
vectorizer.fit([preprocess(doc, remove_stops=True) for doc in documents.values()])
X = vectorizer.transform([preprocess(doc, remove_stops=True) for doc in documents.values()])