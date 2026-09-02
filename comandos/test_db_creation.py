# criação de trilhas de aprendizagem
import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases

load_dotenv()

client = Client()
client.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
client.set_project(os.getenv("APPWRITE_PROJECT"))
client.set_key(os.getenv("APPWRITE_API_KEY"))

databases = Databases(client)
db_id = "escola"

try:
    col = databases.create_collection(database_id=db_id, collection_id="trilhas", name="Trilhas de Aprendizagem")
    print("Colecao trilhas criada com sucesso!")
except Exception as e:
    print("Info colecao trilhas:", e)

