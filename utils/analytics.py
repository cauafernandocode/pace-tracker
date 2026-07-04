import pandas as pd
from datetime import datetime, timedelta
from utils.data_manager import parse_pace, formatar_pace, formatar_tempo

DISTANCIAS_PROVA = [
    ("5K", 5.0),
    ("10K", 10.0),
    ("21K", 21.0975),
    ("42K", 42.195),
]
EXPOENTE_RIEGEL = 1.06


def historico_para_dataframe(historico):
    if not historico:
        return pd.DataFrame(columns=[
            "data", "distancia", "tempo", "pace_str", "pace_num", "tipo", "notas",
        ])

    df = pd.DataFrame(historico)
    df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d", errors="coerce")
    df["pace_str"] = df["pace"]
    df["pace_num"] = df["pace"].apply(parse_pace)
    df["distancia"] = pd.to_numeric(df["distancia"], errors="coerce")
    df["tempo"] = pd.to_numeric(df["tempo"], errors="coerce")
    df = df.sort_values("data").reset_index(drop=True)
    df["semana"] = df["data"].dt.isocalendar().week.astype(int)
    df["mes"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year
    df["dia_semana"] = df["data"].dt.dayofweek
    df["semana_label"] = df["data"].dt.strftime("Sem %W/%Y")
    df["mes_label"] = df["data"].dt.strftime("%b/%Y")
    return df


def metricas_gerais(df):
    if df.empty:
        return {
            "total_km": 0, "total_corridas": 0, "total_tempo": 0,
            "pace_medio": 0, "melhor_pace": 0, "pior_pace": 0,
            "maior_distancia": 0, "media_distancia": 0,
        }

    validos = df[df["pace_num"] > 0]
    return {
        "total_km": round(df["distancia"].sum(), 1),
        "total_corridas": len(df),
        "total_tempo": round(df["tempo"].sum(), 1),
        "pace_medio": round(validos["pace_num"].mean(), 2) if not validos.empty else 0,
        "melhor_pace": round(validos["pace_num"].min(), 2) if not validos.empty else 0,
        "pior_pace": round(validos["pace_num"].max(), 2) if not validos.empty else 0,
        "maior_distancia": round(df["distancia"].max(), 1),
        "media_distancia": round(df["distancia"].mean(), 1),
    }


def metricas_semanais(df):
    if df.empty:
        return pd.DataFrame()
    grupo = df.groupby("semana_label").agg(
        km_total=("distancia", "sum"),
        corridas=("distancia", "count"),
        pace_medio=("pace_num", lambda x: x[x > 0].mean() if (x > 0).any() else 0),
        tempo_total=("tempo", "sum"),
        inicio=("data", "min"),
    ).reset_index()
    grupo = grupo.sort_values("inicio")
    grupo["km_total"] = grupo["km_total"].round(1)
    grupo["pace_medio"] = grupo["pace_medio"].round(2)
    grupo["pace_fmt"] = grupo["pace_medio"].apply(formatar_pace)
    return grupo


def metricas_mensais(df):
    if df.empty:
        return pd.DataFrame()
    grupo = df.groupby("mes_label").agg(
        km_total=("distancia", "sum"),
        corridas=("distancia", "count"),
        pace_medio=("pace_num", lambda x: x[x > 0].mean() if (x > 0).any() else 0),
        tempo_total=("tempo", "sum"),
        inicio=("data", "min"),
    ).reset_index()
    grupo = grupo.sort_values("inicio")
    grupo["km_total"] = grupo["km_total"].round(1)
    grupo["pace_medio"] = grupo["pace_medio"].round(2)
    grupo["pace_fmt"] = grupo["pace_medio"].apply(formatar_pace)
    return grupo


def frequencia_por_dia_semana(df):
    if df.empty:
        return pd.DataFrame()
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    contagem = df["dia_semana"].value_counts().reindex(range(7), fill_value=0)
    return pd.DataFrame({"dia": dias, "corridas": contagem.values})


def calcular_streak(df):
    if df.empty:
        return {"atual": 0, "melhor": 0}

    datas = sorted(df["data"].dt.date.unique())
    if not datas:
        return {"atual": 0, "melhor": 0}

    melhor = 1
    atual = 1
    for i in range(1, len(datas)):
        diff = (datas[i] - datas[i - 1]).days
        if diff == 1:
            atual += 1
            melhor = max(melhor, atual)
        elif diff > 1:
            atual = 1

    hoje = datetime.now().date()
    ultimo = datas[-1]
    streak_atual = 0
    if (hoje - ultimo).days <= 1:
        streak_atual = 1
        for i in range(len(datas) - 2, -1, -1):
            if (datas[i + 1] - datas[i]).days == 1:
                streak_atual += 1
            else:
                break

    return {"atual": streak_atual, "melhor": melhor}


def evolucao_acumulada(df):
    if df.empty:
        return pd.DataFrame()
    df_sorted = df.sort_values("data").copy()
    df_sorted["km_acumulado"] = df_sorted["distancia"].cumsum().round(1)
    return df_sorted[["data", "km_acumulado"]]


def prever_tempos_prova(df):
    """Prevê tempos de prova para distâncias-padrão a partir do melhor
    desempenho registrado, usando a fórmula de Riegel: T2 = T1 * (D2/D1)^1.06."""
    if df.empty:
        return None

    candidatos = df[(df["pace_num"] > 0) & (df["distancia"] >= 1)]
    if candidatos.empty:
        return None

    baseline = candidatos.loc[candidatos["pace_num"].idxmin()]
    d1 = baseline["distancia"]
    t1 = baseline["pace_num"] * d1

    previsoes = []
    for nome, d2 in DISTANCIAS_PROVA:
        t2 = t1 * (d2 / d1) ** EXPOENTE_RIEGEL
        pace2 = t2 / d2
        previsoes.append({
            "prova": nome,
            "distancia": d2,
            "tempo_min": round(t2, 2),
            "tempo_fmt": formatar_tempo(t2),
            "pace_num": round(pace2, 2),
            "pace_fmt": formatar_pace(pace2),
        })

    return {
        "baseline_distancia": round(d1, 2),
        "baseline_pace_fmt": formatar_pace(baseline["pace_num"]),
        "baseline_data": baseline["data"],
        "previsoes": previsoes,
    }


def gerar_insights(df):
    insights = []
    if df.empty or len(df) < 2:
        insights.append({
            "tipo": "info",
            "icone": "ℹ️",
            "titulo": "Comece a registrar",
            "descricao": "Registre mais corridas para receber insights personalizados sobre seu desempenho.",
        })
        return insights

    metricas = metricas_gerais(df)

    insights.append({
        "tipo": "info",
        "icone": "🏃",
        "titulo": f"{metricas['total_km']} km percorridos",
        "descricao": f"Você completou {metricas['total_corridas']} corridas com uma média de {metricas['media_distancia']} km por treino.",
    })

    melhor = metricas["melhor_pace"]
    if melhor > 0:
        insights.append({
            "tipo": "positivo",
            "icone": "⚡",
            "titulo": f"Melhor pace: {formatar_pace(melhor)} min/km",
            "descricao": f"Seu ritmo mais rápido registrado. Pace médio geral: {formatar_pace(metricas['pace_medio'])} min/km.",
        })

    semanal = metricas_semanais(df)
    if len(semanal) >= 2:
        ultima = semanal.iloc[-1]
        penultima = semanal.iloc[-2]
        if penultima["km_total"] > 0:
            variacao = ((ultima["km_total"] - penultima["km_total"]) / penultima["km_total"]) * 100
            if variacao > 0:
                insights.append({
                    "tipo": "positivo",
                    "icone": "📈",
                    "titulo": f"Volume semanal +{variacao:.0f}%",
                    "descricao": f"Sua quilometragem subiu de {penultima['km_total']} km para {ultima['km_total']} km na última semana.",
                })
            elif variacao < -10:
                insights.append({
                    "tipo": "negativo",
                    "icone": "📉",
                    "titulo": f"Volume semanal {variacao:.0f}%",
                    "descricao": f"Sua quilometragem caiu de {penultima['km_total']} km para {ultima['km_total']} km. Considere manter a consistência.",
                })

    validos = df[df["pace_num"] > 0].sort_values("data")
    if len(validos) >= 4:
        metade = len(validos) // 2
        pace_primeira = validos.iloc[:metade]["pace_num"].mean()
        pace_segunda = validos.iloc[metade:]["pace_num"].mean()
        diff = pace_primeira - pace_segunda
        if diff > 0.1:
            insights.append({
                "tipo": "positivo",
                "icone": "🚀",
                "titulo": "Pace em evolução",
                "descricao": f"Seu ritmo médio melhorou de {formatar_pace(pace_primeira)} para {formatar_pace(pace_segunda)} min/km nas corridas recentes.",
            })
        elif diff < -0.1:
            insights.append({
                "tipo": "negativo",
                "icone": "🐢",
                "titulo": "Pace desacelerando",
                "descricao": f"Seu ritmo médio foi de {formatar_pace(pace_primeira)} para {formatar_pace(pace_segunda)} min/km. Pode ser overtraining ou falta de treinos de velocidade.",
            })

    freq = frequencia_por_dia_semana(df)
    if not freq.empty:
        dia_top = freq.loc[freq["corridas"].idxmax()]
        insights.append({
            "tipo": "info",
            "icone": "📅",
            "titulo": f"Dia favorito: {dia_top['dia']}",
            "descricao": f"Você treina mais às {dia_top['dia']}s, com {int(dia_top['corridas'])} corridas registradas nesse dia.",
        })

    streak = calcular_streak(df)
    if streak["melhor"] >= 2:
        insights.append({
            "tipo": "positivo",
            "icone": "🔥",
            "titulo": f"Maior sequência: {streak['melhor']} dias",
            "descricao": f"Sua melhor sequência de treinos consecutivos. Sequência atual: {streak['atual']} dia(s).",
        })

    mensal = metricas_mensais(df)
    if not mensal.empty:
        melhor_mes = mensal.loc[mensal["km_total"].idxmax()]
        insights.append({
            "tipo": "info",
            "icone": "🏆",
            "titulo": f"Melhor mês: {melhor_mes['mes_label']}",
            "descricao": f"Com {melhor_mes['km_total']} km em {int(melhor_mes['corridas'])} corridas e pace médio de {melhor_mes['pace_fmt']} min/km.",
        })

    return insights
