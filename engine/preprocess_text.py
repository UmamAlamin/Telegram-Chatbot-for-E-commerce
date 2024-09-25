import re
import nltk
from nltk.tokenize import word_tokenize

# Remove stopwords function (assuming you have a list of stopwords)
stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves"]
def remove_stopwords(text):
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords]
    return " ".join(filtered_words)

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove stopwords
    text = remove_stopwords(text)
    return text

nltk.download('punkt')

def preprocess_text_with_tokenizer(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Tokenize
    text = word_tokenize(text)
    # Remove stopwords
    text = [word for word in text if word not in stopwords]
    return text
