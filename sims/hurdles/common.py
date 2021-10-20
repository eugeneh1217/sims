import os
import shutil

def build_path(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)