import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases

load_dotenv()

endpoint = os.getenv("APPWRITE_ENDPOINT")
project_id = os.getenv("APPWRITE_PROJECT")
api_key = os.getenv("APPWRITE_API_KEY")

print("Conectando ao Appwrite em:", endpoint)
print("Project ID:", project_id)

client = Client()
client.set_endpoint(endpoint)
client.set_project(project_id)
client.set_key(api_key)

databases = Databases(client)

try:
    result = databases.list()
    print("SUCCESS: Conexao com Appwrite realizada com sucesso!")
    print("Total de Bancos de Dados:", result.total)
    for db in result.databases:
        print(" - Nome:", db.name, "| ID:", db.id)
except Exception as e:
    print("ERROR ao conectar com Appwrite:", e)

