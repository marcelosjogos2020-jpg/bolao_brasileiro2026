import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página para emular dispositivo móvel/web limpo
st.set_page_config(page_title="Da Copa - Brasileirão 2026", page_icon="⚽", layout="centered")

# ============================================================
# INTERFACE DE ESTILO - RÉPLICA FIEL DO "DA COPA" (LIGHT MODE)
# ============================================================
# Bloqueador contra o Google Tradutor nativo
st.markdown('<meta name="google" content="notranslate" />', unsafe_allow_html=True)

st.markdown("""
    <style>
        /* Forçar Modo Claro Absoluto em todas as camadas internas do Streamlit */
        html, body, .stApp, .main, [data-testid="stAppViewBlockContainer"] {
            background-color: #f8fafc !important;
            color: #1e293b !important;
        }
        
        /* Esconder cabeçalho nativo */
        [data-testid="stHeader"] { display: none !important; }
        
        /* Cabeçalho de Saudação */
        .saudacao-title { font-size: 26px; font-weight: 800; color: #0f172a; margin-bottom: 2px; }
        .saudacao-sub { font-size: 16px; color: #64748b; margin-bottom: 20px; }
        
        /* Estilização dos Botões Reais para parecerem Cartões do App */
        div.stButton > button {
            background-color: #f1f5f9 !important;
            color: #334155 !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 14px 10px !important;
            font-weight: bold !important;
            font-size: 14px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
            width: 100% !important;
            transition: all 0.2s ease;
        }
        div.stButton > button:hover {
            background-color: #e2e8f0 !important;
            color: #00b25c !important;
        }
        
        /* Cartão de Grupo de Apostas */
        .grupo-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 18px;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
        }
        .badge-posicao {
            background-color: #e2fbe8;
            color: #00b25c;
            font-size: 12px;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: 8px;
            float: right;
        }
        
        /* Leaderboard / Classificação */
        .row-ranking {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 14px 16px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .row-ranking.voce {
            border: 2px solid #00b25c !important;
            background-color: #f6fdf8;
        }
        .player-avatar {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background-color: #e2e8f0;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #475569;
            margin-right: 12px;
        }
        .player-name { font-weight: 700; color: #1e293b; font-size: 15px; }
        .player-username { font-size: 12px; color: #94a3b8; display: block; }
        .points-display { font-size: 18px; font-weight: 800; color: #1e293b; text-align: right; }
        .points-var { font-size: 11px; color: #00b25c; font-weight: bold; display: block; }

        /* Partidas e Match Cards */
        .date-divider {
            font-size: 13px;
            font-weight: 800;
            color: #64748b;
            text-transform: uppercase;
            margin: 20px 0 10px 0;
            letter-spacing: 0.5px;
        }
        .match-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.01);
        }
        .match-header { font-size: 12px; color: #94a3b8; font-weight: 600; margin-bottom: 10px; }
        .match-row-teams { display: flex; align-items: center; justify-content: space-between; }
        .team-block { flex: 1; font-weight: 700; color: #334155; font-size: 15px; }
        .team-block.right { text-align: right; }
        .score-pill {
            background-color: #f1f5f9;
            padding: 6px 16px;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 800;
            color: #1e293b;
            letter-spacing: 4px;
        }
        
        /* Forçar visibilidade permanente dos títulos das abas */
        div[data-testid="stTabs"] button {
            padding: 6px 14px !important;
        }
        div[data-testid="stTabs"] button p {
            color: #334155 !important;
            font-weight: 800 !important;
            font-size: 14px !important;
            display: block !important;
            visibility: visible !important;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] p {
            color: #00b25c !important;
        }
        
        .rule-box {
            background-color: #ffffff;
            border-left: 4px solid #00b25c;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 10px;
            border: 1px solid #e2e8f0;
            color: #334155;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# BANCO DE DADOS E MOTOR DE CÁLCULO
# ============================================================
ARQUIVO_JOGOS = "jogos_2026.csv"
ARQUIVO_PALPITES = "palpites_2026.csv"

forçar_recriacao = False
if os.path.exists(ARQUIVO_JOGOS):
    try:
        df_teste = pd.read_csv(ARQUIVO_JOGOS)
        if "tipo" not in df_teste.columns: forçar_recriacao = True
    except: forçar_recriacao = True

if not os.path.exists(ARQUIVO_JOGOS) or forçar_recriacao:
    jogos_iniciais = [
        {"id": 1, "rodada": 1, "data_texto": "Terça-feira, 14 de Julho de 2026", "hora": "16:00", "tipo": "Anterior", "home": "Flamengo", "away": "Palmeiras", "score_home": "2", "score_away": "1"},
        {"id": 2, "rodada": 1, "data_texto": "Terça-feira, 14 de Julho de 2026", "hora": "19:30", "tipo": "Anterior", "home": "São Paulo", "away": "Corinthians", "score_home": "0", "score_away": "0"},
        {"id": 3, "rodada": 1, "data_texto": "Quarta-feira, 15 de Julho de 2026", "hora": "16:00", "tipo": "Próxima", "home": "Atlético-MG", "away": "Cruzeiro", "score_home": "-", "score_away": "-"},
        {"id": 4, "rodada": 1, "data_texto": "Quarta-feira, 15 de Julho de 2026", "hora": "21:45", "tipo": "Próxima", "home": "Botafogo", "away": "Fluminense", "score_home": "-", "score_away": "-"},
        {"id": 5, "rodada": 2, "data_texto": "Sábado, 18 de Julho de 2026", "hora": "18:00", "tipo": "Próxima", "home": "Internacional", "away": "Grêmio", "score_home": "-", "score_away": "-"}
    ]
    pd.DataFrame(jogos_iniciais).to_csv(ARQUIVO_JOGOS, index=False)

if not os.path.exists(ARQUIVO_PALPITES):
    pd.DataFrame(columns=["usuario", "jogo_id", "palpite_home", "palpite_away"]).to_csv(ARQUIVO_PALPITES, index=False)

def carregar_jogos(): return pd.read_csv(ARQUIVO_JOGOS)
def carregar_palpites(): return pd.read_csv(ARQUIVO_PALPITES)

def calcular_pontos(p_home, p_away, r_home, r_away):
    if str(r_home) == "-" or str(r_away) == "-": return 0
    try:
        ph, pa, rh, ra = int(p_home), int(p_away), int(r_home), int(r_away)
    except:
        return 0
    if ph == rh and pa == ra: return 10
    if ((ph - pa > 0 and rh - ra > 0) or (ph - pa < 0 and rh - ra < 0) or (ph - pa == 0 and rh - ra == 0)): return 5
    return 0

# Memória estável do Usuário Ativo
if "user_ativo" not in st.session_state:
    st.session_state["user_ativo"] = "Marcelo"

# ============================================================
# SIDEBAR - CONFIGURAÇÃO CORRIGIDA CONTRA CRASHES
# ============================================================
with st.sidebar:
    st.header("👥 Quem está jogando?")
    df_p_init = carregar_palpites()
    usuarios_cadastrados = list(df_p_init["usuario"].dropna().unique())
    if "Marcelo" not in usuarios_cadastrados:
        usuarios_cadastrados.insert(0, "Marcelo")
    
    op_user = st.radio("Ação Perfil:", ["Escolher Existente", "Criar Novo Amigo"])
    if op_user == "Criar Novo Amigo":
        novo_amigo = st.text_input("Nome do Amigo:").strip()
        if st.button("➕ Adicionar ao Bolão") and novo_amigo:
            if novo_amigo not in usuarios_cadastrados:
                usuarios_cadastrados.append(novo_amigo)
                st.session_state["user_ativo"] = novo_amigo
                st.success(f"{novo_amigo} adicionado!")
                st.rerun()
            else:
                st.warning("Nome já cadastrado.")
    else:
        current_user = st.session_state["user_ativo"]
        idx_default = sorted(usuarios_cadastrados).index(current_user) if current_user in usuarios_cadastrados else 0
        user_sel = st.selectbox("Selecione seu nome:", sorted(usuarios_cadastrados), index=idx_default)
        st.session_state["user_ativo"] = user_sel

    user_ativo = st.session_state["user_ativo"]
    username_mock = f"@{user_ativo.lower()}1000"
    st.divider()
    modo_admin = st.checkbox("⚙️ Ativar Modo Administrador")

# ============================================================
# PROCESSAMENTO DE PONTOS DO RANKING
# ============================================================
df_j_calc = carregar_jogos()
df_p_calc = carregar_palpites()

pontos_user_ativo = 0
posicao_user_ativo = 1
total_jogadores = len(usuarios_cadastrados)

if not df_p_calc.empty:
    lista_ranking = []
    for u in usuarios_cadastrados:
        pts = 0
        p_u = df_p_calc[df_p_calc["usuario"] == u]
        for _, palpite in p_u.iterrows():
            j_real = df_j_calc[df_j_calc["id"] == palpite["jogo_id"]]
            if not j_real.empty:
                pts += calcular_pontos(palpite["palpite_home"], palpite["palpite_away"], j_real.iloc[0]["score_home"], j_real.iloc[0]["score_away"])
        lista_ranking.append({"usuario": u, "pontos": pts})
    
    df_rk = pd.DataFrame(lista_ranking).sort_values(by="pontos", ascending=False).reset_index(drop=True)
    
    idx_voce = df_rk[df_rk["usuario"] == user_ativo].index
    if len(idx_voce) > 0:
        posicao_user_ativo = idx_voce[0] + 1
        pontos_user_ativo = df_rk.loc[idx_voce[0], "pontos"]

# ============================================================
# ABAS DE NAVEGAÇÃO
# ============================================================
menu_inicio, menu_classificacao, menu_partidas, menu_admin = st.tabs([
    "🏠 Início", 
    "📊 Classificação", 
    "📅 Partidas", 
    "🛠️ Painel Admin"
])

# ----------- 1. ABA INÍCIO -----------
with menu_inicio:
    st.markdown(f'<div class="saudacao-title">Olá, {user_ativo}!</div>', unsafe_allow_html=True)
    st.markdown('<div class="saudacao-sub">Vamos fazer uns palpites?</div>', unsafe_allow_html=True)
    
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    clicou_criar = c_btn1.button("➕\nCriar Bolão")
    clicou_entrar = c_btn2.button("👤\nEntrar Bolão")
    clicou_regras = c_btn3.button("📖\nRegras")
    
    if clicou_criar: st.info("🏆 Recurso Premium: Criação de novos grupos paralelos liberada nas próximas rodadas!")
    if clicou_entrar: st.info("🔑 Envie o link desta página para seus amigos entrarem diretamente no seu grupo.")
    if clicou_regras:
        st.markdown("""
        <div class="rule-box">
            <strong>📜 Sistema Oficial de Pontos:</strong><br>
            • 🟢 <strong>10 Pontos:</strong> Acerto em cheio do placar exato.<br>
            • 🟡 <strong>5 Pontos:</strong> Acerto do vencedor ou do empate (errou os gols).<br>
            • 🔴 <strong>0 Pontos:</strong> Erro total do resultado.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Seus Grupos")
    st.markdown(f"""
        <div class="grupo-card">
            <span class="badge-posicao">{posicao_user_ativo}º lugar</span>
            <div style="font-weight: 800; font-size: 16px; color: #0f172a;">Bolão Brasileirão 2026 - Família</div>
            <div style="font-size: 13px; color: #64748b; margin-top: 4px;">Campeonato Brasileiro • {total_jogadores} participantes</div>
            <div style="font-size: 15px; font-weight: bold; color: #00b25c; margin-top: 12px;">{pontos_user_ativo} pts</div>
        </div>
    """, unsafe_allow_html=True)

# ----------- 2. ABA CLASSIFICAÇÃO -----------
with menu_classificacao:
    st.markdown("## Classificação Geral")
    
    if df_p_calc.empty:
        st.markdown(f"""
            <div class="row-ranking voce">
                <div style="display:flex; align-items:center;">
                    <span style="font-weight:900; margin-right:15px; color:#00b25c;">1</span>
                    <div class="player-avatar" style="background-color:#e6f4ea; color:#00b25c;">M</div>
                    <div>
                        <span class="player-name">{user_ativo} (Você)</span>
                        <span class="player-username">{username_mock}</span>
                    </div>
                </div>
                <div class="points-display" style="color:#00b25c;">0<span class="points-var">+0</span></div>
            </div>
        """, unsafe_allow_html=True)
    else:
        for idx, row in df_rk.iterrows():
            is_voce = (row["usuario"] == user_ativo)
            classe_voce = "voce" if is_voce else ""
            cor_txt = "#00b25c" if is_voce else "#1e293b"
            
            st.markdown(f"""
                <div class="row-ranking {classe_voce}">
                    <div style="display:flex; align-items:center;">
                        <span style="font-weight:900; margin-right:15px; color:{cor_txt};">{idx + 1}</span>
                        <div class="player-avatar">{row['usuario'][0].upper()}</div>
                        <div>
                            <span class="player-name">{row['usuario']} {"(Você)" if is_voce else ""}</span>
                            <span class="player-username">@{row['usuario'].lower()}1000</span>
                        </div>
                    </div>
                    <div class="points-display" style="color:{cor_txt};">{row['pontos']}<span class="points-var">+0</span></div>
                </div>
            """, unsafe_allow_html=True)

# ----------- 3. ABA PARTIDAS -----------
with menu_partidas:
    st.markdown("## Partidas")
    
    df_jogos = carregar_jogos()
    df_palpites = carregar_palpites()
    
    sub_filtros = st.radio("Status:", ["Anteriores", "Ao Vivo (0)", "Próximas"], horizontal=True, label_visibility="collapsed")
    filtro_tipo = "Anterior" if sub_filtros == "Anteriores" else "Próxima"
    
    jogos_filtrados = df_jogos[df_jogos["tipo"] == filtro_tipo]
    datas_unicas = jogos_filtrados["data_texto"].unique()
    
    if len(jogos_filtrados) == 0:
        st.info(f"Nenhuma partida registrada nesta categoria.")
    
    for data_box in datas_unicas:
        st.markdown(f'<div class="date-divider">{data_box}</div>', unsafe_allow_html=True)
        jogos_do_dia = jogos_filtrados[jogos_filtrados["data_texto"] == data_box]
        
        for _, jogo in jogos_do_dia.iterrows():
            placar_exibicao = f"{jogo['score_home']} : {jogo['score_away']}" if filtro_tipo == "Anterior" else "- : -"
            
            st.markdown(f"""
                <div class="match-card">
                    <div class="match-header">{jogo['hora']} · Série A</div>
                    <div class="match-row-teams">
                        <div class="team-block">{jogo['home']}</div>
                        <div class="score-pill">{placar_exibicao}</div>
                        <div class="team-block right">{jogo['away']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if filtro_tipo == "Próxima":
                p_ant = df_palpites[(df_palpites["usuario"] == user_ativo) & (df_palpites["jogo_id"] == jogo["id"])]
                init_h = int(p_ant.iloc[0]["palpite_home"]) if not p_ant.empty else 0
                init_a = int(p_ant.iloc[0]["palpite_away"]) if not p_ant.empty else 0
                
                with st.expander(f"📝 Preencher Palpite: {jogo['home']} x {jogo['away']}"):
                    c_in1, c_in2, c_btn = st.columns([1, 1, 2])
                    val_h = c_in1.number_input(f"{jogo['home']}:", 0, 15, init_h, key=f"user_h_{jogo['id']}")
                    val_a = c_in2.number_input(f"{jogo['away']}:", 0, 15, init_a, key=f"user_a_{jogo['id']}")
                    
                    if c_btn.button("Salvar meu palpite", key=f"btn_salvar_{jogo['id']}", use_container_width=True):
                        df_palpites = df_palpites[~((df_palpites["usuario"] == user_ativo) & (df_palpites["jogo_id"] == jogo["id"]))]
                        novo_p = pd.DataFrame([{"usuario": user_ativo, "jogo_id": jogo["id"], "palpite_home": val_h, "palpite_away": val_a}])
                        df_final = pd.concat([df_palpites, novo_p], ignore_index=True)
                        df_final.to_csv(ARQUIVO_PALPITES, index=False)
                        st.success("Aposta registrada!")
                        st.rerun()

# ----------- 4. ABA ADMIN -----------
with menu_admin:
    if not modo_admin:
        st.info("Ative o 'Modo Administrador' na barra lateral esquerda para lançar as cotações e encerramentos reais.")
    else:
        st.subheader("Lançador de Placar Oficial")
        df_jogos = carregar_jogos()
        
        with st.form("painel_admin_form"):
            updates = []
            for _, jg in df_jogos.iterrows():
                st.write(f"⚽ **{jg['home']} x {jg['away']}**")
                c_h, c_a, c_status = st.columns(3)
                
                init_h = int(jg["score_home"]) if str(jg["score_home"]) != "-" else 0
                init_a = int(jg["score_away"]) if str(jg["score_away"]) != "-" else 0
                
                r_h = c_h.number_input("Gols Casa", 0, 15, init_h, key=f"adm_h_{jg['id']}")
                r_a = c_a.number_input("Gols Fora", 0, 15, init_a, key=f"adm_a_{jg['id']}")
                finalizado = c_status.checkbox("Partida Encerrada", value=(str(jg["score_home"]) != "-"), key=f"adm_enc_{jg['id']}")
                
                updates.append({
                    "id": jg["id"], "rodada": jg["rodada"], "data_texto": jg["data_texto"], "hora": jg["hora"],
                    "home": jg["home"], "away": jg["away"],
                    "tipo": "Anterior" if finalizado else "Próxima",
                    "score_home": r_h if finalizado else "-", "score_away": r_a if finalizado else "-"
                })
                st.divider()
                
            if st.form_submit_button("🔔 Salvar Resultados da Rodada", use_container_width=True):
                pd.DataFrame(updates).to_csv(ARQUIVO_JOGOS, index=False)
                st.success("Placar consolidado e atualizado no ranking!")
                st.rerun()
