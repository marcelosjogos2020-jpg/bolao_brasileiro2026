import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página para emular dispositivo móvel/web limpo
st.set_page_config(page_title="Da Copa - Brasileirão 2026", page_icon="⚽", layout="centered")

# ============================================================
# INTERFACE DE ESTILO - RÉPLICA FIEL DO "DA COPA" (LIGHT MODE)
# ============================================================
st.markdown("""
    <style>
        /* Forçar Modo Claro Absoluto */
        html, body, .stApp, .main {
            background-color: #f8fafc !important;
            color: #1e293b !important;
        }
        
        /* Esconder elementos nativos do Streamlit */
        [data-testid="stHeader"] { display: none !important; }
        
        /* Cabeçalho de Saudação */
        .saudacao-title { font-size: 26px; font-weight: 800; color: #0f172a; margin-bottom: 2px; }
        .saudacao-sub { font-size: 16px; color: #64748b; margin-bottom: 20px; }
        
        /* Botões Rápidos da Home */
        .action-container { display: flex; gap: 12px; margin-bottom: 25px; }
        .action-card {
            background-color: #f1f5f9;
            border-radius: 16px;
            padding: 16px;
            flex: 1;
            text-align: center;
            font-weight: bold;
            font-size: 14px;
            color: #334155;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        
        /* Cartão de Grupo de Apostas */
        .grupo-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
        }
        .badge-posicao {
            background-color: #e2fbe8;
            color: #00b25c;
            font-size: 12px;
            font-weight: 800;
            padding: 4px 8px;
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
        
        /* Estilização Customizada para as Abas de Menu */
        div[data-testid="stTabs"] button {
            font-size: 14px !important;
            font-weight: bold !important;
            color: #64748b !important;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #00b25c !important;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# SISTEMA DE DADOS COM VERIFICAÇÃO AUTOMÁTICA DE CONFLITOS
# ============================================================
ARQUIVO_JOGOS = "jogos_2026.csv"
ARQUIVO_PALPITES = "palpites_2026.csv"

# Força o reset se o arquivo antigo não tiver a coluna "tipo" do novo layout
forçar_recriacao = False
if os.path.exists(ARQUIVO_JOGOS):
    try:
        df_teste = pd.read_csv(ARQUIVO_JOGOS)
        if "tipo" not in df_teste.columns:
            forçar_recriacao = True
    except:
        forçar_recriacao = True

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

# Sistema de cálculo de pontos
def calcular_pontos(p_home, p_away, r_home, r_away):
    if str(r_home) == "-" or str(r_away) == "-": return 0
    ph, pa, rh, ra = int(p_home), int(p_away), int(r_home), int(r_away)
    if ph == rh and pa == ra: return 10
    if ((ph - pa > 0 and rh - ra > 0) or (ph - pa < 0 and rh - ra < 0) or (ph - pa == 0 and rh - ra == 0)): return 5
    return 0

# ============================================================
# BARRA LATERAL
# ============================================================
with st.sidebar:
    st.header("👤 Perfil Ativo")
    user_ativo = st.text_input("Seu Nome no Bolão:", value="Marcelo").strip()
    username_mock = f"@{user_ativo.lower()}1000"
    st.caption(f"Seu usuário no app: {username_mock}")
    st.divider()
    modo_admin = st.checkbox("⚙️ Ativar Modo Administrador")

# ============================================================
# NAVEGAÇÃO POR ABAS (ESTILO DA COPA)
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
    
    st.markdown("""
        <div class="action-container">
            <div class="action-card">➕<br>Criar Bolão</div>
            <div class="action-card">👤<br>Entrar em Bolão</div>
            <div class="action-card">📖<br>Regras</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Seus Grupos")
    st.markdown(f"""
        <div class="grupo-card">
            <span class="badge-posicao">2º lugar</span>
            <div style="font-weight: 800; font-size: 16px; color: #0f172a;">Bolão Brasileirão 2026 - Família</div>
            <div style="font-size: 13px; color: #64748b; margin-top: 4px;">Campeonato Brasileiro • 2 membros</div>
            <div style="font-size: 15px; font-weight: bold; color: #00b25c; margin-top: 12px;">850 pts</div>
        </div>
    """, unsafe_allow_html=True)

# ----------- 2. ABA CLASSIFICAÇÃO -----------
with menu_classificacao:
    st.markdown("## Classificação")
    
    st.markdown(f"""
        <div class="row-ranking">
            <div style="display:flex; align-items:center;">
                <span style="font-weight:900; margin-right:15px; color:#64748b;">1</span>
                <div class="player-avatar">W</div>
                <div>
                    <span class="player-name">Wellington Menezes</span>
                    <span class="player-username">@wmenezes</span>
                </div>
            </div>
            <div class="points-display">966<span class="points-var">+24</span></div>
        </div>
        
        <div class="row-ranking voce">
            <div style="display:flex; align-items:center;">
                <span style="font-weight:900; margin-right:15px; color:#00b25c;">2</span>
                <div class="player-avatar" style="background-color:#e6f4ea; color:#00b25c;">M</div>
                <div>
                    <span class="player-name">{user_ativo} (Você)</span>
                    <span class="player-username">{username_mock}</span>
                </div>
            </div>
            <div class="points-display" style="color:#00b25c;">850<span class="points-var">+10</span></div>
        </div>
    """, unsafe_allow_html=True)

# ----------- 3. ABA PARTIDAS -----------
with menu_partidas:
    st.markdown("## Partidas")
    
    df_jogos = carregar_jogos()
    df_palpites = carregar_palpites()
    
    sub_filtros = st.radio("Filtros:", ["Anteriores", "Ao Vivo (0)", "Próximas"], horizontal=True, label_visibility="collapsed")
    
    filtro_tipo = "Anterior" if sub_filtros == "Anteriores" else "Próxima"
    jogos_filtrados = df_jogos[df_jogos["tipo"] == filtro_tipo]
    
    datas_unicas = jogos_filtrados["data_texto"].unique()
    
    if len(jogos_filtrados) == 0:
        st.info(f"Nenhuma partida marcada como '{sub_filtros}' no momento.")
    
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
                
                with st.expander(f"📝 Dar palpite para {jogo['home']} x {jogo['away']}", expanded=True):
                    c_in1, c_in2, c_btn = st.columns([1, 1, 2])
                    val_h = c_in1.number_input(f"{jogo['home']}:", 0, 15, init_h, key=f"user_h_{jogo['id']}")
                    val_a = c_in2.number_input(f"{jogo['away']}:", 0, 15, init_a, key=f"user_a_{jogo['id']}")
                    
                    if c_btn.button("Salvar Palpite", key=f"btn_salvar_{jogo['id']}", use_container_width=True):
                        df_palpites = df_palpites[~((df_palpites["usuario"] == user_ativo) & (df_palpites["jogo_id"] == jogo["id"]))]
                        novo_p = pd.DataFrame([{"usuario": user_ativo, "jogo_id": jogo["id"], "palpite_home": val_h, "palpite_away": val_a}])
                        df_final = pd.concat([df_palpites, novo_p], ignore_index=True)
                        df_final.to_csv(ARQUIVO_PALPITES, index=False)
                        st.success("Palpite salvo!")
                        st.rerun()

# ----------- 4. ABA ADMIN (LANÇAR PLACARES REAIS) -----------
with menu_admin:
    if not modo_admin:
        st.info("Ative a opção 'Modo Administrador' na barra lateral para lançar os encerramentos reais das partidas.")
    else:
        st.subheader("Lançador Oficial de Resultados")
        df_jogos = carregar_jogos()
        
        with st.form("painel_admin_form"):
            updates = []
            for _, jg in df_jogos.iterrows():
                st.write(f"⚽ **{jg['home']} x {jg['away']}** ({jg['data_texto']})")
                c_h, c_a, c_status = st.columns(3)
                
                init_h = int(jg["score_home"]) if str(jg["score_home"]) != "-" else 0
                init_a = int(jg["score_away"]) if str(jg["score_away"]) != "-" else 0
                
                r_h = c_h.number_input("Gols Casa", 0, 15, init_h, key=f"adm_h_{jg['id']}")
                r_a = c_a.number_input("Gols Fora", 0, 15, init_a, key=f"adm_a_{jg['id']}")
                finalizado = c_status.checkbox("Encerrado", value=(str(jg["score_home"]) != "-"), key=f"adm_enc_{jg['id']}")
                
                updates.append({
                    "id": jg["id"], "rodada": jg["rodada"], "data_texto": jg["data_texto"], "hora": jg["hora"],
                    "home": jg["home"], "away": jg["away"],
                    "tipo": "Anterior" if finalizado else "Próxima",
                    "score_home": r_h if finalizado else "-", "score_away": r_a if finalizado else "-"
                })
                st.divider()
                
            if st.form_submit_button("🔔 Publicar Placares Oficiais", use_container_width=True):
                pd.DataFrame(updates).to_csv(ARQUIVO_JOGOS, index=False)
                st.success("Resultados oficiais publicados e consolidados com sucesso!")
                st.rerun()
