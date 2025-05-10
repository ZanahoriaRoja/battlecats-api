from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/cat-stats")
def get_cat_stats(name: str = Query(..., description="Nombre del gato")):
    page_name = name.replace(" ", "_")
    url = f"https://battle-cats.fandom.com/wiki/{page_name}"

    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Gato no encontrado en la wiki.")

    soup = BeautifulSoup(response.text, "html.parser")
    infobox = soup.find("table", {"class": "wikitable"})

    if not infobox:
        raise HTTPException(status_code=404, detail="No se encontraron estadísticas.")

    text = infobox.get_text()

    def extract_stat(label):
        for line in text.splitlines():
            if label in line:
                return ''.join(filter(str.isdigit, line.split(label)[-1]))
        return None

    return JSONResponse({
        "name": name,
        "hp": int(extract_stat("Health")) if extract_stat("Health") else None,
        "damage": int(extract_stat("Attack Power")) if extract_stat("Attack Power") else None,
        "special": "No extraído aún",
        "traits": [],
        "cost": int(extract_stat("Cost")) if extract_stat("Cost") else None
    })
