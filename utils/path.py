import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

def get_path(relative_path):
    return os.path.join(ROOT_DIR, relative_path)