# Relatório de Testes — Conexão Appwrite (test_appwrite)

**Arquivo testado:** `comandos/test_appwrite.py` (lógica de conexão)  
**Suite de testes:** `testes/test_appwrite.py`  
**Framework:** `pytest 9.1.1` · `unittest.mock`  
**Python:** 3.13.9  
**Resultado geral:** ✅ **9 / 9 aprovados — 0 falhas**

---

## Objetivo

Verificar que a inicialização do `Client` Appwrite e do serviço `TablesDB` ocorre
corretamente, e que `db.list()` retorna e mapeia bancos de dados de forma adequada —
tudo sem dependência de rede real.

---

## Suites e Casos de Teste

### `TestAppwriteConnection` — Inicialização do Client e TablesDB

| # | Caso de Teste | Resultado |
|---|---|---|
| 1 | `Client.set_endpoint` é chamado com o valor de `APPWRITE_ENDPOINT` | ✅ PASS |
| 2 | `Client.set_project` é chamado com o valor de `APPWRITE_PROJECT` | ✅ PASS |
| 3 | `Client.set_key` é chamado com o valor de `APPWRITE_API_KEY` | ✅ PASS |
| 4 | `TablesDB` é instanciado recebendo o `Client` como argumento | ✅ PASS |

**Comportamento verificado:** encadeamento correto das três chamadas de configuração do
client e repasse do client ao construtor do `TablesDB`.

---

### `TestAppwriteListDatabases` — Listagem de bancos de dados

| # | Caso de Teste | Resultado |
|---|---|---|
| 5 | `db.list()` retorna o número correto de bancos (`total`) | ✅ PASS |
| 6 | `db.list()` retorna o nome correto de cada banco | ✅ PASS |
| 7 | `db.list()` retorna o ID correto de cada banco | ✅ PASS |
| 8 | `db.list()` retorna `total=0` e lista vazia quando não há bancos | ✅ PASS |
| 9 | `db.list()` propaga exceção (`Unauthorized`) quando o SDK falha | ✅ PASS |

**Comportamento verificado:** mapeamento de `result.total` e `result.databases[*].name/id`,
resposta vazia e propagação de erro de autenticação.

> **Nota técnica:** `MagicMock(name=...)` é um argumento especial do construtor do mock
> (define o nome interno da instância) e **não** cria o atributo `.name`. Os mocks de banco
> usam atribuição direta (`item.name = "escola"`) para garantir o valor correto.

---

## Resumo Executivo

```
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-9.1.1
collected 9 items

testes/test_appwrite.py::TestAppwriteConnection::test_client_inicializado_com_api_key      PASSED
testes/test_appwrite.py::TestAppwriteConnection::test_client_inicializado_com_endpoint     PASSED
testes/test_appwrite.py::TestAppwriteConnection::test_client_inicializado_com_project      PASSED
testes/test_appwrite.py::TestAppwriteConnection::test_tablesdb_instanciado_com_client      PASSED
testes/test_appwrite.py::TestAppwriteListDatabases::test_list_lanca_excecao_em_erro        PASSED
testes/test_appwrite.py::TestAppwriteListDatabases::test_list_retorna_ids_dos_bancos       PASSED
testes/test_appwrite.py::TestAppwriteListDatabases::test_list_retorna_lista_vazia          PASSED
testes/test_appwrite.py::TestAppwriteListDatabases::test_list_retorna_nome_dos_bancos      PASSED
testes/test_appwrite.py::TestAppwriteListDatabases::test_list_retorna_total_correto        PASSED

============================== 9 passed in 0.60s ==============================
```

---

## Como Executar

```bash
uv run pytest testes/test_appwrite.py -v
```
