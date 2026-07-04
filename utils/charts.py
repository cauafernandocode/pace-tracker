import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data_manager import formatar_pace

COLORS = {
    "primary": "#FF6B35",
    "secondary": "#00D4AA",
    "accent": "#4B8BFF",
    "warning": "#FFB347",
    "danger": "#FF4B4B",
    "purple": "#8B5CF6",
    "gradient": ["#FF6B35", "#FF8F65", "#FFB347", "#00D4AA", "#4B8BFF", "#8B5CF6"],
}

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#FAFAFA", family="Inter, sans-serif", size=12),
    margin=dict(l=50, r=20, t=50, b=50),
    xaxis=dict(gridcolor="#2D3348", zerolinecolor="#2D3348", showgrid=True),
    yaxis=dict(gridcolor="#2D3348", zerolinecolor="#2D3348", showgrid=True),
    hoverlabel=dict(bgcolor="#1A1F2E", font_size=13, bordercolor="#FF6B35"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#2D3348"),
)


def _aplicar_layout(fig, titulo="", height=400):
    fig.update_layout(**LAYOUT_BASE, title=dict(text=titulo, font=dict(size=16, color="#FAFAFA")), height=height)
    return fig


def grafico_quilometragem_semanal(semanal_df):
    if semanal_df.empty:
        return _fig_vazio("Sem dados semanais")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=semanal_df["semana_label"],
        y=semanal_df["km_total"],
        marker=dict(
            color=semanal_df["km_total"],
            colorscale=[[0, "#FF6B35"], [1, "#00D4AA"]],
            cornerradius=6,
        ),
        text=semanal_df["km_total"].apply(lambda x: f"{x:.0f} km"),
        textposition="outside",
        textfont=dict(color="#FAFAFA", size=11),
        hovertemplate="<b>%{x}</b><br>Distância: %{y:.1f} km<extra></extra>",
    ))
    return _aplicar_layout(fig, "Quilometragem Semanal")


def grafico_quilometragem_mensal(mensal_df):
    if mensal_df.empty:
        return _fig_vazio("Sem dados mensais")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=mensal_df["mes_label"],
        y=mensal_df["km_total"],
        marker=dict(color=COLORS["secondary"], cornerradius=6),
        text=mensal_df["km_total"].apply(lambda x: f"{x:.0f} km"),
        textposition="outside",
        textfont=dict(color="#FAFAFA", size=11),
        hovertemplate="<b>%{x}</b><br>Distância: %{y:.1f} km<extra></extra>",
    ))
    return _aplicar_layout(fig, "Quilometragem Mensal")


def grafico_evolucao_pace(df):
    validos = df[df["pace_num"] > 0].sort_values("data")
    if validos.empty:
        return _fig_vazio("Sem dados de pace")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=validos["data"],
        y=validos["pace_num"],
        mode="lines+markers",
        name="Pace",
        line=dict(color=COLORS["primary"], width=3, shape="spline"),
        marker=dict(size=8, color=COLORS["primary"], line=dict(width=2, color="#FAFAFA")),
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Pace: %{customdata} min/km<extra></extra>",
        customdata=validos["pace_num"].apply(formatar_pace),
    ))
    if len(validos) >= 3:
        media_movel = validos["pace_num"].rolling(window=min(3, len(validos)), min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=validos["data"],
            y=media_movel,
            mode="lines",
            name="Tendência",
            line=dict(color=COLORS["warning"], width=2, dash="dash"),
        ))
    fig.update_yaxes(autorange="reversed", title_text="Pace (min/km)")
    return _aplicar_layout(fig, "Evolução do Pace")


def grafico_frequencia_semanal(freq_df):
    if freq_df.empty:
        return _fig_vazio("Sem dados de frequência")
    cores = [COLORS["primary"] if v == freq_df["corridas"].max() else COLORS["accent"] for v in freq_df["corridas"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=freq_df["dia"],
        y=freq_df["corridas"],
        marker=dict(color=cores, cornerradius=6),
        text=freq_df["corridas"],
        textposition="outside",
        textfont=dict(color="#FAFAFA"),
        hovertemplate="<b>%{x}</b><br>Corridas: %{y}<extra></extra>",
    ))
    return _aplicar_layout(fig, "Frequência por Dia da Semana", height=350)


def grafico_distribuicao_distancia(df):
    if df.empty:
        return _fig_vazio("Sem dados")
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df["distancia"],
        nbinsx=10,
        marker=dict(color=COLORS["purple"], line=dict(color="#FAFAFA", width=1)),
        hovertemplate="Distância: %{x:.1f} km<br>Frequência: %{y}<extra></extra>",
    ))
    fig.update_xaxes(title_text="Distância (km)")
    fig.update_yaxes(title_text="Frequência")
    return _aplicar_layout(fig, "Distribuição de Distâncias", height=350)


def grafico_acumulado(acum_df):
    if acum_df.empty:
        return _fig_vazio("Sem dados acumulados")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=acum_df["data"],
        y=acum_df["km_acumulado"],
        fill="tozeroy",
        mode="lines",
        line=dict(color=COLORS["secondary"], width=3),
        fillcolor="rgba(0,212,170,0.15)",
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Total: %{y:.1f} km<extra></extra>",
    ))
    fig.update_yaxes(title_text="Km Acumulados")
    return _aplicar_layout(fig, "Quilometragem Acumulada")


def grafico_distribuicao_tipo(df):
    if df.empty or "tipo" not in df.columns:
        return _fig_vazio("Sem dados")
    contagem = df["tipo"].value_counts()
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=contagem.index,
        values=contagem.values,
        hole=0.5,
        marker=dict(colors=COLORS["gradient"][:len(contagem)]),
        textinfo="label+percent",
        textfont=dict(size=12, color="#FAFAFA"),
        hovertemplate="<b>%{label}</b><br>Corridas: %{value}<br>Porcentagem: %{percent}<extra></extra>",
    ))
    return _aplicar_layout(fig, "Tipos de Treino", height=350)


def grafico_evolucao_distancia(df):
    if df.empty:
        return _fig_vazio("Sem dados")
    df_sorted = df.sort_values("data")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sorted["data"],
        y=df_sorted["distancia"],
        mode="lines+markers",
        line=dict(color=COLORS["accent"], width=2, shape="spline"),
        marker=dict(size=7, color=COLORS["accent"]),
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Distância: %{y:.1f} km<extra></extra>",
    ))
    fig.update_yaxes(title_text="Distância (km)")
    return _aplicar_layout(fig, "Evolução da Distância")


def grafico_pace_vs_distancia(df):
    validos = df[(df["pace_num"] > 0) & (df["distancia"] > 0)]
    if validos.empty:
        return _fig_vazio("Sem dados")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=validos["distancia"],
        y=validos["pace_num"],
        mode="markers",
        marker=dict(
            size=12,
            color=validos["tempo"],
            colorscale=[[0, "#00D4AA"], [1, "#FF6B35"]],
            showscale=True,
            colorbar=dict(title="Tempo (min)"),
            line=dict(width=1, color="#FAFAFA"),
        ),
        hovertemplate="<b>%{customdata}</b><br>Distância: %{x:.1f} km<br>Pace: %{y:.2f} min/km<extra></extra>",
        customdata=validos["data"].dt.strftime("%d/%m/%Y"),
    ))
    fig.update_xaxes(title_text="Distância (km)")
    fig.update_yaxes(title_text="Pace (min/km)", autorange="reversed")
    return _aplicar_layout(fig, "Pace vs Distância")


def grafico_previsao_provas(previsoes):
    if not previsoes:
        return _fig_vazio("Sem dados suficientes para previsão")
    df = pd.DataFrame(previsoes)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["prova"],
        y=df["pace_num"],
        marker=dict(color=COLORS["gradient"][:len(df)], cornerradius=6),
        text=df["tempo_fmt"],
        textposition="outside",
        textfont=dict(color="#FAFAFA", size=13),
        customdata=df["tempo_fmt"],
        hovertemplate="<b>%{x}</b><br>Pace previsto: %{y:.2f} min/km<br>Tempo estimado: %{customdata}<extra></extra>",
    ))
    fig.update_yaxes(title_text="Pace Previsto (min/km)")
    return _aplicar_layout(fig, "Previsão de Tempos por Distância", height=400)


def _fig_vazio(msg="Sem dados disponíveis"):
    fig = go.Figure()
    fig.add_annotation(
        text=msg, xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False, font=dict(size=16, color="#666"),
    )
    return _aplicar_layout(fig, "", height=300)
