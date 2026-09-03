# Geo-Explorer 🌍🤖

> **Desafio de Projeto DIO:** *"Construindo Seu Primeiro Produto com um Agente de IA"*  
> **Apoio de IA:** IBM Bob & DIO Agent (+Antigravity)  
> **Desenvolvedor:** Mario TavFer ([@marioTavFer](https://github.com/marioTavFer))  
> **Tecnologias:** Python 3.13, `uv`, Appwrite Cloud 1.8.0+, FastMCP, Streamlit, SQLite, Git.

---

## 📌 Sobre o Geo-Explorer

O **Geo-Explorer** é uma aplicação interativa desenvolvida para simular a navegação por trilhas de aprendizagem em tecnologia da **DIO (Digital Innovation One)**, permitindo que a pessoa usuária:

- **Consulte 30 formações e trilhas de aprendizagem** divididas em categorias como *Back-end*, *Front-end*, *Fullstack*, *Mobile*, *Data & AI*, *Cloud & DevOps*, *Segurança* e *Carreira*.
- **Receba um Desafio de Código prático** relativo à trilha escolhida.
- **Simule a resolução e obtenha um Certificado Fictício de Conclusão** com código único de autenticidade, devidamente persistido no Appwrite.
- **Interaja via MCP (Model Context Protocol)** com assistentes de IA como o IBM Bob.
- **Faça backup local** dos dados do Appwrite em um banco SQLite.

---

## 🛠️ Estrutura do Projeto

```text
IBM_Bob_GeoExplorer/
├── comandos/
│   └── mcp_server.py              # Servidor MCP (FastMCP) para integração com Agentes de IA
├── dados/
│   ├── setup_geoexplorer.py       # Cria tabelas e popula as 30 trilhas no Appwrite
│   └── backup_db_appwrite.py      # Backup incremental Appwrite → SQLite local
├── documentacao/
│   └── Descricao_projeto_Geo_Explorer.md  # Documentação técnica detalhada
├── testes/
│   ├── test_appwrite.py           # Testes unitários — conexão e TablesDB
│   ├── test_db_creation.py        # Testes unitários — criação de tabelas e colunas
│   ├── test_mcp_server.py         # Testes unitários — ferramentas MCP (20 casos)
│   ├── relatorio_test_appwrite.md # Relatório de testes — conexão Appwrite
│   ├── relatorio_test_db_creation.md  # Relatório de testes — criação de tabelas
│   └── relatorio_testes_MCP.md    # Relatório de testes — servidor MCP (atualizado a cada run)
├── main.py                        # Aplicação CLI interativa (terminal)
├── app_streamlit.py               # Aplicação Web interativa (Streamlit)
├── .env.example                   # Exemplo de configuração de variáveis de ambiente
├── pyproject.toml                 # Dependências e configuração do uv
└── README.md                      # Este arquivo
```

---

## ⚡ Como Executar o Projeto

### 1. Pré-requisitos

- Python 3.13+ ou [`uv`](https://github.com/astral-sh/uv) instalado
- Conta e projeto criados no [Appwrite Cloud](https://appwrite.io)

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:

```env
APPWRITE_ENDPOINT=https://nyc.cloud.appwrite.io/v1
APPWRITE_PROJECT=seu_project_id
APPWRITE_API_KEY=sua_api_key
```

### 3. Instalar Dependências

```powershell
uv sync
```

### 4. Popular o Banco no Appwrite (primeira execução)

```powershell
uv run python dados/setup_geoexplorer.py
```

### 5. Rodar a Aplicação Interativa

Escolha entre duas interfaces:

**Opção A — CLI (terminal)**
```powershell
uv run python main.py
```

**Opção B — Web (Streamlit)**
```powershell
uv run streamlit run app_streamlit.py
```
Abre em `http://localhost:8501`. Páginas disponíveis no menu lateral:

| Página | Funcionalidade |
|---|---|
| 🏠 **Início** | Status de conexão Appwrite e métricas gerais |
| 📚 **Trilhas** | Lista com filtro por categoria e busca por palavra-chave |
| 💻 **Desafio de Código** | Recebe o desafio da trilha, submete a solução e **emite o certificado** |
| 🏅 **Consultar Certificado** | Consulta certificados já emitidos por nome e trilha; redireciona ao desafio se não encontrado |
| 📋 **Certificados Emitidos** | Lista todos os certificados com filtros, métricas e detalhes individuais |
| 💾 **Backup SQLite** | Backup incremental Appwrite → SQLite com histórico de execuções |

> **Regra:** certificados só são emitidos pela página **💻 Desafio de Código**, após submissão da solução.

### 6. Rodar o Servidor MCP para Agentes de IA

```powershell
uv run python comandos/mcp_server.py
```

### 7. Fazer Backup Local (Appwrite → SQLite)

```powershell
uv run python dados/backup_db_appwrite.py
```

Gera/atualiza `dados/backup_db_appwrite.sqlite` com as tabelas `trilhas`, `desafios` e `certificados`.

---

## 🧪 Testes

Todos os testes são unitários e isolados de rede (sem chamadas reais ao Appwrite).

```powershell
# Rodar toda a suite
uv run pytest testes/ -v

# Rodar suite específica
uv run pytest testes/test_mcp_server.py -v
uv run pytest testes/test_appwrite.py -v
uv run pytest testes/test_db_creation.py -v
```

| Suite | Casos | Cobertura |
|---|---|---|
| `test_appwrite.py` | 9 | Inicialização do Client, TablesDB, `db.list()` |
| `test_db_creation.py` | 14 | `create_table`, colunas de `trilhas`, `desafios`, `certificados` |
| `test_mcp_server.py` | 20 | `fetch_rows`, `create_row`, `listar_trilhas`, `obter_desafio`, `emitir_certificado` |
| **Total** | **43** | |

> O arquivo `testes/relatorio_testes_MCP.md` é atualizado automaticamente com a data e hora de cada execução de `test_mcp_server.py`.

---

## 🔧 Ferramentas MCP Expostas

O servidor MCP (`comandos/mcp_server.py`) expõe 3 ferramentas para Agentes de IA:

| Ferramenta | Parâmetros | Descrição |
|---|---|---|
| `listar_trilhas` | `categoria` *(opcional)* | Lista trilhas, com filtro opcional por categoria |
| `obter_desafio` | `trilha_titulo` | Retorna ou gera desafio de código para a trilha |
| `emitir_certificado` | `nome_usuario`, `trilha_nome` | Gera e persiste certificado com código único |

---

## 📄 Documentação Detalhada

Para conferir o detalhamento completo sobre conexão GitHub, credenciais Appwrite, estrutura das tabelas e especificação do servidor MCP, consulte:

👉 [`documentacao/Descricao_projeto_Geo_Explorer.md`](documentacao/Descricao_projeto_Geo_Explorer.md)
