from datetime import datetime, timedelta

import pandas as pd
import pytest

from utils.analytics import (
    calcular_streak,
    evolucao_acumulada,
    frequencia_por_dia_semana,
    gerar_insights,
    historico_para_dataframe,
    metricas_gerais,
    metricas_mensais,
    metricas_semanais,
    prever_tempos_prova,
)


def historico_exemplo():
    return [
        {"data": "2026-01-01", "distancia": 5.0, "tempo": 30.0, "pace": "6:00", "tipo": "Treino", "notas": ""},
        {"data": "2026-01-02", "distancia": 10.0, "tempo": 55.0, "pace": "5:30", "tipo": "Treino", "notas": ""},
        {"data": "2026-02-08", "distancia": 8.0, "tempo": 40.0, "pace": "5:00", "tipo": "Longao", "notas": ""},
    ]


def test_historico_para_dataframe_vazio():
    df = historico_para_dataframe([])
    assert df.empty
    assert list(df.columns) == [
        "data", "distancia", "tempo", "pace_str", "pace_num", "tipo", "notas",
    ]


def test_historico_para_dataframe_colunas_derivadas():
    df = historico_para_dataframe(historico_exemplo())
    assert len(df) == 3
    assert df["pace_num"].tolist() == [6.0, 5.5, 5.0]
    assert df.loc[0, "dia_semana"] == pd.Timestamp("2026-01-01").dayofweek
    assert df.loc[0, "mes"] == 1
    assert df.loc[2, "mes"] == 2


def test_metricas_gerais_vazio():
    df = historico_para_dataframe([])
    metricas = metricas_gerais(df)
    assert metricas == {
        "total_km": 0, "total_corridas": 0, "total_tempo": 0,
        "pace_medio": 0, "melhor_pace": 0, "pior_pace": 0,
        "maior_distancia": 0, "media_distancia": 0,
    }


def test_metricas_gerais_com_dados():
    df = historico_para_dataframe(historico_exemplo())
    metricas = metricas_gerais(df)
    assert metricas["total_km"] == 23.0
    assert metricas["total_corridas"] == 3
    assert metricas["total_tempo"] == 125.0
    assert metricas["melhor_pace"] == 5.0
    assert metricas["pior_pace"] == 6.0
    assert metricas["maior_distancia"] == 10.0
    assert metricas["media_distancia"] == round(23 / 3, 1)


def test_metricas_semanais_soma_bate_com_total():
    df = historico_para_dataframe(historico_exemplo())
    semanal = metricas_semanais(df)
    assert round(semanal["km_total"].sum(), 1) == 23.0
    assert semanal["corridas"].sum() == 3


def test_metricas_mensais_agrupa_por_mes():
    df = historico_para_dataframe(historico_exemplo())
    mensal = metricas_mensais(df)
    assert len(mensal) == 2
    assert round(mensal["km_total"].sum(), 1) == 23.0


def test_metricas_semanais_vazio():
    df = historico_para_dataframe([])
    assert metricas_semanais(df).empty


def test_frequencia_por_dia_semana():
    df = historico_para_dataframe(historico_exemplo())
    freq = frequencia_por_dia_semana(df)
    assert len(freq) == 7
    assert freq["corridas"].sum() == 3


def test_evolucao_acumulada():
    df = historico_para_dataframe(historico_exemplo())
    evolucao = evolucao_acumulada(df)
    assert evolucao["km_acumulado"].is_monotonic_increasing
    assert evolucao["km_acumulado"].iloc[-1] == 23.0


def test_calcular_streak_sem_dados():
    df = historico_para_dataframe([])
    assert calcular_streak(df) == {"atual": 0, "melhor": 0}


def test_calcular_streak_sequencia_ate_hoje():
    hoje = datetime.now()
    historico = [
        {
            "data": (hoje - timedelta(days=i)).strftime("%Y-%m-%d"),
            "distancia": 5.0, "tempo": 30.0, "pace": "6:00",
            "tipo": "Treino", "notas": "",
        }
        for i in range(3)
    ]
    df = historico_para_dataframe(historico)
    streak = calcular_streak(df)
    assert streak["atual"] == 3
    assert streak["melhor"] == 3


def test_calcular_streak_com_gap_nao_conta_atual():
    historico = [
        {"data": "2020-01-01", "distancia": 5.0, "tempo": 30.0, "pace": "6:00", "tipo": "Treino", "notas": ""},
        {"data": "2020-01-02", "distancia": 5.0, "tempo": 30.0, "pace": "6:00", "tipo": "Treino", "notas": ""},
        {"data": "2020-01-10", "distancia": 5.0, "tempo": 30.0, "pace": "6:00", "tipo": "Treino", "notas": ""},
    ]
    df = historico_para_dataframe(historico)
    streak = calcular_streak(df)
    assert streak["melhor"] == 2
    assert streak["atual"] == 0


def test_prever_tempos_prova_vazio():
    df = historico_para_dataframe([])
    assert prever_tempos_prova(df) is None


def test_prever_tempos_prova_sem_pace_valido():
    historico = [
        {"data": "2026-01-01", "distancia": 5.0, "tempo": 30.0, "pace": "0:00", "tipo": "Treino", "notas": ""},
    ]
    df = historico_para_dataframe(historico)
    assert prever_tempos_prova(df) is None


def test_prever_tempos_prova_usa_melhor_pace_como_baseline():
    historico = [
        {"data": "2026-01-01", "distancia": 5.0, "tempo": 27.5, "pace": "5:30", "tipo": "Treino", "notas": ""},
        {"data": "2026-01-05", "distancia": 10.0, "tempo": 50.0, "pace": "5:00", "tipo": "Treino", "notas": ""},
    ]
    df = historico_para_dataframe(historico)
    previsao = prever_tempos_prova(df)

    assert previsao["baseline_distancia"] == 10.0
    assert previsao["baseline_pace_fmt"] == "5:00"

    provas = {p["prova"]: p for p in previsao["previsoes"]}
    assert set(provas) == {"5K", "10K", "21K", "42K"}

    t1 = 5.0 * 10.0
    esperado_5k = t1 * (5.0 / 10.0) ** 1.06
    assert provas["5K"]["tempo_min"] == pytest.approx(esperado_5k, abs=0.01)
    assert provas["10K"]["tempo_min"] == pytest.approx(t1, abs=0.01)

    assert provas["5K"]["tempo_min"] < provas["10K"]["tempo_min"] < provas["21K"]["tempo_min"] < provas["42K"]["tempo_min"]
    assert provas["5K"]["pace_num"] < provas["10K"]["pace_num"] < provas["21K"]["pace_num"] < provas["42K"]["pace_num"]


def test_prever_tempos_prova_ignora_distancias_menores_que_1km():
    historico = [
        {"data": "2026-01-01", "distancia": 0.5, "tempo": 2.0, "pace": "4:00", "tipo": "Treino", "notas": ""},
        {"data": "2026-01-05", "distancia": 5.0, "tempo": 27.5, "pace": "5:30", "tipo": "Treino", "notas": ""},
    ]
    df = historico_para_dataframe(historico)
    previsao = prever_tempos_prova(df)
    assert previsao["baseline_distancia"] == 5.0


def test_gerar_insights_poucos_dados():
    df = historico_para_dataframe([])
    insights = gerar_insights(df)
    assert len(insights) == 1
    assert insights[0]["titulo"] == "Comece a registrar"


def test_gerar_insights_com_dados_suficientes():
    df = historico_para_dataframe(historico_exemplo())
    insights = gerar_insights(df)
    assert len(insights) >= 1
    assert "km percorridos" in insights[0]["titulo"]
