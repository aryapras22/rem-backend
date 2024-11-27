from rem.models import query_collection
import uuid


def createUserStories(_id):
    # Fetch data from the database
    data = query_collection.find_one({"_id": _id})
    if not data:
        return
    
    # Retrieve user stories data
    userstories_data = data.get('user_stories', {})
    updates = {}

    # Define handlers for different sources
    handlers = {
        'appstore': handleReviews,
        'playstore': handleReviews,
        'news': handleNewsData,
    }

    # Process all stories from the defined handlers
    all_stories = []
    for source, handler in handlers.items():
        source_data = userstories_data.get(source, [])
        if source_data:
            all_stories.extend(handler(source_data))

    # If there are any stories, process them
    if all_stories:
        unique_who = getUniqueWho(all_stories)
        unique_what = getUniqueWhat(all_stories)

        # Update the nested structure for stories
        updates['stories'] = {
            'data': all_stories,
            'who': unique_who,
            'what': unique_what
        }

        # Apply the updates to the database
        query_collection.update_one({"_id": _id}, {"$set": updates})
    

def getUniqueWhat(stories):
    what = []
    for story in stories:
        what.append(story['what'])
    return list(set(what))        
    
def getUniqueWho(stories):
    who = []
    for story in stories:
        who.append(story['who'])
    return list(set(who))



def handleReviews(apps):
    stories = []
    _id = str(uuid.uuid4())
    for app in apps:
        for story in app['stories']:
            stories.append({
                'id': _id,
                'user_story': f'As a {story["who"]} I want to {story["what"]}',\
                'who': story['who'],
                'what': story['what'],
                'full_sentence': story['full_sentence'],
            })

    return stories

def handleNewsData(articles):
    stories = []
    _id = str(uuid.uuid4())
    for article in articles:
        for story in article['stories']:
            stories.append({
                'id': _id,
                'user_story': f'As a {story["who"]} I want to {story["what"]}',\
                'who': story['who'],
                'what': story['what'],
                'full_sentence': story['full_sentence'],
            })

    return stories