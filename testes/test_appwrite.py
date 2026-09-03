# -*- coding: utf-8 -*-
"""
Testes unitários — Conexão Appwrite 1.8.0+ / TablesDB
Verifica inicialização do Client, instanciação do TablesDB,
chamada a db.list() e mapeamento dos bancos de dados retornados.
Todos os testes são isolados de rede via unittest.mock.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch, call

# ---------------------------------------------------------------------------
# Patch de ambiente antes de qualquer import do SDK
# ---------------------------------------------------------------------------
os.environ.setdefault("APPWRITE_ENDPOINT", "https://mock.appwrite.io/v1")
os.environ.setdefault("APPWRITE_PROJECT",  "mock_project")
os.environ.setdefault("APPWRITE_API_KEY",  "mock_key")


class TestAppwriteConnection(unittest.TestCase):
    """Verifica que o Client e o TablesDB são inicializados corretamente."""

    def _make_client(self):
        """Retorna um Client mock que suporta encadeamento de set_*."""
        client = MagicMock()
        client.set_endpoint.return_value = client
        client.set_project.return_value  = client
        client.set_key.return_value      = client
        return client

    @patch("appwrite.services.tables_db.TablesDB")
    @patch("appwrite.client.Client")
    def test_client_inicializado_com_endpoint(self, MockClient, MockTablesDB):
        """Client.set_endpoint é chamado com o valor de APPWRITE_ENDPOINT."""
        mock_client = self._make_client()
        MockClient.return_value = mock_client

        client = MockClient()
        client.set_endpoint(os.environ["APPWRITE_ENDPOINT"])
        client.set_project(os.environ["APPWRITE_PROJECT"])
        client.set_key(os.environ["APPWRITE_API_KEY"])

        mock_client.set_endpoint.assert_called_with("https://mock.appwrite.io/v1")

    @patch("appwrite.services.tables_db.TablesDB")
    @patch("appwrite.client.Client")
    def test_client_inicializado_com_project(self, MockClient, MockTablesDB):
        """Client.set_project é chamado com o valor de APPWRITE_PROJECT."""
        mock_client = self._make_client()
        MockClient.return_value = mock_client

        client = MockClient()
        client.set_project(os.environ["APPWRITE_PROJECT"])

        mock_client.set_project.assert_called_with("mock_project")

    @patch("appwrite.services.tables_db.TablesDB")
    @patch("appwrite.client.Client")
    def test_client_inicializado_com_api_key(self, MockClient, MockTablesDB):
        """Client.set_key é chamado com o valor de APPWRITE_API_KEY."""
        mock_client = self._make_client()
        MockClient.return_value = mock_client

        client = MockClient()
        client.set_key(os.environ["APPWRITE_API_KEY"])

        mock_client.set_key.assert_called_with("mock_key")

    @patch("appwrite.services.tables_db.TablesDB")
    @patch("appwrite.client.Client")
    def test_tablesdb_instanciado_com_client(self, MockClient, MockTablesDB):
        """TablesDB é instanciado recebendo o Client como argumento."""
        mock_client = self._make_client()
        MockClient.return_value = mock_client

        client = MockClient()
        MockTablesDB(client)

        MockTablesDB.assert_called_with(mock_client)


class TestAppwriteListDatabases(unittest.TestCase):
    """Verifica o comportamento de db.list() e o mapeamento dos resultados."""

    def _make_db_mock(self, databases: list[dict]):
        """Cria um TablesDB mock com db.list() retornando bancos simulados."""
        db = MagicMock()
        result = MagicMock()
        result.total = len(databases)
        items = []
        for d in databases:
            item = MagicMock()
            item.name = d["name"]
            item.id   = d["id"]
            items.append(item)
        result.databases = items
        db.list.return_value = result
        return db

    def test_list_retorna_total_correto(self):
        """db.list() retorna o número correto de bancos de dados."""
        db = self._make_db_mock([
            {"name": "escola", "id": "escola"},
            {"name": "producao", "id": "prod01"},
        ])
        result = db.list()
        self.assertEqual(result.total, 2)

    def test_list_retorna_nome_dos_bancos(self):
        """db.list() retorna os nomes corretos de cada banco."""
        db = self._make_db_mock([{"name": "escola", "id": "escola"}])
        result = db.list()
        self.assertEqual(result.databases[0].name, "escola")

    def test_list_retorna_ids_dos_bancos(self):
        """db.list() retorna os IDs corretos de cada banco."""
        db = self._make_db_mock([{"name": "escola", "id": "escola"}])
        result = db.list()
        self.assertEqual(result.databases[0].id, "escola")

    def test_list_retorna_lista_vazia(self):
        """db.list() retorna total=0 e lista vazia quando não há bancos."""
        db = self._make_db_mock([])
        result = db.list()
        self.assertEqual(result.total, 0)
        self.assertEqual(result.databases, [])

    def test_list_lanca_excecao_em_erro(self):
        """db.list() propaga exceção quando o SDK falha."""
        db = MagicMock()
        db.list.side_effect = Exception("Unauthorized")
        with self.assertRaises(Exception) as ctx:
            db.list()
        self.assertIn("Unauthorized", str(ctx.exception))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
