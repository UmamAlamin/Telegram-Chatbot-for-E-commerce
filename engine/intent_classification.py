from engine.preprocess_text import preprocess_text_with_tokenizer, preprocess_text
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import nltk
from nltk import FreqDist, NaiveBayesClassifier
import random

data = json.load(open('data/intents.json'))

def exact_match_classification(user_input):
    user_input = preprocess_text(user_input)
    for intent_class in data["data"]:
        for intent in intent_class["intent"]:
            if preprocess_text(intent) == user_input:
                return intent_class["class"]
    return "No match"

def fuzzy_match_classification(user_input, threshold=80):
    user_input = preprocess_text(user_input)
    best_score = 0
    best_class = "No match"

    for intent_class in data["data"]:
        for intent in intent_class["intent"]:
            score = fuzz.ratio(user_input, preprocess_text(intent))
            if score > best_score and score >= threshold:
                best_score = score
                best_class = intent_class["class"]
    
    return best_class

# Define a feature extractor function
def document_features(document, word_freq):
    document_words = set(document)
    features = {}
    for word in word_freq:
        features[f'contains({word})'] = (word in document_words)
    return features

def build_naive_bayes():
    all_intents = []
    for intent_class in data["data"]:
        for intent in intent_class["intent"]:
            all_intents.append((preprocess_text_with_tokenizer(intent), intent_class["class"]))
    
    # Shuffle the dataset for randomness
    random.shuffle(all_intents)

    # Extract features (words) from the intents
    all_words = []
    for tokens, _ in all_intents:
        all_words.extend(tokens)

    # Calculate word frequencies
    word_freq = FreqDist(all_words)

    # Create feature sets
    featuresets = [(document_features(tokens, word_freq), intent_class) for (tokens, intent_class) in all_intents]

    # Train the Naive Bayes classifier
    classifier = NaiveBayesClassifier.train(featuresets)

    return classifier, word_freq

def naive_bayes_classification(user_input, classifier, word_freq, threshold=0.7):
    tokens = preprocess_text_with_tokenizer(user_input)
    features = document_features(tokens, word_freq)
    prob_dist = classifier.prob_classify(features)
    pred_class = prob_dist.max()
    pred_prob = prob_dist.prob(pred_class)
    if pred_prob >= threshold:
        return pred_class
    else:
        return "No match"

def classify_intent(user_input, classifier, word_freq, naive_bayes_threshold=0.7, fuzzy_match_threshold=80):
    res = exact_match_classification(user_input)
    if res != "No match":
        return res
    res = fuzzy_match_classification(user_input, fuzzy_match_threshold)
    if res != "No match":
        return res
    res = naive_bayes_classification(user_input, classifier, word_freq, naive_bayes_threshold)
    if res != "No match":
        return res
    return "No match"