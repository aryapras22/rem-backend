from rem.models import query_collection
import emoji


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
            # lang = langdetect.detect(review_text)
            # if lang != "en":
            #     break
            review_text = stripData(review_text)
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
            "App Name": data["App Name"],
            "App ID": data["App ID"],
            "reviews": [],
        }
        for review in app["Reviews"]:
            review_text = review["Review"]
            review_text = removeEmoji(review_text)
            # lang = langdetect.detect(review_text)
            # if lang != "en":
            #     break
            review_text = stripData(review_text)
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
