import os

import gdown

destination = os.path.join(os.getcwd(), "src", "agents", "db", "travel.sqlite")

url = "https://drive.google.com/uc?id=1c2rehOGMRxi8Peih3Of0ALkR7h2evBc3"
if not os.path.exists(destination):
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    gdown.download(url, destination, quiet=False)
