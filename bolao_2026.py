"""
Dashboard Brasileirão 2026
--------------------------
Aplicação Streamlit para acompanhar:

- Jogos ao vivo
- Calendário e resultados
- Tabela de classificação
- Detalhes dos times
- Artilharia
- Estatísticas e detalhes das partidas

Fonte de dados:
API Futebol — https://www.api-futebol.com.br/

Execução:
streamlit run app.py
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh


# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

st.set_page_config(
    page_title="Brasileirão 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = "https://api.api-futebol.com.br/v1"
FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")

# Atualiza a página a cada 45 segundos.
# Isso é especialmente útil na área de jogos em andamento.
st_autorefresh(interval=45_000, key="atualizacao_automatica")


# ============================================================
# ESTILIZAÇÃO RESPONSIVA
# ============================================================

st.markdown(
    """
    <style>
        :root {
            --verde: #0b8f4d;
            --verde-escuro: #056b38;
            --amarelo: #f8c630;
            --fundo: #f5f7fb;
            --texto: #172033;
            --muted: #6a7487;
            --card: #ffffff;
            --borda: #e7ebf2;
        }

        .stApp {
            background: var(--fundo);
            color: var(--texto);
        }

        [data-testid="stHeader"] {
            background: rgba(0, 0, 0, 0);
        }

        .hero {
            background: linear-gradient(135deg, #056b38, #0b8f4d);
            color: white;
            padding: 28px;
            border-radius: 22px;
            margin-bottom: 22px;
            box-shadow: 0 12px 28px rgba(5, 107, 56, 0.18);
        }

        .hero h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 800;
        }

        .hero p {
            margin: 8px 0 0 0;
            opacity: 0.9;
            font-size: 1rem;
        }

        .status-live {
            display: inline-block;
            background: #ffebee;
            color: #d81b30;
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.4px;
        }

        .status-finished {
            display: inline-block;
            background: #edf7ef;
            color: #16723a;
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 800;
        }

        .status-scheduled {
            display: inline-block;
            background: #fff7df;
            color: #8a5a00;
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 800;
        }

        .match-card {
            background: var(--card);
            border: 1px solid var(--borda);
            border-radius: 18px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(29, 39, 57, 0.04);
        }

        .match-meta {
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 12px;
        }

        .match-teams {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
        }

        .match-team {
            width: 36%;
            font-weight: 750;
            font-size: 15px;
        }

        .match-team.away {
            text-align: right;
        }

        .score {
            min-width: 86px;
            text-align: center;
            background: #f0f3f8;
            border-radius: 12px;
            padding: 8px 10px;
            font-size: 18px;
            font-weight: 900;
        }

        .table-team {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 700;
        }

        .team-logo {
            width: 28px;
            height: 28px;
            object-fit: contain;
        }

        .source-note {
            color: var(--muted);
            font-size: 12px;
            margin-top: 12px;
        }

        @media (max-width: 700px) {
            .hero h1 {
                font-size: 1.55rem;
            }

            .match-team {
                font-size: 13px;
            }

            .score {
                min-width: 64px;
                font-size: 16px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÕES DE APOIO
# ============================================================

def obter_token() -> str:
    """
    Lê o token da API pelo secrets.toml ou variável de ambiente.

    Alternativa via terminal:
    export API_FUTEBOL_TOKEN="SUA_CHAVE"
    """
    token = ""

    try:
        token = st.secrets.get("API_FUTEBOL_TOKEN", "")
    except Exception:
        pass

    if not token:
        token = os.getenv("API_FUTEBOL_TOKEN", "")

    return str(token).strip()


def primeiro_valor(dados: dict[str, Any], *chaves: str, padrao: Any = None) -> Any:
    """Retorna o primeiro valor existente para uma lista de chaves."""
    for chave in chaves:
        if chave in dados and dados[chave] is not None:
            return dados[chave]
    return padrao


def formatar_data(data_iso: Optional[str]) -> str:
    """Converte data ISO para o padrão brasileiro."""
    if not data_iso:
        return "Data a definir"

    try:
        data = datetime.fromisoformat(data_iso.replace("Z", "+00:00"))
        data_local = data.astimezone(FUSO_BRASILIA)
        return data_local.strftime("%d/%m/%Y às %H:%M")
    except (ValueError, TypeError):
        return str(data_iso)


def normalizar_status(status: str) -> tuple[str, str]:
    """
    Retorna:
    - texto amigável do status
    - classe CSS correspondente
    """
    status = (status or "").lower().strip()

    if status in {"andamento", "ao-vivo", "ao_vivo", "live", "em_andamento"}:
        return "● AO VIVO", "status-live"

    if status in {"finalizado", "encerrado", "finished"}:
        return "ENCERRADO", "status-finished"

    if status in {"adiado", "suspensa", "cancelado"}:
        return status.upper(), "status-scheduled"

    return "AGENDADO", "status-scheduled"


# ============================================================
# CLIENTE DA API FUTEBOL
# ============================================================

class APIFutebolClient:
    """
    Cliente simples para a API Futebol.

    Os dados são buscados no backend Streamlit. Portanto,
    a chave da API não é exposta ao navegador do usuário.
    """

    def __init__(self, token: str) -> None:
        self.token = token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            }
        )

    def get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> Any:
        """Executa uma requisição GET e retorna JSON."""
        url = f"{API_BASE_URL}{endpoint}"

        try:
            resposta = self.session.get(
                url,
                params=params,
                timeout=20,
            )
        except requests.RequestException as erro:
            raise RuntimeError(
                "Não foi possível conectar à API de futebol. "
                f"Detalhe: {erro}"
            ) from erro

        if resposta.status_code == 401:
            raise RuntimeError(
                "Token inválido ou ausente. Verifique API_FUTEBOL_TOKEN "
                "no arquivo .streamlit/secrets.toml."
            )

        if resposta.status_code == 403:
            raise RuntimeError(
                "Seu plano da API não possui acesso a este recurso."
            )

        if resposta.status_code == 429:
            raise RuntimeError(
                "Limite de requisições da API atingido. Aguarde alguns instantes."
            )

        if not resposta.ok:
            raise RuntimeError(
                f"Erro da API ({resposta.status_code}): {resposta.text[:250]}"
            )

        return resposta.json()

    def campeonatos(self) -> list[dict[str, Any]]:
        dados = self.get("/campeonatos")
        return dados if isinstance(dados, list) else dados.get("campeonatos", [])

    def encontrar_brasileirao_2026(self) -> dict[str, Any]:
        """
        Procura o Campeonato Brasileiro cuja edição atual seja 2026.

        Isso evita depender de um ID fixo de campeonato.
        """
        campeonatos = self.campeonatos()

        candidatos = []
        for campeonato in campeonatos:
            nome = str(
                primeiro_valor(
                    campeonato,
                    "nome_popular",
                    "nome",
                    "slug",
                    padrao="",
                )
            ).lower()

            edicao = campeonato.get("edicao_atual") or {}
            temporada = str(edicao.get("temporada", ""))

            possui_nome = (
                "brasile" in nome
                or "serie-a" in nome
                or "série a" in nome
            )

            if possui_nome and "2026" in temporada:
                candidatos.append(campeonato)

        if not candidatos:
            # Caso a API retorne o campeonato sem a temporada no objeto,
            # tenta localizar ao menos o Brasileirão principal.
            for campeonato in campeonatos:
                nome = str(
                    primeiro_valor(
                        campeonato,
                        "nome_popular",
                        "nome",
                        "slug",
                        padrao="",
                    )
                ).lower()

                if "brasile" in nome and (
                    "serie-a" in nome or "série a" in nome or "brasileirão" in nome
                ):
                    candidatos.append(campeonato)

        if not candidatos:
            raise RuntimeError(
                "Não foi encontrado um campeonato do Brasileirão Série A 2026 "
                "entre os recursos liberados pela sua chave."
            )

        return candidatos[0]

    def tabela(self, campeonato_id: int) -> Any:
        return self.get(f"/campeonatos/{campeonato_id}/tabela")

    def partidas(self, campeonato_id: int) -> Any:
        return self.get(f"/campeonatos/{campeonato_id}/partidas")

    def rodada(self, campeonato_id: int, rodada: int) -> Any:
        return self.get(f"/campeonatos/{campeonato_id}/rodadas/{rodada}")

    def artilharia(self, campeonato_id: int) -> Any:
        return self.get(f"/campeonatos/{campeonato_id}/artilharia")

    def detalhes_partida(self, partida_id: int) -> Any:
        return self.get(f"/partidas/{partida_id}")

    def detalhes_time(self, time_id: int) -> Any:
        return self.get(f"/times/{time_id}")

    def partidas_ao_vivo(self) -> Any:
        """
        Em algumas contas/versões da API, este endpoint pode estar
        disponível como /partidas/ao-vivo ou /partidas/aovivo.
        """
        try:
            return self.get("/partidas/ao-vivo")
        except RuntimeError:
            return self.get("/partidas/aovivo")


# ============================================================
# CONSULTAS COM CACHE
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_campeonato(token: str) -> dict[str, Any]:
    cliente = APIFutebolClient(token)
    return cliente.encontrar_brasileirao_2026()


@st.cache_data(ttl=90, show_spinner=False)
def buscar_tabela(token: str, campeonato_id: int) -> Any:
    return APIFutebolClient(token).tabela(campeonato_id)


@st.cache_data(ttl=90, show_spinner=False)
def buscar_partidas(token: str, campeonato_id: int) -> Any:
    return APIFutebolClient(token).partidas(campeonato_id)


@st.cache_data(ttl=90, show_spinner=False)
def buscar_rodada(token: str, campeonato_id: int, rodada: int) -> Any:
    return APIFutebolClient(token).rodada(campeonato_id, rodada)


@st.cache_data(ttl=300, show_spinner=False)
def buscar_artilharia(token: str, campeonato_id: int) -> Any:
    return APIFutebolClient(token).artilharia(campeonato_id)


@st.cache_data(ttl=60, show_spinner=False)
def buscar_detalhes_partida(token: str, partida_id: int) -> Any:
    return APIFutebolClient(token).detalhes_partida(partida_id)


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_detalhes_time(token: str, time_id: int) -> Any:
    return APIFutebolClient(token).detalhes_time(time_id)


# ============================================================
# NORMALIZAÇÃO DE DADOS
# ============================================================

def extrair_lista_tabela(dados: Any) -> list[dict[str, Any]]:
    """Aceita formatos diferentes retornados pela API."""
    if isinstance(dados, list):
        return dados

    if isinstance(dados, dict):
        for chave in ("tabela", "classificacao", "classificação", "data"):
            if isinstance(dados.get(chave), list):
                return dados[chave]

    return []


def extrair_partidas(dados: Any) -> list[dict[str, Any]]:
    """
    A API pode devolver partidas organizadas por fase/rodada.
    Esta função percorre os níveis e transforma tudo em lista.
    """
    if isinstance(dados, list):
        return dados

    if not isinstance(dados, dict):
        return []

    if isinstance(dados.get("partidas"), list):
        return dados["partidas"]

    estrutura = dados.get("partidas", dados)
    resultado: list[dict[str, Any]] = []

    def percorrer(item: Any) -> None:
        if isinstance(item, list):
            for subitem in item:
                percorrer(subitem)

        elif isinstance(item, dict):
            if "partida_id" in item or "id" in item:
                resultado.append(item)
            else:
                for valor in item.values():
                    percorrer(valor)

    percorrer(estrutura)
    return resultado


def obter_time(partida: dict[str, Any], mandante: bool = True) -> dict[str, Any]:
    """Obtém dados do time mandante ou visitante."""
    if mandante:
        return primeiro_valor(
            partida,
            "time_mandante",
            "mandante",
            "home",
            padrao={},
        ) or {}

    return primeiro_valor(
        partida,
        "time_visitante",
        "visitante",
        "away",
        padrao={},
    ) or {}


def obter_nome_time(time: dict[str, Any]) -> str:
    return str(
        primeiro_valor(
            time,
            "nome_popular",
            "nome",
            "sigla",
            "name",
            padrao="Time não informado",
        )
    )


def obter_escudo_time(time: dict[str, Any]) -> str:
    return str(
        primeiro_valor(
            time,
            "escudo",
            "logo",
            "imagem",
            padrao="",
        )
    )


def obter_placar(partida: dict[str, Any]) -> tuple[str, str]:
    """
    Extrai placar em formatos compatíveis com variações da API.
    """
    placar = partida.get("placar") or {}

    gols_mandante = primeiro_valor(
        partida,
        "placar_mandante",
        "gols_mandante",
        "score_home",
        padrao=primeiro_valor(placar, "mandante", "home", padrao="-"),
    )

    gols_visitante = primeiro_valor(
        partida,
        "placar_visitante",
        "gols_visitante",
        "score_away",
        padrao=primeiro_valor(placar, "visitante", "away", padrao="-"),
    )

    return str(gols_mandante), str(gols_visitante)


def renderizar_card_partida(partida: dict[str, Any], exibir_botao: bool = False) -> None:
    """Desenha um card visual de uma partida."""
    mandante = obter_time(partida, mandante=True)
    visitante = obter_time(partida, mandante=False)

    nome_mandante = obter_nome_time(mandante)
    nome_visitante = obter_nome_time(visitante)

    gols_mandante, gols_visitante = obter_placar(partida)

    status = str(partida.get("status", "agendado"))
    status_texto, status_css = normalizar_status(status)

    rodada = primeiro_valor(partida, "rodada", "rodada_nome", padrao="")
    estadio = primeiro_valor(
        partida,
        "estadio",
        "estádio",
        "local",
        padrao="",
    )

    if isinstance(estadio, dict):
        estadio = primeiro_valor(estadio, "nome_popular", "nome", padrao="")

    data = primeiro_valor(
        partida,
        "data_realizacao_iso",
        "data",
        "data_partida",
        padrao=None,
    )

    st.markdown(
        f"""
        <div class="match-card">
            <div class="match-meta">
                {formatar_data(data)}
                {" · " + str(rodada) if rodada else ""}
                {" · " + str(estadio) if estadio else ""}
                <span class="{status_css}" style="float:right;">{status_texto}</span>
            </div>

            <div class="match-teams">
                <div class="match-team">{nome_mandante}</div>
                <div class="score">{gols_mandante} x {gols_visitante}</div>
                <div class="match-team away">{nome_visitante}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    partida_id = primeiro_valor(partida, "partida_id", "id", padrao=None)

    if exibir_botao and partida_id:
        if st.button(
            "Ver detalhes da partida",
            key=f"detalhes_partida_{partida_id}",
            use_container_width=True,
        ):
            st.session_state["partida_selecionada"] = int(partida_id)


# ============================================================
# INTERFACE PRINCIPAL
# ============================================================

token = obter_token()

if not token:
    st.error(
        "Configure sua chave da API Futebol no arquivo "
        "`.streamlit/secrets.toml` antes de iniciar o aplicativo."
    )
    st.code(
        'API_FUTEBOL_TOKEN = "SUA_CHAVE_AQUI"',
        language="toml",
    )
    st.stop()

try:
    campeonato = buscar_campeonato(token)

    campeonato_id = int(
        primeiro_valor(
            campeonato,
            "campeonato_id",
            "id",
            padrao=0,
        )
    )

    if not campeonato_id:
        raise RuntimeError("Não foi possível identificar o ID do campeonato.")

    nome_campeonato = str(
        primeiro_valor(
            campeonato,
            "nome_popular",
            "nome",
            padrao="Campeonato Brasileiro Série A",
        )
    )

except Exception as erro:
    st.error("Não foi possível inicializar os dados do Brasileirão 2026.")
    st.exception(erro)
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.image(
        campeonato.get("logo", "https://cdn-icons-png.flaticon.com/512/53/53283.png"),
        width=72,
    )

    st.title("Brasileirão 2026")
    st.caption("Central de dados e resultados")

    st.divider()

    if st.button("🔄 Atualizar agora", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        "Atualização automática configurada para aproximadamente "
        "45 segundos."
    )

    st.divider()

    pagina = st.radio(
        "Navegação",
        [
            "🏠 Visão geral",
            "🔴 Ao vivo",
            "📅 Calendário",
            "📊 Classificação",
            "👕 Times",
            "🥇 Artilharia",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Dados fornecidos pela API Futebol.")
    st.caption(
        f"Última renderização: "
        f"{datetime.now(FUSO_BRASILIA).strftime('%d/%m/%Y %H:%M:%S')}"
    )


# ============================================================
# CABEÇALHO
# ============================================================

rodada_atual = campeonato.get("rodada_atual") or {}
numero_rodada_atual = primeiro_valor(
    rodada_atual,
    "rodada",
    "numero",
    padrao="",
)

st.markdown(
    f"""
    <section class="hero">
        <h1>⚽ {nome_campeonato} 2026</h1>
        <p>
            Calendário, classificação, estatísticas, times e resultados
            atualizados automaticamente.
            {" Rodada atual: " + str(numero_rodada_atual) if numero_rodada_atual else ""}
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PÁGINA: VISÃO GERAL
# ============================================================

if pagina == "🏠 Visão geral":
    try:
        tabela_dados = buscar_tabela(token, campeonato_id)
        tabela = extrair_lista_tabela(tabela_dados)

        partidas_dados = buscar_partidas(token, campeonato_id)
        partidas = extrair_partidas(partidas_dados)

        partidas_ao_vivo = [
            partida
            for partida in partidas
            if str(partida.get("status", "")).lower()
            in {"andamento", "ao-vivo", "ao_vivo", "live"}
        ]

        proximas = [
            partida
            for partida in partidas
            if str(partida.get("status", "")).lower()
            in {"agendado", "pre-jogo"}
        ]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Times", len(tabela) if tabela else 20)
        col2.metric("Partidas ao vivo", len(partidas_ao_vivo))
        col3.metric("Rodada atual", numero_rodada_atual or "—")
        col4.metric("Partidas carregadas", len(partidas))

        esquerda, direita = st.columns([1.15, 1])

        with esquerda:
            st.subheader("🔴 Jogos ao vivo")

            if partidas_ao_vivo:
                for partida in partidas_ao_vivo:
                    renderizar_card_partida(partida, exibir_botao=True)
            else:
                st.info("Não há partidas em andamento neste momento.")

            st.subheader("📅 Próximas partidas")

            if proximas:
                proximas_ordenadas = sorted(
                    proximas,
                    key=lambda item: str(
                        primeiro_valor(
                            item,
                            "data_realizacao_iso",
                            "data",
                            padrao="9999-12-31",
                        )
                    ),
                )

                for partida in proximas_ordenadas[:5]:
                    renderizar_card_partida(partida, exibir_botao=True)
            else:
                st.info("Não há próximas partidas disponíveis.")

        with direita:
            st.subheader("📊 Top 6 da classificação")

            if tabela:
                linhas = []

                for indice, item in enumerate(tabela[:6], start=1):
                    time = primeiro_valor(item, "time", "equipe", padrao={}) or {}
                    nome = obter_nome_time(time)

                    pontos = primeiro_valor(
                        item,
                        "pontos",
                        "pts",
                        padrao=0,
                    )

                    jogos = primeiro_valor(
                        item,
                        "jogos",
                        "partidas_jogadas",
                        "j",
                        padrao=0,
                    )

                    linhas.append(
                        {
                            "#": indice,
                            "Time": nome,
                            "Pts": pontos,
                            "J": jogos,
                        }
                    )

                st.dataframe(
                    pd.DataFrame(linhas),
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.warning("A tabela ainda não está disponível.")

    except Exception as erro:
        st.error("Erro ao carregar a visão geral.")
        st.exception(erro)


# ============================================================
# PÁGINA: AO VIVO
# ============================================================

elif pagina == "🔴 Ao vivo":
    st.subheader("🔴 Partidas em andamento")

    try:
        partidas_dados = buscar_partidas(token, campeonato_id)
        partidas = extrair_partidas(partidas_dados)

        ao_vivo = [
            partida
            for partida in partidas
            if str(partida.get("status", "")).lower()
            in {"andamento", "ao-vivo", "ao_vivo", "live"}
        ]

        if ao_vivo:
            for partida in ao_vivo:
                renderizar_card_partida(partida, exibir_botao=True)
        else:
            st.info(
                "Não há jogos em andamento no Brasileirão neste momento. "
                "Esta tela será atualizada automaticamente."
            )

    except Exception as erro:
        st.error("Não foi possível consultar as partidas ao vivo.")
        st.exception(erro)


# ============================================================
# PÁGINA: CALENDÁRIO
# ============================================================

elif pagina == "📅 Calendário":
    st.subheader("📅 Calendário e resultados")

    try:
        partidas_dados = buscar_partidas(token, campeonato_id)
        partidas = extrair_partidas(partidas_dados)

        if not partidas:
            st.info("Nenhuma partida foi retornada pela API.")
            st.stop()

        rodadas_disponiveis = sorted(
            {
                str(primeiro_valor(partida, "rodada", "rodada_nome", padrao="Sem rodada"))
                for partida in partidas
            }
        )

        filtros_col1, filtros_col2 = st.columns(2)

        with filtros_col1:
            rodada_escolhida = st.selectbox(
                "Filtrar por rodada",
                ["Todas"] + rodadas_disponiveis,
            )

        with filtros_col2:
            status_escolhido = st.selectbox(
                "Situação",
                ["Todos", "Agendados", "Ao vivo", "Encerrados"],
            )

        partidas_filtradas = partidas.copy()

        if rodada_escolhida != "Todas":
            partidas_filtradas = [
                partida
                for partida in partidas_filtradas
                if str(
                    primeiro_valor(
                        partida,
                        "rodada",
                        "rodada_nome",
                        padrao="Sem rodada",
                    )
                ) == rodada_escolhida
            ]

        mapa_status = {
            "Agendados": {"agendado", "pre-jogo"},
            "Ao vivo": {"andamento", "ao-vivo", "ao_vivo", "live"},
            "Encerrados": {"finalizado", "encerrado", "finished"},
        }

        if status_escolhido != "Todos":
            permitidos = mapa_status[status_escolhido]
            partidas_filtradas = [
                partida
                for partida in partidas_filtradas
                if str(partida.get("status", "")).lower() in permitidos
            ]

        partidas_filtradas = sorted(
            partidas_filtradas,
            key=lambda item: str(
                primeiro_valor(
                    item,
                    "data_realizacao_iso",
                    "data",
                    padrao="9999-12-31",
                )
            ),
        )

        st.caption(f"{len(partidas_filtradas)} partida(s) encontrada(s).")

        for partida in partidas_filtradas:
            renderizar_card_partida(partida, exibir_botao=True)

    except Exception as erro:
        st.error("Não foi possível carregar o calendário.")
        st.exception(erro)


# ============================================================
# PÁGINA: CLASSIFICAÇÃO
# ============================================================

elif pagina == "📊 Classificação":
    st.subheader("📊 Tabela de classificação")

    try:
        tabela_dados = buscar_tabela(token, campeonato_id)
        tabela = extrair_lista_tabela(tabela_dados)

        if not tabela:
            st.warning("A classificação ainda não está disponível.")
            st.stop()

        linhas_tabela = []

        for indice, item in enumerate(tabela, start=1):
            time = primeiro_valor(item, "time", "equipe", padrao={}) or {}

            posicao = primeiro_valor(
                item,
                "posicao",
                "posição",
                "colocacao",
                "colocação",
                padrao=indice,
            )

            linhas_tabela.append(
                {
                    "Pos": posicao,
                    "Time": obter_nome_time(time),
                    "Pts": primeiro_valor(item, "pontos", "pts", padrao=0),
                    "J": primeiro_valor(item, "jogos", "partidas_jogadas", "j", padrao=0),
                    "V": primeiro_valor(item, "vitorias", "vitórias", "v", padrao=0),
                    "E": primeiro_valor(item, "empates", "e", padrao=0),
                    "D": primeiro_valor(item, "derrotas", "d", padrao=0),
                    "GP": primeiro_valor(item, "gols_pro", "gp", padrao=0),
                    "GC": primeiro_valor(item, "gols_contra", "gc", padrao=0),
                    "SG": primeiro_valor(item, "saldo_gols", "sg", padrao=0),
                }
            )

        dataframe_tabela = pd.DataFrame(linhas_tabela)

        st.dataframe(
            dataframe_tabela,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Pos": st.column_config.NumberColumn("Pos.", width="small"),
                "Time": st.column_config.TextColumn("Time", width="medium"),
                "Pts": st.column_config.NumberColumn("Pontos", width="small"),
            },
        )

        st.caption(
            "Critérios de desempate e zonas de classificação são definidos "
            "conforme a regulamentação oficial da competição."
        )

    except Exception as erro:
        st.error("Não foi possível carregar a classificação.")
        st.exception(erro)


# ============================================================
# PÁGINA: TIMES
# ============================================================

elif pagina == "👕 Times":
    st.subheader("👕 Detalhes dos times")

    try:
        tabela_dados = buscar_tabela(token, campeonato_id)
        tabela = extrair_lista_tabela(tabela_dados)

        times: list[dict[str, Any]] = []

        for item in tabela:
            time = primeiro_valor(item, "time", "equipe", padrao={}) or {}

            time_id = primeiro_valor(time, "time_id", "id", padrao=None)
            if time_id:
                times.append(time)

        if not times:
            st.warning("Não foi possível montar a lista de times.")
            st.stop()

        mapa_times = {
            obter_nome_time(time): time
            for time in times
        }

        nome_time = st.selectbox(
            "Selecione um time",
            sorted(mapa_times.keys()),
        )

        time_selecionado = mapa_times[nome_time]
        time_id = int(primeiro_valor(time_selecionado, "time_id", "id"))

        detalhes = buscar_detalhes_time(token, time_id)

        nome = primeiro_valor(
            detalhes,
            "nome_popular",
            "nome",
            padrao=nome_time,
        )

        escudo = primeiro_valor(
            detalhes,
            "escudo",
            "logo",
            padrao=obter_escudo_time(time_selecionado),
        )

        col_logo, col_info = st.columns([1, 4])

        with col_logo:
            if escudo:
                st.image(escudo, width=130)

        with col_info:
            st.markdown(f"## {nome}")

            cidade = primeiro_valor(
                detalhes,
                "cidade",
                "sede",
                padrao="Não informada",
            )

            estado = primeiro_valor(
                detalhes,
                "estado",
                "uf",
                padrao="",
            )

            estadio = primeiro_valor(
                detalhes,
                "estadio",
                "estádio",
                padrao="Não informado",
            )

            if isinstance(estadio, dict):
                estadio = primeiro_valor(estadio, "nome_popular", "nome", padrao="Não informado")

            fundacao = primeiro_valor(
                detalhes,
                "fundacao",
                "fundação",
                "data_fundacao",
                padrao="Não informada",
            )

            st.write(f"**Cidade:** {cidade} {f'– {estado}' if estado else ''}")
            st.write(f"**Estádio:** {estadio}")
            st.write(f"**Fundação:** {fundacao}")

        with st.expander("Ver resposta completa da API para este time"):
            st.json(detalhes)

    except Exception as erro:
        st.error("Não foi possível carregar as informações do time.")
        st.exception(erro)


# ============================================================
# PÁGINA: ARTILHARIA
# ============================================================

elif pagina == "🥇 Artilharia":
    st.subheader("🥇 Artilharia do Brasileirão 2026")

    try:
        dados_artilharia = buscar_artilharia(token, campeonato_id)

        if isinstance(dados_artilharia, dict):
            artilheiros = (
                dados_artilharia.get("artilharia")
                or dados_artilharia.get("jogadores")
                or dados_artilharia.get("data")
                or []
            )
        else:
            artilheiros = dados_artilharia

        if not isinstance(artilheiros, list) or not artilheiros:
            st.info("A artilharia ainda não está disponível para esta edição.")
            st.stop()

        linhas_artilharia = []

        for indice, jogador in enumerate(artilheiros, start=1):
            atleta = primeiro_valor(
                jogador,
                "atleta",
                "jogador",
                padrao={},
            ) or {}

            time = primeiro_valor(
                jogador,
                "time",
                "equipe",
                padrao={},
            ) or {}

            nome_atleta = primeiro_valor(
                atleta,
                "nome_popular",
                "nome",
                padrao=primeiro_valor(
                    jogador,
                    "nome_popular",
                    "nome",
                    padrao="Jogador não informado",
                ),
            )

            linhas_artilharia.append(
                {
                    "#": indice,
                    "Jogador": nome_atleta,
                    "Time": obter_nome_time(time),
                    "Gols": primeiro_valor(
                        jogador,
                        "gols",
                        "quantidade_gols",
                        "total",
                        padrao=0,
                    ),
                }
            )

        st.dataframe(
            pd.DataFrame(linhas_artilharia),
            hide_index=True,
            use_container_width=True,
        )

    except Exception as erro:
        st.error("Não foi possível carregar a artilharia.")
        st.exception(erro)


# ============================================================
# MODAL/SEÇÃO DE DETALHES DA PARTIDA SELECIONADA
# ============================================================

if st.session_state.get("partida_selecionada"):
    st.divider()
    partida_id = st.session_state["partida_selecionada"]

    st.subheader(f"🔎 Detalhes da partida #{partida_id}")

    if st.button("Fechar detalhes", key="fechar_detalhes"):
        del st.session_state["partida_selecionada"]
        st.rerun()

    try:
        detalhes = buscar_detalhes_partida(token, partida_id)

        partida = detalhes.get("partida", detalhes) if isinstance(detalhes, dict) else detalhes

        if isinstance(partida, dict):
            renderizar_card_partida(partida)

        eventos = []
        if isinstance(detalhes, dict):
            eventos = (
                detalhes.get("gols")
                or detalhes.get("eventos")
                or detalhes.get("lances")
                or []
            )

        estatisticas = []
        if isinstance(detalhes, dict):
            estatisticas = (
                detalhes.get("estatisticas")
                or detalhes.get("estatísticas")
                or []
            )

        aba_eventos, aba_estatisticas, aba_json = st.tabs(
            ["Eventos", "Estatísticas", "Dados técnicos"]
        )

        with aba_eventos:
            if eventos:
                st.dataframe(
                    pd.DataFrame(eventos),
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.info("Não há eventos detalhados disponíveis para esta partida.")

        with aba_estatisticas:
            if estatisticas:
                if isinstance(estatisticas, dict):
                    st.json(estatisticas)
                else:
                    st.dataframe(
                        pd.DataFrame(estatisticas),
                        hide_index=True,
                        use_container_width=True,
                    )
            else:
                st.info(
                    "As estatísticas detalhadas dependem da disponibilidade "
                    "da partida e do plano contratado na API."
                )

        with aba_json:
            st.json(detalhes)

    except Exception as erro:
        st.error("Não foi possível carregar os detalhes da partida.")
        st.exception(erro)
