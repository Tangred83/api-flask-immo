import os
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = "19216fa0fcb24b1f97dc2c7e09514748"
NOTION_URL = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
NOTION_META_URL = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

@app.route('/')
def home():
    return {'message': 'API en ligne !'}

@app.route('/immeubles')
def get_immeubles():
    response = requests.post(NOTION_URL, headers=HEADERS)
    if response.status_code != 200:
        return {
            "error": "Impossible d'accéder à Notion",
            "status_code": response.status_code,
            "response_text": response.text
        }, response.status_code
    data = response.json()
    results = data.get("results", [])

    correspondance = [
        {
            "nom": r["properties"]["Nom"]["title"][0]["plain_text"] if r["properties"]["Nom"]["title"] else None,
            "page_id": r["id"]
        } for r in results
    ]
    return jsonify(correspondance)

@app.route('/immeuble/<page_id>')
def get_immeuble(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return {
            "error": "Impossible de récupérer l'immeuble",
            "status_code": response.status_code,
            "response_text": response.text
        }, response.status_code
    return jsonify(response.json())

@app.route('/attributs')
def get_attributs():
    response = requests.get(NOTION_META_URL, headers=HEADERS)
    if response.status_code != 200:
        return {
            "error": "Impossible de récupérer les attributs",
            "status_code": response.status_code,
            "response_text": response.text
        }, response.status_code

    data = response.json()
    properties = data.get("properties", {})
    attributs = [{"nom": key, "id": val.get("id"), "type": val.get("type")} for key, val in properties.items()]
    return jsonify(attributs)

@app.route('/update-page/<page_id>', methods=['PATCH'])
def update_page(page_id):
    payload = request.get_json()
    if not payload:
        return {"error": "Aucune donnée fournie"}, 400

    properties = {}
    for key, value in payload.items():
        properties[key] = {"number": value} if isinstance(value, (int, float)) else {"rich_text": [{"text": {"content": value}}]}

    update_url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "properties": properties
    }
    response = requests.patch(update_url, headers=HEADERS, json=data)
    if response.status_code != 200:
        return {
            "error": "Échec de la mise à jour",
            "status_code": response.status_code,
            "response_text": response.text
        }, response.status_code
    return {"success": True, "page_id": page_id, "updated_fields": list(payload.keys())}

@app.route('/ajouter-attribut', methods=['PATCH'])
def ajouter_attribut():
    payload = request.get_json()
    nom = payload.get("nom")
    type_ = payload.get("type", "rich_text")

    if not nom:
        return {"error": "Le nom de l'attribut est requis"}, 400

    update_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    nouvelle_structure = {
        "properties": {
            nom: {type_: {}}
        }
    }

    response = requests.patch(update_url, headers=HEADERS, json=nouvelle_structure)
    if response.status_code != 200:
        return {
            "error": "Échec de la création de l'attribut",
            "status_code": response.status_code,
            "response_text": response.text
        }, response.status_code

    return {"success": True, "attribut": nom, "type": type_}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
