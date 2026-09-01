# Geo-Explorer 🌍🤖

> **Desafio de Projeto DIO:** *"Construindo Seu Primeiro Produto com um Agente de IA"*  
> **Apoio de IA:** IBM Bob & DIO Agent  
> **Desenvolvedor:** Mario TavFer ([@marioTavFer](https://github.com/marioTavFer))  
> **Tecnologias:** Python 3.13, `uv`, Appwrite Cloud, FastMCP, Git.

---

## 📌 Sobre o Geo-Explorer

O **Geo-Explorer** é uma aplicação interativa desenvolvida para simular a navegação por trilhas de aprendizagem em tecnologia da **DIO (Digital Innovation One)**, permitindo que a pessoa usuária:
- **Consulte 30 formações e trilhas de aprendizagem** divididas em categorias como *Back-end*, *Front-end*, *Fullstack*, *Mobile*, *Data & AI*, *Cloud & DevOps*, *Segurança* e *Carreira*.
- **Receba um Desafio de Código prático** relativo à trilha escolhida.
- **Simule a resolução e obtenha um Certificado Fictício de Conclusão** com código único de autenticidade, devidamente persistido em banco de dados em nuvem.
- **Interaja via MCP (Model Context Protocol)** com assistentes de IA como o IBM Bob.

---

## 🛠️ Estrutura do Projeto

```text
D:\IBM_Bob_GeoExplorer\
├── comandos/
│   ├── mcp_server.py        # Servidor MCP (FastMCP) para integração com Agentes de IA
│   └── test_appwrite.py     # Teste de conexão com o banco Appwrite
├── dados/
│   └── setup_geoexplorer.py # Script que cria coleções e popula as 30 trilhas da DIO
├── documentacao/
│   └── Descricao_projeto_Geo_Explorer.md # Documentação técnica detalhada
├── testes/                  # Testes unitários e de integração
├── main.py                  # Aplicação CLI interativa
├── .env.example             # Exemplo de configuração de variáveis de ambiente
├── pyproject.toml           # Dependências e configuração do uv
└── README.md                # Apresentação do projeto
```

---

## ⚡ Como Executar o Projeto

### 1. Pré-requisitos
Certifique-se de ter o `uv` (ou Python 3.12+) instalado no seu sistema.

### 2. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:
```env
APPWRITE_ENDPOINT=https://nyc.cloud.appwrite.io/v1
APPWRITE_PROJECT=seu_project_id
APPWRITE_API_KEY=sua_api_key
```

### 3. Rodar a Aplicação Interativa (CLI)
```powershell
uv run python main.py
```

### 4. Rodar o Servidor MCP para Agentes de IA
```powershell
uv run python comandos/mcp_server.py
```

---

## 📄 Documentação Detalhada

Para conferir o detalhamento completo sobre a conexão com o GitHub, credenciais do Appwrite, estrutura detalhada das tabelas (`trilhas`, `desafios`, `certificados`) e especificações do servidor MCP, consulte o arquivo de documentação oficial em:
👉 [`documentacao/Descricao_projeto_Geo_Explorer.md`](documentacao/Descricao_projeto_Geo_Explorer.md)