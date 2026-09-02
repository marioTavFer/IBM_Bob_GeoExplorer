# Documentação Detalhada do Projeto Geo-Explorer

> **Projeto desenvolvido para o Desafio de Projeto da DIO:** *"Construindo Seu Primeiro Produto com um Agente de IA"*  
> **Mentor de IA / Apoio:** IBM Bob / DIO Agent (Antigravity) 
> **Desenvolvedor:** Mario TavFer (`marioTavFer`)  
> **Repositório:** [https://github.com/marioTavFer/IBM_Bob_GeoExplorer](https://github.com/marioTavFer/IBM_Bob_GeoExplorer)

---

## 1. Visão Geral do Produto

O **Geo-Explorer** é uma solução completa para exploração de trilhas de aprendizagem em tecnologia da DIO (Digital Innovation One). Ele permite que a pessoa usuária:
1. **Navegue e consulte** trilhas de conhecimento organizadas por categorias e níveis de senioridade.
2. **Realize buscas dinâmicas** por palavras-chave em títulos e descrições de trilhas.
3. **Receba desafios práticos de código** diretamente vinculados às trilhas selecionadas.
4. **Simule a resolução e emita um certificado fictício de conclusão** com hash único de autenticidade, devidamente persistido em banco de dados em nuvem.
5. **Disponibilize ferramentas MCP (Model Context Protocol)** para que Agentes de IA (como o IBM Bob e o Antigravity) consultem o sistema e emitam certificados de forma autônoma.

---

## 2. Estrutura e Organização do Projeto

A arquitetura do projeto segue a separação modular proposta com o apoio do IBM Bob:

```text
D:\IBM_Bob_GeoExplorer\
├── comandos/
│   ├── mcp_server.py        # Servidor MCP (FastMCP) para integração com Agentes de IA
│   ├── test_appwrite.py     # Script de verificação da conexão com o Appwrite
│   ├── test_db_creation.py  # Script de teste de criação e estruturas no banco
│   └── .gitkeep
├── dados/
│   ├── setup_geoexplorer.py # Script de automação de coleções e população de 30 trilhas
│   └── .gitkeep
├── documentacao/
│   ├── Descricao_projeto_Geo_Explorer.md # Documentação técnica detalhada (este arquivo)
│   └── .gitkeep
├── testes/
│   └── .gitkeep
├── main.py                  # Aplicação principal interativa via CLI (terminal, refatorada com TablesDB)
├── .env                     # Variáveis de ambiente secretas (ignorado pelo Git)
├── .env.example             # Modelo das variáveis de ambiente necessárias
├── .gitignore               # Regras de exclusão de versão do Git
├── .python-version          # Versão do Python utilizada (3.13)
├── pyproject.toml           # Arquivo de configuração de projeto e dependências do uv
├── uv.lock                  # Trava de versões exatas das dependências do uv
└── README.md                # Apresentação principal do repositório
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
- **Modernização de API:** O código do projeto utiliza a API modernizada **`TablesDB`** (`list_rows`, `create_row`) a partir da versão 1.8.0+ do SDK, eliminando avisos de depreciação (`DeprecationWarning`) do antigo módulo `Databases`.
- **Segurança de Variáveis de Ambiente:** As credenciais (`APPWRITE_ENDPOINT`, `APPWRITE_PROJECT`, `APPWRITE_API_KEY`) foram centralizadas no arquivo `.env`. O arquivo `.env` foi explicitamente inserido no `.gitignore` para proteção do projeto no GitHub.

---

## 4. Modelagem e Estrutura do Banco de Dados

O banco de dados do **Geo-Explorer** foi modelado no Appwrite com três coleções/tabelas principais:

### 4.1. Coleção/Tabela: `trilhas` (Trilhas de Aprendizagem)
Armazena a grade de 30 formações e trilhas de aprendizagem da DIO.

| Atributo | Tipo | Tamanho | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `titulo` | String | 255 | Sim | Nome da Formação/Trilha da DIO |
| `categoria` | String | 100 | Sim | Categoria de tecnologia (ex: Back-end, Data & AI) |
| `nivel` | String | 50 | Sim | Nível exigido (Iniciante, Intermediário, Avançado) |
| `descricao` | String | 1000 | Sim | Resumo descritivo dos conteúdos da trilha |
| `duracao_horas` | Integer | - | Não | Carga horária estimada em horas |

#### Categoria e Grade Populada (30 Trilhas):
1. **Back-end:** Formação Python Developer, Formação Java Developer, Formação .NET Developer, Formação Node.js Developer, Formação Golang Developer, Formação C++ Developer.
2. **Front-end:** Formação JavaScript Developer, Formação React Web Developer, Formação Angular Developer, Formação HTML & CSS Web Developer.
3. **Fullstack & Mobile:** Formação TypeScript Fullstack, Formação PHP Fullstack Developer, Formação Flutter Specialist, Formação Android Developer (Kotlin), Formação iOS Developer (Swift).
4. **Data & AI:** Formação Ciência de Dados com Python, Formação Machine Learning Specialist, Formação Engenharia de Dados, Formação Power BI Analyst, Formação Engenharia de Prompts e IA Generativa, Formação Inteligência Artificial Fundamentos.
5. **Cloud & DevOps:** Formação AWS Cloud Practitioner, Formação Azure Cloud Associate, Formação DevOps Fundamentals, Formação Docker & Kubernetes.
6. **Segurança & Outros:** Formação Cybersecurity Specialist, Formação SQL & Banco de Dados Relacionais, Formação NoSQL & MongoDB, Formação Linux Fundamentals, Formação English4Tech - Comunicação Internacional.

---

### 4.2. Coleção/Tabela: `desafios` (Desafios de Código)
Armazena os exercícios práticos vinculados a cada trilha.

| Atributo | Tipo | Tamanho | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `trilha_id` | String | 100 | Sim | ID de documento da trilha correspondente |
| `titulo` | String | 255 | Sim | Título do desafio de código |
| `enunciado` | String | 2000 | Sim | Descrição do problema a ser resolvido |
| `template_codigo` | String | 2000 | Sim | Código esqueleto inicial |

---

### 4.3. Coleção/Tabela: `certificados` (Certificados Emitidos)
Registra o histórico de certificados fictícios gerados após a resolução dos desafios.

| Atributo | Tipo | Tamanho | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `codigo` | String | 100 | Sim | Código de autenticidade (ex: `GEO-CERT-2026-A1B2C3D4`) |
| `usuario` | String | 100 | Sim | Nome completo do participante |
| `trilha_nome` | String | 255 | Sim | Nome da trilha concluída |
| `data_emissao` | String | 100 | Sim | Data e hora exata da emissão do registro |

---

## 5. Servidor MCP (Model Context Protocol) & Ferramentas Disponíveis

O **Geo-Explorer** disponibiliza uma camada de integração com Agentes de IA através do padrão **Model Context Protocol (MCP)**, implementada em `comandos/mcp_server.py` utilizando o framework `FastMCP`.

### 5.1. O que é o Servidor MCP?
O Servidor MCP atua como uma ponte padronizada (JSON-RPC) que permite que assistentes virtuais de IA (como IBM Bob, Antigravity, Claude Desktop, Cursor, etc.) consultem e interajam autonomamente com os dados do Appwrite sem necessidade de interface gráfica ou comandos manuais.

### 5.2. Comandos e Ferramentas (Tools) Expostas

O servidor expõe **3 ferramentas principais**:

#### 1. `listar_trilhas(categoria: str = None)`
- **Descrição:** Lista as trilhas de aprendizagem cadastradas na nuvem Appwrite sem limitação de paginação (`Query.limit(100)`). Permite filtragem opcional por categoria.
- **Parâmetros:**
  - `categoria` *(opcional, string)*: Nome da categoria para filtrar (ex: `"Back-end"`, `"Data & AI"`). Se omitido, retorna todas as trilhas.
- **Formato de Retorno (JSON Array):**
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

#### 2. `obter_desafio(trilha_titulo: str)`
- **Descrição:** Busca o desafio de código existente para uma trilha ou gera um novo desafio contextualizado com base na categoria da trilha caso ainda não exista no banco de dados.
- **Parâmetros:**
  - `trilha_titulo` *(obrigatório, string)*: Título exato ou parcial da trilha (ex: `"Python"`, `"AWS Cloud Practitioner"`).
- **Formato de Retorno (JSON Object):**
  ```json
  {
    "trilha": "Formacao Python Developer",
    "titulo_desafio": "Desafio Pratico: Formacao Python Developer",
    "enunciado": "Desenvolva uma funcao em Python que receba uma lista de numeros e retorne apenas os valores maiores que a media da lista.",
    "template_codigo": "# Desafio Pratico: Formacao Python Developer\ndef solucao():\n    return True\n"
  }
  ```

---

#### 3. `emitir_certificado(nome_usuario: str, trilha_nome: str)`
- **Descrição:** Gera e persiste um certificado fictício de conclusão no Appwrite, gerando um código único de autenticidade no formato `GEO-CERT-YYYY-HASH8`.
- **Parâmetros:**
  - `nome_usuario` *(obrigatório, string)*: Nome completo do estudante.
  - `trilha_nome` *(obrigatório, string)*: Nome da trilha concluída.
- **Formato de Retorno (JSON Object):**
  ```json
  {
    "codigo": "GEO-CERT-2026-B8E2D91F",
    "usuario": "Mario TavFer",
    "trilha_nome": "Formacao Python Developer",
    "data_emissao": "02/09/2026 15:45:00"
  }
  ```

### 5.3. Inicialização e Testes do Servidor MCP
Para rodar o servidor MCP localmente em modo standalone:
```powershell
uv run python comandos/mcp_server.py
```

---

## 6. Guia de Comandos do Projeto

Todos os comandos devem ser executados a partir do diretório raiz `D:\IBM_Bob_GeoExplorer`:

### 6.1. Executar a Aplicação Interativa (CLI)
```powershell
uv run python main.py
```

### 6.2. Repopular/Configurar o Banco de Dados no Appwrite
```powershell
uv run python dados/setup_geoexplorer.py
```

### 6.3. Testar a Conexão com o Appwrite
```powershell
uv run python comandos/test_appwrite.py
```

### 6.4. Iniciar o Servidor MCP para Agentes de IA
```powershell
uv run python comandos/mcp_server.py
```

### 6.5. Gerenciar Pacotes e Dependências com `uv`
```powershell
# Adicionar nova biblioteca
uv add <nome-do-pacote>

# Sincronizar ambiente virtual
uv sync
```