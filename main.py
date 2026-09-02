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
from appwrite.id import ID
from appwrite.query import Query

# Suporte ao API moderno TablesDB (Appwrite 1.8.0+) com fallback para Databases
try:
    from appwrite.services.tables_db import TablesDB
    IS_TABLES_DB = True
except ImportError:
    from appwrite.services.databases import Databases
    IS_TABLES_DB = False

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

if IS_TABLES_DB:
    db_service = TablesDB(client)
else:
    db_service = Databases(client)

DB_ID = "escola"


def limpar_tela() -> None:
    """Limpa o console de acordo com o sistema operacional."""
    os.system("cls" if os.name == "nt" else "clear")


def exibir_banner() -> None:
    """Exibe o cabeçalho oficial do Geo-Explorer."""
    print("=" * 65)
    print("      GEO-EXPLORER | Trilhas de Aprendizagem & Desafios (DIO)")
    print("=" * 65)


def fetch_rows(collection_id: str, queries: list = None) -> list[dict]:
    """Busca registros no Appwrite utilizando a API modernizada do TablesDB com fallback."""
    if queries is None:
        queries = []

    try:
        if IS_TABLES_DB:
            resultado = db_service.list_rows(
                database_id=DB_ID,
                table_id=collection_id,
                queries=queries
            )
            rows = getattr(resultado, "rows", [])
            return [{"$id": getattr(r, "id", ""), **getattr(r, "data", {})} for r in rows]
        else:
            resultado = db_service.list_documents(
                database_id=DB_ID,
                collection_id=collection_id,
                queries=queries
            )
            docs = getattr(resultado, "documents", [])
            return [{"$id": getattr(d, "id", ""), **getattr(d, "data", {})} for d in docs]
    except Exception as e:
        print(f"Erro ao consultar '{collection_id}' no Appwrite: {e}")
        return []


def create_row(collection_id: str, data: dict) -> dict:
    """Cria um registro no Appwrite utilizando a API modernizada do TablesDB com fallback."""
    row_id = ID.unique()
    try:
        if IS_TABLES_DB:
            res = db_service.create_row(
                database_id=DB_ID,
                table_id=collection_id,
                row_id=row_id,
                data=data
            )
            return {"$id": getattr(res, "id", row_id), **getattr(res, "data", data)}
        else:
            res = db_service.create_document(
                database_id=DB_ID,
                collection_id=collection_id,
                document_id=row_id,
                data=data
            )
            return {"$id": getattr(res, "id", row_id), **data}
    except Exception as e:
        print(f"  (Aviso: erro ao registrar documento no Appwrite: {e})")
        return {"$id": row_id, **data}


def listar_trilhas() -> list[dict]:
    """Busca todas as trilhas cadastradas no Appwrite (sem truncamento de paginação)."""
    return fetch_rows("trilhas", queries=[Query.limit(100)])


def buscar_ou_criar_desafio(trilha: dict) -> dict:
    """Busca um desafio existente associado à trilha ou cria um novo com base na categoria."""
    trilha_id = trilha.get("$id", "")
    trilha_titulo = trilha.get("titulo", "Trilha")
    trilha_categoria = trilha.get("categoria", "Geral")

    if trilha_id:
        desafios = fetch_rows(
            "desafios",
            queries=[Query.equal("trilha_id", trilha_id), Query.limit(1)]
        )
        if desafios:
            return desafios[0]

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
        "Mobile": (
            "Desenvolva uma tela com gerenciamento de estado para listar itens consumidos de uma API REST."
        ),
        "Segurança": (
            "Implemente uma rotina de verificacao de integridade de arquivos utilizando hashes SHA-256."
        ),
        "Banco de Dados": (
            "Escreva uma consulta SQL com JOINs e agregacao para listar os top 5 clientes por volume de vendas."
        ),
        "Fullstack": (
            "Construa uma integracao entre um formulario no front-end e um endpoint POST RESTful no back-end."
        )
    }

    enunciado = enunciados.get(
        trilha_categoria,
        f"Implemente uma solucao basica em codigo aplicando os conceitos da trilha '{trilha_titulo}'."
    )

    template = (
        f"# Desafio Pratico: {trilha_titulo}\n"
        f"# Categoria: {trilha_categoria}\n\n"
        f"def solucao():\n"
        f"    # Escreva seu codigo aqui\n"
        f"    return True\n"
    )

    novo_desafio = {
        "trilha_id": trilha_id,
        "titulo": f"Desafio Pratico: {trilha_titulo}",
        "enunciado": enunciado,
        "template_codigo": template
    }

    return create_row("desafios", novo_desafio)


def emitir_certificado(nome_usuario: str, trilha_nome: str) -> dict:
    """Emite um certificado fictício de conclusão e salva no Appwrite."""
    codigo_cert = f"GEO-CERT-{datetime.now().year}-{uuid.uuid4().hex[:8].upper()}"
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    dados_cert = {
        "codigo": codigo_cert,
        "usuario": nome_usuario,
        "trilha_nome": trilha_nome,
        "data_emissao": data_hoje
    }

    return create_row("certificados", dados_cert)


def exibir_certificado_ascii(cert: dict) -> None:
    """Formata e exibe a arte ASCII do certificado emitido."""
    usuario = cert.get("usuario", "").upper()
    trilha = cert.get("trilha_nome", "")
    codigo = cert.get("codigo", "")
    data_emissao = cert.get("data_emissao", "")

    largura = 65
    print("\n" + "*" * largura)
    print("               CERTIFICADO DE CONCLUSAO".center(largura))
    print("                    GEO-EXPLORER - DIO".center(largura))
    print("*" * largura)
    print(f" Certificamos que:        {usuario}")
    print(f" Concluiu a Trilha:        {trilha}")
    print(f" Codigo de Autenticidade: {codigo}")
    print(f" Data de Emissao:         {data_emissao}")
    print("*" * largura + "\n")


def menu_principal() -> None:
    """Loop principal da aplicação interativa Geo-Explorer (sem recursividade)."""
    while True:
        limpar_tela()
        exibir_banner()
        print("\nCarregando trilhas de aprendizagem do Appwrite...\n")

        trilhas = listar_trilhas()
        if not trilhas:
            print("Nenhuma trilha encontrada. Execute dados/setup_geoexplorer.py primeiro.")
            input("\nPressione Enter para tentar novamente...")
            continue

        print(f"Foram encontradas {len(trilhas)} trilhas disponiveis!\n")

        # Agrupar categorias com contadores
        categories_dict = {}
        for t in trilhas:
            cat = t.get("categoria", "Geral")
            categories_dict[cat] = categories_dict.get(cat, 0) + 1

        categories = sorted(list(categories_dict.keys()))

        print("Categorias disponiveis:")
        for idx, cat in enumerate(categories, 1):
            qtd = categories_dict[cat]
            print(f"  [{idx}] {cat} ({qtd} trilhas)")
        print("  [S] Buscar trilha por palavra-chave")
        print("  [0] Sair")

        opcao_cat = input("\nEscolha uma categoria, 'S' para buscar ou '0' para sair: ").strip()

        if opcao_cat == "0":
            print("\nObrigado por utilizar o Geo-Explorer! Bons estudos na DIO!")
            break

        if opcao_cat.upper() == "S":
            termo = input("\nDigite o nome ou palavra-chave da trilha: ").strip().lower()
            if not termo:
                continue
            trilhas_filtradas = [
                t for t in trilhas
                if termo in t.get("titulo", "").lower() or termo in t.get("descricao", "").lower()
            ]
            cat_escolhida = f"Busca: '{termo}'"
        elif opcao_cat.isdigit():
            idx_cat = int(opcao_cat) - 1
            if idx_cat < 0 or idx_cat >= len(categories):
                print("Opcao invalida.")
                input("Pressione Enter para tentar novamente...")
                continue
            cat_escolhida = categories[idx_cat]
            trilhas_filtradas = [t for t in trilhas if t.get("categoria") == cat_escolhida]
        else:
            print("Opcao invalida.")
            input("Pressione Enter para tentar novamente...")
            continue

        if not trilhas_filtradas:
            print(f"\nNenhuma trilha encontrada para: {cat_escolhida}")
            input("Pressione Enter para retornar ao menu principal...")
            continue

        # Loop do submenu de seleção de trilhas
        while True:
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
            if opcao_trilha == "0":
                break

            if not opcao_trilha.isdigit():
                print("Opcao invalida.")
                input("Pressione Enter para tentar novamente...")
                continue

            idx_trilha = int(opcao_trilha) - 1
            if idx_trilha < 0 or idx_trilha >= len(trilhas_filtradas):
                print("Opcao invalida.")
                input("Pressione Enter para retornar...")
                continue

            trilha_selecionada = trilhas_filtradas[idx_trilha]

            # Submenu de detalhes da trilha e desafio
            while True:
                limpar_tela()
                exibir_banner()
                print("\n>>> DETALHES DA TRILHA:", trilha_selecionada.get("titulo"), "<<<")
                print("Categoria:", trilha_selecionada.get("categoria"))
                print("Nivel:    ", trilha_selecionada.get("nivel"))
                print("Duracao:  ", trilha_selecionada.get("duracao_horas"), "horas")
                print("Descricao:", trilha_selecionada.get("descricao"), "\n")

                print("Acoes disponiveis:")
                print("  [1] Iniciar Desafio de Codigo")
                print("  [0] Voltar a lista de trilhas")
                acao = input("\nEscolha uma opcao: ").strip()

                if acao == "0":
                    break
                elif acao == "1":
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
                    input("Pressione Enter para retornar ao menu de trilhas...")
                    break
                else:
                    print("Opcao invalida.")
                    input("Pressione Enter para tentar novamente...")

            if acao in ["0", "1"]:
                break


if __name__ == "__main__":
    menu_principal()
