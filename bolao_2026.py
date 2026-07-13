import streamlit as st
import pandas as pd
import os

# Configuração de ecrã limpo focado em Mobile/Web
st.set_page_config(page_title="Da Copa - Brasileirão 2026", page_icon="⚽", layout="centered")

# Injeta meta tag para tentar bloquear o tradutor de quebrar o app
st.markdown('<meta name="google" content="notranslate" />', unsafe_allow_html=True)

# ============================================================
# ESTILIZAÇÃO COMPLETA - ESTILO "DA COPA" EM MODO CLARO
# ============================================================
st.markdown("""
    <style>
        html, body, .stApp, .main, [data-testid="stAppViewBlockContainer"] {
            background-color: #f8fafc !important;
            color: #1e293b !important;
        }
        [data-testid="stHeader"] { display: none !important; }
        
        .saudacao-title { font-size: 26px; font-weight: 800; color: #0f172a; margin-bottom: 2px; }
        .saudacao-sub { font-size: 16px; color: #64748b; margin-bottom: 20px; }
        
        /* Cartão do Grupo Ativo */
        .grupo-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 18px;
            margin-bottom: 20px;
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
        
        /* Lista do Ranking */
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
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background-color: #e2e8f0;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #475569;
            margin-right: 12px;
        }
        
        /* Cartões de Jogos */
        .date-divider {
            font-size: 13px;
            font-weight: 800;
            color: #64748b;
            text-transform: uppercase;
            margin: 20px 0 10px 0;
        }
        .match-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.01);
        }
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
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# GERENCIADOR DE BANCO DE DADOS (CSVs)
# ============================================================
ARQUIVO_GRUPOS = "bolao_grupos.csv"
ARQUIVO_JOGOS = "bolao_jogos.csv"
ARQUIVO_PALPITES = "bolao_palpites.csv"

# Inicializa grupos padrões se não existirem
if not os.path.exists(ARQUIVO_GRUPOS):
    pd.DataFrame({"nome_grupo": ["Brasileirão Família", "Amigos do Futebol"]}).to_csv(ARQUIVO_GRUPOS, index=False)

if not os.path.exists(ARQUIVO_JOGOS):
    jogos_iniciais = [
        {"id": 1, "rodada": 1, "data_texto": "Terça-feira, 14 de Julho de 2026", "hora": "16:00", "tipo": "Anterior", "home": "Flamengo", "away": "Palmeiras", "score_home": "2", "score_away": "1"},
        {"id": 2, "rodada": 1, "data_texto": "Terça-feira, 14 de Julho de 2026", "hora": "19:30", "tipo": "Anterior", "home": "São Paulo", "away": "Corinthians", "score_home": "0", "score_away": "0"},
        {"id": 3, "rodada": 1, "data_texto": "Quarta-feira, 15 de Julho de 2026", "hora": "16:00", "tipo": "Próxima", "home": "Atlético-MG", "away": "Cruzeiro", "score_home": "-", "score_away": "-"},
        {"id": 4, "rodada": 1, "data_texto": "Quarta-feira, 15 de Julho de 2026", "hora": "21:45", "tipo": "Próxima", "home": "Botafogo", "away": "Fluminense", "score_home": "-", "score_away": "-"}
    ]
    pd.DataFrame(jogos_iniciais).to_csv(ARQUIVO_JOGOS, index=False)

if not os.path.exists(ARQUIVO_PALPITES):
    pd.DataFrame(columns=["grupo", "usuario", "jogo_id", "palpite_home", "palpite_away"]).to_csv(ARQUIVO_PALPITES, index=False)

def ler_grupos(): return pd.read_csv(ARQUIVO_GRUPOS)["nome_grupo"].tolist()
def ler_jogos(): return pd.read_csv(ARQUIVO_JOGOS)
def ler_palpites(): return pd.read_csv(ARQUIVO_PALPITES)

def calcular_pontos(p_home, p_away, r_home, r_away):
    if str(r_home) == "-" or str(r_away) == "-": return 0
    try:
        ph, pa, rh, ra = int(p_home), int(p_away), int(r_home), int(r_away)
    except: return 0
    if ph == rh and pa == ra: return 10
    if ((ph - pa > 0 and rh - ra > 0) or (ph - pa < 0 and rh - ra < 0) or (ph - pa == 0 and rh - ra == 0)): return 5
    return 0

# ============================================================
# CONTROLADORES DE ESTADO DA SESSÃO (SESSION STATE)
# ============================================================
if "aba_atual" not in st.session_state: st.session_state["aba_atual"] = "🏠 Início"
if "grupo_selecionado" not in st.session_state: st.session_state["grupo_selecionado"] = ler_grupos()[0]
if "user_atual" not in st.session_state: st.session_state["user_atual"] = "Marcelo"

grupo_atual = st.session_state["grupo_selecionado"]

# ============================================================
# SIDEBAR - SELEÇÃO DE AMIGOS E MODOS
# ============================================================
with st.sidebar:
    st.header("👤 Jogador Ativo")
    df_p_temp = ler_palpites()
    
    # Filtra participantes que já pertencem a este bolão ativo
    participantes_do_grupo = ["Marcelo"]
    if not df_p_temp.empty and "grupo" in df_p_temp.columns:
        usuarios_f = df_p_temp[df_p_temp["grupo"] == grupo_atual]["usuario"].dropna().unique().tolist()
        for u in usuarios_f:
            if u not in participantes_do_grupo: participantes_do_grupo.append(u)
            
    st.session_state["user_atual"] = st.selectbox("Você está jogando como:", sorted(participantes_do_grupo))
    user_ativo = st.session_state["user_atual"]
    
    st.divider()
    st.header("➕ Entrar/Adicionar Amigo")
    novo_amigo = st.text_input("Nome do Amigo(a):").strip()
    if st.button("Adicionar Convidado ao Grupo") and novo_amigo:
        st.session_state["user_atual"] = novo_amigo
        st.success(f"{novo_amigo} entrou no grupo {grupo_atual}!")
        st.rerun()
        
    st.divider()
    modo_admin = st.checkbox("⚙️ Modo Administrador (Resultados)")

# ============================================================
# NAVEGAÇÃO SUPERIOR ROBUSTA (SUBSTITUTO INFALÍVEL DAS TABS)
# ============================================================
c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
if c_nav1.button("🏠 Início", use_container_width=True): st.session_state["aba_atual"] = "🏠 Início"
if c_nav2.button("📊 Ranking", use_container_width=True): st.session_state["aba_atual"] = "📊 Ranking"
if c_nav3.button("📅 Partidas", use_container_width=True): st.session_state["aba_atual"] = "📅 Partidas"
if c_nav4.button("⚙️ Admin", use_container_width=True): st.session_state["aba_atual"] = "⚙️ Admin"

st.divider()
aba_ativa = st.session_state["aba_atual"]

# ============================================================
# CÁLCULO DE PONTOS DINÂMICO PARA O GRUPO ATIVO
# ============================================================
df_jogos_c = ler_jogos()
df_palpites_c = ler_palpites()

pontos_voce = 0
posicao_voce = 1
ranking_usuarios = []

# Garante que a lista de competidores inclua todos que apostaram no grupo atual
competidores = participantes_do_grupo.copy()

if not df_palpites_c.empty:
    df_p_grupo = df_palpites_c[df_palpites_c["grupo"] == grupo_atual]
    for comp in competidores:
        total_pts = 0
        p_comp = df_p_grupo[df_p_grupo["usuario"] == comp]
        for _, palp in p_comp.iterrows():
            match_r = df_jogos_c[df_jogos_c["id"] == palp["jogo_id"]]
            if not match_r.empty:
                total_pts += calcular_pontos(palp["palpite_home"], palp["palpite_away"], match_r.iloc[0]["score_home"], match_r.iloc[0]["score_away"])
        ranking_usuarios.append({"usuario": comp, "pontos": total_pts})
        
    df_ranking_final = pd.DataFrame(ranking_usuarios).sort_values(by="pontos", ascending=False).reset_index(drop=True)
    if not df_ranking_final.empty:
        idx_v = df_ranking_final[df_ranking_final["usuario"] == user_ativo].index
        if len(idx_v) > 0:
            posicao_voce = idx_v[0] + 1
            pontos_voce = df_ranking_final.loc[idx_v[0], "pontos"]
else:
    df_ranking_final = pd.DataFrame([{"usuario": user_ativo, "pontos": 0}])

# ============================================================
# CONTROLO DE TELAS / VISÕES DO APLICATIVO
# ============================================================

# ----------- TELA 1: INÍCIO -----------
if aba_ativa == "🏠 Início":
    st.markdown(f'<div class="saudacao-title">Olá, {user_ativo}!</div>', unsafe_allow_html=True)
    st.markdown('<div class="saudacao-sub">Gerencie ou selecione seus grupos de apostas:</div>', unsafe_allow_html=True)
    
    # SEÇÃO PARA CRIAR UM NOVO BOLÃO DO ZERO (REQUISITO COMPLETO)
    with st.expander("➕ CRIAR UM NOVO BOLÃO COM MEU NOME", expanded=False):
        novo_nome_bolao = st.text_input("Digite o Nome do seu Novo Bolão (Ex: Bolão do Marcelo 2026):").strip()
        if st.button("Confirmar e Salvar Novo Bolão"):
            if novo_nome_bolao:
                lista_g_existentes = ler_grupos()
                if novo_nome_bolao not in lista_g_existentes:
                    df_novos_g = pd.DataFrame({"nome_grupo": lista_g_existentes + [novo_nome_bolao]})
                    df_novos_g.to_csv(ARQUIVO_GRUPOS, index=False)
                    st.session_state["grupo_selected"] = novo_nome_bolao
                    st.success(f"🎉 O Bolão '{novo_nome_bolao}' foi criado com sucesso! Agora seus amigos já podem entrar nele.")
                    st.rerun()
                else: st.warning("Um bolão com esse nome já existe.")
    
    # SEÇÃO PARA SELECIONAR EM QUAL BOLÃO ENTRAR / VISUALIZAR
    st.markdown("### Selecione o Bolão Ativo:")
    lista_para_escolha = ler_grupos()
    idx_g_def = lista_para_escolha.index(grupo_atual) if grupo_atual in lista_para_escolha else 0
    grupo_escolhido = st.selectbox("Escolha qual bolão quer jogar agora:", lista_para_escolha, index=idx_g_def)
    if grupo_escolhido != grupo_atual:
        st.session_state["grupo_selecionado"] = grupo_escolhido
        st.rerun()

    # Exibição do Cartão do Grupo Atualizado
    st.markdown(f"""
        <div class="grupo-card">
            <span class="badge-posicao">{posicao_voce}º lugar</span>
            <div style="font-weight: 800; font-size: 17px; color: #0f172a;">🏆 {grupo_atual}</div>
            <div style="font-size: 13px; color: #64748b; margin-top: 4px;">Campeonato Brasileiro 2026 · {len(competidores)} participantes</div>
            <div style="font-size: 16px; font-weight: bold; color: #00b25c; margin-top: 14px;">Seus Pontos: {pontos_voce} pts</div>
        </div>
    """, unsafe_allow_html=True)

# ----------- TELA 2: RANKING -----------
elif aba_ativa == "📊 Ranking":
    st.markdown(f"## Classificação: {grupo_atual}")
    st.caption("A tabela atualiza de forma automática assim que novos placares oficiais são lançados.")
    
    for idx, row in df_ranking_final.iterrows():
        is_voce = (row["usuario"] == user_ativo)
        classe_css = "voce" if is_voce else ""
        cor_pontos = "#00b25c" if is_voce else "#1e293b"
        
        st.markdown(f"""
            <div class="row-ranking {classe_css}">
                <div style="display:flex; align-items:center;">
                    <span style="font-weight:900; margin-right:15px; color:{cor_pontos};">#{idx + 1}</span>
                    <div class="player-avatar">{row['usuario'][0].upper()}</div>
                    <div>
                        <span style="font-weight:700;">{row['usuario']} {"(Você)" if is_voce else ""}</span>
                        <span style="font-size:12px; color:#94a3b8; display:block;">@{row['usuario'].lower()}2026</span>
                    </div>
                </div>
                <div class="points-display" style="color:{cor_pontos};">{row['pontos']} pts</div>
            </div>
        """, unsafe_allow_html=True)

# ----------- TELA 3: PARTIDAS (SALVAR PALPITES DIRETO) -----------
elif aba_ativa == "📅 Partidas":
    st.markdown(f"## Palpites de {user_ativo} para {grupo_atual}")
    
    df_jogos = ler_jogos()
    df_palpites = ler_palpites()
    
    filtro_status = st.radio("Filtrar Jogos:", ["Próximas Partidas (Dê seus Palpites)", "Resultados Anteriores"], horizontal=True)
    tipo_busca = "Próxima" if "Próximas" in filtro_status else "Anterior"
    
    jogos_f = df_jogos[df_jogos["tipo"] == tipo_busca]
    
    if jogos_f.empty:
        st.info("Nenhum jogo cadastrado para esta categoria.")
    else:
        datas_f = jogos_f["data_texto"].unique()
        for d_box in datas_f:
            st.markdown(f'<div class="date-divider">📅 {d_box}</div>', unsafe_allow_html=True)
            jogos_dia = jogos_f[jogos_f["data_texto"] == d_box]
            
            for _, jg in jogos_dia.iterrows():
                # Tenta puxar palpite já salvo anteriormente para não resetar o campo
                p_salvo = df_palpites[(df_palpites["grupo"] == grupo_atual) & (df_palpites["usuario"] == user_ativo) & (df_palpites["jogo_id"] == jg["id"])]
                init_h = int(p_salvo.iloc[0]["palpite_home"]) if not p_salvo.empty else 0
                init_a = int(p_salvo.iloc[0]["palpite_away"]) if not p_salvo.empty else 0
                
                # Exibição do Card
                placar_pill = f"{jg['score_home']} : {jg['score_away']}" if tipo_busca == "Anterior" else "vs"
                st.markdown(f"""
                    <div class="match-card">
                        <div style="font-size:12px; color:#94a3b8; margin-bottom:8px;">⏱️ {jg['hora']} · Rodada {jg['rodada']}</div>
                        <div class="match-row-teams">
                            <div class="team-block">{jg['home']}</div>
                            <div class="score-pill">{placar_pill}</div>
                            <div class="team-block right">{jg['away']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Se for jogo futuro, exibe o form direto para digitação sem travar
                if tipo_busca == "Próxima":
                    with st.form(key=f"form_palpite_{jg['id']}"):
                        c_in1, c_in2 = st.columns(2)
                        p_h = c_in1.number_input(f"Gols {jg['home']}", 0, 15, init_h, key=f"in_h_{jg['id']}")
                        p_a = c_in2.number_input(f"Gols {jg['away']}", 0, 15, init_a, key=f"in_a_{jg['id']}")
                        
                        if st.form_submit_button(f"💾 Confirmar Palpite ({jg['home']} x {jg['away']})"):
                            # Remove duplicados antigos e adiciona o novo registro limpo
                            df_p_atual = ler_palpites()
                            df_p_atual = df_p_atual[~((df_p_atual["grupo"] == grupo_atual) & (df_p_atual["usuario"] == user_ativo) & (df_p_atual["jogo_id"] == jg["id"]))]
                            
                            linha_nova = pd.DataFrame([{"grupo": grupo_atual, "usuario": user_ativo, "jogo_id": jg["id"], "palpite_home": p_h, "palpite_away": p_a}])
                            df_p_final = pd.concat([df_p_atual, linha_nova], ignore_index=True)
                            df_p_final.to_csv(ARQUIVO_PALPITES, index=False)
                            st.success("Palpite registrado com sucesso!")
                            st.rerun()

# ----------- TELA 4: ADMIN (LANÇAR OS RESULTADOS REAIS) -----------
elif aba_ativa == "⚙️ Admin":
    if not modo_admin:
        st.info("Ative a opção 'Modo Administrador' na barra lateral esquerda para poder fechar rodadas e lançar os placares reais.")
    else:
        st.subheader("Lançador de Placar Oficial do Campeonato")
        df_jogos_adm = ler_jogos()
        
        with st.form("form_consolidar_admin"):
            novos_dados_jogos = []
            for _, jg in df_jogos_adm.iterrows():
                st.write(f"🏟️ **{jg['home']} x {jg['away']}** ({jg['data_texto']})")
                c_h, c_a, c_status = st.columns(3)
                
                init_h = int(jg["score_home"]) if str(jg["score_home"]) != "-" else 0
                init_a = int(jg["score_away"]) if str(jg["score_away"]) != "-" else 0
                
                res_h = c_h.number_input("Gols Casa", 0, 15, init_h, key=f"adm_g_h_{jg['id']}")
                res_a = c_a.number_input("Gols Fora", 0, 15, init_a, key=f"adm_g_a_{jg['id']}")
                encerrado = c_status.checkbox("Partida Encerrada", value=(str(jg["score_home"]) != "-"), key=f"adm_c_{jg['id']}")
                
                novos_dados_jogos.append({
                    "id": jg["id"], "rodada": jg["rodada"], "data_texto": jg["data_texto"], "hora": jg["hora"],
                    "home": jg["home"], "away": jg["away"],
                    "tipo": "Anterior" if encerrado else "Próxima",
                    "score_home": res_h if encerrado else "-", "score_away": res_a if encerrado else "-"
                })
                st.divider()
                
            if st.form_submit_button("🔔 Publicar Placares Oficiais e Atualizar Rankings"):
                pd.DataFrame(novos_dados_jogos).to_csv(ARQUIVO_JOGOS, index=False)
                st.success("Placares atualizados! O ranking de todos os grupos foi recalculado.")
                st.rerun()
