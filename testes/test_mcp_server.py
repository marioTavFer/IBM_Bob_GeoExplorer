# -*- coding: utf-8 -*-
"""
Testes unitários para os comandos MCP do Geo-Explorer (comandos/mcp_server.py).
Utiliza unittest.mock para isolar chamadas ao Appwrite — sem dependência de rede.

Cobertura:
  - fetch_rows        : retorno normal, lista vazia, exceção
  - create_row        : retorno normal, exceção com fallback
  - listar_trilhas    : sem filtro, com filtro de categoria, sem resultados, erro
  - obter_desafio     : desafio existente, desafio gerado, trilha não encontrada, erro
  - emitir_certificado: campos obrigatórios, formato do código, persistência
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
import pathlib

# ---------------------------------------------------------------------------
# Timestamp de execução — atualizado no relatorio_testes_MCP.md ao rodar
# ---------------------------------------------------------------------------
_REPORT_PATH = pathlib.Path(__file__).parent / "relatorio_testes_MCP.md"
_RUN_TS      = datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def _update_report_timestamp() -> None:
    """Substitui a linha **Data:** no relatório pela data/hora de execução."""
    if not _REPORT_PATH.exists():
        return
    content = _REPORT_PATH.read_text(encoding="utf-8")
    new_line = f"**Data de execução:** {_RUN_TS}  "
    lines = content.splitlines()
    updated = []
    for line in lines:
        if line.startswith("**Data"):
            updated.append(new_line)
        else:
            updated.append(line)
    _REPORT_PATH.write_text("\n".join(updated) + "\n", encoding="utf-8")


_update_report_timestamp()

# ---------------------------------------------------------------------------
# Garante que 'comandos/' está no path para importar mcp_server sem instalar
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "comandos"))


# ---------------------------------------------------------------------------
# Patch do ambiente ANTES de importar mcp_server (evita load_dotenv + Client)
# ---------------------------------------------------------------------------
_env_patch = patch.dict(os.environ, {
    "APPWRITE_ENDPOINT": "https://mock.appwrite.io/v1",
    "APPWRITE_PROJECT":  "mock_project",
    "APPWRITE_API_KEY":  "mock_key",
})
_env_patch.start()

with patch("appwrite.client.Client"), \
     patch("appwrite.services.tables_db.TablesDB"):
    import mcp_server  # noqa: E402

_env_patch.stop()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_row(row_id: str, data: dict):
    """Cria um objeto simulando um Row do TablesDB."""
    row = MagicMock()
    row.id   = row_id
    row.data = data
    return row


def _make_list_result(rows: list):
    """Cria um objeto simulando o resultado de list_rows."""
    result = MagicMock()
    result.rows = rows
    return result


def _make_create_result(row_id: str, data: dict):
    """Cria um objeto simulando o resultado de create_row."""
    res = MagicMock()
    res.id   = row_id
    res.data = data
    return res


# ---------------------------------------------------------------------------
# Testes: fetch_rows
# ---------------------------------------------------------------------------

class TestFetchRows(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        mcp_server.db = self.mock_db

    def test_retorna_lista_de_dicts(self):
        """fetch_rows converte rows em lista de dicts com $id."""
        rows = [_make_row("id1", {"titulo": "Python"})]
        self.mock_db.list_rows.return_value = _make_list_result(rows)

        result = mcp_server.fetch_rows("trilhas")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["$id"], "id1")
        self.assertEqual(result[0]["titulo"], "Python")

    def test_retorna_lista_vazia_quando_sem_rows(self):
        """fetch_rows retorna [] quando não há registros."""
        self.mock_db.list_rows.return_value = _make_list_result([])

        result = mcp_server.fetch_rows("trilhas")

        self.assertEqual(result, [])

    def test_retorna_lista_vazia_em_excecao(self):
        """fetch_rows retorna [] em caso de exceção do SDK."""
        self.mock_db.list_rows.side_effect = Exception("SDK error")

        result = mcp_server.fetch_rows("trilhas")

        self.assertEqual(result, [])

    def test_passa_queries_corretamente(self):
        """fetch_rows encaminha o argumento queries ao SDK."""
        self.mock_db.list_rows.return_value = _make_list_result([])
        queries = ["Query.limit(10)"]

        mcp_server.fetch_rows("trilhas", queries=queries)

        call_kwargs = self.mock_db.list_rows.call_args.kwargs
        self.assertEqual(call_kwargs["queries"], queries)

    def test_queries_none_passa_lista_vazia(self):
        """fetch_rows passa [] ao SDK quando queries=None."""
        self.mock_db.list_rows.return_value = _make_list_result([])

        mcp_server.fetch_rows("trilhas", queries=None)

        call_kwargs = self.mock_db.list_rows.call_args.kwargs
        self.assertEqual(call_kwargs["queries"], [])


# ---------------------------------------------------------------------------
# Testes: create_row
# ---------------------------------------------------------------------------

class TestCreateRow(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        mcp_server.db = self.mock_db

    def test_retorna_dict_com_id_e_dados(self):
        """create_row retorna o registro criado com $id."""
        data = {"titulo": "Flask"}
        self.mock_db.create_row.return_value = _make_create_result("abc123", data)

        result = mcp_server.create_row("trilhas", data)

        self.assertEqual(result["$id"], "abc123")
        self.assertEqual(result["titulo"], "Flask")

    def test_fallback_em_excecao(self):
        """create_row retorna dict local com $id gerado em caso de erro."""
        self.mock_db.create_row.side_effect = Exception("SDK error")
        data = {"titulo": "Django"}

        result = mcp_server.create_row("trilhas", data)

        self.assertIn("$id", result)
        self.assertEqual(result["titulo"], "Django")


# ---------------------------------------------------------------------------
# Testes: listar_trilhas
# ---------------------------------------------------------------------------

class TestListarTrilhas(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        mcp_server.db = self.mock_db

    def _mock_trilhas(self, trilhas: list[dict]):
        rows = [_make_row(t.pop("$id", f"id{i}"), t) for i, t in enumerate(trilhas)]
        self.mock_db.list_rows.return_value = _make_list_result(rows)

    def test_lista_todas_sem_filtro(self):
        """listar_trilhas sem categoria retorna todas as trilhas."""
        self._mock_trilhas([
            {"$id": "1", "titulo": "Python", "categoria": "Back-end", "nivel": "Basico", "duracao_horas": 10, "descricao": ""},
            {"$id": "2", "titulo": "React",  "categoria": "Front-end", "nivel": "Medio",  "duracao_horas": 20, "descricao": ""},
        ])

        result = mcp_server.listar_trilhas()

        self.assertEqual(len(result), 2)

    def test_filtra_por_categoria(self):
        """listar_trilhas com categoria retorna apenas trilhas correspondentes."""
        self._mock_trilhas([
            {"$id": "1", "titulo": "Python", "categoria": "Back-end",  "nivel": "Basico", "duracao_horas": 10, "descricao": ""},
            {"$id": "2", "titulo": "React",  "categoria": "Front-end", "nivel": "Medio",  "duracao_horas": 20, "descricao": ""},
        ])

        result = mcp_server.listar_trilhas(categoria="Back-end")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["titulo"], "Python")

    def test_filtra_categoria_case_insensitive(self):
        """listar_trilhas filtra categoria ignorando maiúsculas/minúsculas."""
        self._mock_trilhas([
            {"$id": "1", "titulo": "Python", "categoria": "Back-end", "nivel": "Basico", "duracao_horas": 10, "descricao": ""},
        ])

        result = mcp_server.listar_trilhas(categoria="back-end")

        self.assertEqual(len(result), 1)

    def test_retorna_lista_vazia_sem_resultados(self):
        """listar_trilhas retorna [] quando não há trilhas."""
        self.mock_db.list_rows.return_value = _make_list_result([])

        result = mcp_server.listar_trilhas()

        self.assertEqual(result, [])

    def test_retorna_lista_vazia_quando_fetch_rows_falha(self):
        """listar_trilhas retorna [] quando fetch_rows absorve a exceção do SDK."""
        self.mock_db.list_rows.side_effect = Exception("falha")

        result = mcp_server.listar_trilhas()

        # fetch_rows captura a exceção e retorna [] — listar_trilhas propaga []
        self.assertEqual(result, [])


# ---------------------------------------------------------------------------
# Testes: obter_desafio
# ---------------------------------------------------------------------------

class TestObterDesafio(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        mcp_server.db = self.mock_db

    def _mock_trilha(self, trilha_id="t1", titulo="Python Avancado", categoria="Back-end"):
        row = _make_row(trilha_id, {"titulo": titulo, "categoria": categoria})
        self.mock_db.list_rows.return_value = _make_list_result([row])

    def _mock_desafio_existente(self):
        row = _make_row("d1", {
            "trilha_id":       "t1",
            "titulo":          "Desafio Python",
            "enunciado":       "Resolva X",
            "template_codigo": "def solucao(): pass",
        })
        # segunda chamada list_rows retorna o desafio
        self.mock_db.list_rows.side_effect = [
            _make_list_result([_make_row("t1", {"titulo": "Python Avancado", "categoria": "Back-end"})]),
            _make_list_result([row]),
        ]

    def test_retorna_desafio_existente(self):
        """obter_desafio retorna desafio já cadastrado para a trilha."""
        self._mock_desafio_existente()

        result = mcp_server.obter_desafio("Python Avancado")

        self.assertEqual(result["titulo_desafio"], "Desafio Python")
        self.assertEqual(result["enunciado"], "Resolva X")

    def test_gera_novo_desafio_quando_nao_existe(self):
        """obter_desafio cria e retorna novo desafio quando não há nenhum cadastrado."""
        self.mock_db.list_rows.side_effect = [
            _make_list_result([_make_row("t1", {"titulo": "Python Avancado", "categoria": "Back-end"})]),
            _make_list_result([]),  # sem desafios existentes
        ]
        self.mock_db.create_row.return_value = _make_create_result("d_novo", {})

        result = mcp_server.obter_desafio("Python Avancado")

        self.assertIn("titulo_desafio", result)
        self.assertIn("Desafio Pratico", result["titulo_desafio"])

    def test_retorna_erro_quando_trilha_nao_encontrada(self):
        """obter_desafio retorna {'error': ...} quando trilha não existe."""
        self.mock_db.list_rows.return_value = _make_list_result([])

        result = mcp_server.obter_desafio("Trilha Inexistente")

        self.assertIn("error", result)
        self.assertIn("Trilha Inexistente", result["error"])

    def test_retorna_erro_em_excecao(self):
        """obter_desafio retorna {'error': ...} em caso de exceção."""
        self.mock_db.list_rows.side_effect = Exception("SDK crash")

        result = mcp_server.obter_desafio("Qualquer")

        self.assertIn("error", result)


# ---------------------------------------------------------------------------
# Testes: emitir_certificado
# ---------------------------------------------------------------------------

class TestEmitirCertificado(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        mcp_server.db = self.mock_db
        self.mock_db.create_row.return_value = _make_create_result("cert1", {})

    def test_retorna_campos_obrigatorios(self):
        """emitir_certificado retorna dict com todos os campos esperados."""
        result = mcp_server.emitir_certificado("Ana Silva", "Python Avancado")

        self.assertIn("codigo",       result)
        self.assertIn("usuario",      result)
        self.assertIn("trilha_nome",  result)
        self.assertIn("data_emissao", result)

    def test_codigo_formato_geo_cert(self):
        """emitir_certificado gera código no formato GEO-CERT-AAAA-XXXXXXXX."""
        result = mcp_server.emitir_certificado("Ana Silva", "Python Avancado")

        self.assertTrue(result["codigo"].startswith("GEO-CERT-"))
        partes = result["codigo"].split("-")
        self.assertEqual(len(partes), 4)
        self.assertEqual(partes[2], str(datetime.now().year))

    def test_usuario_e_trilha_corretos(self):
        """emitir_certificado registra nome e trilha fornecidos."""
        result = mcp_server.emitir_certificado("Carlos Melo", "React Hooks")

        self.assertEqual(result["usuario"],     "Carlos Melo")
        self.assertEqual(result["trilha_nome"], "React Hooks")

    def test_persiste_no_appwrite(self):
        """emitir_certificado chama create_row para salvar o certificado."""
        mcp_server.emitir_certificado("Ana Silva", "Python Avancado")

        self.mock_db.create_row.assert_called_once()
        call_kwargs = self.mock_db.create_row.call_args.kwargs
        self.assertEqual(call_kwargs["table_id"], "certificados")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
