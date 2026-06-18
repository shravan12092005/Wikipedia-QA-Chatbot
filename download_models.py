import nltk
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, AutoModelForSeq2SeqLM

print("--- Pre-downloading NLP Models for Production Caching ---")

print("1. Downloading deepset/roberta-base-squad2...")
AutoTokenizer.from_pretrained("deepset/roberta-base-squad2")
AutoModelForQuestionAnswering.from_pretrained("deepset/roberta-base-squad2")

print("2. Downloading facebook/bart-large-cnn...")
AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

print("3. Downloading t5-small...")
AutoTokenizer.from_pretrained("t5-small")
AutoModelForSeq2SeqLM.from_pretrained("t5-small")

print("4. Downloading NLTK tokenizer models...")
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

print("--- NLP model caching complete! ---")
