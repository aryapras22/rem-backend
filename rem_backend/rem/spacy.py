import spacy
from spacy.matcher import Matcher
from rem.models import query_collection

# Load SpaCy model and set up pipelines
nlp = spacy.load("en_core_web_lg")
nlp.add_pipe("merge_noun_chunks", before="ner")


# main function
def extract_goals(_id):
    data = query_collection.find_one({"_id": _id})
    userstories = {}
    appstore_data = data.get("preprocessed_data", {}).get("appstore", [])
    if appstore_data:
        appstore_dict = dict(handle_appstore_data(appstore_data))
        userstories.update(appstore_dict)
    playstore_data = data.get("preprocessed_data", {}).get("playstore", [])
    if playstore_data:
        playstore_dict = dict(handle_playstore_data(playstore_data))
        userstories.update(playstore_dict)
    news_data = data.get("preprocessed_data", {}).get("news", [])
    if news_data:
        news_dict = dict(handle_news_data(news_data))
        userstories.update(news_dict)
    return userstories
   
    

# handle appstore data
def handle_appstore_data(apps):
    candidates = []
    for app in apps:
        app_name = app['app_name']
        matches = []
        for review in app['reviews']:
            doc = nlp(review['text'])
            review_matches = find_matches_review(doc) 
            matches.extend(review_matches)  
        candidates.append(
            {
                'app_name': app_name,
                'what_candidate': matches,
            }
        )
    for candidate in candidates:
        
        candidate['what_candidate'] = check_software_context(
            candidate['what_candidate'],
            software_functionality_dict,
            0.7
        )
    return {'appstore': candidates}
            
def handle_playstore_data(apps):
    candidates = []
    for app in apps:
        app_name = app['app_name']
        matches = []
        for review in app['reviews']:
            doc = nlp(review['text'])
            review_matches = find_matches_review(doc) 
            matches.extend(review_matches)  
        candidates.append(
            {
                'app_name': app_name,
                'what_candidate': matches,
            }
        )
    for candidate in candidates:
        
        candidate['what_candidate'] = check_software_context(
            candidate['what_candidate'],
            software_functionality_dict,
            0.7
        )
    return {'playstore': candidates}

def handle_news_data(news):
    candidates = []
    for article in news:
        doc = nlp(article['text'])
        matches = find_matches_news(doc)
        entities = find_ents(doc)
        candidates.append(
            {
                'title': article['news_title'],
                'what_candidate': matches,
                'entities': entities,
            }
        )
    for candidate in candidates:
        candidate['what_candidate'] = check_software_context(
            candidate['what_candidate'],
            software_functionality_dict,
            0.7
        )
    return {'news': candidates}

# Initialize the matcher with patterns
matcher = Matcher(nlp.vocab)
patterns = [
    # Pattern 1: VERB + ADJ + NOUN
    [{"POS": "VERB"}, {"POS": "ADJ"}, {"POS": "NOUN"}],
    # Pattern 2: VERB + NOUN
    [{"POS": "VERB"}, {"POS": "NOUN"}],
    # Pattern 3: VERB + ADV + ADJ + NOUN (ADV optional)
    [{"POS": "VERB"}, {"POS": "ADV", "OP": "?"}, {"POS": "ADJ"}, {"POS": "NOUN"}],
    # Pattern 4: NOUN + VERB
    [{"POS": "NOUN"}, {"POS": "VERB"}],
]
for i, pattern in enumerate(patterns):
    matcher.add(f"GOAL_PATTERN_{i+1}", [pattern])

def find_matches_review(doc):
    matches = matcher(doc)
    results = []
    for match_id, start, end in matches:
        pattern_name = nlp.vocab.strings[match_id]
        span = doc[start:end]  # Get the matched span
        sentence = span.sent
        results.append(
            {
             'who':'user',
             'what':span.text,
             'full sentence':sentence.text,
             }
        )
    return results

def find_matches_news(doc):
    matches = matcher(doc)
    results = []
    for match_id, start, end in matches:
        pattern_name = nlp.vocab.strings[match_id]
        span = doc[start:end]  # Get the matched span

        try:
            sentence = span.sent
        except Exception as e:
            print(f"Error retrieving sentence for span: {span.text}")
            sentence = span  # Fall back to the span itself

        who = find_ents(sentence.text)
        if not who:
            who = ['user']  # Ensure consistency in return type

        results.append({
            'who': who[0],
            'what': span.text,
            'full sentence': sentence.text if hasattr(sentence, "text") else str(sentence),
        })

    return results

def find_ents(text):
    if not text or not isinstance(text, str):
        return []
    try:
        doc = nlp(text)
    except Exception as e:
        print(f"Error processing text in find_ents: {text[:100]}")
        return []

    entities = []
    for sent in doc.sents:  # Process by sentence
        entities.extend([ent.text for ent in sent.ents if ent.label_ in {'PERSON', 'ORG', 'NORP'}])
    return entities

def check_software_context(feedback_list, keywords, threshold):
    # Convert keywords into SpaCy vectors
    keyword_docs = [nlp(keyword) for keyword in keywords]

    relevant_phrases = []
    for feedback in feedback_list:
        feedback_doc = nlp(feedback['what'])
        max_similarity = 0

        # Compare feedback with each keyword
        for keyword_doc in keyword_docs:
            similarity = feedback_doc.similarity(keyword_doc)
            if similarity > max_similarity:
                max_similarity = similarity

        # Check if similarity exceeds the threshold
        if max_similarity >= threshold:
            relevant_phrases.append({
                'who': feedback['who'],
                'what': feedback['what'],
                'full_sentence': feedback['full sentence'],
                'similarity': max_similarity
            })

    return relevant_phrases




software_functionality_dict = [
    # General Terms
    "feature", "functionality", "module", "component",

    # User Management
    "login", "logout", "authentication", "authorization",
    "register", "sign up", "create account", "user profile",
    "edit profile", "password reset", "forgot password",
    "account settings", "change email", "update contact information",

    # Data Management
    "create record", "delete record", "update record", "read record",
    "add data", "remove data", "edit data", "import data",
    "export data", "data backup", "data recovery", "data syncing",
    "upload file", "download file", "document management",

    # Search & Filter
    "search query", "advanced filter", "keyword search", "sort by",
    "facet search", "filter options", "real-time search",
    "find product", "search by name", "search by category",
    "filter by price", "filter by rating", "filter by date",

    # Notifications
    "push notification", "email alert", "real-time update",
    "system alert", "notification settings", "SMS alert",
    "reminders", "event notifications", "updates about changes",

    # Security
    "data encryption", "two-factor authentication", "access control",
    "role-based access", "user permissions", "security audit",
    "secure login", "session timeout", "activity logs",
    "password strength checker", "CAPTCHA validation",

    # Reports & Visualization
    "dashboard", "pie chart", "bar graph", "line chart",
    "data export", "report generation", "analytics", "data visualization",
    "trend analysis", "performance tracking", "real-time metrics",
    "download report", "customize report", "generate summary",

    # Integration
    "API", "webhook", "plugin", "third-party service",
    "external integration", "data synchronization", "REST API", "OAuth",
    "connect to Google services", "sync with calendar", "payment gateway",

    # E-commerce Features
    "add to cart", "remove from cart", "checkout process",
    "apply discount", "order history", "track order",
    "payment confirmation", "wishlist", "product reviews",
    "promo code", "discount coupon", "apply voucher",

    # Collaboration & Communication
    "chat feature", "send message", "comment on post",
    "create group", "share file", "video conferencing",
    "real-time collaboration", "task assignment", "activity tracking",

    # Productivity Features
    "schedule event", "set reminder", "task management",
    "calendar view", "time tracking", "add to-do list",
    "mark as complete", "priority setting", "goal tracking",

    # Payment Methods
    "pay with card", "credit card payment", "debit card payment",
    "pay via health insurance", "health insurance payment",
    "insurance coverage", "use insurance", "pay with wallet",
    "online payment", "mobile payment", "bank transfer",
    "installment payment", "split payment", "apply for loan",
    "payment history", "payment receipt",

    # Healthcare-Specific
    "book appointment", "schedule consultation", "find doctor",
    "health insurance coverage", "check insurance eligibility",
    "medical records", "view prescription", "update health details",
    "connect with hospital", "hospital payment options",

    # Miscellaneous
    "performance optimization", "user experience", "accessibility",
    "scalability", "customization", "user engagement",
    "cross-platform support", "offline access", "dark mode",
    "multi-language support", "help center", "tutorials",
    "frequently asked questions", "live support"
]