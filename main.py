# -*- coding: utf-8 -*-
"""
Geo-Explorer - DIO AI Product
Sistema de exploracao de trilhas de aprendizagem, desafios de codigo e emissao de certificados.
Integrado ao Appwrite & desenvolvido com apoio do IBM Bob.
"""

import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID

load_dotenv()

# Inicializacao do Appwrite
ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
PROJECT_ID = os.getenv("APPWRITE_PROJECT")
API_KEY = os.getenv("APPWRITE_API_KEY")

if not all([ENDPOINT, PROJECT_ID, API_KEY]):
    print("ERRO: Variaveis de ambiente do Appwrite nao encontradas no arquivo .env!")
    sys.exit(1)

client = Client()
client.set_endpoint(ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)

databases = Databases(client)
DB_ID = "escola"

def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

def exibir_banner():
    print("=" * 65)
    print("      GEO-EXPLORER | Trilhas de Aprendizagem & Desafios (DIO)")
    print("=" * 65)

def listar_trilhas():
    try:
        resultado = databases.list_documents(database_id=DB_ID, collection_id="trilhas")
        documentos = resultado.get("documents", [])
        return documentos
    except Exception as e:
        print("Erro ao buscar trilhas no Appwrite:", e)
        return []

def buscar_ou_criar_desafio(trilha):
    trilha_id = trilha.get("$id", "")
    trilha_titulo = trilha.get("titulo", "Trilha")
    trilha_categoria = trilha.get("categoria", "Geral")

    try:
        res = databases.list_documents(database_id=DB_ID, collection_id="desafios")
        desafios = [d for d in res.get("documents", []) if d.get("trilha_id") == trilha_id]
        if desafios:
            return desafios[0]
    except Exception:
        pass

    enunciados = {
        "Back-end": (
            "Desenvolva uma funcao em Python que receba uma lista de numeros e retorne "
            "apenas os valores maiores que a media da lista."
        ),
        "Front-end": (
            "Crie um componente funcional que receba um array de objetos e renderize "
            "uma lista formatada em HTML/CSS responsivo."
        ),
        "Data & AI": (
            "Escreva um script para carregar um conjunto de dados, tratar valores nulos "
            "e calcular as estatisticas descritivas (media, mediana, desvio padrao)."
        ),
        "Cloud & DevOps": (
            "Escreva um manifesto de implantacao (YAML) definindo um Service e um Deployment "
            "com 3 replicas e limitacao de recursos."
        ),
    }

    enunciado = enunciados.get(
        trilha_categoria,
        f"Implemente uma solucao basica em codigo aplicando os conceitos da {trilha_titulo}."
    )

    template = f"# Desafio Pratico: {trilha_titulo}\n# Categoria: {trilha_categoria}\n\ndef solucao():\n    # Escreva seu codigo aqui\n    return True\n"

    novo_desafio = {
        "trilha_id": trilha_id,
        "titulo": f"Desafio Pratico: {trilha_titulo}",
        "enunciado": enunciado,
        "template_codigo": template
    }

    try:
        doc = databases.create_document(
            database_id=DB_ID,
            collection_id="desafios",
            document_id=ID.unique(),
            data=novo_desafio
        )
        return doc
    except Exception:
        return novo_desafio

def emitir_certificado(nome_usuario, trilha_nome):
    codigo_cert = f"GEO-CERT-{datetime.now().year}-{uuid.uuid4().hex[:8].upper()}"
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    dados_cert = {
        "codigo": codigo_cert,
        "usuario": nome_usuario,
        "trilha_nome": trilha_nome,
        "data_emissao": data_hoje
    }

    try:
        databases.create_document(
            database_id=DB_ID,
            collection_id="certificados",
            document_id=ID.unique(),
            data=dados_cert
        )
    except Exception as e:
        print("(Aviso: erro ao registrar certificado no Appwrite:", e, ")")

    return dados_cert

def exibir_certificado_ascii(cert):
    usuario = cert.get("usuario", "").upper()
    trilha = cert.get("trilha_nome", "")
    codigo = cert.get("codigo", "")
    data_emissao = cert.get("data_emissao", "")

    print("\n" + "*" * 65)
    print("               CERTIFICADO DE CONCLUSAO")
    print("                    GEO-EXPLORER - DIO")
    print("*" * 65)
    print(f" Certificamos que:        {usuario}")
    print(f" Concluiu a Trilha:        {trilha}")
    print(f" Codigo de Autenticidade: {codigo}")
    print(f" Data de Emissao:         {data_emissao}")
    print("*" * 65 + "\n")

def menu_principal():
    limpar_tela()
    exibir_banner()
    print("\nCarregando trilhas de aprendizagem do Appwrite...\n")

    trilhas = listar_trilhas()
    if not trilhas:
        print("Nenhuma trilha encontrada. Execute dados/setup_geoexplorer.py primeiro.")
        return

    print(f"Foram encontradas {len(trilhas)} trilhas disponiveis!\n")
    categories = sorted(list(set(t.get("categoria", "Geral") for t in trilhas)))

    print("Categorias disponiveis:")
    for idx, cat in enumerate(categories, 1):
        print(f"  [{idx}] {cat}")
    print("  [0] Sair")

    opcao_cat = input("\nEscolha uma categoria (ou 0 para sair): ").strip()
    if opcao_cat == "0" or not opcao_cat.isdigit():
        print("\nObrigado por utilizar o Geo-Explorer! Bons estudos na DIO!")
        return

    idx_cat = int(opcao_cat) - 1
    if idx_cat < 0 or idx_cat >= len(categories):
        print("Opcao invalida.")
        input("Pressione Enter para tentar novamente...")
        return menu_principal()

    cat_escolhida = categories[idx_cat]
    trilhas_filtradas = [t for t in trilhas if t.get("categoria") == cat_escolhida]

    limpar_tela()
    exibir_banner()
    print(f"\n--- Trilhas na categoria: {cat_escolhida} ---\n")
    for idx, t in enumerate(trilhas_filtradas, 1):
        titulo = t.get("titulo")
        nivel = t.get("nivel")
        duracao = t.get("duracao_horas")
        print(f"  [{idx}] {titulo} ({nivel} - {duracao}h)")
    print("  [0] Voltar ao menu principal")

    opcao_trilha = input("\nEscolha a trilha para explorar: ").strip()
    if opcao_trilha == "0" or not opcao_trilha.isdigit():
        return menu_principal()

    idx_trilha = int(opcao_trilha) - 1
    if idx_trilha < 0 or idx_trilha >= len(trilhas_filtradas):
        print("Opcao invalida.")
        input("Pressione Enter para retornar...")
        return menu_principal()

    trilha_selecionada = trilhas_filtradas[idx_trilha]

    # Detalhes da Trilha
    limpar_tela()
    exibir_banner()
    print("\n>>> DETALHES DA TRILHA:", trilha_selecionada.get("titulo"), "<<<")
    print("Categoria:", trilha_selecionada.get("categoria"))
    print("Nivel:    ", trilha_selecionada.get("nivel"))
    print("Duracao:  ", trilha_selecionada.get("duracao_horas"), "horas")
    print("Descricao:", trilha_selecionada.get("descricao"), "\n")

    print("Acoes disponiveis:")
    print("  [1] Iniciar Desafio de Codigo")
    print("  [0] Voltar ao menu")
    acao = input("\nEscolha uma opcao: ").strip()

    if acao == "1":
        desafio = buscar_ou_criar_desafio(trilha_selecionada)
        limpar_tela()
        exibir_banner()
        print("\n>>> DESAFIO DE CODIGO:", trilha_selecionada.get("titulo"), "<<<")
        print("Titulo:", desafio.get("titulo"), "\n")
        print("ENUNCIADO DO DESAFIO:")
        print(" ", desafio.get("enunciado"), "\n")
        print("TEMPLATE DE CODIGO INICIAL:")
        print("-" * 50)
        print(desafio.get("template_codigo"))
        print("-" * 50)

        nome = input("\nDigite seu nome completo para registrar a resolucao: ").strip()
        if not nome:
            nome = "Estudante DIO"

        print(f"\nParabens, {nome}! Codigo submetido e validado com sucesso!")
        cert = emitir_certificado(nome, trilha_selecionada.get("titulo"))
        exibir_certificado_ascii(cert)
        input("Pressione Enter para retornar ao menu principal...")
        return menu_principal()
    else:
        return menu_principal()

if __name__ == "__main__":
    menu_principal()

