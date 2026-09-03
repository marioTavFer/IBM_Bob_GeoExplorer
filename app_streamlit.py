# -*- coding: utf-8 -*-
"""
Geo-Explorer — Interface Web (Streamlit)
Alternativa visual ao main.py para explorar trilhas, desafios e certificados DIO.
"""

import os
import sys
import uuid
import sqlite3
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

import streamlit as st

# ─────────────────────────────────────────────────────────
# Configuração da página (deve ser a primeira chamada st.*)
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Geo-Explorer | DIO",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# Appwrite — inicialização com cache de conexão
# ─────────────────────────────────────────────────────────
load_dotenv()

@st.cache_resource(show_spinner=False)
def get_db_service():
    from appwrite.client import Client
    from appwrite.services.tables_db import TablesDB

    endpoint   = os.getenv("APPWRITE_ENDPOINT")
    project_id = os.getenv("APPWRITE_PROJECT")
    api_key    = os.getenv("APPWRITE_API_KEY")

    if not all([endpoint, project_id, api_key]):
        return None

    client = Client()
    client.set_endpoint(endpoint)
    client.set_project(project_id)
    client.set_key(api_key)
    return TablesDB(client)


DB_ID       = "escola"
SQLITE_PATH = Path("dados") / "backup_db_appwrite.sqlite"

# ─────────────────────────────────────────────────────────
# Helpers Appwrite
# ─────────────────────────────────────────────────────────

def fetch_rows(table_id: str, queries: list | None = None) -> list[dict]:
    from appwrite.query import Query
    db = get_db_service()
    if db is None:
        return []
    try:
        result = db.list_rows(
            database_id=DB_ID,
            table_id=table_id,
            queries=queries if queries is not None else [],
        )
        return [{"$id": r.id, **r.data} for r in result.rows]
    except Exception as e:
        st.error(f"Erro ao consultar '{table_id}': {e}")
        return []


def create_row(table_id: str, data: dict) -> dict:
    from appwrite.id import ID
    db = get_db_service()
    row_id = ID.unique()
    if db is None:
        return {"$id": row_id, **data}
    try:
        res = db.create_row(database_id=DB_ID, table_id=table_id, row_id=row_id, data=data)
        return {"$id": res.id, **res.data}
    except Exception as e:
        st.warning(f"Aviso ao salvar em '{table_id}': {e}")
        return {"$id": row_id, **data}


@st.cache_data(show_spinner="Carregando trilhas...")
def listar_trilhas_cached() -> list[dict]:
    from appwrite.query import Query
    return fetch_rows("trilhas", queries=[Query.limit(100)])


def buscar_ou_criar_desafio(trilha: dict) -> dict:
    from appwrite.query import Query
    trilha_id       = trilha.get("$id", "")
    trilha_titulo   = trilha.get("titulo", "Trilha")
    trilha_categoria = trilha.get("categoria", "Geral")

    if trilha_id:
        desafios = fetch_rows("desafios", queries=[
            Query.equal("trilha_id", trilha_id), Query.limit(1)
        ])
        if desafios:
            return desafios[0]

    enunciados = {
        "Back-end":      "Desenvolva uma funcao em Python que receba uma lista de numeros e retorne apenas os valores maiores que a media da lista.",
        "Front-end":     "Crie um componente funcional que receba um array de objetos e renderize uma lista formatada em HTML/CSS responsivo.",
        "Data & AI":     "Escreva um script para carregar um conjunto de dados, tratar valores nulos e calcular as estatisticas descritivas (media, mediana, desvio padrao).",
        "Cloud & DevOps":"Escreva um manifesto de implantacao (YAML) definindo um Service e um Deployment com 3 replicas e limitacao de recursos.",
        "Mobile":        "Desenvolva uma tela com gerenciamento de estado para listar itens consumidos de uma API REST.",
        "Segurança":     "Implemente uma rotina de verificacao de integridade de arquivos utilizando hashes SHA-256.",
        "Banco de Dados":"Escreva uma consulta SQL com JOINs e agregacao para listar os top 5 clientes por volume de vendas.",
        "Fullstack":     "Construa uma integracao entre um formulario no front-end e um endpoint POST RESTful no back-end.",
    }

    enunciado = enunciados.get(
        trilha_categoria,
        f"Implemente uma solucao basica em codigo aplicando os conceitos da trilha '{trilha_titulo}'.",
    )
    template = (
        f"# Desafio Pratico: {trilha_titulo}\n"
        f"# Categoria: {trilha_categoria}\n\n"
        f"def solucao():\n"
        f"    # Escreva seu codigo aqui\n"
        f"    return True\n"
    )
    novo = {
        "trilha_id":       trilha_id,
        "titulo":          f"Desafio Pratico: {trilha_titulo}",
        "enunciado":       enunciado,
        "template_codigo": template,
    }
    return create_row("desafios", novo)


def emitir_certificado(nome_usuario: str, trilha_nome: str) -> dict:
    cert = {
        "codigo":       f"GEO-CERT-{datetime.now().year}-{uuid.uuid4().hex[:8].upper()}",
        "usuario":      nome_usuario,
        "trilha_nome":  trilha_nome,
        "data_emissao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }
    create_row("certificados", cert)
    return cert


# ─────────────────────────────────────────────────────────
# Helpers Backup SQLite
# ─────────────────────────────────────────────────────────

def run_backup() -> dict:
    """Executa o backup Appwrite → SQLite e retorna totais."""
    sys.path.insert(0, str(Path(__file__).parent / "dados"))
    import backup_db_appwrite as bk
    import importlib
    importlib.reload(bk)

    ts   = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    conn = sqlite3.connect(SQLITE_PATH)
    bk.setup_sqlite(conn)
    totais = {}
    for nome, fn in [("trilhas", bk.backup_trilhas), ("desafios", bk.backup_desafios), ("certificados", bk.backup_certificados)]:
        try:
            totais[nome] = fn(conn, ts)
        except Exception as e:
            totais[nome] = 0
            totais[f"{nome}_erro"] = str(e)
    conn.execute(
        "INSERT INTO backup_log (executado_em, trilhas, desafios, certificados) VALUES (?, ?, ?, ?)",
        (ts, totais.get("trilhas", 0), totais.get("desafios", 0), totais.get("certificados", 0)),
    )
    conn.commit()
    conn.close()
    totais["ts"] = ts
    return totais


# ─────────────────────────────────────────────────────────
# UI — Sidebar
# ─────────────────────────────────────────────────────────

_PAGINAS = [
    "🏠 Início",
    "📚 Trilhas",
    "💻 Desafio de Código",
    "🏅 Certificado",
    "📋 Certificados Emitidos",
    "💾 Backup SQLite",
]

# Garante valor inicial no session_state
if "pagina" not in st.session_state:
    st.session_state["pagina"] = _PAGINAS[0]

with st.sidebar:
    st.image("https://hermes.dio.me/assets/diome/logo-full.svg", width=160)
    st.markdown("## 🌍 Geo-Explorer")
    st.caption("Trilhas de Aprendizagem & Desafios DIO")
    st.divider()
    pagina = st.radio(
        "Navegação",
        _PAGINAS,
        index=_PAGINAS.index(st.session_state["pagina"]),
        label_visibility="collapsed",
        key="pagina",
    )
    st.divider()
    st.caption("Powered by Appwrite · FastMCP · IBM Bob")

# ─────────────────────────────────────────────────────────
# UI — Página: Início
# ─────────────────────────────────────────────────────────

if pagina == "🏠 Início":
    st.title("🌍 Geo-Explorer")
    st.subheader("Plataforma de Trilhas de Aprendizagem — DIO")
    st.markdown("""
    Bem-vindo ao **Geo-Explorer**, uma aplicação interativa para explorar as trilhas de aprendizagem
    em tecnologia da **Digital Innovation One (DIO)**.

    ### O que você pode fazer aqui:
    - 📚 **Explorar 30 trilhas** organizadas por categoria e nível
    - 💻 **Receber um Desafio de Código** prático da trilha escolhida
    - 🏅 **Emitir seu Certificado Fictício de Conclusão** com código único
    - 💾 **Fazer backup local** dos dados do Appwrite em SQLite
    """)

    db = get_db_service()
    if db is None:
        st.error("Variáveis de ambiente do Appwrite não configuradas. Verifique o arquivo `.env`.")
    else:
        st.success("Conexão com Appwrite estabelecida com sucesso.")

    col1, col2, col3 = st.columns(3)
    trilhas = listar_trilhas_cached()
    col1.metric("Trilhas disponíveis", len(trilhas))
    categorias = len(set(t.get("categoria", "") for t in trilhas))
    col2.metric("Categorias", categorias)
    col3.metric("Banco de dados", "escola (Appwrite)")

# ─────────────────────────────────────────────────────────
# UI — Página: Trilhas
# ─────────────────────────────────────────────────────────

elif pagina == "📚 Trilhas":
    st.title("📚 Trilhas de Aprendizagem")

    trilhas = listar_trilhas_cached()
    if not trilhas:
        st.warning("Nenhuma trilha encontrada. Execute `dados/setup_geoexplorer.py` primeiro.")
        st.stop()

    categorias = sorted(set(t.get("categoria", "Geral") for t in trilhas))

    col_filtro, col_busca = st.columns([1, 2])
    with col_filtro:
        cat_sel = st.selectbox("Filtrar por categoria", ["Todas"] + categorias)
    with col_busca:
        termo = st.text_input("Buscar por palavra-chave", placeholder="ex: Python, AWS, Machine Learning...")

    filtradas = trilhas
    if cat_sel != "Todas":
        filtradas = [t for t in filtradas if t.get("categoria") == cat_sel]
    if termo:
        filtradas = [
            t for t in filtradas
            if termo.lower() in t.get("titulo", "").lower()
            or termo.lower() in t.get("descricao", "").lower()
        ]

    st.caption(f"{len(filtradas)} trilha(s) encontrada(s)")
    st.divider()

    for t in filtradas:
        with st.expander(f"**{t.get('titulo')}** — {t.get('categoria')} · {t.get('nivel')} · {t.get('duracao_horas')}h"):
            st.write(t.get("descricao", ""))
            if st.button("Ir para o Desafio desta Trilha", key=f"desafio_{t.get('$id')}"):
                st.session_state["trilha_selecionada"] = t
                st.session_state["pagina_redirect"] = "💻 Desafio de Código"
                st.rerun()

# ─────────────────────────────────────────────────────────
# UI — Página: Desafio de Código
# ─────────────────────────────────────────────────────────

elif pagina == "💻 Desafio de Código":
    st.title("💻 Desafio de Código")

    trilhas = listar_trilhas_cached()
    if not trilhas:
        st.warning("Nenhuma trilha encontrada.")
        st.stop()

    trilha_default = st.session_state.get("trilha_selecionada")
    titulos        = [t.get("titulo") for t in trilhas]
    default_idx    = titulos.index(trilha_default.get("titulo")) if trilha_default else 0

    titulo_sel = st.selectbox("Selecione a trilha", titulos, index=default_idx)
    trilha_sel = next(t for t in trilhas if t.get("titulo") == titulo_sel)

    st.markdown(f"**Categoria:** {trilha_sel.get('categoria')} | **Nível:** {trilha_sel.get('nivel')} | **Duração:** {trilha_sel.get('duracao_horas')}h")
    st.caption(trilha_sel.get("descricao", ""))
    st.divider()

    with st.spinner("Carregando desafio..."):
        desafio = buscar_ou_criar_desafio(trilha_sel)

    st.subheader(desafio.get("titulo", ""))
    st.markdown(f"**Enunciado:**\n\n{desafio.get('enunciado', '')}")
    st.code(desafio.get("template_codigo", ""), language="python")
    st.divider()

    st.markdown("### Submeter solução e emitir certificado")
    nome = st.text_input("Digite seu nome completo", placeholder="Ex: Maria Silva")

    if st.button("Submeter e Emitir Certificado", type="primary", disabled=not nome.strip()):
        with st.spinner("Registrando certificado no Appwrite..."):
            cert = emitir_certificado(nome.strip(), trilha_sel.get("titulo"))
        st.session_state["certificado"] = cert
        st.success(f"Parabens, {nome.strip()}! Codigo submetido e validado com sucesso!")
        st.balloons()

        st.markdown("---")
        st.markdown("### 🏅 Certificado de Conclusão")
        c1, c2 = st.columns(2)
        c1.metric("Participante", cert["usuario"])
        c1.metric("Trilha", cert["trilha_nome"])
        c2.metric("Código", cert["codigo"])
        c2.metric("Data de Emissão", cert["data_emissao"])

# ─────────────────────────────────────────────────────────
# UI — Página: Certificado
# ─────────────────────────────────────────────────────────

elif pagina == "🏅 Certificado":
    st.title("🏅 Consultar Certificado")
    st.markdown(
        "Certificados são emitidos exclusivamente na página **💻 Desafio de Código**, "
        "após a submissão da solução. Aqui você pode consultar certificados já emitidos."
    )

    trilhas = listar_trilhas_cached()
    titulos = [t.get("titulo") for t in trilhas]

    def _render_cert_card(cert: dict) -> None:
        st.markdown(
            f"""
            <div style="border:2px solid #1f77b4;border-radius:12px;padding:2rem;text-align:center;background:#f0f6ff">
            <h2>CERTIFICADO DE CONCLUSAO</h2>
            <h3>GEO-EXPLORER — DIO</h3>
            <hr>
            <p><strong>Certificamos que:</strong> {cert['usuario'].upper()}</p>
            <p><strong>Concluiu a Trilha:</strong> {cert['trilha_nome']}</p>
            <p><strong>Código de Autenticidade:</strong> <code>{cert['codigo']}</code></p>
            <p><strong>Data de Emissão:</strong> {cert['data_emissao']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.form("form_cert"):
        nome_cert   = st.text_input("Nome completo do participante")
        trilha_cert = st.selectbox("Trilha", titulos)
        submitted   = st.form_submit_button("Consultar Certificado", type="primary")

    if submitted:
        nome_limpo = nome_cert.strip()
        if not nome_limpo:
            st.warning("Informe seu nome para consultar.")
        else:
            # ── Busca certificados do usuário no Appwrite ────────────────────
            with st.spinner("Consultando certificados..."):
                from appwrite.query import Query
                existentes = fetch_rows(
                    "certificados",
                    queries=[Query.equal("usuario", nome_limpo), Query.limit(25)],
                )

            # ── Verifica se há certificado para esta trilha ──────────────────
            cert_trilha = next(
                (c for c in existentes if c.get("trilha_nome") == trilha_cert),
                None,
            )

            if cert_trilha:
                # Encontrou — exibe
                st.success(f"Certificado encontrado para **{nome_limpo}**!")
                _render_cert_card(cert_trilha)

                outros = [c for c in existentes if c.get("trilha_nome") != trilha_cert]
                if outros:
                    with st.expander(f"Ver outros {len(outros)} certificado(s) de {nome_limpo}"):
                        for c in outros:
                            st.markdown(
                                f"- **{c.get('trilha_nome')}** — `{c.get('codigo')}` — {c.get('data_emissao')}"
                            )
            else:
                # Não encontrou — orienta ir para o desafio
                trilha_obj = next(
                    (t for t in trilhas if t.get("titulo") == trilha_cert), None
                )
                st.error(
                    f"Nenhum certificado encontrado para **{nome_limpo}** "
                    f"na trilha **{trilha_cert}**."
                )
                st.info(
                    "Para obter o certificado você precisa concluir o "
                    "**Desafio de Código** desta trilha."
                )
                if st.button("Ir para o Desafio de Código", type="primary"):
                    st.session_state["trilha_selecionada"] = trilha_obj
                    st.session_state["pagina"] = "💻 Desafio de Código"
                    st.rerun()

# ─────────────────────────────────────────────────────────
# UI — Página: Backup SQLite
# ─────────────────────────────────────────────────────────

elif pagina == "💾 Backup SQLite":
    st.title("💾 Backup Appwrite → SQLite")
    st.markdown(
        "Realiza um backup incremental das tabelas **trilhas**, **desafios** e **certificados** "
        "do Appwrite para o arquivo `dados/backup_db_appwrite.sqlite`."
    )

    st.info(f"Arquivo de destino: `{SQLITE_PATH.resolve()}`")

    if st.button("Executar Backup Agora", type="primary"):
        with st.spinner("Executando backup..."):
            try:
                resultado = run_backup()
                st.success(f"Backup concluído em {resultado['ts']}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Trilhas copiadas",      resultado.get("trilhas", 0))
                col2.metric("Desafios copiados",     resultado.get("desafios", 0))
                col3.metric("Certificados copiados", resultado.get("certificados", 0))
            except Exception as e:
                st.error(f"Erro ao executar o backup: {e}")

    st.divider()
    st.markdown("### Histórico de backups")

    if SQLITE_PATH.exists():
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            logs = conn.execute(
                "SELECT executado_em, trilhas, desafios, certificados FROM backup_log ORDER BY id DESC LIMIT 10"
            ).fetchall()
            conn.close()
            if logs:
                import pandas as pd
                df = pd.DataFrame(logs, columns=["Executado em", "Trilhas", "Desafios", "Certificados"])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.caption("Nenhum backup registrado ainda.")
        except Exception as e:
            st.caption(f"Não foi possível ler o histórico: {e}")
    else:
        st.caption("Arquivo SQLite ainda não existe. Execute o backup pela primeira vez.")

# ─────────────────────────────────────────────────────────
# UI — Página: Certificados Emitidos
# ─────────────────────────────────────────────────────────

elif pagina == "📋 Certificados Emitidos":
    st.title("📋 Certificados Emitidos")
    st.markdown("Lista todos os certificados registrados no Appwrite.")

    # ── Controles de filtro ──────────────────────────────────────────────────
    col_nome, col_trilha, col_btn = st.columns([2, 2, 1])
    with col_nome:
        filtro_nome = st.text_input("Filtrar por nome", placeholder="Ex: Maria Silva")
    with col_trilha:
        filtro_trilha = st.text_input("Filtrar por trilha", placeholder="Ex: Python, AWS...")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        recarregar = st.button("Atualizar lista", use_container_width=True)

    # ── Busca no Appwrite ────────────────────────────────────────────────────
    @st.cache_data(show_spinner="Carregando certificados...", ttl=30)
    def _listar_certificados() -> list[dict]:
        from appwrite.query import Query
        return fetch_rows("certificados", queries=[Query.limit(100)])

    if recarregar:
        st.cache_data.clear()

    certificados = _listar_certificados()

    # ── Filtros locais ───────────────────────────────────────────────────────
    if filtro_nome.strip():
        certificados = [
            c for c in certificados
            if filtro_nome.strip().lower() in c.get("usuario", "").lower()
        ]
    if filtro_trilha.strip():
        certificados = [
            c for c in certificados
            if filtro_trilha.strip().lower() in c.get("trilha_nome", "").lower()
        ]

    # ── Métricas ─────────────────────────────────────────────────────────────
    total = len(certificados)
    participantes = len(set(c.get("usuario", "") for c in certificados))
    trilhas_distintas = len(set(c.get("trilha_nome", "") for c in certificados))

    m1, m2, m3 = st.columns(3)
    m1.metric("Total de certificados", total)
    m2.metric("Participantes únicos", participantes)
    m3.metric("Trilhas contempladas", trilhas_distintas)
    st.divider()

    # ── Tabela de resultados ──────────────────────────────────────────────────
    if not certificados:
        st.info("Nenhum certificado encontrado para os filtros aplicados.")
    else:
        import pandas as pd
        df = pd.DataFrame(
            [
                {
                    "Participante":  c.get("usuario", ""),
                    "Trilha":        c.get("trilha_nome", ""),
                    "Código":        c.get("codigo", ""),
                    "Data Emissão":  c.get("data_emissao", ""),
                }
                for c in certificados
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

        # ── Detalhes individuais via expander ─────────────────────────────────
        st.divider()
        st.markdown("### Detalhes individuais")
        for c in certificados:
            label = f"**{c.get('usuario')}** — {c.get('trilha_nome')} — `{c.get('codigo')}`"
            with st.expander(label):
                col_a, col_b = st.columns(2)
                col_a.markdown(f"**Participante:** {c.get('usuario', '').upper()}")
                col_a.markdown(f"**Trilha:** {c.get('trilha_nome', '')}")
                col_b.markdown(f"**Código:** `{c.get('codigo', '')}`")
                col_b.markdown(f"**Data de Emissão:** {c.get('data_emissao', '')}")
