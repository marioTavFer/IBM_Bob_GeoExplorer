# -*- coding: utf-8 -*-
import os
import time
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID

load_dotenv()

client = Client()
client.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
client.set_project(os.getenv("APPWRITE_PROJECT"))
client.set_key(os.getenv("APPWRITE_API_KEY"))

databases = Databases(client)
db_id = "escola"

# 1. Garantir Coleções
collections = {
    "trilhas": "Trilhas de Aprendizagem",
    "desafios": "Desafios de Codigo",
    "certificados": "Certificados Emitidos"
}

for col_id, col_name in collections.items():
    try:
        databases.create_collection(database_id=db_id, collection_id=col_id, name=col_name)
        print(f"Colecao {col_id} criada!")
    except Exception as e:
        print(f"Nota colecao {col_id}: {e}")

# 2. Atributos da colecao trilhas
attributes_trilhas = [
    ("titulo", "string", 255, True),
    ("categoria", "string", 100, True),
    ("nivel", "string", 50, True),
    ("descricao", "string", 1000, True),
    ("duracao_horas", "integer", None, False),
]

for name, type_, size, required in attributes_trilhas:
    try:
        if type_ == "string":
            databases.create_string_attribute(database_id=db_id, collection_id="trilhas", key=name, size=size, required=required)
        elif type_ == "integer":
            databases.create_integer_attribute(database_id=db_id, collection_id="trilhas", key=name, required=required, min=0, max=1000)
        print(f"Atributo {name} adicionado a trilhas.")
    except Exception as e:
        pass

# Atributos de desafios e certificados
attributes_desafios = [
    ("trilha_id", "string", 100, True),
    ("titulo", "string", 255, True),
    ("enunciado", "string", 2000, True),
    ("template_codigo", "string", 2000, True),
]
for name, type_, size, required in attributes_desafios:
    try:
        databases.create_string_attribute(database_id=db_id, collection_id="desafios", key=name, size=size, required=required)
    except Exception:
        pass

attributes_certificados = [
    ("codigo", "string", 100, True),
    ("usuario", "string", 100, True),
    ("trilha_nome", "string", 255, True),
    ("data_emissao", "string", 100, True),
]
for name, type_, size, required in attributes_certificados:
    try:
        databases.create_string_attribute(database_id=db_id, collection_id="certificados", key=name, size=size, required=required)
    except Exception:
        pass

print("Aguardando indexacao dos atributos no Appwrite...")
time.sleep(5)

# 3. Lista das 30 Trilhas da DIO
trilhas_data = [
    {"titulo": "Formacao Python Developer", "categoria": "Back-end", "nivel": "Iniciante", "descricao": "Aprenda Python do zero, POO, estruturas de dados, consumo de APIs e framework FastAPI.", "duracao_horas": 65},
    {"titulo": "Formacao Java Developer", "categoria": "Back-end", "nivel": "Intermediario", "descricao": "Domine Java moderno, Spring Boot, arquitetura de microservicos e testes unitarios.", "duracao_horas": 80},
    {"titulo": "Formacao .NET Developer", "categoria": "Back-end", "nivel": "Intermediario", "descricao": "Construa aplicacoes robustas com C#, ASP.NET Core, Entity Framework e Azure.", "duracao_horas": 75},
    {"titulo": "Formacao JavaScript Developer", "categoria": "Front-end", "nivel": "Iniciante", "descricao": "Fundamentos de JavaScript ES6+, manipulacao de DOM, assincronismo e requisicoes AJAX.", "duracao_horas": 45},
    {"titulo": "Formacao React Web Developer", "categoria": "Front-end", "nivel": "Intermediario", "descricao": "Crie UIs modernas com React, Hooks, Redux, Styled Components e Next.js.", "duracao_horas": 60},
    {"titulo": "Formacao Angular Developer", "categoria": "Front-end", "nivel": "Intermediario", "descricao": "Desenvolva SPAs corporativas com Angular, RxJS, TypeScript e arquitetura modular.", "duracao_horas": 55},
    {"titulo": "Formacao HTML & CSS Web Developer", "categoria": "Front-end", "nivel": "Iniciante", "descricao": "Base da web: construa paginas semanticas, responsivas com Flexbox e CSS Grid.", "duracao_horas": 30},
    {"titulo": "Formacao TypeScript Fullstack", "categoria": "Fullstack", "nivel": "Intermediario", "descricao": "Desenvolvimento tipado no front e no back com Node.js, Express e React/TypeScript.", "duracao_horas": 70},
    {"titulo": "Formacao Node.js Developer", "categoria": "Back-end", "nivel": "Intermediario", "descricao": "APIs RESTful de alta performance com Node.js, Express, ORMs e WebSockets.", "duracao_horas": 50},
    {"titulo": "Formacao Golang Developer", "categoria": "Back-end", "nivel": "Avancado", "descricao": "Concorrencia, goroutines, canais e APIs de altíssimo desempenho com Go.", "duracao_horas": 40},
    {"titulo": "Formacao C++ Developer", "categoria": "Software", "nivel": "Avancado", "descricao": "Gerenciamento de memoria, ponteiros e desenvolvimento de software de alta performance.", "duracao_horas": 50},
    {"titulo": "Formacao PHP Fullstack Developer", "categoria": "Fullstack", "nivel": "Intermediario", "descricao": "Desenvolvimento web moderno com PHP 8, Laravel e integracao com bancos de dados.", "duracao_horas": 55},
    {"titulo": "Formacao Flutter Specialist", "categoria": "Mobile", "nivel": "Intermediario", "descricao": "Crie apps multiplataforma (Android/iOS) nativos com Dart e Flutter.", "duracao_horas": 65},
    {"titulo": "Formacao Android Developer (Kotlin)", "categoria": "Mobile", "nivel": "Intermediario", "descricao": "Desenvolvimento Android nativo com Kotlin, Jetpack Compose e Android Studio.", "duracao_horas": 70},
    {"titulo": "Formacao iOS Developer (Swift)", "categoria": "Mobile", "nivel": "Intermediario", "descricao": "Construa aplicativos para o ecossistema Apple com Swift e SwiftUI.", "duracao_horas": 60},
    {"titulo": "Formacao Ciencia de Dados com Python", "categoria": "Data & AI", "nivel": "Intermediario", "descricao": "Analise de dados, Pandas, NumPy, Matplotlib, Seaborn e modelos preditivos.", "duracao_horas": 85},
    {"titulo": "Formacao Machine Learning Specialist", "categoria": "Data & AI", "nivel": "Avancado", "descricao": "Algoritmos supervisionados, nao-supervisionados, Scikit-Learn e TensorFlow.", "duracao_horas": 90},
    {"titulo": "Formacao Engenharia de Dados", "categoria": "Data & AI", "nivel": "Avancado", "descricao": "Pipelines de dados, Apache Spark, Airflow, Data Warehouses e ETL em nuvem.", "duracao_horas": 80},
    {"titulo": "Formacao Power BI Analyst", "categoria": "Data & AI", "nivel": "Iniciante", "descricao": "Dashboards interativos, modelagem de dados, linguagem DAX e Business Intelligence.", "duracao_horas": 40},
    {"titulo": "Formacao Engenharia de Prompts e IA Generativa", "categoria": "Data & AI", "nivel": "Iniciante", "descricao": "Técnicas avançadas de prompt engineering, LLMs, ChatGPT, Claude e integracao via API.", "duracao_horas": 35},
    {"titulo": "Formacao Inteligencia Artificial Fundamentos", "categoria": "Data & AI", "nivel": "Iniciante", "descricao": "Introducao aos conceitos de IA, Visao Computacional, PLN e Ética em IA.", "duracao_horas": 30},
    {"titulo": "Formacao AWS Cloud Practitioner", "categoria": "Cloud & DevOps", "nivel": "Iniciante", "descricao": "Servicos essenciais da AWS: EC2, S3, RDS, IAM e preparacao para certificacao.", "duracao_horas": 50},
    {"titulo": "Formacao Azure Cloud Associate", "categoria": "Cloud & DevOps", "nivel": "Intermediario", "descricao": "Computacao em nuvem na Microsoft Azure: Maquinas Virtuais, Serverless e Seguranca.", "duracao_horas": 55},
    {"titulo": "Formacao DevOps Fundamentals", "categoria": "Cloud & DevOps", "nivel": "Intermediario", "descricao": "Cultura DevOps, CI/CD com GitHub Actions, IaC com Terraform e automacao.", "duracao_horas": 60},
    {"titulo": "Formacao Docker & Kubernetes", "categoria": "Cloud & DevOps", "nivel": "Avancado", "descricao": "Containerizacao de aplicacoes com Docker e orquestracao em escala com Kubernetes.", "duracao_horas": 45},
    {"titulo": "Formacao Cybersecurity Specialist", "categoria": "Seguranca", "nivel": "Intermediario", "descricao": "Fundamentos de seguranca da informacao, pentest, analise de vulnerabilidade e Criptografia.", "duracao_horas": 65},
    {"titulo": "Formacao SQL & Banco de Dados Relacionais", "categoria": "Banco de Dados", "nivel": "Iniciante", "descricao": "Modelagem relacional, consultas SQL avançadas, JOINs, Triggers e Stored Procedures.", "duracao_horas": 35},
    {"titulo": "Formacao NoSQL & MongoDB", "categoria": "Banco de Dados", "nivel": "Intermediario", "descricao": "Bancos orientados a documentos, alta escalabilidade e queries no MongoDB.", "duracao_horas": 30},
    {"titulo": "Formacao Linux Fundamentals", "categoria": "Infraestrutura", "nivel": "Iniciante", "descricao": "Comandos de terminal Linux, permissoes de arquivos, shell scripting e administracao.", "duracao_horas": 25},
    {"titulo": "Formacao English4Tech - Comunicacao Internacional", "categoria": "Carreira", "nivel": "Iniciante", "descricao": "Inglês para devs: entrevistas de emprego, code review e vocabulario tecnico internacional.", "duracao_horas": 40}
]

print(f"Inserindo {len(trilhas_data)} trilhas no Appwrite...")
sucesso = 0
for t in trilhas_data:
    try:
        databases.create_document(
            database_id=db_id,
            collection_id="trilhas",
            document_id=ID.unique(),
            data=t
        )
        sucesso += 1
    except Exception as e:
        tit = t.get("titulo")
        print(f"Erro ao inserir {tit}: {e}")

print(f"Concluido! {sucesso}/{len(trilhas_data)} trilhas cadastradas no Appwrite!")

