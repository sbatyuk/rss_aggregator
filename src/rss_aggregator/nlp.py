from sentence_transformers import SentenceTransformer
from keybert import KeyBERT

embedder = SentenceTransformer("all-MiniLM-L6-v2")
keyword_extractor = KeyBERT(model=embedder)
