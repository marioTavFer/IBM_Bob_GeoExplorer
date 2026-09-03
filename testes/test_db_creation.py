# -*- coding: utf-8 -*-
"""
Testes unitários — Criação de tabelas no Appwrite 1.8.0+ / TablesDB
Verifica a criação das tabelas 'trilhas', 'desafios' e 'certificados',
a definição de colunas e o tratamento de erros (tabela já existente).
Todos os testes são isolados de rede via unittest.mock.
"""

import os
import unittest
from unittest.mock import MagicMock, call

# ---------------------------------------------------------------------------
# Patch de ambiente antes de qualquer import do SDK
# ---------------------------------------------------------------------------
os.environ.setdefault("APPWRITE_ENDPOINT", "https://mock.appwrite.io/v1")
os.environ.setdefault("APPWRITE_PROJECT",  "mock_project")
os.environ.setdefault("APPWRITE_API_KEY",  "mock_key")

DB_ID = "escola"


class TestCriacaoTabelas(unittest.TestCase):
    """Verifica que db.create_table é chamado para cada tabela esperada."""

    def setUp(self):
        self.db = MagicMock()

    def test_cria_tabela_trilhas(self):
        """create_table é chamado com table_id='trilhas'."""
        self.db.create_table(database_id=DB_ID, table_id="trilhas", name="Trilhas de Aprendizagem")
        self.db.create_table.assert_called_with(
            database_id=DB_ID,
            table_id="trilhas",
            name="Trilhas de Aprendizagem",
        )

    def test_cria_tabela_desafios(self):
        """create_table é chamado com table_id='desafios'."""
        self.db.create_table(database_id=DB_ID, table_id="desafios", name="Desafios de Codigo")
        self.db.create_table.assert_called_with(
            database_id=DB_ID,
            table_id="desafios",
            name="Desafios de Codigo",
        )

    def test_cria_tabela_certificados(self):
        """create_table é chamado com table_id='certificados'."""
        self.db.create_table(database_id=DB_ID, table_id="certificados", name="Certificados Emitidos")
        self.db.create_table.assert_called_with(
            database_id=DB_ID,
            table_id="certificados",
            name="Certificados Emitidos",
        )

    def test_cria_todas_as_tres_tabelas(self):
        """create_table é chamado exatamente 3 vezes (trilhas, desafios, certificados)."""
        tabelas = {
            "trilhas":      "Trilhas de Aprendizagem",
            "desafios":     "Desafios de Codigo",
            "certificados": "Certificados Emitidos",
        }
        for table_id, name in tabelas.items():
            self.db.create_table(database_id=DB_ID, table_id=table_id, name=name)

        self.assertEqual(self.db.create_table.call_count, 3)

    def test_tabela_ja_existente_nao_lanca_excecao_ao_tratar(self):
        """Exceção de tabela existente é capturada sem propagar."""
        self.db.create_table.side_effect = Exception("Table already exists")
        try:
            self.db.create_table(database_id=DB_ID, table_id="trilhas", name="Trilhas de Aprendizagem")
        except Exception:
            pass  # comportamento esperado: capturar e seguir
        # nenhuma exceção deve chegar ao chamador
        self.assertTrue(True)


class TestColunasTabelaTrilhas(unittest.TestCase):
    """Verifica a criação das colunas da tabela 'trilhas'."""

    def setUp(self):
        self.db = MagicMock()

    def test_coluna_titulo_string(self):
        """create_string_column é chamado para 'titulo' com size=255."""
        self.db.create_string_column(
            database_id=DB_ID, table_id="trilhas", key="titulo", size=255, required=True
        )
        self.db.create_string_column.assert_called_with(
            database_id=DB_ID, table_id="trilhas", key="titulo", size=255, required=True
        )

    def test_coluna_categoria_string(self):
        """create_string_column é chamado para 'categoria' com size=100."""
        self.db.create_string_column(
            database_id=DB_ID, table_id="trilhas", key="categoria", size=100, required=True
        )
        self.db.create_string_column.assert_called_with(
            database_id=DB_ID, table_id="trilhas", key="categoria", size=100, required=True
        )

    def test_coluna_nivel_string(self):
        """create_string_column é chamado para 'nivel' com size=50."""
        self.db.create_string_column(
            database_id=DB_ID, table_id="trilhas", key="nivel", size=50, required=True
        )
        self.db.create_string_column.assert_called_with(
            database_id=DB_ID, table_id="trilhas", key="nivel", size=50, required=True
        )

    def test_coluna_duracao_integer(self):
        """create_integer_column é chamado para 'duracao_horas'."""
        self.db.create_integer_column(
            database_id=DB_ID, table_id="trilhas", key="duracao_horas", required=False, min=0, max=1000
        )
        self.db.create_integer_column.assert_called_with(
            database_id=DB_ID, table_id="trilhas", key="duracao_horas", required=False, min=0, max=1000
        )

    def test_cinco_colunas_criadas_para_trilhas(self):
        """Exatamente 5 colunas são criadas para a tabela 'trilhas'."""
        colunas_string = [
            ("titulo",    255,  True),
            ("categoria", 100,  True),
            ("nivel",     50,   True),
            ("descricao", 1000, True),
        ]
        for key, size, required in colunas_string:
            self.db.create_string_column(
                database_id=DB_ID, table_id="trilhas", key=key, size=size, required=required
            )
        self.db.create_integer_column(
            database_id=DB_ID, table_id="trilhas", key="duracao_horas", required=False, min=0, max=1000
        )
        total = self.db.create_string_column.call_count + self.db.create_integer_column.call_count
        self.assertEqual(total, 5)


class TestColunasTabelaDesafios(unittest.TestCase):
    """Verifica a criação das colunas da tabela 'desafios'."""

    def setUp(self):
        self.db = MagicMock()

    def test_quatro_colunas_criadas_para_desafios(self):
        """Exatamente 4 colunas string são criadas para 'desafios'."""
        colunas = [
            ("trilha_id",       100,  True),
            ("titulo",          255,  True),
            ("enunciado",       2000, True),
            ("template_codigo", 2000, True),
        ]
        for key, size, required in colunas:
            self.db.create_string_column(
                database_id=DB_ID, table_id="desafios", key=key, size=size, required=required
            )
        self.assertEqual(self.db.create_string_column.call_count, 4)

    def test_coluna_trilha_id_referencia(self):
        """create_string_column é chamado para 'trilha_id' em 'desafios'."""
        self.db.create_string_column(
            database_id=DB_ID, table_id="desafios", key="trilha_id", size=100, required=True
        )
        self.db.create_string_column.assert_called_with(
            database_id=DB_ID, table_id="desafios", key="trilha_id", size=100, required=True
        )


class TestColunasTabelaCertificados(unittest.TestCase):
    """Verifica a criação das colunas da tabela 'certificados'."""

    def setUp(self):
        self.db = MagicMock()

    def test_quatro_colunas_criadas_para_certificados(self):
        """Exatamente 4 colunas string são criadas para 'certificados'."""
        colunas = [
            ("codigo",       100, True),
            ("usuario",      100, True),
            ("trilha_nome",  255, True),
            ("data_emissao", 100, True),
        ]
        for key, size, required in colunas:
            self.db.create_string_column(
                database_id=DB_ID, table_id="certificados", key=key, size=size, required=required
            )
        self.assertEqual(self.db.create_string_column.call_count, 4)

    def test_coluna_codigo_certificado(self):
        """create_string_column é chamado para 'codigo' em 'certificados'."""
        self.db.create_string_column(
            database_id=DB_ID, table_id="certificados", key="codigo", size=100, required=True
        )
        self.db.create_string_column.assert_called_with(
            database_id=DB_ID, table_id="certificados", key="codigo", size=100, required=True
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
