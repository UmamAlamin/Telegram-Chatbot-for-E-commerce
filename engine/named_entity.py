import re
import requests
from fuzzywuzzy import fuzz

class NERExtractor:
    def __init__(self, api_url):
        self.api_url = api_url
        self.product_data = self.get_product_data()
        self.order_data = self.get_order_data()
        
        self.product_names = [product["nama_produk"] for product in self.product_data]
        self.order_ids = [order["id_transaction"] for order in self.order_data]
        print(self.order_ids)

    def get_product_data(self):
        response = requests.get(self.api_url + "/products/")
        return response.json()

    def get_order_data(self):
        response = requests.get(self.api_url + "/orders/")
        return response.json()

    def extract_entities(self, sentence):
        entities = []
        for product_name in self.product_names:
            ratio = fuzz.partial_ratio(product_name.lower(), sentence.lower())
            if ratio >= 80:  # Adjust the threshold as needed
                entities.append((product_name, ratio))

        for order_id in self.order_ids:
            if order_id.lower() in sentence.lower():
                entities.append((order_id, 100))
        return entities

    def replace_entities(self, sentence):
        entities = self.extract_entities(sentence)
        for entity, _ in entities:
            sentence = sentence.replace(entity, "[PRODUCT]")

        # Replace numbers in the sentence with [NUMBER]
        sentence_temp = []
        for word in sentence.split():
            if word.isdigit():
                sentence_temp.append("[NUMBER]")
                sentence.replace(word, "[NUMBER]")
                entities.append((word, 100))
            else:
                sentence_temp.append(word)

        return sentence, [entity[0] for entity in entities]

if __name__ == '__main__':
    # Sample product data (replace with your actual product data)
    product_data = 'http://localhost:8000'

    # Initialize the NERExtractor with the product data
    ner_extractor = NERExtractor(product_data)

    # Test the NERExtractor
    input_sentence = "I want to buy jacket for 10 pieces"
    result_sentence, extracted_entities = ner_extractor.replace_entities(input_sentence)
    print("Original Sentence:", input_sentence)
    print("Modified Sentence:", result_sentence)
    print("Extracted Entities:", extracted_entities)