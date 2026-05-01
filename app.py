import streamlit as st
import random
import requests
from deep_translator import GoogleTranslator
from utils.steam_api import get_owned_games, get_user_profile

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="WSIPT", layout="wide")

# =========================
# SESSION STATE
# =========================
if "df_salvo" not in st.session_state:
    st.session_state.df_salvo = None

if "profile_salvo" not in st.session_state:
    st.session_state.profile_salvo = None

if "ultimo_jogo" not in st.session_state:
    st.session_state.ultimo_jogo = None

# =========================
# TRADUÇÃO
# =========================
def traduzir(texto):
    try:
        return GoogleTranslator(source='auto', target='pt').translate(texto)
    except:
        return texto

# =========================
# CACHE API STEAM
# =========================
@st.cache_data
def get_game_details(appid):
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=pt-br"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data[str(appid)]["success"]:
            jogo = data[str(appid)]["data"]

            descricao = jogo.get("short_description", "")

            if descricao:
                descricao = traduzir(descricao)

            return {
                "descricao": descricao if descricao else "Sem descrição.",
                "imagem": jogo.get("header_image", None),
                "generos": [g["description"] for g in jogo.get("genres", [])]
            }

    except Exception as e:
        print("Erro Steam API:", e)

    return None

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
.stApp { background-color: #1b2838; }
h1, h2, h3, h4 { color: white; }
</style>
""", unsafe_allow_html=True)

# =========================
# LOGIN
# =========================
if st.session_state.df_salvo is None:

    st.markdown("## 🎮 What Should I Play Tonight")
    st.write("Conecte sua conta Steam para começar")

    steam_id = st.text_input("Digite seu Steam ID")
    confirmar = st.button("🔍 Conectar")

    if confirmar:
        profile = get_user_profile(steam_id)
        df = get_owned_games(steam_id)

        if profile and df is not None:
            st.session_state.df_salvo = df
            st.session_state.profile_salvo = profile
            st.rerun()
        else:
            st.error("Erro ao carregar dados da Steam. Verifique o ID ou privacidade do perfil.")

# =========================
# APP PRINCIPAL
# =========================
else:

    profile = st.session_state.profile_salvo
    df = st.session_state.df_salvo

    # =========================
    # PERFIL
    # =========================
    col1, col2 = st.columns([1, 5])

    with col1:
        st.image(profile["avatarfull"], width=120)

    with col2:
        st.markdown(f"# {profile['personaname']}")
        st.caption("Conta conectada")

    if st.button("🔓 Desconectar"):
        st.session_state.df_salvo = None
        st.session_state.profile_salvo = None
        st.session_state.ultimo_jogo = None
        st.rerun()

    st.divider()

    # =========================
    # TABS
    # =========================
    tab1, tab2 = st.tabs(["🎯 Recomendação", "📚 Biblioteca"])

    # =====================================================
    # 🎯 RECOMENDAÇÃO
    # =====================================================
    with tab1:

        st.subheader("O que jogar hoje?")

        tempo_disponivel = st.selectbox(
            "Quanto tempo você tem hoje?",
            ["30 min", "1 hora", "2 horas", "3+ horas"]
        )

        mood = st.selectbox(
            "O que você quer hoje?",
            [
                "Descobrir algo novo",
                "Continuar um jogo",
                "Jogar algo confiável",
                "Me surpreenda"
            ]
        )

        if st.button("🎮 Recomendar jogo"):

            jogos = df.copy()

            nao_iniciados = jogos[jogos["playtime_forever"] == 0]
            pouco_jogados = jogos[
                (jogos["playtime_forever"] > 0) &
                (jogos["playtime_forever"] < 300)
            ]
            muito_jogados = jogos[jogos["playtime_forever"] >= 300]

            if mood == "Descobrir algo novo":
                pool = nao_iniciados
            elif mood == "Continuar um jogo":
                pool = pouco_jogados
            elif mood == "Jogar algo confiável":
                pool = muito_jogados
            elif mood == "Me surpreenda":
                pool = jogos.sample(min(len(jogos), 20))
            else:
                pool = jogos

            if pool.empty:
                pool = jogos

            if tempo_disponivel == "30 min":
                pool = pool[pool["playtime_forever"] > 0]
            elif tempo_disponivel == "3+ horas":
                if not nao_iniciados.empty:
                    pool = nao_iniciados

            if pool.empty:
                pool = jogos

            pool = pool[pool["name"] != st.session_state.ultimo_jogo]

            if pool.empty:
                pool = jogos

            escolhido = pool.sample(1).iloc[0]
            st.session_state.ultimo_jogo = escolhido["name"]

            appid = escolhido["appid"]
            detalhes = get_game_details(appid)

            imagem = detalhes["imagem"] if detalhes else f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
            descricao = detalhes["descricao"] if detalhes else "Descrição não disponível."

            col1, col2 = st.columns([2, 3])

            with col1:
                st.image(imagem)

            with col2:
                st.markdown(f"## 🎮 {escolhido['name']}")
                st.success("Recomendação da noite")
                st.write(descricao)

    # =====================================================
    # 📚 BIBLIOTECA
    # =====================================================
    with tab2:

        st.subheader("Biblioteca")

        biblioteca_df = df.rename(
            columns={
                "name": "Nome do jogo",
                "playtime_forever": "Tempo jogado (min)"
            }
        )

        ordem = st.selectbox(
            "Ordenar por",
            [
                "Alfabética (A-Z)",
                "Alfabética (Z-A)",
                "Tempo crescente",
                "Tempo decrescente"
            ]
        )

        unidade = st.radio(
            "Unidade de tempo",
            ["Minutos", "Horas"],
            horizontal=True
        )

        tabela = biblioteca_df.copy()

        if unidade == "Horas":
            tabela["Tempo jogado"] = (tabela["Tempo jogado (min)"] / 60).round(1)
        else:
            tabela["Tempo jogado"] = tabela["Tempo jogado (min)"]

        if ordem == "Alfabética (A-Z)":
            tabela = tabela.sort_values("Nome do jogo")
        elif ordem == "Alfabética (Z-A)":
            tabela = tabela.sort_values("Nome do jogo", ascending=False)
        elif ordem == "Tempo crescente":
            tabela = tabela.sort_values("Tempo jogado")
        elif ordem == "Tempo decrescente":
            tabela = tabela.sort_values("Tempo jogado", ascending=False)

        st.table(tabela[["Nome do jogo", "Tempo jogado"]])

        st.divider()

        st.subheader("🎮 Ver detalhes do jogo")

        jogo_selecionado = st.selectbox(
            "Escolha um jogo",
            tabela["Nome do jogo"]
        )

        jogo_info = tabela[tabela["Nome do jogo"] == jogo_selecionado].iloc[0]
        appid = df[df["name"] == jogo_selecionado]["appid"].iloc[0]

        detalhes = get_game_details(appid)

        if detalhes:
            imagem = detalhes["imagem"]
            descricao = detalhes["descricao"]
        else:
            imagem = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
            descricao = "Descrição não disponível."

        horas = jogo_info["Tempo jogado (min)"] / 60

        col1, col2 = st.columns([2, 3])

        with col1:
            st.image(imagem)

        with col2:
            st.markdown(f"## {jogo_selecionado}")
            st.write(f"⏱️ {horas:.1f} horas jogadas")
            st.write("📖 Sobre o jogo:")
            st.write(descricao)