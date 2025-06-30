from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")
keyword_extractor = KeyBERT(model=embedder)
