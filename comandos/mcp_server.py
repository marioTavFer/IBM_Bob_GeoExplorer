# -*- coding: utf-8 -*-
"""
Servidor MCP para o Geo-Explorer (Appwrite Integration)
Permite que Agentes de IA (como IBM Bob) consultem trilhas, desafios e emitam certificados via MCP.
"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID

load_dotenv()

mcp = FastMCP("Geo-Explorer MCP Server")

ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
PROJECT_ID = os.getenv("APPWRITE_PROJECT")
API_KEY = os.getenv("APPWRITE_API_KEY")

client = Client()
client.set_endpoint(ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)

databases = Databases(client)
DB_ID = "escola"

@mcp.tool()
def listar_trilhas(categoria: str = None) -> list:
    """Lista as trilhas de aprendizagem registradas no Appwrite. Pode filtrar por categoria."""
    try:
        res = databases.list_documents(database_id=DB_ID, collection_id="trilhas")
        docs = res.get("documents", [])
        if categoria:
            docs = [d for d in docs if d.get("categoria", "").lower() == categoria.lower()]
        return [
            {
                "id": d.get("$id"),
                "titulo": d.get("titulo"),
                "categoria": d.get("categoria"),
                "nivel": d.get("nivel"),
                "duracao_horas": d.get("duracao_horas"),
                "descricao": d.get("descricao")
            }
            for d in docs
        ]
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def obter_desafio(trilha_titulo: str) -> dict:
    """Obtem ou gera um desafio de codigo para uma determinada trilha de aprendizagem."""
    try:
        res_trilhas = databases.list_documents(database_id=DB_ID, collection_id="trilhas")
        trilha = None
        for t in res_trilhas.get("documents", []):
            t_titulo = t.get("titulo", "")
            if trilha_titulo.lower() in t_titulo.lower():
                trilha = t
                break

        if not trilha:
            return {"error": f"Trilha '{trilha_titulo}' nao encontrada."}

        trilha_id = trilha.get("$id")
        t_nome = trilha.get("titulo", "")
        t_cat = trilha.get("categoria", "")

        res_desafios = databases.list_documents(database_id=DB_ID, collection_id="desafios")
        for d in res_desafios.get("documents", []):
            if d.get("trilha_id") == trilha_id:
                return {
                    "trilha": t_nome,
                    "titulo_desafio": d.get("titulo"),
                    "enunciado": d.get("enunciado"),
                    "template_codigo": d.get("template_codigo")
                }

        novo_desafio = {
            "trilha_id": trilha_id,
            "titulo": f"Desafio Pratico - {t_nome}",
            "enunciado": f"Implemente a solucao dos conceitos de {t_cat} para a trilha {t_nome}.",
            "template_codigo": f"# Solucao para {t_nome}\ndef solucao():\n    pass\n"
        }
        databases.create_document(database_id=DB_ID, collection_id="desafios", document_id=ID.unique(), data=novo_desafio)
        return {
            "trilha": t_nome,
            "titulo_desafio": novo_desafio["titulo"],
            "enunciado": novo_desafio["enunciado"],
            "template_codigo": novo_desafio["template_codigo"]
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def emitir_certificado(nome_usuario: str, trilha_nome: str) -> dict:
    """Emite um certificado ficticio de conclusao de trilha e registra no Appwrite."""
    codigo_cert = f"GEO-CERT-{datetime.now().year}-{uuid.uuid4().hex[:8].upper()}"
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cert = {
        "codigo": codigo_cert,
        "usuario": nome_usuario,
        "trilha_nome": trilha_nome,
        "data_emissao": data_hoje
    }

    try:
        databases.create_document(
            database_id=DB_ID,
            collection_id="certificados",
            document_id=ID.unique(),
            data=cert
        )
    except Exception:
        pass

    return cert

if __name__ == "__main__":
    mcp.run()