import requests
import pandas as pd

url = "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/menus-cantines/records?limit=20"
req = requests.get(url)

if req.status_code == 200:
    raw_menus = req.json()
    records = raw_menus.get("results")

    if records:
        menus = pd.DataFrame(records)
        print(menus)
    else:
        print("No records found.")
else:
    print(f"Failed to retrieve data. Status code: {req.status_code}.\n{req.text}")