import os

def create_file_at_path_if_nonexistent(path):
    """Creates an empty file at the specified path if it does not exist"""
    if not os.path.exists(path):
        with open(path, "w") as file:
            pass