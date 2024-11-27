from rem.models import query_collection
import emoji
import re
from langdetect import detect


def preprocess(_id):
    data = query_collection.find_one({"_id": _id})
    preprocessed_data = {}

    # preprocess appstore data
    appstore_data = data.get("sources", {}).get("appstore", [])
    if appstore_data:
        appstore_dict = dict(handle_appstore_data(appstore_data))
        preprocessed_data.update(appstore_dict)

    # preprocess playstore data
    playstore_data = data.get("sources", {}).get("playstore", [])
    if playstore_data:
        playstore_dict = dict(handle_playstore_data(playstore_data))
        preprocessed_data.update(playstore_dict)

    # preprocess news data
    news_data = data.get("sources", {}).get("news", [])
    if news_data:
        news_dict = dict(handle_news_data(news_data))
        preprocessed_data.update(news_dict)

    return preprocessed_data


def handle_appstore_data(apps):
    appstore_data = []
    i = 1
    for app in apps:
        app_data = {
            "app_name": app["app_name"],
            "app_id": app["app_id"],
            "reviews": [],
        }
        # for every review in app
        for review in app["reviews"]:
            review_text = review["review"]
            review_text = removeEmoji(review_text)
            
            review_text = stripData(review_text)
            # lang = detect(review_text)
            # if lang != "en":
            #     break
            review_text = clean_app_review(review_text)
            app_data["reviews"].append(
                {
                    "id": "appstore_review_" + str(i),
                    "text": review_text,
                }
            )
            i += 1

        appstore_data.append(app_data)

    # Directly return a dictionary instead of a list of dictionaries
    return {"appstore": appstore_data}


def handle_playstore_data(apps):
    preprocessed_data = []
    playstore_data = []
    i = 1
    for app in apps:
        # for every review in app
        data = app["App Details"]
        app_data = {
            "app_name": data["App Name"],
            "app_id": data["App ID"],
            "reviews": [],
        }
        for review in app["Reviews"]:
            review_text = review["Review"]
            review_text = removeEmoji(review_text)
            review_text = stripData(review_text)
            # lang = detect(review_text)
            # if lang != "en":
            #     break
            review_text = clean_app_review(review_text)
            app_data["reviews"].append(
                {
                    "id": "playstore_review_" + str(i),
                    "text": review_text,
                }
            )
            i += 1
        playstore_data.append(app_data)

    return {"playstore": playstore_data}


def handle_news_data(news):
    preprocessed_data = []
    i = 1
    for article in news["articles"]:
        article_text = article["summary"]
        article_text = removeEmoji(article_text)
        article_text = clean_news(article_text)
        article_text = stripData(article_text)
        preprocessed_data.append(
            {
                "id": "news_" + str(i),
                "news_title": article["title"],
                "text": article_text,
                "link": article["link"],
            }
        )
        i += 1

    # Return a dictionary with a single key "news"
    return {"news": preprocessed_data}


def removeEmoji(text):
    removedEmoji = emoji.replace_emoji(text, " ")
    return removedEmoji


def stripData(text):
    return text.strip()


def clean_app_review(text):
    # Remove greetings or irrelevant openings
    text = re.sub(
        r"(?i)\b(hi|hello|thanks|thank you|please|dear developer|team|good job)\b.*?[.,!?]",
        "",
        text,
    )
    # Remove generic ratings-related comments
    text = re.sub(
        r"(?i)\b(5 stars|4 stars|1 star|rate this app|recommend this app|like this app|hate this app)\b.*",
        "",
        text,
    )
    # Remove links
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    # Remove email addresses
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "", text)
    # Remove phone numbers
    text = re.sub(
        r"\+?\d{1,4}?[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}", "", text
    )
    # Remove mentions of app version numbers (e.g., "v1.2.3" or "since the last update")
    text = re.sub(
        r"\b(v\d+\.\d+(\.\d+)?|version \d+\.\d+(\.\d+)?|update \d+)\b",
        "",
        text,
        flags=re.IGNORECASE,
    )
    # Remove device-specific mentions
    text = re.sub(
        r"(?i)\b(on my|using a|works on|doesn't work on|galaxy|iphone|ipad|android)\b.*",
        "",
        text,
    )
    # Remove generic praise/complaint phrases
    text = re.sub(
        r"(?i)\b(great app|terrible app|awesome|worst|nice|bad|thank you)b.*", "", text
    )
    # Remove redundant feedback phrases
    text = re.sub(
        r"(?i)\b(appreciate your work|keep it up|waiting for update|more features please|download)\b.*",
        "",
        text,
    )
    # Remove repeated characters or spammy patterns
    text = re.sub(r"(.)\1{2,}", r"\1", text)  # e.g., "loooove" -> "love"
    # Remove extra whitespaces
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'\s+', ' ', text).strip()    # Normalize whitespace
    return text

def clean_news(text):
    # Remove bullet points and arrow symbols
    text = re.sub(r"[•→←↑↓↔↕⇆⇅⇄➔➜➤➥➦➨➩➪➮➯➱➲➳➵➸➹➺➻➼➽➾➡]", "", text)
    # Remove links
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    # Remove email addresses
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "", text)
    # Remove phone numbers
    text = re.sub(r"\+?\d{1,4}?[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}", "", text)
    # Remove phrases related to news sources
    text = re.sub(r"(Reported by|Source:|Contact us|For more details).*", "", text, flags=re.IGNORECASE)
    # Remove extra whitespaces
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r'[^\x00-\x7F]+', ' ', text) 
    
    #remove \n \t
    text = text.replace("\n", " ")
    return text