import streamlit as st
from datetime import datetime

from utils.data_manager import (
    carregar_historico, adicionar_corrida, deletar_corrida,
    carregar_conhecimento, carregar_conversas, salvar_conversa,
    carregar_config, salvar_config, formatar_pace, parse_pace,
)
from utils.analytics import (
    historico_para_dataframe, metricas_gerais, metricas_semanais,
    metricas_mensais, frequencia_por_dia_semana, calcular_streak,
    evolucao_acumulada, gerar_insights, prever_tempos_prova,
)
from utils.charts import (
    grafico_quilometragem_semanal, grafico_quilometragem_mensal,
    grafico_evolucao_pace, grafico_frequencia_semanal,
    grafico_distribuicao_distancia, grafico_acumulado,
    grafico_distribuicao_tipo, grafico_evolucao_distancia,
    grafico_pace_vs_distancia, grafico_previsao_provas,
)
from router import classificar, extrair_dados_corrida
from ai_client import AIClient

st.set_page_config(
    page_title="Pace Tracker",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded",
)


def injetar_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e17 0%, #141b2d 50%, #0a0e17 100%);
        border-right: 1px solid #1e2a40;
    }
    [data-testid="stSidebar"] .stRadio > label { display: none; }
    [data-testid="stSidebar"] .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    [data-testid="stSidebar"] .stRadio > div > label {
        background: transparent;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1rem;
        font-size: 0.95rem;
        font-weight: 500;
        color: #a0aec0;
        cursor: pointer;
        transition: all 0.2s ease;
        margin: 0;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(255,107,53,0.08);
        color: #FF6B35;
    }
    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: linear-gradient(135deg, rgba(255,107,53,0.15) 0%, rgba(255,107,53,0.05) 100%);
        color: #FF6B35;
        font-weight: 600;
        border-left: 3px solid #FF6B35;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #141b2d 0%, #1a2236 100%);
        border: 1px solid #1e2a40;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #a0aec0;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #141b2d;
        border-radius: 12px;
        padding: 4px;
        border: 1px solid #1e2a40;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 500;
        color: #a0aec0;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF6B35, #e55a2b) !important;
        color: white !important;
        font-weight: 600;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border: 1px solid #1e2a40;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(255,107,53,0.3);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF6B35, #e55a2b);
        color: white;
        border: none;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: #141b2d;
        border-radius: 10px;
        border: 1px solid #1e2a40;
        font-weight: 500;
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #1e2a40;
    }

    /* Custom cards */
    .hero-container {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #0a0e17 0%, #141b2d 40%, #1a2236 60%, #0a0e17 100%);
        border-radius: 20px;
        border: 1px solid #1e2a40;
        margin-bottom: 2rem;
        box-shadow: 0 8px 40px rgba(0,0,0,0.4);
        position: relative;
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #FF6B35, #00D4AA, #4B8BFF, #FF6B35);
    }
    .hero-title {
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #FF6B35 0%, #FF8F65 50%, #FFB347 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        color: #a0aec0;
        font-weight: 400;
        margin-bottom: 0;
    }

    .card {
        background: linear-gradient(135deg, #141b2d 0%, #1a2236 100%);
        border: 1px solid #1e2a40;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    .card:hover { transform: translateY(-2px); }

    .feature-card {
        background: linear-gradient(135deg, #141b2d 0%, #1a2236 100%);
        border: 1px solid #1e2a40;
        border-left: 4px solid #FF6B35;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 0.8rem;
        min-height: 140px;
    }
    .feature-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .feature-title { font-size: 1.05rem; font-weight: 700; color: #FAFAFA; margin-bottom: 0.3rem; }
    .feature-desc { font-size: 0.85rem; color: #a0aec0; line-height: 1.5; }

    .insight-card {
        background: linear-gradient(135deg, #141b2d 0%, #1a2236 100%);
        border: 1px solid #1e2a40;
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 0.8rem;
    }
    .insight-positivo { border-left: 4px solid #00D4AA; }
    .insight-negativo { border-left: 4px solid #FF4B4B; }
    .insight-info { border-left: 4px solid #4B8BFF; }
    .insight-icon { font-size: 1.5rem; float: left; margin-right: 1rem; margin-top: 0.2rem; }
    .insight-title { font-size: 1rem; font-weight: 700; color: #FAFAFA; }
    .insight-desc { font-size: 0.88rem; color: #a0aec0; margin-top: 0.2rem; }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #FF6B35;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
    }

    .section-header {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1e2a40;
    }

    .video-card {
        background: linear-gradient(135deg, #141b2d 0%, #1a2236 100%);
        border: 1px solid #1e2a40;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    .video-card iframe {
        width: 100%;
        height: 215px;
        border: none;
    }
    .video-info {
        padding: 1rem 1.2rem;
    }
    .video-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #FAFAFA;
        margin-bottom: 0.3rem;
    }
    .video-desc {
        font-size: 0.8rem;
        color: #a0aec0;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 14px;
        border: 1px solid #1e2a40;
        margin-bottom: 0.5rem;
    }

    .pace-result {
        background: linear-gradient(135deg, #141b2d 0%, #1a2236 100%);
        border: 1px solid #1e2a40;
        border-left: 4px solid #00D4AA;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
    }
    .pace-result .pace-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #00D4AA;
    }
    .pace-result .pace-unit {
        font-size: 0.9rem;
        color: #a0aec0;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #1e2a40, transparent);
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def navegacao_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 1.5rem 0 1rem 0;">
            <div style="font-size: 2.5rem;">🏃</div>
            <div style="font-size: 1.3rem; font-weight: 800; background: linear-gradient(135deg, #FF6B35, #FFB347); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px;">PACE TRACKER</div>
            <div style="font-size: 0.75rem; color: #546480; margin-top: 2px;">Seu assistente de corrida</div>
        </div>
        <div style="height:1px; background: linear-gradient(90deg, transparent, #1e2a40, transparent); margin: 0.5rem 1rem 1rem 1rem;"></div>
        """, unsafe_allow_html=True)

        pagina = st.radio(
            "Navegação",
            [
                "🏠  Home",
                "📊  Dashboard",
                "➕  Registrar Treino",
                "📋  Histórico",
                "📈  Análise",
                "🏁  Previsão de Provas",
                "💡  Insights",
                "🤖  Chatbot",
                "📚  Conteúdo",
            ],
            label_visibility="collapsed",
        )

        st.markdown('<div style="height:1px; background: linear-gradient(90deg, transparent, #1e2a40, transparent); margin: 1rem;"></div>', unsafe_allow_html=True)

        historico = carregar_historico()
        df = historico_para_dataframe(historico)
        if not df.empty:
            m = metricas_gerais(df)
            st.markdown(f"""
            <div style="padding: 0 0.5rem;">
                <div style="font-size: 0.7rem; color: #546480; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.8rem;">Resumo rápido</div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: #a0aec0; font-size: 0.82rem;">Total</span>
                    <span style="color: #FF6B35; font-weight: 700; font-size: 0.82rem;">{m['total_km']} km</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: #a0aec0; font-size: 0.82rem;">Corridas</span>
                    <span style="color: #00D4AA; font-weight: 700; font-size: 0.82rem;">{m['total_corridas']}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #a0aec0; font-size: 0.82rem;">Pace médio</span>
                    <span style="color: #4B8BFF; font-weight: 700; font-size: 0.82rem;">{formatar_pace(m['pace_medio'])}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="position: fixed; bottom: 1rem; padding: 0 1rem;">
            <div style="font-size: 0.7rem; color: #394560;">Pace Tracker v2.0</div>
        </div>
        """, unsafe_allow_html=True)

    return pagina


# ─── PAGES ────────────────────────────────────────────────

def pagina_home():
    st.markdown("""
    <div class="hero-container">
        <div style="font-size: 4rem; margin-bottom: 0.5rem;">🏃‍♂️</div>
        <div class="hero-title">PACE TRACKER</div>
        <div class="hero-subtitle">Seu assistente inteligente para análise de desempenho em corrida</div>
        <div style="margin-top: 1rem; display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap;">
            <span style="background: rgba(255,107,53,0.15); color: #FF6B35; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.78rem; font-weight: 500;">Análise de dados</span>
            <span style="background: rgba(0,212,170,0.15); color: #00D4AA; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.78rem; font-weight: 500;">Insights automáticos</span>
            <span style="background: rgba(75,139,255,0.15); color: #4B8BFF; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.78rem; font-weight: 500;">Chatbot com IA</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    historico = carregar_historico()
    df = historico_para_dataframe(historico)
    m = metricas_gerais(df)
    streak = calcular_streak(df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="card" style="text-align:center;">
            <div class="stat-number">{m['total_km']}</div>
            <div class="stat-label">Km Percorridos</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="card" style="text-align:center;">
            <div class="stat-number" style="color:#00D4AA;">{m['total_corridas']}</div>
            <div class="stat-label">Corridas</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="card" style="text-align:center;">
            <div class="stat-number" style="color:#4B8BFF;">{formatar_pace(m['pace_medio'])}</div>
            <div class="stat-label">Pace Médio</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="card" style="text-align:center;">
            <div class="stat-number" style="color:#8B5CF6;">{streak['atual']}</div>
            <div class="stat-label">Dias Seguidos</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">✨ Recursos</div>', unsafe_allow_html=True)

    features = [
        ("📊", "Dashboard Analítico", "KPIs, gráficos interativos e métricas de desempenho em tempo real."),
        ("⚡", "Calculadora Inteligente", "Calcule pace, tempo e distância com formulários ou linguagem natural."),
        ("📈", "Evolução de Desempenho", "Acompanhe quilometragem, ritmo e frequência com gráficos Plotly."),
        ("💡", "Insights Automáticos", "Receba análises geradas automaticamente a partir dos seus dados."),
        ("🤖", "Chatbot com IA", "Tire dúvidas sobre corrida com base de conhecimento e IA local."),
        ("📚", "Conteúdo Educacional", "Dicas de treino, nutrição, prevenção de lesões e mais."),
        ("🏆", "Melhores Desempenhos", "Identifique seus melhores paces, maiores distâncias e recordes."),
        ("📅", "Análise Temporal", "Compare períodos, veja tendências semanais e mensais."),
    ]
    cols = st.columns(4)
    for i, (icone, titulo, desc) in enumerate(features):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icone}</div>
                <div class="feature-title">{titulo}</div>
                <div class="feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def pagina_dashboard():
    st.markdown('<div class="section-header">📊 Dashboard</div>', unsafe_allow_html=True)

    historico = carregar_historico()
    df = historico_para_dataframe(historico)

    if df.empty:
        st.info("Nenhuma corrida registrada ainda. Vá para **Registrar Treino** para começar.")
        return

    m = metricas_gerais(df)
    streak = calcular_streak(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🏃 Distância Total", f"{m['total_km']} km")
    c2.metric("📋 Total de Corridas", m["total_corridas"])
    c3.metric("⚡ Pace Médio", f"{formatar_pace(m['pace_medio'])}")
    c4.metric("🏆 Melhor Pace", f"{formatar_pace(m['melhor_pace'])}")
    c5.metric("🔥 Sequência", f"{streak['atual']} dias")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    semanal = metricas_semanais(df)
    mensal = metricas_mensais(df)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(grafico_quilometragem_semanal(semanal), use_container_width=True)
    with col2:
        st.plotly_chart(grafico_evolucao_pace(df), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(grafico_acumulado(evolucao_acumulada(df)), use_container_width=True)
    with col4:
        st.plotly_chart(grafico_frequencia_semanal(frequencia_por_dia_semana(df)), use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("##### Últimas Corridas")
    ultimas = df.sort_values("data", ascending=False).head(5)
    display_df = ultimas[["data", "distancia", "tempo", "pace_str", "tipo"]].copy()
    display_df.columns = ["Data", "Distância (km)", "Tempo (min)", "Pace", "Tipo"]
    display_df["Data"] = display_df["Data"].dt.strftime("%d/%m/%Y")
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def pagina_registrar():
    st.markdown('<div class="section-header">➕ Registrar Treino</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📝 Formulário", "💬 Linguagem Natural"])

    with tab1:
        with st.form("form_treino", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("Data da corrida", value=datetime.now())
                distancia = st.number_input("Distância (km)", min_value=0.1, max_value=200.0, value=5.0, step=0.1)
                tipo = st.selectbox("Tipo de treino", [
                    "Treino", "Treino Leve", "Intervalado", "Tiro",
                    "Longão", "Recuperação", "Prova", "Outro",
                ])
            with col2:
                st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
                horas = st.number_input("Horas", min_value=0, max_value=24, value=0, step=1)
                minutos = st.number_input("Minutos", min_value=0, max_value=59, value=25, step=1)
                notas = st.text_area("Notas (opcional)", height=80, placeholder="Como foi o treino?")

            submitted = st.form_submit_button("🏃 Registrar Corrida", type="primary", use_container_width=True)

            if submitted:
                tempo_total = horas * 60 + minutos
                if tempo_total <= 0:
                    st.error("O tempo deve ser maior que zero.")
                elif distancia <= 0:
                    st.error("A distância deve ser maior que zero.")
                else:
                    pace_valor = tempo_total / distancia
                    adicionar_corrida(
                        distancia, tempo_total, pace_valor,
                        data=data.strftime("%Y-%m-%d"),
                        tipo=tipo, notas=notas,
                    )
                    st.success("Corrida registrada com sucesso!")
                    st.markdown(f"""
                    <div class="pace-result">
                        <div class="pace-value">{formatar_pace(pace_valor)}</div>
                        <div class="pace-unit">min/km</div>
                        <div style="margin-top: 0.8rem; font-size: 0.9rem; color: #a0aec0;">
                            {distancia} km em {int(horas)}h{int(minutos):02d}min
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div class="card">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">Como usar:</div>
            <div style="color: #a0aec0; font-size: 0.88rem; line-height: 1.8;">
                • "corri 10km em 50min"<br>
                • "5km pace 5:30"<br>
                • "fiz 21km em 1h45"<br>
                • "corrida de 8km em 40 minutos"
            </div>
        </div>
        """, unsafe_allow_html=True)

        texto = st.text_input("Descreva sua corrida:", placeholder="Ex: corri 10km em 50 minutos")
        if texto:
            distancia, tempo, pace = extrair_dados_corrida(texto)
            if distancia and tempo:
                pace_calc = tempo / distancia
                adicionar_corrida(distancia, tempo, pace_calc)
                st.success("Corrida registrada!")
                st.markdown(f"""
                <div class="pace-result">
                    <div class="pace-value">{formatar_pace(pace_calc)}</div>
                    <div class="pace-unit">min/km</div>
                    <div style="margin-top: 0.5rem; color: #a0aec0; font-size: 0.9rem;">
                        {distancia} km em {tempo:.0f} min
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif distancia and pace:
                tempo_calc = pace * distancia
                h = int(tempo_calc // 60)
                m = int(tempo_calc % 60)
                tempo_str = f"{h}h{m:02d}min" if h > 0 else f"{m} min"
                st.info(f"Com pace de {formatar_pace(pace)} e distância de {distancia} km, tempo estimado: **{tempo_str}**")
            elif distancia:
                st.warning(f"Distância detectada: {distancia} km. Informe também o tempo ou pace.")
            elif tempo:
                st.warning(f"Tempo detectado: {tempo:.0f} min. Informe também a distância.")
            else:
                st.error("Não consegui extrair os dados. Tente algo como: 'corri 5km em 25min'")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("##### Calculadora Rápida")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Calcular Pace**")
        calc_dist = st.number_input("Distância (km)", min_value=0.1, value=5.0, step=0.1, key="calc_dist")
        calc_tempo = st.number_input("Tempo (min)", min_value=0.1, value=25.0, step=0.5, key="calc_tempo")
        if st.button("Calcular Pace", key="btn_pace"):
            p = calc_tempo / calc_dist
            st.markdown(f"""<div class="pace-result">
                <div class="pace-value">{formatar_pace(p)}</div>
                <div class="pace-unit">min/km</div>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("**Calcular Tempo**")
        calc_pace_str = st.text_input("Pace (min/km)", value="5:00", key="calc_pace")
        calc_dist2 = st.number_input("Distância (km)", min_value=0.1, value=10.0, step=0.1, key="calc_dist2")
        if st.button("Calcular Tempo", key="btn_tempo"):
            p = parse_pace(calc_pace_str)
            if p > 0:
                t = p * calc_dist2
                h = int(t // 60)
                m = int(t % 60)
                s = int((t - int(t)) * 60)
                st.markdown(f"""<div class="pace-result">
                    <div class="pace-value">{h}h{m:02d}:{s:02d}</div>
                    <div class="pace-unit">tempo estimado</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.error("Pace inválido. Use o formato M:SS (ex: 5:30)")


def pagina_historico():
    st.markdown('<div class="section-header">📋 Histórico de Corridas</div>', unsafe_allow_html=True)

    historico = carregar_historico()
    df = historico_para_dataframe(historico)

    if df.empty:
        st.info("Nenhuma corrida registrada. Vá para **Registrar Treino** para começar.")
        return

    st.markdown("##### Filtros")
    col1, col2, col3 = st.columns(3)
    with col1:
        data_min = df["data"].min().date()
        data_max = df["data"].max().date()
        datas = st.date_input("Período", value=(data_min, data_max), min_value=data_min, max_value=data_max)
    with col2:
        dist_range = st.slider("Distância (km)", float(df["distancia"].min()), float(df["distancia"].max()),
                               (float(df["distancia"].min()), float(df["distancia"].max())), step=0.5)
    with col3:
        tipos = ["Todos"] + sorted(df["tipo"].unique().tolist())
        tipo_filtro = st.selectbox("Tipo", tipos)

    filtrado = df.copy()
    if isinstance(datas, tuple) and len(datas) == 2:
        filtrado = filtrado[(filtrado["data"].dt.date >= datas[0]) & (filtrado["data"].dt.date <= datas[1])]
    filtrado = filtrado[(filtrado["distancia"] >= dist_range[0]) & (filtrado["distancia"] <= dist_range[1])]
    if tipo_filtro != "Todos":
        filtrado = filtrado[filtrado["tipo"] == tipo_filtro]

    m = metricas_gerais(filtrado)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Corridas", m["total_corridas"])
    c2.metric("Distância Total", f"{m['total_km']} km")
    c3.metric("Pace Médio", formatar_pace(m["pace_medio"]))
    c4.metric("Maior Distância", f"{m['maior_distancia']} km")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    display = filtrado[["data", "distancia", "tempo", "pace_str", "tipo", "notas"]].copy()
    display.columns = ["Data", "Distância (km)", "Tempo (min)", "Pace", "Tipo", "Notas"]
    display["Data"] = display["Data"].dt.strftime("%d/%m/%Y")
    display = display.sort_values("Data", ascending=False)
    st.dataframe(display, use_container_width=True, hide_index=True, height=400)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    with st.expander("🗑️ Remover corrida"):
        st.warning("Selecione o índice da corrida para remover (baseado na ordem do histórico).")
        idx = st.number_input("Índice da corrida", min_value=0, max_value=max(0, len(historico) - 1), value=0, step=1)
        if idx < len(historico):
            c = historico[idx]
            st.write(f"**Corrida selecionada:** {c.get('distancia')} km, {c.get('tempo')} min, Pace: {c.get('pace')}, Data: {c.get('data', 'N/A')}")
        if st.button("Remover", type="secondary"):
            removida = deletar_corrida(idx)
            if removida:
                st.success("Corrida removida!")
                st.rerun()


def pagina_analise():
    st.markdown('<div class="section-header">📈 Análise de Desempenho</div>', unsafe_allow_html=True)

    historico = carregar_historico()
    df = historico_para_dataframe(historico)

    if df.empty:
        st.info("Registre corridas para visualizar análises de desempenho.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["🏃 Quilometragem", "⚡ Ritmo", "📅 Frequência", "🔬 Avançado"])

    semanal = metricas_semanais(df)
    mensal = metricas_mensais(df)

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(grafico_quilometragem_semanal(semanal), use_container_width=True)
        with col2:
            st.plotly_chart(grafico_quilometragem_mensal(mensal), use_container_width=True)

        st.plotly_chart(grafico_acumulado(evolucao_acumulada(df)), use_container_width=True)
        st.plotly_chart(grafico_evolucao_distancia(df), use_container_width=True)

        if not semanal.empty:
            st.markdown("##### Resumo Semanal")
            sem_display = semanal[["semana_label", "km_total", "corridas", "pace_fmt", "tempo_total"]].copy()
            sem_display.columns = ["Semana", "Km Total", "Corridas", "Pace Médio", "Tempo Total (min)"]
            sem_display["Tempo Total (min)"] = sem_display["Tempo Total (min)"].round(0).astype(int)
            st.dataframe(sem_display, use_container_width=True, hide_index=True)

    with tab2:
        st.plotly_chart(grafico_evolucao_pace(df), use_container_width=True)
        st.plotly_chart(grafico_pace_vs_distancia(df), use_container_width=True)

        m = metricas_gerais(df)
        col1, col2, col3 = st.columns(3)
        col1.metric("Pace Médio", formatar_pace(m["pace_medio"]))
        col2.metric("Melhor Pace", formatar_pace(m["melhor_pace"]))
        col3.metric("Pace mais Lento", formatar_pace(m["pior_pace"]))

        if not mensal.empty:
            st.markdown("##### Evolução Mensal do Pace")
            men_display = mensal[["mes_label", "pace_fmt", "km_total", "corridas"]].copy()
            men_display.columns = ["Mês", "Pace Médio", "Km Total", "Corridas"]
            st.dataframe(men_display, use_container_width=True, hide_index=True)

    with tab3:
        freq = frequencia_por_dia_semana(df)
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(grafico_frequencia_semanal(freq), use_container_width=True)
        with col2:
            st.plotly_chart(grafico_distribuicao_tipo(df), use_container_width=True)

        streak = calcular_streak(df)
        col1, col2, col3 = st.columns(3)
        col1.metric("Sequência Atual", f"{streak['atual']} dias")
        col2.metric("Maior Sequência", f"{streak['melhor']} dias")
        col3.metric("Média de Treinos/Semana", f"{len(df) / max(1, len(semanal)):.1f}")

    with tab4:
        st.plotly_chart(grafico_distribuicao_distancia(df), use_container_width=True)

        st.markdown("##### Melhores Desempenhos")
        validos = df[df["pace_num"] > 0].sort_values("pace_num")
        if not validos.empty:
            top = validos.head(5)[["data", "distancia", "tempo", "pace_str", "tipo"]].copy()
            top.columns = ["Data", "Distância (km)", "Tempo (min)", "Pace", "Tipo"]
            top["Data"] = top["Data"].dt.strftime("%d/%m/%Y")
            st.dataframe(top, use_container_width=True, hide_index=True)

        st.markdown("##### Estatísticas Completas")
        m = metricas_gerais(df)
        stats = {
            "Total de Quilômetros": f"{m['total_km']} km",
            "Total de Corridas": m["total_corridas"],
            "Tempo Total": f"{int(m['total_tempo'] // 60)}h {int(m['total_tempo'] % 60)}min",
            "Distância Média": f"{m['media_distancia']} km",
            "Maior Distância": f"{m['maior_distancia']} km",
            "Pace Médio": formatar_pace(m["pace_medio"]),
            "Melhor Pace": formatar_pace(m["melhor_pace"]),
            "Pace mais Lento": formatar_pace(m["pior_pace"]),
        }
        col1, col2 = st.columns(2)
        items = list(stats.items())
        for k, v in items[:4]:
            col1.metric(k, v)
        for k, v in items[4:]:
            col2.metric(k, v)


def pagina_previsao():
    st.markdown('<div class="section-header">🏁 Previsão de Tempos de Prova</div>', unsafe_allow_html=True)

    historico = carregar_historico()
    df = historico_para_dataframe(historico)

    if df.empty:
        st.info("Registre corridas para gerar sua previsão de provas.")
        return

    previsao = prever_tempos_prova(df)
    if previsao is None:
        st.info("Registre ao menos uma corrida com distância e pace válidos (≥ 1 km) para gerar a previsão.")
        return

    st.markdown(f"""
    <div class="card" style="margin-bottom:1.5rem;">
        <div style="color:#a0aec0; font-size:0.9rem;">
            Previsão calculada a partir do seu melhor desempenho registrado:
            <b style="color:#FF6B35;">{previsao['baseline_distancia']} km</b> a
            <b style="color:#00D4AA;">{previsao['baseline_pace_fmt']} min/km</b>
            em {previsao['baseline_data'].strftime('%d/%m/%Y')}.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(grafico_previsao_provas(previsao["previsoes"]), use_container_width=True)

    cols = st.columns(len(previsao["previsoes"]))
    for col, p in zip(cols, previsao["previsoes"]):
        col.metric(p["prova"], p["tempo_fmt"], help=f"Pace previsto: {p['pace_fmt']} min/km")

    st.caption(
        "⚠️ Estimativa baseada na fórmula de Riegel (T2 = T1 × (D2/D1)^1.06), "
        "amplamente usada em ciência do esporte para prever desempenho entre distâncias. "
        "Resultados reais variam conforme treino específico, clima e estratégia de prova."
    )


def pagina_insights():
    st.markdown('<div class="section-header">💡 Insights Automáticos</div>', unsafe_allow_html=True)

    historico = carregar_historico()
    df = historico_para_dataframe(historico)
    insights = gerar_insights(df)

    if not insights:
        st.info("Registre mais corridas para receber insights.")
        return

    for insight in insights:
        css_class = f"insight-{insight['tipo']}"
        st.markdown(f"""
        <div class="insight-card {css_class}">
            <div class="insight-icon">{insight['icone']}</div>
            <div class="insight-title">{insight['titulo']}</div>
            <div class="insight-desc">{insight['descricao']}</div>
            <div style="clear:both;"></div>
        </div>
        """, unsafe_allow_html=True)

    if not df.empty:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("##### Recomendações")

        m = metricas_gerais(df)
        semanal = metricas_semanais(df)

        recs = []
        if m["total_corridas"] < 3:
            recs.append("🎯 Tente correr pelo menos 3 vezes por semana para construir uma base sólida.")
        if m["pace_medio"] > 7:
            recs.append("🐢 Seu pace médio está alto. Tente incluir treinos intervalados para melhorar a velocidade.")
        if not semanal.empty and semanal.iloc[-1]["km_total"] < 10:
            recs.append("📈 Aumente gradualmente o volume semanal. A regra dos 10%: não aumente mais que 10% por semana.")
        if m["maior_distancia"] < 10:
            recs.append("🏃 Considere incluir um longão semanal para aumentar sua resistência aeróbica.")

        recs.append("💧 Mantenha-se hidratado: beba água antes, durante e depois do treino.")
        recs.append("😴 Priorize o descanso: 1-2 dias de folga por semana são essenciais para a recuperação.")

        for rec in recs:
            st.markdown(f"""<div class="card" style="padding: 1rem 1.2rem; font-size: 0.92rem;">
                {rec}
            </div>""", unsafe_allow_html=True)


def pagina_chatbot():
    st.markdown('<div class="section-header">🤖 Chatbot de Corrida</div>', unsafe_allow_html=True)

    ai = AIClient()
    ia_ativa = ai.ia_ativada()

    col1, col2 = st.columns([3, 1])
    with col1:
        if ia_ativa:
            st.markdown('<span style="color: #00D4AA; font-size: 0.85rem;">● IA Ativa (Ollama)</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span style="color: #a0aec0; font-size: 0.85rem;">● Modo Local (base de conhecimento)</span>', unsafe_allow_html=True)
    with col2:
        config = carregar_config()
        if st.toggle("IA", value=config.get("ia_ativada", False), key="ia_toggle"):
            config["ia_ativada"] = True
        else:
            config["ia_ativada"] = False
        salvar_config(config)

    if "mensagens_chat" not in st.session_state:
        st.session_state.mensagens_chat = [
            {"role": "assistant", "content": "Olá! Sou seu assistente de corrida. Posso ajudar com:\n\n• Dúvidas sobre treino, nutrição e lesões\n• Registrar corridas por texto natural\n• Consultar suas estatísticas\n\nComo posso ajudar?"}
        ]

    for msg in st.session_state.mensagens_chat:
        with st.chat_message(msg["role"], avatar="🏃" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Digite sua mensagem..."):
        st.session_state.mensagens_chat.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        tipo = classificar(prompt)

        if tipo == "calculo":
            resposta = _processar_calculo(prompt)
        elif tipo == "comando":
            resposta = _processar_comando(prompt)
        elif tipo == "conhecimento":
            resposta = _buscar_resposta(prompt)
        elif ai.ia_ativada():
            with st.spinner("Pensando..."):
                conversas = carregar_conversas()
                resposta_ia = ai.responder(prompt, conversas[-5:] if conversas else [])
                resposta = resposta_ia or _buscar_resposta(prompt)
        else:
            resposta = _buscar_resposta(prompt)

        st.session_state.mensagens_chat.append({"role": "assistant", "content": resposta})
        with st.chat_message("assistant", avatar="🏃"):
            st.markdown(resposta)

        salvar_conversa(prompt, resposta)


def _processar_calculo(mensagem):
    distancia, tempo, pace = extrair_dados_corrida(mensagem)
    if distancia and tempo:
        pace_calc = tempo / distancia
        adicionar_corrida(distancia, tempo, pace_calc)
        return f"✅ **Corrida registrada!**\n\n🏃 Distância: **{distancia} km**\n⏱️ Tempo: **{tempo:.0f} min**\n⚡ Pace: **{formatar_pace(pace_calc)} min/km**"
    if distancia and pace:
        tempo_calc = pace * distancia
        h = int(tempo_calc // 60)
        m = int(tempo_calc % 60)
        tempo_str = f"{h}h{m:02d}min" if h > 0 else f"{m} minutos"
        return f"Com pace de **{formatar_pace(pace)}** e distância de **{distancia} km**, tempo estimado: **{tempo_str}**."
    if tempo and pace:
        dist_calc = tempo / pace
        return f"Com pace de **{formatar_pace(pace)}** em **{tempo:.0f} min**, você corre **{dist_calc:.1f} km**."
    if distancia:
        return f"Distância detectada: **{distancia} km**. Informe também o tempo ou pace."
    if tempo:
        return f"Tempo detectado: **{tempo:.0f} min**. Informe também a distância."
    return "Não consegui extrair os dados. Tente algo como: 'corri 5km em 25min' ou '5km pace 5'."


def _processar_comando(mensagem):
    msg = mensagem.lower()
    historico = carregar_historico()
    if not historico:
        return "Nenhuma corrida registrada ainda."

    if "pace médio" in msg or "pace medio" in msg:
        total_pace = sum(parse_pace(c["pace"]) for c in historico)
        media = total_pace / len(historico)
        return f"Seu pace médio é **{formatar_pace(media)} min/km** ({len(historico)} corridas)."

    if "melhor pace" in msg:
        paces = [parse_pace(c["pace"]) for c in historico if parse_pace(c["pace"]) > 0]
        if paces:
            return f"Seu melhor pace é **{formatar_pace(min(paces))} min/km**."
        return "Sem dados de pace válidos."

    if "pior pace" in msg:
        paces = [parse_pace(c["pace"]) for c in historico if parse_pace(c["pace"]) > 0]
        if paces:
            return f"Seu pace mais lento é **{formatar_pace(max(paces))} min/km**."
        return "Sem dados de pace válidos."

    if "última corrida" in msg or "ultima corrida" in msg:
        u = historico[-1]
        return f"Última corrida: **{u['distancia']} km** em **{u['tempo']} min** (Pace: **{u['pace']}**)."

    if "quantas corridas" in msg:
        return f"Você tem **{len(historico)} corridas** registradas."

    return "Comando não reconhecido. Tente: 'pace médio', 'melhor pace', 'última corrida' ou 'quantas corridas'."


def _buscar_resposta(pergunta):
    conhecimento = carregar_conhecimento()
    pergunta_lower = pergunta.lower()
    for _, dados in conhecimento.items():
        for palavra in dados["palavras_chave"]:
            if palavra.lower() in pergunta_lower:
                return dados["respostas"][0]
    return "Não encontrei uma resposta específica. Tente perguntar sobre: pace, aquecimento, hidratação, tênis, lesões, nutrição, treino, provas ou descanso."


def pagina_conteudo():
    st.markdown('<div class="section-header">📚 Conteúdo Educacional</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📖 Base de Conhecimento", "🎯 Dicas para Corredores", "🎬 Vídeos"])

    with tab1:
        conhecimento = carregar_conhecimento()
        if not conhecimento:
            st.info("Base de conhecimento não encontrada.")
            return

        for topico, dados in conhecimento.items():
            with st.expander(f"{'🏃' if topico in ('pace','treino') else '💡'} {topico.capitalize()}", expanded=False):
                st.markdown(f"**Palavras-chave:** {', '.join(dados['palavras_chave'])}")
                for resp in dados["respostas"]:
                    st.markdown(f"> {resp}")

    with tab2:
        dicas = [
            ("🏁", "Regra dos 10%", "Nunca aumente seu volume de treino semanal em mais de 10%. Isso previne lesões por sobrecarga e permite adaptação gradual do corpo."),
            ("👟", "Troque seu tênis regularmente", "Um tênis de corrida dura entre 500 e 800 km. Após esse período, o amortecimento perde eficiência e o risco de lesões aumenta."),
            ("💧", "Hidratação estratégica", "Beba 500ml de água 2 horas antes de correr. Em corridas acima de 60 minutos, hidrate-se a cada 15-20 minutos com água ou isotônico."),
            ("🍌", "Nutrição pré-treino", "Coma carboidratos de fácil digestão 1-2 horas antes do treino. Banana, aveia ou torrada com geleia são boas opções."),
            ("😴", "Sono é treino", "Seu corpo se recupera e fortalece durante o sono. Dormir 7-9 horas por noite é tão importante quanto o treino em si."),
            ("🔥", "Aquecimento dinâmico", "Substitua alongamentos estáticos por movimentos dinâmicos antes de correr: elevação de joelhos, rotação de quadril e deslocamentos laterais."),
            ("📊", "Monitore seu pace", "Acompanhe a evolução do seu pace ao longo das semanas. Melhorias graduais e consistentes são melhores que picos isolados de performance."),
            ("🧊", "Recuperação ativa", "Nos dias de descanso, faça caminhadas leves ou alongamentos. A recuperação ativa acelera a regeneração muscular."),
            ("🎯", "Treine com propósito", "Cada treino deve ter um objetivo: resistência (longão), velocidade (tiros), manutenção (treino leve) ou recuperação. Evite treinar sem planejamento."),
            ("🏋️", "Fortalecimento muscular", "Inclua 2-3 sessões de fortalecimento por semana. Foque em glúteos, quadríceps, panturrilha e core para prevenir lesões e melhorar performance."),
        ]
        cols = st.columns(2)
        for i, (icone, titulo, desc) in enumerate(dicas):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="feature-card">
                    <div class="feature-icon">{icone}</div>
                    <div class="feature-title">{titulo}</div>
                    <div class="feature-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div class="card" style="margin-bottom: 1.5rem;">
            <div style="font-weight: 600; margin-bottom: 0.3rem;">🎬 Vídeos Educacionais</div>
            <div style="color: #a0aec0; font-size: 0.88rem;">
                Conteúdo selecionado sobre técnica de corrida, treinamento e nutrição esportiva.
            </div>
        </div>
        """, unsafe_allow_html=True)

        videos = [
            {
                "titulo": "Técnica de Corrida para Iniciantes",
                "descricao": "Aprenda os fundamentos da técnica de corrida: postura, cadência, pisada e respiração.",
                "url": "https://www.youtube.com/embed/brFHyOtTwH4",
            },
            {
                "titulo": "Como Melhorar seu Pace",
                "descricao": "Estratégias práticas para evoluir seu ritmo de corrida com segurança e consistência.",
                "url": "https://www.youtube.com/embed/9L2b2khySLE",
            },
            {
                "titulo": "Nutrição para Corredores",
                "descricao": "O que comer antes, durante e depois da corrida para maximizar performance e recuperação.",
                "url": "https://www.youtube.com/embed/1hhGMCnRkbQ",
            },
            {
                "titulo": "Prevenção de Lesões na Corrida",
                "descricao": "Exercícios de fortalecimento e alongamento para prevenir as lesões mais comuns em corredores.",
                "url": "https://www.youtube.com/embed/bMfJEp2juGI",
            },
            {
                "titulo": "Treino Intervalado (HIIT) para Corrida",
                "descricao": "Como usar treinos intervalados para melhorar velocidade e resistência aeróbica.",
                "url": "https://www.youtube.com/embed/DSQzKHGqniA",
            },
            {
                "titulo": "Preparação para Primeira Prova",
                "descricao": "Tudo que você precisa saber para participar da sua primeira corrida de rua com confiança.",
                "url": "https://www.youtube.com/embed/lbfgKmKB-Ks",
            },
        ]

        cols = st.columns(2)
        for i, video in enumerate(videos):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="video-card">
                    <iframe src="{video['url']}" allowfullscreen></iframe>
                    <div class="video-info">
                        <div class="video-title">{video['titulo']}</div>
                        <div class="video-desc">{video['descricao']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ─── MAIN ─────────────────────────────────────────────────

def main():
    injetar_css()
    pagina = navegacao_sidebar()

    rotas = {
        "🏠  Home": pagina_home,
        "📊  Dashboard": pagina_dashboard,
        "➕  Registrar Treino": pagina_registrar,
        "📋  Histórico": pagina_historico,
        "📈  Análise": pagina_analise,
        "🏁  Previsão de Provas": pagina_previsao,
        "💡  Insights": pagina_insights,
        "🤖  Chatbot": pagina_chatbot,
        "📚  Conteúdo": pagina_conteudo,
    }

    renderizar = rotas.get(pagina, pagina_home)
    renderizar()


if __name__ == "__main__":
    main()
