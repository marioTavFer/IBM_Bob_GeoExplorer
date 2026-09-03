# Relatório de Testes — Criação de Tabelas Appwrite (test_db_creation)

**Arquivo testado:** `comandos/test_db_creation.py` (lógica de criação de tabelas)  
**Suite de testes:** `testes/test_db_creation.py`  
**Framework:** `pytest 9.1.1` · `unittest.mock`  
**Python:** 3.13.9  
**Resultado geral:** ✅ **14 / 14 aprovados — 0 falhas**

---

## Objetivo

Verificar que a criação das três tabelas do banco `escola` (`trilhas`, `desafios`,
`certificados`) e de todas as suas colunas é realizada com os parâmetros corretos,
e que erros de tabela já existente são tratados sem propagar exceção.

---

## Suites e Casos de Teste

### `TestCriacaoTabelas` — Criação das 3 tabelas

| # | Caso de Teste | Resultado |
|---|---|---|
| 1 | `create_table` é chamado com `table_id='trilhas'` | ✅ PASS |
| 2 | `create_table` é chamado com `table_id='desafios'` | ✅ PASS |
| 3 | `create_table` é chamado com `table_id='certificados'` | ✅ PASS |
| 4 | `create_table` é chamado exatamente 3 vezes no total | ✅ PASS |
| 5 | Exceção de tabela já existente é capturada sem propagar | ✅ PASS |

**Comportamento verificado:** chamada correta para cada tabela, contagem total de
invocações e resiliência a tabelas pré-existentes.

---

### `TestColunasTabelaTrilhas` — Colunas da tabela `trilhas`

| # | Caso de Teste | Resultado |
|---|---|---|
| 6 | `create_string_column` para `titulo` com `size=255` | ✅ PASS |
| 7 | `create_string_column` para `categoria` com `size=100` | ✅ PASS |
| 8 | `create_string_column` para `nivel` com `size=50` | ✅ PASS |
| 9 | `create_integer_column` para `duracao_horas` com `min=0, max=1000` | ✅ PASS |
| 10 | Exatamente 5 colunas criadas para `trilhas` (4 string + 1 integer) | ✅ PASS |

**Comportamento verificado:** tipo, tamanho e obrigatoriedade de cada coluna,
além da contagem total de colunas da tabela.

---

### `TestColunasTabelaDesafios` — Colunas da tabela `desafios`

| # | Caso de Teste | Resultado |
|---|---|---|
| 11 | Exatamente 4 colunas string criadas para `desafios` | ✅ PASS |
| 12 | `create_string_column` para `trilha_id` com `size=100` | ✅ PASS |

**Comportamento verificado:** estrutura da tabela de desafios com referência
`trilha_id` para vínculo com a trilha.

---

### `TestColunasTabelaCertificados` — Colunas da tabela `certificados`

| # | Caso de Teste | Resultado |
|---|---|---|
| 13 | Exatamente 4 colunas string criadas para `certificados` | ✅ PASS |
| 14 | `create_string_column` para `codigo` com `size=100` | ✅ PASS |

**Comportamento verificado:** estrutura completa da tabela de certificados
(código, usuário, trilha e data de emissão).

---

## Resumo Executivo

```
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-9.1.1
collected 14 items

testes/test_db_creation.py::TestCriacaoTabelas::test_cria_tabela_certificados                       PASSED
testes/test_db_creation.py::TestCriacaoTabelas::test_cria_tabela_desafios                           PASSED
testes/test_db_creation.py::TestCriacaoTabelas::test_cria_tabela_trilhas                            PASSED
testes/test_db_creation.py::TestCriacaoTabelas::test_cria_todas_as_tres_tabelas                     PASSED
testes/test_db_creation.py::TestCriacaoTabelas::test_tabela_ja_existente_nao_lanca_excecao_ao_tratar PASSED
testes/test_db_creation.py::TestColunasTabelaTrilhas::test_cinco_colunas_criadas_para_trilhas        PASSED
testes/test_db_creation.py::TestColunasTabelaTrilhas::test_coluna_categoria_string                  PASSED
testes/test_db_creation.py::TestColunasTabelaTrilhas::test_coluna_duracao_integer                   PASSED
testes/test_db_creation.py::TestColunasTabelaTrilhas::test_coluna_nivel_string                      PASSED
testes/test_db_creation.py::TestColunasTabelaTrilhas::test_coluna_titulo_string                     PASSED
testes/test_db_creation.py::TestColunasTabelaDesafios::test_coluna_trilha_id_referencia             PASSED
testes/test_db_creation.py::TestColunasTabelaDesafios::test_quatro_colunas_criadas_para_desafios    PASSED
testes/test_db_creation.py::TestColunasTabelaCertificados::test_coluna_codigo_certificado           PASSED
testes/test_db_creation.py::TestColunasTabelaCertificados::test_quatro_colunas_criadas_para_certificados PASSED

============================== 14 passed in 0.06s ==============================
```

---

## Como Executar

```bash
uv run pytest testes/test_db_creation.py -v
```
