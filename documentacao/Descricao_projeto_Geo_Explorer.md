# Documentação Detalhada do Projeto Geo-Explorer

> **Projeto desenvolvido para o Desafio de Projeto da DIO:** *"Construindo Seu Primeiro Produto com um Agente de IA"*  
> **Mentor de IA / Apoio:** IBM Bob / DIO Agent  
> **Desenvolvedor:** Mario TavFer (`marioTavFer`)  
> **Repositório:** [https://github.com/marioTavFer/IBM_Bob_GeoExplorer](https://github.com/marioTavFer/IBM_Bob_GeoExplorer)

---

## 1. Visão Geral do Produto

O **Geo-Explorer** é uma solução completa para exploração de trilhas de aprendizagem em tecnologia da DIO (Digital Innovation One). Ele permite que a pessoa usuária:
1. **Navegue e consulte** trilhas de conhecimento organizadas por categorias e níveis de senioridade.
2. **Receba desafios práticos de código** diretamente vinculados às trilhas.
3. **Simule a resolução e emita um certificado fictício de conclusão** com hash único de autenticidade, devidamente persistido em banco de dados em nuvem.
4. **Disponibilize ferramentas MCP (Model Context Protocol)** para que Agentes de IA (como o IBM Bob) consultem o sistema e emitam certificados de forma autônoma.

---

## 2. Estrutura e Organização do Projeto

A arquitetura do projeto segue a separação modular proposta com o apoio do IBM Bob:

```
D:\IBM_Bob_GeoExplorer\
├── comandos/
│   ├── mcp_server.py        # Servidor MCP (FastMCP) para integração com Agentes de IA
│   ├── test_appwrite.py     # Script de verificação da conexão com o Appwrite
│   └── .gitkeep
├── dados/
│   ├── setup_geoexplorer.py # Script de automação de coleções e população de 30 trilhas
│   └── .gitkeep
├── documentacao/
│   ├── Descricao_projeto_Geo_Explorer.md # Documentação técnica detalhada (este arquivo)
│   └── .gitkeep
├── testes/
│   └── .gitkeep
├── main.py                  # Aplicação principal interativa via CLI (terminal)
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
- **Segurança de Variáveis de Ambiente:** As credenciais (`APPWRITE_ENDPOINT`, `APPWRITE_PROJECT`, `APPWRITE_API_KEY`) foram centralizadas no arquivo `.env`. O arquivo `.env` foi explicitamente inserido no `.gitignore` para proteção do projeto no GitHub.

---

## 4. Modelagem e Estrutura do Banco de Dados

O banco de dados do **Geo-Explorer** foi modelado no Appwrite com três coleções principais:

### 4.1. Coleção: `trilhas` (Trilhas de Aprendizagem)
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

### 4.2. Coleção: `desafios` (Desafios de Código)
Armazena os exercícios práticos vinculados a cada trilha.

| Atributo | Tipo | Tamanho | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `trilha_id` | String | 100 | Sim | ID de documento da trilha correspondente |
| `titulo` | String | 255 | Sim | Título do desafio de código |
| `enunciado` | String | 2000 | Sim | Descrição do problema a ser resolvido |
| `template_codigo` | String | 2000 | Sim | Código esqueleto inicial |

---

### 4.3. Coleção: `certificados` (Certificados Emitidos)
Registra o histórico de certificados fictícios gerados após a resolução dos desafios.

| Atributo | Tipo | Tamanho | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `codigo` | String | 100 | Sim | Código de autenticidade (ex: `GEO-CERT-2026-A1B2C3D4`) |
| `usuario` | String | 100 | Sim | Nome completo do participante |
| `trilha_nome` | String | 255 | Sim | Nome da trilha concluída |
| `data_emissao` | String | 100 | Sim | Data e hora exata da emissão do registro |

---

## 5. Servidor MCP (Model Context Protocol)

O projeto implementa um servidor MCP nativo em `comandos/mcp_server.py` utilizando o framework `FastMCP`. Ele expõe ferramentas estruturadas em JSON-RPC para que o IBM Bob ou outros agentes de IA possam operar a plataforma:

- **`listar_trilhas(categoria: str = None)`**: Retorna em JSON a lista de trilhas cadastradas no Appwrite, permitindo filtro opcional por categoria.
- **`obter_desafio(trilha_titulo: str)`**: Busca ou gera automaticamente o desafio de código para uma trilha selecionada.
- **`emitir_certificado(nome_usuario: str, trilha_nome: str)`**: Emite e salva um novo certificado no Appwrite para a pessoa usuária.

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