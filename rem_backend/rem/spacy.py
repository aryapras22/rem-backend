import spacy
from spacy.matcher import Matcher
from rem.models import query_collection
from rem.dict import software_functionality_dict

# Load SpaCy model and set up pipelines
nlp = spacy.load("en_core_web_lg")
nlp.add_pipe("merge_noun_chunks", before="ner")

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


# main function
def extract_goals(_id):
    data = query_collection.find_one({"_id": _id})
    if not data:
        return
    
    preprocessed_data = data.get("preprocessed_data", {})
    updates = {}

    handlers = {
        "appstore": handle_appstore_data,
        "playstore": handle_playstore_data,
        "news": handle_news_data,
    }

    for source, handler in handlers.items():
        source_data = preprocessed_data.get(source, [])
        if source_data:
            updates[f"user_stories.{source}"] = handler(source_data)
    
    if updates:
        query_collection.update_one({"_id": _id}, {"$set": updates})
   
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
                'stories': matches,
            }
        )
    for candidate in candidates:
        candidate['stories'] = check_software_context(
            candidate['stories'],
            software_functionality_dict,
            0.7
        )
    return candidates  # No additional wrapping

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
                'stories': matches,
            }
        )
    for candidate in candidates:
        candidate['stories'] = check_software_context(
            candidate['stories'],
            software_functionality_dict,
            0.7
        )
    return candidates  # No additional wrapping

def handle_news_data(news):
    candidates = []
    for article in news:
        doc = nlp(article['text'])
        matches = find_matches_news(doc)
        entities = find_ents(doc)
        candidates.append(
            {
                'title': article['news_title'],
                'stories': matches,
                'entities': entities,
            }
        )
    for candidate in candidates:
        candidate['stories'] = check_software_context(
            candidate['stories'],
            software_functionality_dict,
            0.7
        )
    return candidates  # No additional wrapping

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
            'full sentence': sentence.text,
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