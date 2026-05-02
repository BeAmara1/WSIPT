import os
import sys
import streamlit as st

st.write("PATH:", sys.path)
st.write("ROOT FILES:", os.listdir())
st.write("UTILS FOLDER:", os.listdir("utils") if os.path.exists("utils") else "NOT FOUND")

import streamlit as st
import pandas as pd

from utils.steam_api import (
    get_owned_games,
    get_user_profile,
    get_game_details
)

st.set_page_config(page_title="WSIPT", layout="wide")



# =========================
# 🎨 CSS AVANÇADO
# =========================
st.markdown("""
<style>

/* Fundo geral */
body {
    background-color: #0f172a;
}

/* Container principal */
.block-container {
    padding-top: 2rem;
}

/* Cards */
.card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 20px;
    transition: all 0.25s ease;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.6);
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0px 10px 25px rgba(0,0,0,0.8);
}

/* Imagem */
.card img {
    width: 100%;
    border-radius: 10px;
    margin-bottom: 10px;
}

/* Título */
.card-title {
    font-size: 18px;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 5px;
}

/* Info */
.card-info {
    font-size: 13px;
    color: #94a3b8;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-size: 15px;
    font-weight: 500;
}

/* Botões */
.stButton>button {
    border-radius: 8px;
    background-color: #1e293b;
    color: white;
    border: 1px solid #334155;
}

.stButton>button:hover {
    background-color: #334155;
}

</style>
""", unsafe_allow_html=True)

# =========================
# ESTADO
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

# =========================
# FUNÇÃO
# =========================
def carregar_dados(steam_id):
    profile = get_user_profile(steam_id)
    jogos = get_owned_games(steam_id)

    if profile is None or jogos is None or jogos.empty:
        return None, None

    df = jogos.copy()

    df = df.rename(columns={
        "name": "Nome",
        "playtime_forever": "Minutos Jogados"
    })

    df["Horas Jogadas"] = (df["Minutos Jogados"] / 60).round(1)

    df["Status"] = df["Minutos Jogados"].apply(
        lambda x: "Não iniciado" if x == 0 else "Jogado"
    )

    return profile, df

# =========================
# HOME
# =========================
if not st.session_state.logado:
    st.title("What Should I Play Tonight")
    st.write("Descubra o próximo jogo ideal da sua biblioteca Steam")

    steam_id = st.text_input("Digite seu Steam ID")

    if st.button("Entrar"):
        if steam_id:
            profile, df = carregar_dados(steam_id)

            if profile is None:
                st.error("Steam ID inválido ou perfil privado.")
            else:
                st.session_state.profile = profile
                st.session_state.df = df
                st.session_state.logado = True
                st.session_state.historico_recomendacoes = []
                st.rerun()
        else:
            st.warning("Digite um Steam ID válido")

# =========================
# APP
# =========================
else:
    profile = st.session_state.profile
    df = st.session_state.df

    col1, col2 = st.columns([1, 6])
    with col1:
        st.image(profile["avatarfull"], width=70)
    with col2:
        st.markdown(f"### {profile['personaname']}")

    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs([
        "Perfil",
        "Recomendação",
        "Biblioteca",
        "Inspecionar"
    ])

    # =========================
    # PERFIL
    # =========================
    with tab1:
        total = len(df)
        horas = int(df["Horas Jogadas"].sum())
        nao = int((len(df[df["Status"] == "Não iniciado"]) / total) * 100)

        c1, c2, c3 = st.columns(3)
        c1.metric("Jogos", total)
        c2.metric("Horas", horas)
        c3.metric("Não iniciados", f"{nao}%")

    # =========================
    # RECOMENDAÇÃO
    # =========================
    with tab2:
        tipo = st.selectbox("Tipo", ["Relaxar", "Ação", "História", "Multiplayer"])
        prioridade = st.selectbox("Prioridade", ["Não iniciado", "Pouco jogado", "Tanto faz"])

        if "historico_recomendacoes" not in st.session_state:
            st.session_state.historico_recomendacoes = []

        col1, col2 = st.columns(2)
        gerar = col1.button("Gerar")
        novas = col2.button("Novas")

        if gerar or novas:
            df_f = df.copy()

            if prioridade == "Não iniciado":
                df_f = df_f[df_f["Status"] == "Não iniciado"]
            elif prioridade == "Pouco jogado":
                df_f = df_f[df_f["Horas Jogadas"] < 2]

            df_f_novo = df_f[~df_f["Nome"].isin(st.session_state.historico_recomendacoes)]

            if df_f_novo.empty:
                st.warning("Você já viu tudo para esse filtro.")
                if st.button("Recomeçar"):
                    st.session_state.historico_recomendacoes = []
                    st.rerun()

            else:
                jogos = df_f_novo.sample(min(6, len(df_f_novo)))
                st.session_state.historico_recomendacoes.extend(jogos["Nome"].tolist())

                cols = st.columns(3)

                for i, (_, jogo) in enumerate(jogos.iterrows()):
                    nome = jogo["Nome"]
                    detalhes = get_game_details(nome)
                    imagem = detalhes["image"] if detalhes else ""

                    with cols[i % 3]:
                        st.markdown(f"""
                        <div class="card">
                            <img src="{imagem}">
                            <div class="card-title">{nome}</div>
                            <div class="card-info">{jogo['Horas Jogadas']} horas</div>
                        </div>
                        """, unsafe_allow_html=True)

    # =========================
    # BIBLIOTECA
    # =========================
    with tab3:
        st.dataframe(df[["Nome", "Horas Jogadas", "Status"]], use_container_width=True)

    # =========================
    # INSPECIONAR
    # =========================
    with tab4:
        nome = st.selectbox("Escolha um jogo", df["Nome"])
        jogo = df[df["Nome"] == nome].iloc[0]
        detalhes = get_game_details(nome)

        col1, col2 = st.columns([1, 2])

        with col1:
            if detalhes:
                st.image(detalhes["image"], use_container_width=True)

        with col2:
            st.subheader(nome)
            st.write(f"{jogo['Horas Jogadas']} horas")
            if detalhes:
                st.write(detalhes["description"])