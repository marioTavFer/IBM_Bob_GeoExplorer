# -*- coding: utf-8 -*-
"""
Servidor MCP para o Geo-Explorer (Appwrite 1.8.0+ / TablesDB)
Permite que Agentes de IA (como IBM Bob & DIO Agent + Antigravity) consultem
trilhas, desafios e emitam certificados via MCP.
"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP
from appwrite.client import Client
from appwrite.id import ID
from appwrite.query import Query
from appwrite.services.tables_db import TablesDB

load_dotenv()

mcp = FastMCP("Geo-Explorer MCP Server")

ENDPOINT   = os.getenv("APPWRITE_ENDPOINT")
PROJECT_ID = os.getenv("APPWRITE_PROJECT")
API_KEY    = os.getenv("APPWRITE_API_KEY")

client = Client()
client.set_endpoint(ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)

db = TablesDB(client)
DB_ID = "escola"


def fetch_rows(table_id: str, queries: list | None = None) -> list[dict]:
    """Consulta linhas de uma tabela e retorna lista de dicts com $id + dados."""
    try:
        result = db.list_rows(
            database_id=DB_ID,
            table_id=table_id,
            queries=queries if queries is not None else [],
        )
        return [{"$id": r.id, **r.data} for r in result.rows]
    except Exception as e:
        print(f"[fetch_rows] erro em '{table_id}': {e}")
        return []


def create_row(table_id: str, data: dict) -> dict:
    """Insere uma nova linha numa tabela e retorna o registro com $id."""
    row_id = ID.unique()
    try:
        res = db.create_row(database_id=DB_ID, table_id=table_id, row_id=row_id, data=data)
        return {"$id": res.id, **res.data}
    except Exception as e:
        print(f"[create_row] erro em '{table_id}': {e}")
        return {"$id": row_id, **data}


@mcp.tool()
def listar_trilhas(categoria: str | None = None) -> list:
    """Lista as trilhas de aprendizagem registradas no Appwrite. Pode filtrar por categoria."""
    try:
        rows = fetch_rows("trilhas", queries=[Query.limit(100)])
        if categoria:
            rows = [r for r in rows if r.get("categoria", "").lower() == categoria.lower()]
        return [
            {
                "id":            r.get("$id"),
                "titulo":        r.get("titulo"),
                "categoria":     r.get("categoria"),
                "nivel":         r.get("nivel"),
                "duracao_horas": r.get("duracao_horas"),
                "descricao":     r.get("descricao"),
            }
            for r in rows
        ]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def obter_desafio(trilha_titulo: str) -> dict:
    """Obtém ou gera um desafio de código para uma determinada trilha de aprendizagem."""
    try:
        trilha = next(
            (t for t in fetch_rows("trilhas", queries=[Query.limit(100)])
             if trilha_titulo.lower() in t.get("titulo", "").lower()),
            None,
        )
        if not trilha:
            return {"error": f"Trilha '{trilha_titulo}' nao encontrada."}

        trilha_id = trilha["$id"]
        t_nome    = trilha.get("titulo", "")
        t_cat     = trilha.get("categoria", "")

        desafios = fetch_rows("desafios", queries=[Query.equal("trilha_id", trilha_id), Query.limit(1)])
        if desafios:
            d = desafios[0]
            return {
                "trilha":          t_nome,
                "titulo_desafio":  d.get("titulo"),
                "enunciado":       d.get("enunciado"),
                "template_codigo": d.get("template_codigo"),
            }

        novo = {
            "trilha_id":       trilha_id,
            "titulo":          f"Desafio Pratico - {t_nome}",
            "enunciado":       f"Implemente a solucao dos conceitos de {t_cat} para a trilha {t_nome}.",
            "template_codigo": f"# Solucao para {t_nome}\ndef solucao():\n    pass\n",
        }
        create_row("desafios", novo)
        return {
            "trilha":          t_nome,
            "titulo_desafio":  novo["titulo"],
            "enunciado":       novo["enunciado"],
            "template_codigo": novo["template_codigo"],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def emitir_certificado(nome_usuario: str, trilha_nome: str) -> dict:
    """Emite um certificado de conclusão de trilha e registra no Appwrite."""
    cert = {
        "codigo":       f"GEO-CERT-{datetime.now().year}-{uuid.uuid4().hex[:8].upper()}",
        "usuario":      nome_usuario,
        "trilha_nome":  trilha_nome,
        "data_emissao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }
    create_row("certificados", cert)
    return cert


if __name__ == "__main__":
    mcp.run()
