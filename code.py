"""Catálogo de aulas de programação e criação de websites.

Executar:  streamlit run code.py
Ficheiros: code.py + style.css (na mesma pasta)

Fonte de dados (por ordem):
1. MySQL        -> se existir [mysql] em .streamlit/secrets.toml
2. Google Sheets -> se existir [gsheets] em .streamlit/secrets.toml
3. Lista local  -> AULAS_EXEMPLO (para testar)
"""
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Aulas de Programação", page_icon="💻", layout="centered")

COLUNAS = ["titulo", "categoria", "nivel", "duracao", "preco", "descricao"]

AULAS_EXEMPLO = [
    ("Python do zero", "Programação", "Iniciante", "8 aulas", 80, "Variáveis, ciclos, funções e primeiros programas."),
    ("Python para automatizar tarefas", "Programação", "Intermédio", "6 aulas", 70, "Ficheiros, Excel, Google Sheets e pequenos scripts."),
    ("Streamlit: apps web com Python", "Programação", "Intermédio", "6 aulas", 70, "Cria e publica apps online só com Python."),
    ("Bases de dados com MySQL", "Programação", "Intermédio", "5 aulas", 60, "Tabelas, consultas SQL e ligação ao Python."),
    ("HTML e CSS: o teu primeiro website", "Websites", "Iniciante", "8 aulas", 80, "Estrutura, estilos e design responsivo."),
    ("JavaScript e React", "Websites", "Avançado", "10 aulas", 110, "Componentes, estado e publicação no Vercel."),
]


def carregar_css(caminho: str = "style.css") -> None:
    css = Path(__file__).with_name(caminho)
    if css.exists():
        st.markdown(f"<style>{css.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def carregar_aulas() -> pd.DataFrame:
    try:
        if "mysql" in st.secrets:
            import mysql.connector

            ligacao = mysql.connector.connect(**st.secrets["mysql"])
            df = pd.read_sql(f"SELECT {', '.join(COLUNAS)} FROM aulas", ligacao)
            ligacao.close()
            return df
        if "gsheets" in st.secrets:
            import gspread

            cliente = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
            folha = cliente.open_by_key(st.secrets["gsheets"]["sheet_id"]).sheet1
            return pd.DataFrame(folha.get_all_records())[COLUNAS]
    except Exception as erro:  # usa a lista local se a ligação falhar
        st.warning(f"Não foi possível ler a base de dados ({erro}). A mostrar exemplos.")
    return pd.DataFrame(AULAS_EXEMPLO, columns=COLUNAS)


def cartao(aula: pd.Series) -> str:
    classe = "aula web" if aula["categoria"] == "Websites" else "aula"
    return f"""
    <div class="{classe}">
      <h3>{aula['titulo']}</h3>
      <p>{aula['descricao']}</p>
      <div class="meta">
        <span>{aula['categoria']}</span>
        <span>{aula['nivel']}</span>
        <span>{aula['duracao']}</span>
        <span class="preco">{aula['preco']} €</span>
      </div>
    </div>
    """


carregar_css()

st.markdown(
    """
    <div class="hero">
      <h1>Aulas de programação e websites</h1>
      <p>Escolhe a aula, o nível e o formato que te servem. Aprende a programar e a publicar os teus projetos.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

aulas = carregar_aulas()

col1, col2 = st.columns(2)
categoria = col1.selectbox("Categoria", ["Todas"] + sorted(aulas["categoria"].unique()))
nivel = col2.selectbox("Nível", ["Todos"] + sorted(aulas["nivel"].unique()))
pesquisa = st.text_input("Pesquisar aula", placeholder="Ex.: Python, HTML, MySQL")

filtradas = aulas
if categoria != "Todas":
    filtradas = filtradas[filtradas["categoria"] == categoria]
if nivel != "Todos":
    filtradas = filtradas[filtradas["nivel"] == nivel]
if pesquisa:
    texto = filtradas["titulo"] + " " + filtradas["descricao"]
    filtradas = filtradas[texto.str.contains(pesquisa, case=False, na=False)]

st.caption(f"{len(filtradas)} aula(s) encontrada(s)")

if filtradas.empty:
    st.info("Nenhuma aula encontrada. Limpa a pesquisa ou muda os filtros.")
for _, aula in filtradas.iterrows():
    st.markdown(cartao(aula), unsafe_allow_html=True)