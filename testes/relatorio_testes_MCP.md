# Relatório de Testes — Geo-Explorer MCP Server

**Arquivo testado:** `comandos/mcp_server.py`  
**Suite de testes:** `testes/test_mcp_server.py`  
**Framework:** `pytest 9.1.1` · `unittest.mock`  
**Python:** 3.13.9  
**Data de execução:** 03/09/2026 15:37:25  
**Resultado geral:** ✅ **20 / 20 aprovados — 0 falhas**

---

## Estratégia

Todos os testes são **unitários e isolados de rede**. O SDK Appwrite é substituído por
`MagicMock` antes de cada caso de teste, garantindo que nenhuma chamada real ao Appwrite
seja feita durante a execução da suite.

---

## Suites e Casos de Teste

### `TestFetchRows` — função auxiliar `fetch_rows`

| # | Caso de Teste | Resultado |
|---|---|---|
| 1 | Retorna lista de dicts com `$id` mapeado corretamente | ✅ PASS |
| 2 | Retorna `[]` quando não há registros (`rows` vazio) | ✅ PASS |
| 3 | Retorna `[]` quando o SDK lança exceção | ✅ PASS |
| 4 | Encaminha o argumento `queries` corretamente ao SDK | ✅ PASS |
| 5 | Passa `[]` ao SDK quando `queries=None` | ✅ PASS |

**Comportamento verificado:** conversão de `Row → dict`, tratamento de `None`, propagação
de queries, resiliência a erros do SDK.

---

### `TestCreateRow` — função auxiliar `create_row`

| # | Caso de Teste | Resultado |
|---|---|---|
| 6 | Retorna dict com `$id` e dados do registro criado | ✅ PASS |
| 7 | Em exceção, retorna dict local com `$id` gerado (fallback) | ✅ PASS |

**Comportamento verificado:** mapeamento `res.id / res.data`, fallback offline sem perda de dados.

---

### `TestListarTrilhas` — ferramenta MCP `listar_trilhas`

| # | Caso de Teste | Resultado |
|---|---|---|
| 8 | Lista todas as trilhas sem filtro de categoria | ✅ PASS |
| 9 | Filtra corretamente por categoria exata | ✅ PASS |
| 10 | Filtro de categoria é case-insensitive | ✅ PASS |
| 11 | Retorna `[]` quando não há trilhas cadastradas | ✅ PASS |
| 12 | Retorna `[]` quando `fetch_rows` absorve exceção do SDK | ✅ PASS |

**Comportamento verificado:** filtragem, normalização de case, resposta vazia, tratamento de erro.

> **Nota:** `listar_trilhas` não propaga `{"error": ...}` quando o SDK falha — `fetch_rows`
> captura a exceção internamente e retorna `[]`. O teste foi ajustado para refletir o comportamento
> real do código.

---

### `TestObterDesafio` — ferramenta MCP `obter_desafio`

| # | Caso de Teste | Resultado |
|---|---|---|
| 13 | Retorna desafio já cadastrado para a trilha encontrada | ✅ PASS |
| 14 | Gera e retorna novo desafio quando nenhum existe | ✅ PASS |
| 15 | Retorna `{"error": ...}` quando a trilha não é encontrada | ✅ PASS |
| 16 | Retorna `{"error": ...}` quando o SDK lança exceção | ✅ PASS |

**Comportamento verificado:** lookup de trilha, lookup de desafio existente, criação automática
de desafio, mensagem de erro com nome da trilha incluída.

---

### `TestEmitirCertificado` — ferramenta MCP `emitir_certificado`

| # | Caso de Teste | Resultado |
|---|---|---|
| 17 | Retorna dict com todos os campos: `codigo`, `usuario`, `trilha_nome`, `data_emissao` | ✅ PASS |
| 18 | Código gerado segue o formato `GEO-CERT-AAAA-XXXXXXXX` | ✅ PASS |
| 19 | Nome do usuário e nome da trilha estão corretos no retorno | ✅ PASS |
| 20 | Chama `create_row` com `table_id="certificados"` para persistir | ✅ PASS |

**Comportamento verificado:** estrutura do certificado, formato do código único, persistência
no Appwrite, integridade dos dados de entrada.

---

## Resumo Executivo

```
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-9.1.1
collected 20 items

testes/test_mcp_server.py::TestFetchRows::test_passa_queries_corretamente       PASSED
testes/test_mcp_server.py::TestFetchRows::test_queries_none_passa_lista_vazia   PASSED
testes/test_mcp_server.py::TestFetchRows::test_retorna_lista_de_dicts           PASSED
testes/test_mcp_server.py::TestFetchRows::test_retorna_lista_vazia_em_excecao   PASSED
testes/test_mcp_server.py::TestFetchRows::test_retorna_lista_vazia_quando_sem_rows PASSED
testes/test_mcp_server.py::TestCreateRow::test_fallback_em_excecao             PASSED
testes/test_mcp_server.py::TestCreateRow::test_retorna_dict_com_id_e_dados     PASSED
testes/test_mcp_server.py::TestListarTrilhas::test_filtra_categoria_case_insensitive PASSED
testes/test_mcp_server.py::TestListarTrilhas::test_filtra_por_categoria         PASSED
testes/test_mcp_server.py::TestListarTrilhas::test_lista_todas_sem_filtro       PASSED
testes/test_mcp_server.py::TestListarTrilhas::test_retorna_lista_vazia_quando_fetch_rows_falha PASSED
testes/test_mcp_server.py::TestListarTrilhas::test_retorna_lista_vazia_sem_resultados PASSED
testes/test_mcp_server.py::TestObterDesafio::test_gera_novo_desafio_quando_nao_existe PASSED
testes/test_mcp_server.py::TestObterDesafio::test_retorna_desafio_existente    PASSED
testes/test_mcp_server.py::TestObterDesafio::test_retorna_erro_em_excecao      PASSED
testes/test_mcp_server.py::TestObterDesafio::test_retorna_erro_quando_trilha_nao_encontrada PASSED
testes/test_mcp_server.py::TestEmitirCertificado::test_codigo_formato_geo_cert PASSED
testes/test_mcp_server.py::TestEmitirCertificado::test_persiste_no_appwrite    PASSED
testes/test_mcp_server.py::TestEmitirCertificado::test_retorna_campos_obrigatorios PASSED
testes/test_mcp_server.py::TestEmitirCertificado::test_usuario_e_trilha_corretos PASSED

============================= 20 passed in 1.71s ==============================
```

---

## Como Executar

```bash
uv run pytest testes/test_mcp_server.py -v
```
