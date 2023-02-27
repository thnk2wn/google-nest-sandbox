import os

def get_project_id():
    projectId = os.getenv('NEST_PROJECT_ID')

    if projectId is None:
        raise Exception('NEST_PROJECT_ID')

    return projectId