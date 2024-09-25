import os
import telebot
from dotenv import load_dotenv
from engine.intent_classification import build_naive_bayes, classify_intent
from engine.named_entity import NERExtractor
from engine.commerce import purchase, check_stocks, product_info_logic, user_logic, cart_info, checkout_logic, track_order_logic

load_dotenv()

classifier, word_freq = build_naive_bayes()

bot = telebot.TeleBot(os.getenv("TELEBOT_API_KEY"))

@bot.message_handler(func=lambda message: True)
def reply(message):
    ner_extractor = NERExtractor(os.getenv("API_URL"))
    user_id = str(message.from_user.id)
    username = message.from_user.username
    user_logic(user_id, username, os.getenv("API_URL"))
    print(user_id, username, message.text)
    intent = classify_intent(message.text, classifier, word_freq)
    if message.text == "checkout":
        text = checkout_logic(os.getenv("API_URL"), user_id)
        bot.reply_to(message, text)
    elif intent in ['Purchasing', 'Cart Info', 'Product Info About', 'Stocks Info', 'Order Status Info']:    
        _,extracted_entities = ner_extractor.replace_entities(message.text)
        if intent == "Purchasing":
            text, extracted_entities = purchase(extracted_entities, os.getenv("API_URL"), user_id)
            bot.reply_to(message, text)
        elif intent == "Stocks Info":
            text= check_stocks(extracted_entities, os.getenv("API_URL"))
            bot.reply_to(message, text)
        elif intent == "Product Info About":
            text = product_info_logic(extracted_entities, os.getenv("API_URL"))
            bot.reply_to(message, text)
        elif intent == "Cart Info":
            text = cart_info(os.getenv("API_URL"), user_id)
            bot.reply_to(message, text)
        elif intent == "Order Status Info":
            text = track_order_logic(extracted_entities, os.getenv("API_URL"))
            bot.reply_to(message, text)
        else:
            bot.reply_to(message, intent+" "+str(extracted_entities))
    elif intent == "Greetings":
        bot.reply_to(message, "Hi, welcome to our store!")
    else:
        bot.reply_to(message, "Sorry, I don't understand what you mean")

bot.polling()