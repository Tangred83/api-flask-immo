import requests
import json

BASE_URL = "https://api-flask-immo.onrender.com"

def fetch_immeubles():
    resp = requests.get(f"{BASE_URL}/immeubles")
    resp.raise_for_status()
    return resp.json()

def fetch_attributs():
    resp = requests.get(f"{BASE_URL}/attributs")
    resp.raise_for_status()
    return resp.json()

def main():
    try:
        immeubles = fetch_immeubles()
        attributs = fetch_attributs()
    except Exception as e:
        print("Erreur lors de l’appel API :", e)
        return

    data = {
        "immeubles": immeubles,
        "attributs": attributs
    }

    with open("notion_ids.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Fichier 'notion_ids.json' généré avec succès ✅")

if __name__ == "__main__":
    main()
