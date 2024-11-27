from plantuml import PlantUML
from rem.models import query_collection


def createUseCaseDiagram(_id):
    data = query_collection.find_one({"_id": _id})
    if not data:
        return []

    stories = data.get('stories', {}).get('data', [])
    max_per_diagram = 4
    diagrams = []  # List to store each diagram as a string
    diagram = "@startuml\n"
    usecase_count = 0

    for story in stories:
        actor = story["who"]
        usecase = f'({story["what"]})'
        diagram += f":{actor}: --> {usecase}\n"
        usecase_count += 1

        if usecase_count >= max_per_diagram:
            diagram += "@enduml"
            diagrams.append(diagram)  # Store the current diagram
            usecase_count = 0
            diagram = "@startuml\n"  # Start a new diagram

    # Finalize and store the last diagram if there are remaining use cases
    if usecase_count > 0:
        diagram += "@enduml"
        diagrams.append(diagram)
    
    urls = []
    for diagram in diagrams:
        p = PlantUML(url="http://www.plantuml.com/plantuml/img/")
        u = p.get_url(diagram)
        urls.append(u)
    return {
        'usecasespuml_code': diagrams,
        'diagrams_url': urls
    }
    
