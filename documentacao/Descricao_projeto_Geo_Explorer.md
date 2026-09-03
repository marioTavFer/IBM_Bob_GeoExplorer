# Documentação Detalhada do Projeto Geo-Explorer

> **Projeto desenvolvido para o Desafio de Projeto da DIO:** *"Construindo Seu Primeiro Produto com um Agente de IA"*  
> **Mentor de IA / Apoio:** IBM Bob / DIO Agent (+ Antigravity)  
> **Desenvolvedor:** Mario TavFer (`marioTavFer`)  
> **Repositório:** [https://github.com/marioTavFer/IBM_Bob_GeoExplorer](https://github.com/marioTavFer/IBM_Bob_GeoExplorer)

---

## 1. Visão Geral do Produto

O **Geo-Explorer** é uma solução completa para exploração de trilhas de aprendizagem em tecnologia da DIO (Digital Innovation One). Ele permite que a pessoa usuária:

1. **Navegue e consulte** trilhas de conhecimento organizadas por categorias e níveis de senioridade.
2. **Realize buscas dinâmicas** por palavras-chave em títulos e descrições de trilhas.
3. **Receba desafios práticos de código** diretamente vinculados às trilhas selecionadas.
4. **Simule a resolução e emita um certificado fictício de conclusão** com código único de autenticidade, persistido no Appwrite.
5. **Consulte certificados já emitidos** por nome e trilha, com navegação direta ao desafio caso não encontrado.
6. **Disponibilize ferramentas MCP (Model Context Protocol)** para que Agentes de IA (como o IBM Bob e o Antigravity) consultem o sistema e emitam certificados de forma autônoma.
7. **Faça backup local dos dados** do Appwrite em um banco SQLite para resiliência e auditoria.

O projeto oferece **duas interfaces de uso** — uma CLI (terminal) via `main.py` e uma interface web interativa via `app_streamlit.py` — além de um servidor MCP para integração com agentes de IA.

---

## 2. Estrutura e Organização do Projeto

A arquitetura do projeto segue a separação modular proposta com o apoio do IBM Bob:

```text
IBM_Bob_GeoExplorer/
├── comandos/
│   └── mcp_server.py                  # Servidor MCP (FastMCP) para integração com Agentes de IA
├── dados/
│   ├── setup_geoexplorer.py           # Cria tabelas, colunas e popula as 30 trilhas no Appwrite
│   ├── backup_db_appwrite.py          # Backup incremental Appwrite → SQLite local
│   └── backup_db_appwrite.sqlite      # Banco SQLite gerado pelo backup (ignorado pelo Git)
├── documentacao/
│   └── Descricao_projeto_Geo_Explorer.md  # Documentação técnica detalhada (este arquivo)
├── testes/
│   ├── test_appwrite.py               # Testes unitários — conexão e TablesDB (9 casos)
│   ├── test_db_creation.py            # Testes unitários — criação de tabelas e colunas (14 casos)
│   ├── test_mcp_server.py             # Testes unitários — ferramentas MCP (20 casos)
│   ├── relatorio_test_appwrite.md     # Relatório de testes — conexão Appwrite
│   ├── relatorio_test_db_creation.md  # Relatório de testes — criação de tabelas
│   └── relatorio_testes_MCP.md        # Relatório de testes — servidor MCP (timestamp automático)
├── main.py                            # Aplicação CLI interativa (terminal)
├── app_streamlit.py                   # Aplicação Web interativa (Streamlit)
├── .env                               # Variáveis de ambiente secretas (ignorado pelo Git)
├── .env.example                       # Modelo das variáveis de ambiente necessárias
├── .gitignore                         # Regras de exclusão de versão do Git
├── .python-version                    # Versão do Python utilizada (3.13)
├── pyproject.toml                     # Configuração de projeto e dependências do uv
├── uv.lock                            # Trava de versões exatas das dependências
└── README.md                          # Apresentação principal do repositório
```

---

## 3. Conexões e Configurações de Segurança

### 3.1. Integração com o GitHub
- **Usuário:** `marioTavFer`
- **Repositório Remoto:** `https://github.com/marioTavFer/IBM_Bob_GeoExplorer.git`
- **Autenticação:** Realizada via **Personal Access Token (PAT)**.
- **Boa Prática de Segurança:** O token de acesso foi utilizado pontualmente para efetuar o `push` inicial e a URL do `remote origin` foi higienizada no `.git/config` local para evitar vazamento acidental de credenciais.

### 3.2. Integração com o Appwrite
- **Plataforma:** Appwrite Cloud (`https://nyc.cloud.appwrite.io/v1`)
- **ID do Projeto:** `6a9466d3003871d61864`
- **Banco de Dados:** `escola`
- **SDK:** Appwrite Python SDK **1.8.0+** — utiliza exclusivamente a API **`TablesDB`** (`list_rows`, `create_row`), eliminando o módulo legado `Databases` e os `DeprecationWarning` associados. Não há flag `IS_TABLES_DB` nem fallback condicional em nenhum arquivo do projeto.
- **Segurança de Variáveis de Ambiente:** As credenciais (`APPWRITE_ENDPOINT`, `APPWRITE_PROJECT`, `APPWRITE_API_KEY`) estão centralizadas no arquivo `.env`, explicitamente inserido no `.gitignore`.
- **Cache de conexão no Streamlit:** A instância do `TablesDB` é criada uma única vez via `@st.cache_resource`, evitando reconexões a cada interação do usuário.

---

## 4. Modelagem e Estrutura do Banco de Dados

### 4.1. Banco Appwrite: `escola`

O banco possui três tabelas principais gerenciadas pelo `TablesDB`:

#### Tabela `trilhas` — Trilhas de Aprendizagem

Armazena a grade de 30 formações e trilhas da DIO.

| Atributo | Tipo | Tamanho | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `titulo` | String | 255 | Sim | Nome da Formação/Trilha da DIO |
| `categoria` | String | 100 | Sim | Categoria de tecnologia (ex: Back-end, Data & AI) |
| `nivel` | String | 50 | Sim | Nível exigido (Iniciante, Intermediário, Avançado) |
| `descricao` | String | 1000 | Sim | Resumo descritivo dos conteúdos da trilha |
| `duracao_horas` | Integer | — | Não | Carga horária estimada em horas |

**Grade populada (30 trilhas):**
1. **Back-end:** Python Developer, Java Developer, .NET Developer, Node.js Developer, Golang Developer, C++ Developer.
2. **Front-end:** JavaScript Developer, React Web Developer, Angular Developer, HTML & CSS Web Developer.
3. **Fullstack & Mobile:** TypeScript Fullstack, PHP Fullstack Developer, Flutter Specialist, Android Developer (Kotlin), iOS Developer (Swift).
4. **Data & AI:** Ciência de Dados com Python, Machine Learning Specialist, Engenharia de Dados, Power BI Analyst, Engenharia de Prompts e IA Generativa, Inteligência Artificial Fundamentos.
5. **Cloud & DevOps:** AWS Cloud Practitioner, Azure Cloud Associate, DevOps Fundamentals, Docker & Kubernetes.
6. **Segurança & Outros:** Cybersecurity Specialist, SQL & Banco de Dados Relacionais, NoSQL & MongoDB, Linux Fundamentals, English4Tech.

---

#### Tabela `desafios` — Desafios de Código

Armazena os exercícios práticos vinculados a cada trilha. Criados automaticamente na primeira vez que a trilha é acessada.

| Atributo | Tipo | Tamanho | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `trilha_id` | String | 100 | Sim | `$id` da trilha correspondente no Appwrite |
| `titulo` | String | 255 | Sim | Título do desafio de código |
| `enunciado` | String | 2000 | Sim | Descrição do problema a ser resolvido |
| `template_codigo` | String | 2000 | Sim | Código esqueleto inicial |

**Enunciados por categoria** (gerados automaticamente quando não existem):

| Categoria | Enunciado padrão |
| :--- | :--- |
| Back-end | Função Python que filtra valores acima da média |
| Front-end | Componente funcional com lista formatada em HTML/CSS |
| Data & AI | Script de análise estatística descritiva com Pandas |
| Cloud & DevOps | Manifesto YAML com Service e Deployment Kubernetes |
| Mobile | Tela com gerenciamento de estado consumindo API REST |
| Segurança | Rotina de verificação de integridade via SHA-256 |
| Banco de Dados | Consulta SQL com JOINs e TOP 5 clientes |
| Fullstack | Integração formulário front-end + endpoint POST REST |

---

#### Tabela `certificados` — Certificados Emitidos

Registra o histórico de certificados fictícios gerados após a resolução dos desafios.

| Atributo | Tipo | Tamanho | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `codigo` | String | 100 | Sim | Código de autenticidade (ex: `GEO-CERT-2026-A1B2C3D4`) |
| `usuario` | String | 100 | Sim | Nome completo do participante |
| `trilha_nome` | String | 255 | Sim | Nome da trilha concluída |
| `data_emissao` | String | 100 | Sim | Data e hora exata da emissão do registro |

**Regra de negócio:** certificados são emitidos **exclusivamente** após a submissão da solução na página de desafio (CLI ou Streamlit). A página de consulta de certificados **nunca emite** — apenas exibe ou redireciona ao desafio.

---

### 4.2. Banco SQLite Local: `backup_db_appwrite.sqlite`

Gerado pelo script `dados/backup_db_appwrite.py`. Replica as três tabelas do Appwrite em SQLite para backup incremental local, com uma tabela adicional de auditoria:

| Tabela SQLite | Colunas adicionais | Descrição |
| :--- | :--- | :--- |
| `trilhas` | `appwrite_id`, `backup_em` | Espelho da tabela Appwrite |
| `desafios` | `appwrite_id`, `backup_em` | Espelho da tabela Appwrite |
| `certificados` | `appwrite_id`, `backup_em` | Espelho da tabela Appwrite |
| `backup_log` | `id`, `executado_em`, `trilhas`, `desafios`, `certificados` | Histórico de execuções do backup |

A chave primária de cada tabela é o `appwrite_id` (`$id` do Appwrite), garantindo `INSERT OR REPLACE` idempotente — re-executar o backup não duplica registros.

---

## 5. Interfaces de Uso

O Geo-Explorer oferece duas interfaces de interação equivalentes em funcionalidade, com características diferentes:

### 5.1. Interface CLI — `main.py`

Aplicação interativa de terminal. Navegação por menus numerados, sem dependência de navegador.

**Fluxo de uso:**
```
Menu principal → Escolha de categoria (ou busca por palavra-chave)
    → Lista de trilhas da categoria
        → Detalhes da trilha
            → Iniciar Desafio de Código
                → Submissão com nome → Emissão de Certificado (ASCII art)
```

**Executar:**
```powershell
uv run python main.py
```

---

### 5.2. Interface Web — `app_streamlit.py`

Aplicação web construída com **Streamlit**, acessível em `http://localhost:8501`. Navegação por menu lateral com 6 páginas.

**Executar:**
```powershell
uv run streamlit run app_streamlit.py
```

#### Páginas da Interface Web

| Página | Descrição |
| :--- | :--- |
| 🏠 **Início** | Status de conexão com o Appwrite, métricas de trilhas e categorias disponíveis |
| 📚 **Trilhas** | Listagem com filtro por categoria (selectbox) e busca por palavra-chave (text_input); cada trilha tem um expander com descrição e botão para ir ao desafio |
| 💻 **Desafio de Código** | Seleção de trilha, exibição do enunciado e template de código; campo de nome para submissão; **única origem de emissão de certificados** |
| 🏅 **Consultar Certificado** | Consulta por nome + trilha; exibe certificado se encontrado; se não encontrado, redireciona para o desafio com a trilha pré-selecionada |
| 📋 **Certificados Emitidos** | Lista todos os certificados com filtros por nome e trilha, métricas (total, participantes únicos, trilhas contempladas) e detalhes individuais em expanders |
| 💾 **Backup SQLite** | Executa backup Appwrite → SQLite com 1 clique; exibe métricas por tabela e histórico das últimas 10 execuções |

#### Regras de Negócio da Interface Web

- **Emissão de certificado:** ocorre **exclusivamente** na página 💻 Desafio de Código, após o usuário preencher o nome e submeter a solução.
- **Consulta de certificado:** a página 🏅 apenas exibe certificados existentes. Se não encontrar, orienta o usuário a concluir o desafio primeiro.
- **Cache de trilhas:** `@st.cache_data` com TTL de 30s para certificados e sem expiração para trilhas (botão "Atualizar lista" limpa manualmente).
- **Navegação programática:** o botão "Ir para o Desafio de Código" usa `st.session_state["pagina"]` para redirecionar o radio do sidebar sem recarregar a página do zero.

---

## 6. Servidor MCP (Model Context Protocol) & Ferramentas Disponíveis

O **Geo-Explorer** disponibiliza uma camada de integração com Agentes de IA através do padrão **Model Context Protocol (MCP)**, implementada em `comandos/mcp_server.py` com o framework `FastMCP`.

### 6.1. O que é o Servidor MCP?

O Servidor MCP atua como uma ponte padronizada (JSON-RPC) que permite que assistentes virtuais de IA (como IBM Bob, Antigravity, Claude Desktop, Cursor, etc.) consultem e interajam autonomamente com os dados do Appwrite sem necessidade de interface gráfica ou comandos manuais.

### 6.2. Ferramentas (Tools) Expostas

O servidor expõe **3 ferramentas principais**:

#### `listar_trilhas(categoria: str | None = None)`

- **Descrição:** Lista as trilhas cadastradas no Appwrite (até 100 por chamada). Permite filtragem opcional por categoria, com comparação case-insensitive.
- **Parâmetros:**
  - `categoria` *(opcional, string)*: Nome da categoria (ex: `"Back-end"`, `"Data & AI"`). Se omitido, retorna todas.
- **Retorno (JSON Array):**
  ```json
  [
    {
      "id": "6a9727a2002406507cff",
      "titulo": "Formacao Python Developer",
      "categoria": "Back-end",
      "nivel": "Iniciante",
      "duracao_horas": 65,
      "descricao": "Aprenda Python do zero, POO, estruturas de dados, consumo de APIs e framework FastAPI."
    }
  ]
  ```

---

#### `obter_desafio(trilha_titulo: str)`

- **Descrição:** Busca o desafio existente para uma trilha ou gera um novo desafio contextualizado pela categoria, caso ainda não exista no banco.
- **Parâmetros:**
  - `trilha_titulo` *(obrigatório, string)*: Título exato ou parcial (ex: `"Python"`, `"AWS Cloud Practitioner"`).
- **Retorno (JSON Object):**
  ```json
  {
    "trilha": "Formacao Python Developer",
    "titulo_desafio": "Desafio Pratico: Formacao Python Developer",
    "enunciado": "Desenvolva uma funcao em Python que receba uma lista de numeros e retorne apenas os valores maiores que a media da lista.",
    "template_codigo": "# Desafio Pratico: Formacao Python Developer\ndef solucao():\n    return True\n"
  }
  ```

---

#### `emitir_certificado(nome_usuario: str, trilha_nome: str)`

- **Descrição:** Gera e persiste um certificado fictício de conclusão no Appwrite com código único no formato `GEO-CERT-YYYY-HASH8`.
- **Parâmetros:**
  - `nome_usuario` *(obrigatório, string)*: Nome completo do estudante.
  - `trilha_nome` *(obrigatório, string)*: Nome da trilha concluída.
- **Retorno (JSON Object):**
  ```json
  {
    "codigo": "GEO-CERT-2026-B8E2D91F",
    "usuario": "Mario TavFer",
    "trilha_nome": "Formacao Python Developer",
    "data_emissao": "02/09/2026 15:45:00"
  }
  ```

### 6.3. Inicialização do Servidor MCP

```powershell
uv run python comandos/mcp_server.py
```

---

## 7. Suite de Testes

Todos os testes são **unitários e isolados de rede** — nenhuma chamada real ao Appwrite é feita durante a execução. O SDK é substituído integralmente por `unittest.mock.MagicMock`.

| Arquivo | Classe(s) | Casos | Cobertura |
| :--- | :--- | :--- | :--- |
| `testes/test_appwrite.py` | `TestAppwriteConnection`, `TestAppwriteListDatabases` | 9 | Inicialização Client, TablesDB, `db.list()` |
| `testes/test_db_creation.py` | `TestCriacaoTabelas`, `TestColunasTabelaTrilhas`, `TestColunasTabelaDesafios`, `TestColunasTabelaCertificados` | 14 | `create_table`, tipos e tamanhos de colunas, tratamento de tabela existente |
| `testes/test_mcp_server.py` | `TestFetchRows`, `TestCreateRow`, `TestListarTrilhas`, `TestObterDesafio`, `TestEmitirCertificado` | 20 | Todas as funções e ferramentas MCP |
| **Total** | | **43** | |

### Executar os testes

```powershell
# Suite completa
uv run pytest testes/ -v

# Suite individual
uv run pytest testes/test_mcp_server.py -v
uv run pytest testes/test_appwrite.py -v
uv run pytest testes/test_db_creation.py -v
```

> O arquivo `testes/relatorio_testes_MCP.md` é atualizado automaticamente com a **data e hora de execução** a cada vez que `test_mcp_server.py` é executado.

---

## 8. Dependências do Projeto

Gerenciadas via `uv` e declaradas em `pyproject.toml`:

| Pacote | Versão mínima | Uso |
| :--- | :--- | :--- |
| `appwrite` | 23.0.0 | SDK Appwrite — TablesDB, Client, Query, ID |
| `fastmcp` | 4.0.0 | Framework para servidor MCP |
| `streamlit` | 1.35.0 | Interface web interativa |
| `pandas` | 2.0.0 | Tabelas de dados na interface Streamlit |
| `python-dotenv` | 1.2.3 | Carregamento de variáveis de ambiente do `.env` |
| `pytest` *(dev)* | 8.0.0 | Framework de testes unitários |

---

## 9. Guia de Comandos do Projeto

Todos os comandos devem ser executados a partir do diretório raiz do projeto:

### 9.1. Instalar dependências

```powershell
uv sync
```

### 9.2. Popular o banco de dados no Appwrite (primeira execução)

```powershell
uv run python dados/setup_geoexplorer.py
```

### 9.3. Executar a Aplicação CLI (terminal)

```powershell
uv run python main.py
```

### 9.4. Executar a Aplicação Web (Streamlit)

```powershell
uv run streamlit run app_streamlit.py
```

### 9.5. Iniciar o Servidor MCP para Agentes de IA

```powershell
uv run python comandos/mcp_server.py
```

### 9.6. Fazer Backup Local (Appwrite → SQLite)

```powershell
uv run python dados/backup_db_appwrite.py
```

### 9.7. Executar os Testes Unitários

```powershell
uv run pytest testes/ -v
```

### 9.8. Gerenciar Pacotes e Dependências com `uv`

```powershell
# Adicionar nova biblioteca
uv add <nome-do-pacote>

# Sincronizar ambiente virtual
uv sync
```
