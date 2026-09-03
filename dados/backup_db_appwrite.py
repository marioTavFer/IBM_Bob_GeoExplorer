# -*- coding: utf-8 -*-
"""
Backup do banco 'escola' (Appwrite 1.8.0+ / TablesDB) para SQLite local.
Arquivo gerado: dados/backup_db_appwrite.sqlite

Tabelas copiadas:
  - trilhas      : titulo, categoria, nivel, descricao, duracao_horas
  - desafios     : trilha_id, titulo, enunciado, template_codigo
  - certificados : codigo, usuario, trilha_nome, data_emissao

Cada execução faz um backup incremental (INSERT OR REPLACE), preservando
registros anteriores e atualizando os que já existem pelo $id do Appwrite.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.query import Query
from appwrite.services.tables_db import TablesDB

# ─────────────────────────────────────────────────────────
# Configuração
# ─────────────────────────────────────────────────────────
load_dotenv()

APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
APPWRITE_PROJECT  = os.getenv("APPWRITE_PROJECT")
APPWRITE_API_KEY  = os.getenv("APPWRITE_API_KEY")
APPWRITE_DB_ID    = "escola"

SQLITE_PATH = Path(__file__).parent / "backup_db_appwrite.sqlite"

# ─────────────────────────────────────────────────────────
# Conexão Appwrite
# ─────────────────────────────────────────────────────────
client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT)
client.set_key(APPWRITE_API_KEY)

db = TablesDB(client)


# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────

def fetch_all_rows(table_id: str) -> list[dict]:
    """Busca todos os registros de uma tabela com paginação automática."""
    rows   = []
    offset = 0
    limit  = 100
    while True:
        result = db.list_rows(
            database_id=APPWRITE_DB_ID,
            table_id=table_id,
            queries=[Query.limit(limit), Query.offset(offset)],
        )
        batch = result.rows
        rows += [{"$id": r.id, **r.data} for r in batch]
        if len(batch) < limit:
            break
        offset += limit
    return rows


def setup_sqlite(conn: sqlite3.Connection) -> None:
    """Cria as tabelas no SQLite caso ainda não existam."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS trilhas (
            appwrite_id    TEXT PRIMARY KEY,
            titulo         TEXT,
            categoria      TEXT,
            nivel          TEXT,
            descricao      TEXT,
            duracao_horas  INTEGER,
            backup_em      TEXT
        );

        CREATE TABLE IF NOT EXISTS desafios (
            appwrite_id      TEXT PRIMARY KEY,
            trilha_id        TEXT,
            titulo           TEXT,
            enunciado        TEXT,
            template_codigo  TEXT,
            backup_em        TEXT
        );

        CREATE TABLE IF NOT EXISTS certificados (
            appwrite_id   TEXT PRIMARY KEY,
            codigo        TEXT,
            usuario       TEXT,
            trilha_nome   TEXT,
            data_emissao  TEXT,
            backup_em     TEXT
        );

        CREATE TABLE IF NOT EXISTS backup_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            executado_em TEXT,
            trilhas    INTEGER,
            desafios   INTEGER,
            certificados INTEGER
        );
    """)
    conn.commit()


def backup_trilhas(conn: sqlite3.Connection, ts: str) -> int:
    rows = fetch_all_rows("trilhas")
    conn.executemany(
        """INSERT OR REPLACE INTO trilhas
           (appwrite_id, titulo, categoria, nivel, descricao, duracao_horas, backup_em)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                r["$id"],
                r.get("titulo"),
                r.get("categoria"),
                r.get("nivel"),
                r.get("descricao"),
                r.get("duracao_horas"),
                ts,
            )
            for r in rows
        ],
    )
    conn.commit()
    return len(rows)


def backup_desafios(conn: sqlite3.Connection, ts: str) -> int:
    rows = fetch_all_rows("desafios")
    conn.executemany(
        """INSERT OR REPLACE INTO desafios
           (appwrite_id, trilha_id, titulo, enunciado, template_codigo, backup_em)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [
            (
                r["$id"],
                r.get("trilha_id"),
                r.get("titulo"),
                r.get("enunciado"),
                r.get("template_codigo"),
                ts,
            )
            for r in rows
        ],
    )
    conn.commit()
    return len(rows)


def backup_certificados(conn: sqlite3.Connection, ts: str) -> int:
    rows = fetch_all_rows("certificados")
    conn.executemany(
        """INSERT OR REPLACE INTO certificados
           (appwrite_id, codigo, usuario, trilha_nome, data_emissao, backup_em)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [
            (
                r["$id"],
                r.get("codigo"),
                r.get("usuario"),
                r.get("trilha_nome"),
                r.get("data_emissao"),
                ts,
            )
            for r in rows
        ],
    )
    conn.commit()
    return len(rows)


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────

def main() -> None:
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print("=" * 60)
    print("  GEO-EXPLORER - Backup Appwrite -> SQLite")
    print(f"  Iniciado em: {ts}")
    print("=" * 60)

    conn = sqlite3.connect(SQLITE_PATH)
    setup_sqlite(conn)

    totais: dict[str, int] = {}

    tabelas = [
        ("trilhas",      backup_trilhas),
        ("desafios",     backup_desafios),
        ("certificados", backup_certificados),
    ]

    for nome, fn in tabelas:
        try:
            n = fn(conn, ts)
            totais[nome] = n
            print(f"  [OK] {nome:<14} {n:>4} registro(s) copiado(s)")
        except Exception as e:
            totais[nome] = 0
            print(f"  [ERRO] {nome:<14} {e}")

    # Registra no log de backups
    conn.execute(
        "INSERT INTO backup_log (executado_em, trilhas, desafios, certificados) VALUES (?, ?, ?, ?)",
        (ts, totais.get("trilhas", 0), totais.get("desafios", 0), totais.get("certificados", 0)),
    )
    conn.commit()
    conn.close()

    print("-" * 60)
    print(f"  Backup salvo em: {SQLITE_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
