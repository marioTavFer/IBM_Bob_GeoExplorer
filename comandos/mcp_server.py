# -*- coding: utf-8 -*-
"""
Servidor MCP para o Geo-Explorer (Appwrite Integration)
Permite que Agentes de IA (como IBM Bob & Antigravity) consultem trilhas, desafios e emitam certificados via MCP.
"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP
from appwrite.client import Client
from appwrite.id import ID
from appwrite.query import Query

# Suporte ao API moderno TablesDB (Appwrite 1.8.0+) com fallback para Databases
try:
    from appwrite.services.tables_db import TablesDB
    IS_TABLES_DB = True
except ImportError:
    from appwrite.services.databases import Databases
    IS_TABLES_DB = False

load_dotenv()

mcp = FastMCP("Geo-Explorer MCP Server")

ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
PROJECT_ID = os.getenv("APPWRITE_PROJECT")
API_KEY = os.getenv("APPWRITE_API_KEY")

client = Client()
client.set_endpoint(ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)

if IS_TABLES_DB:
    db_service = TablesDB(client)
else:
    db_service = Databases(client)

DB_ID = "escola"


def fetch_rows_mcp(collection_id: str, queries: list = None) -> list[dict]:
    """Auxiliar para consulta de registros com compatibilidade ao TablesDB."""
    if queries is None:
        queries = []

    try:
        if IS_TABLES_DB:
            resultado = db_service.list_rows(
                database_id=DB_ID,
                table_id=collection_id,
                queries=queries
            )
            rows = getattr(resultado, "rows", [])
            return [{"$id": getattr(r, "id", ""), **getattr(r, "data", {})} for r in rows]
        else:
            resultado = db_service.list_documents(
                database_id=DB_ID,
                collection_id=collection_id,
                queries=queries
            )
            docs = getattr(resultado, "documents", [])
            return [{"$id": getattr(d, "id", ""), **getattr(d, "data", {})} for d in docs]
    except Exception as e:
        print(f"Erro no MCP ao consultar '{collection_id}': {e}")
        return []


def create_row_mcp(collection_id: str, data: dict) -> dict:
    """Auxiliar para inserção de registros no Appwrite."""
    row_id = ID.unique()
    try:
        if IS_TABLES_DB:
            res = db_service.create_row(
                database_id=DB_ID,
                table_id=collection_id,
                row_id=row_id,
                data=data
            )
            return {"$id": getattr(res, "id", row_id), **getattr(res, "data", data)}
        else:
            res = db_service.create_document(
                database_id=DB_ID,
                collection_id=collection_id,
                document_id=row_id,
                data=data
            )
            return {"$id": getattr(res, "id", row_id), **data}
    except Exception as e:
        print(f"Erro no MCP ao criar registro em '{collection_id}': {e}")
        return {"$id": row_id, **data}


@mcp.tool()
def listar_trilhas(categoria: str = None) -> list:
    """Lista as trilhas de aprendizagem registradas no Appwrite. Pode filtrar por categoria."""
    try:
        docs = fetch_rows_mcp("trilhas", queries=[Query.limit(100)])
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
    """Obtém ou gera um desafio de código para uma determinada trilha de aprendizagem."""
    try:
        res_trilhas = fetch_rows_mcp("trilhas", queries=[Query.limit(100)])
        trilha = None
        for t in res_trilhas:
            t_titulo = t.get("titulo", "")
            if trilha_titulo.lower() in t_titulo.lower():
                trilha = t
                break

        if not trilha:
            return {"error": f"Trilha '{trilha_titulo}' nao encontrada."}

        trilha_id = trilha.get("$id")
        t_nome = trilha.get("titulo", "")
        t_cat = trilha.get("categoria", "")

        res_desafios = fetch_rows_mcp("desafios", queries=[Query.equal("trilha_id", trilha_id), Query.limit(1)])
        if res_desafios:
            d = res_desafios[0]
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
        create_row_mcp("desafios", novo_desafio)
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
    """Emite um certificado fictício de conclusão de trilha e registra no Appwrite."""
    codigo_cert = f"GEO-CERT-{datetime.now().year}-{uuid.uuid4().hex[:8].upper()}"
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cert = {
        "codigo": codigo_cert,
        "usuario": nome_usuario,
        "trilha_nome": trilha_nome,
        "data_emissao": data_hoje
    }

    create_row_mcp("certificados", cert)
    return cert


if __name__ == "__main__":
    mcp.run()