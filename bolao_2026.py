import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(page_title="Bolão Brasileirão 2026", page_icon="⚽", layout="wide")

# Estilização Premium Premium (Estilo Dark/Sports)
st.markdown("""
    <style>
        html, body, [class*="css"] { background-color: #0b0f19; color: #ffffff; }
        .main { background-color: #0b0f19; }
        h1, h2, h3 { color: #ffffff; font-weight: 800; }
        
        /* Cartão de Classificação */
        .ranking-card {
            background: linear-gradient(135deg, #1e293b, #0f172a);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .ranking-pos { font-size: 24px; font-weight: 900; color: #38bdf8; }
        .ranking-nome { font-size: 18px; font-weight: bold; color: #ffffff; }
        .ranking-pontos { font-size: 22px; font-weight: 900; color: #4ade80; }
        
        /* Bloco de Match/Jogo */
        .match-box {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            text-align: center;
        }
        .team-name { font-size: 16px; font-weight: bold; color: #f1f5f9; }
        .vs-label { color: #94a3b8; font-weight: bold; margin: 0 10px; }
        
        /* Badge de Regras */
        .rule-box {
            background-color: #111827;
            border-left: 4px solid #3b82f6;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# BANCO DE DADOS LOCAL (CSVs AUTOMÁTICOS)
# ============================================================
ARQUIVO_JOGOS = "jogos_2026.csv"
ARQUIVO_PALPITES = "palpites_2026.csv"

# Inicializar jogos padrões da Rodada 1 se não existirem
if not os.path.exists(ARQUIVO_JOGOS):
    jogos_iniciais = [
        {"id": 1, "rodada": 1, "home": "Flamengo", "away": "Palmeiras", "score_home": "-", "score_away": "-"},
        {"id": 2, "rodada": 1, "home": "São Paulo", "away": "Corinthians", "score_home": "-", "score_away": "-"},
        {"id": 3, "rodada": 1, "home": "Atlético-MG", "away": "Cruzeiro", "score_home": "-", "score_away": "-"},
        {"id": 4, "rodada": 1, "home": "Botafogo", "away": "Fluminense", "score_home": "-", "score_away": "-"},
        {"id": 5, "rodada": 1, "home": "Internacional", "away": "Grêmio", "score_home": "-", "score_away": "-"},
        {"id": 6, "rodada": 2, "home": "Palmeiras", "away": "São Paulo", "score_home": "-", "score_away": "-"},
        {"id": 7, "rodada": 2, "home": "Corinthians", "away": "Flamengo", "score_home": "-", "score_away": "-"},
    ]
    pd.DataFrame(jogos_iniciais).to_csv(ARQUIVO_JOGOS, index=False)

if not os.path.exists(ARQUIVO_PALPITES):
    pd.DataFrame(columns=["usuario", "jogo_id", "palpite_home", "palpite_away"]).to_csv(ARQUIVO_PALPITES, index=False)

# Carregadores de dados estáveis
def carregar_jogos(): return pd.read_csv(ARQUIVO_JOGOS)
def carregar_palpites(): return pd.read_csv(ARQUIVO_PALPITES)

# ============================================================
# MOTOR DE REGRAS E CÁLCULO DE PONTOS
# ============================================================
def calcular_pontos(p_home, p_away, r_home, r_away):
    # Se o jogo não aconteceu ainda, não pontua
    if str(r_home) == "-" or str(r_away) == "-":
        return 0
    try:
        ph, pa, rh, ra = int(p_home), int(p_away), int(r_home), int(r_away)
    except:
        return 0
        
    # 1. Placar Exato = 10 pontos
    if ph == rh and pa == ra:
        return 10
        
    # 2. Acertou Vencedor/Empate mas errou placar = 5 pontos
    saldo_palpite = ph - pa
    saldo_real = rh - ra
    
    if (saldo_palpite > 0 and saldo_real > 0) or (saldo_palpite < 0 and saldo_real < 0) or (saldo_palpite == 0 and saldo_real == 0):
        return 5
        
    return 0

# ============================================================
# SIDEBAR - LOGIN / CONTROLE DE AMIGOS
# ============================================================
with st.sidebar:
    st.header("👤 Quem está jogando?")
    palpites_df = carregar_palpites()
    usuarios_existentes = sorted(list(palpites_df["usuario"].dropna().unique()))
    
    modo_usuario = st.radio("Selecione:", ["Escolher perfil existente", "Cadastrar novo amigo"])
    
    if modo_usuario == "Cadastrar novo amigo" or not usuarios_existentes:
        nome_usuario = st.text_input("Nome do Amigo(a):").strip()
        if st.button("Criar Perfil") and nome_usuario:
            if nome_usuario not in usuarios_existentes:
                st.success(f"Perfil {nome_usuario} pronto!")
                st.session_state["user_atual"] = nome_usuario
            else:
                st.warning("Esse nome já está no bolão.")
    else:
        nome_usuario = st.selectbox("Selecione seu nome:", usuarios_existentes)
        st.session_state["user_atual"] = nome_usuario

    st.divider()
    st.subheader("🛠️ Área do Administrador")
    admin_mode = st.checkbox("Ativar Modo Admin (Lançar Resultados)")

user_ativo = st.session_state.get("user_atual", "Convidado")

# ============================================================
# CONTEÚDO PRINCIPAL - ABAS DO DESIGN (DA COPA style)
# ============================================================
st.title("🏆 Bolão Brasileirão 2026")
st.markdown(f"Você está logado como: **{user_ativo}**")

aba_ranking, aba_palpites, aba_admin, aba_regras = st.tabs([
    "👑 Classificação Geral", 
    "⚽ Meus Palpites", 
    "⚙️ Modo Admin (Jogos)", 
    "📜 Regras de Pontos"
])

# ----------- ABA 1: RANKING GERAL -----------
with aba_ranking:
    st.subheader("Leaderboard do Bolão")
    df_jogos = carregar_jogos()
    df_palpites = carregar_palpites()
    
    if df_palpites.empty:
        st.info("Nenhum palpite registrado ainda. Vá para a aba 'Meus Palpites'!")
    else:
        # Dicionário para computar pontos
        lista_usuarios = df_palpites["usuario"].unique()
        pontuacao_amigos = []
        
        for user in lista_usuarios:
            total_pontos = 0
            palpites_user = df_palpites[df_palpites["usuario"] == user]
            
            for _, palpite in palpites_user.iterrows():
                jogo_real = df_jogos[df_jogos["id"] == palpite["jogo_id"]]
                if not jogo_real.empty:
                    rh = jogo_real.iloc[0]["score_home"]
                    ra = jogo_real.iloc[0]["score_away"]
                    total_pontos += calcular_pontos(palpite["palpite_home"], palpite["palpite_away"], rh, ra)
            
            pontuacao_amigos.append({"Amigo": user, "Pontos": total_pontos})
            
        ranking_final = pd.DataFrame(pontuacao_amigos).sort_values(by="Pontos", ascending=False).reset_index(drop=True)
        
        # Renderização visual bonita
        for index, row in ranking_final.iterrows():
            posicao = index + 1
            st.markdown(f"""
                <div class="ranking-card">
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <span class="ranking-pos">#{posicao}</span>
                        <span class="ranking-nome">{row['Amigo']}</span>
                    </div>
                    <span class="ranking-pontos">{row['Pontos']} pts</span>
                </div>
            """, unsafe_allow_html=True)

# ----------- ABA 2: MEUS PALPITES -----------
with aba_palpites:
    if user_ativo == "Convidado":
        st.warning("Por favor, crie ou selecione um perfil na barra lateral antes de palpitar.")
    else:
        df_jogos = carregar_jogos()
        df_palpites = carregar_palpites()
        
        rodada_atual = st.selectbox("Escolha a Rodada para palpitar:", sorted(df_jogos["rodada"].unique()))
        jogos_da_rodada = df_jogos[df_jogos["rodada"] == rodada_atual]
        
        st.write("Insira seus palpites abaixo:")
        
        with st.form("form_palpites"):
            novos_palpites = []
            for _, jogo in jogos_da_rodada.iterrows():
                # Verifica se o usuário já tinha um palpite anterior salvo para esse jogo
                palpite_anterior = df_palpites[(df_palpites["usuario"] == user_ativo) & (df_palpites["jogo_id"] == jogo["id"])]
                
                val_home = int(palpite_anterior.iloc[0]["palpite_home"]) if not palpite_anterior.empty else 0
                val_away = int(palpite_anterior.iloc[0]["palpite_away"]) if not palpite_anterior.empty else 0
                
                st.markdown(f'<div class="match-box">', unsafe_allow_html=True)
                col_h, col_in1, col_vs, col_in2, col_a = st.columns([3, 1, 1, 1, 3])
                
                with col_h: st.markdown(f"<br><span class='team-name'>{jogo['home']}</span>", unsafe_allow_html=True)
                with col_in1: p_h = st.number_input("", min_value=0, max_value=20, value=val_home, key=f"p_h_{jogo['id']}")
                with col_vs: st.markdown("<br><span class='vs-label'>X</span>", unsafe_allow_html=True)
                with col_in2: p_a = st.number_input("", min_value=0, max_value=20, value=val_away, key=f"p_a_{jogo['id']}")
                with col_a: st.markdown(f"<br><span class='team-name'>{jogo['away']}</span>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                novos_palpites.append({"usuario": user_ativo, "jogo_id": jogo["id"], "palpite_home": p_h, "palpite_away": p_a})
                
            if st.form_submit_button("💾 Salvar Meus Palpites", use_container_width=True):
                # Limpa palpites antigos dessa rodada do usuário e insere os novos
                ids_rodada = jogos_da_rodada["id"].tolist()
                df_palpites = df_palpites[~((df_palpites["usuario"] == user_ativo) & (df_palpites["jogo_id"].isin(ids_rodada)))]
                
                df_novos = pd.DataFrame(novos_palpites)
                df_final_palpites = pd.concat([df_palpites, df_novos], ignore_index=True)
                df_final_palpites.to_csv(ARQUIVO_PALPITES, index=False)
                st.success("Palpites gravados com sucesso! Boa sorte!")
                st.rerun()

# ----------- ABA 3: MODO ADMIN (GERENCIAR RESULTADOS REAIS) -----------
with aba_admin:
    if not admin_mode:
        st.info("Para lançar os placares reais das partidas e atualizar o ranking dos seus amigos, marque a caixinha 'Ativar Modo Admin' na barra lateral.")
    else:
        st.subheader("Painel de Controle de Resultados Reais")
        df_jogos = carregar_jogos()
        
        rodada_admin = st.selectbox("Lançar placar para a Rodada:", sorted(df_jogos["rodada"].unique()), key="sb_admin")
        jogos_admin = df_jogos[df_jogos["rodada"] == rodada_admin]
        
        with st.form("form_admin"):
            lista_updates = []
            for _, jogo in jogos_admin.iterrows():
                # Formata os valores padrões se já existirem
                init_h = int(jogo["score_home"]) if str(jogo["score_home"]) != "-" else 0
                init_a = int(jogo["score_away"]) if str(jogo["score_away"]) != "-" else 0
                
                col_h, col_in1, col_vs, col_in2, col_a, col_status = st.columns([3, 1, 1, 1, 3, 2])
                with col_h: st.markdown(f"<br><strong>{jogo['home']}</strong>", unsafe_allow_html=True)
                with col_in1: r_h = st.number_input("", min_value=0, max_value=20, value=init_h, key=f"r_h_{jogo['id']}")
                with col_vs: st.markdown("<br><span>X</span>", unsafe_allow_html=True)
                with col_in2: r_a = st.number_input("", min_value=0, max_value=20, value=init_a, key=f"r_a_{jogo['id']}")
                with col_a: st.markdown(f"<br><strong>{jogo['away']}</strong>", unsafe_allow_html=True)
                with col_status:
                    ja_ocorreu = st.checkbox("Encerrado/Confirmado", value=(str(jogo["score_home"]) != "-"), key=f"encerrado_{jogo['id']}")
                
                lista_updates.append({
                    "id": jogo["id"], "rodada": jogo["rodada"], "home": jogo["home"], "away": jogo["away"],
                    "score_home": r_h if ja_ocorreu else "-", "score_away": r_a if ja_ocorreu else "-"
                })
                st.divider()
                
            if st.form_submit_button("🔔 Atualizar Resultados Oficiais e Computar Ranking", use_container_width=True):
                df_jogos_atualizados = carregar_jogos()
                for up in lista_updates:
                    df_jogos_atualizados.loc[df_jogos_atualizados["id"] == up["id"], "score_home"] = up["score_home"]
                    df_jogos_atualizados.loc[df_jogos_atualizados["id"] == up["id"], "score_away"] = up["score_away"]
                
                df_jogos_atualizados.to_csv(ARQUIVO_JOGOS, index=False)
                st.success("Resultados oficiais atualizados! O ranking foi recalculado.")
                st.rerun()

# ----------- ABA 4: REGRAS DE PONTOS -----------
with aba_regras:
    st.subheader("📜 Critérios de Pontuação")
    st.markdown("""
    Para deixar a disputa justa e emocionante, o cálculo de pontos do nosso bolão segue a tabela abaixo:
    
    <div class="rule-box">
        🟩 <strong>10 Pontos (Placar Exato):</strong> Você acertou em cheio a quantidade de gols de ambas as equipes.<br>
        <em>Exemplo: Seu Palpite: 2 x 1 | Resultado Real: 2 x 1</em>
    </div>
    <div class="rule-box">
        🟨 <strong>5 Pontos (Acerto de Tendência):</strong> Você acertou qual time ganhou ou se foi empate, mas errou o placar exato.<br>
        <em>Exemplo: Seu Palpite: 1 x 0 (Vitória do Home) | Resultado Real: 3 x 1 (Vitória do Home)</em>
    </div>
    <div class="rule-box">
        🟥 <strong>0 Pontos (Erro Total):</strong> Você errou completamente o vencedor ou o empate do jogo.<br>
        <em>Exemplo: Seu Palpite: 0 x 2 | Resultado Real: 1 x 1</em>
    </div>
    """, unsafe_allow_html=True)