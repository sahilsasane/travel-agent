import os

import gdown

destination = os.path.join(os.getcwd(), "agents", "db", "travel.sqlite")

url = "https://drive.google.com/uc?id=19kjf5LS0dmVMzxLTtdtkdXa94dQNJ08-"

if not os.path.exists(destination):
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    gdown.download(url, destination, quiet=False)
