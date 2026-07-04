import json

import pytest

from utils import data_manager


@pytest.fixture(autouse=True)
def isolar_arquivos(tmp_path, monkeypatch):
    """Redireciona toda leitura/escrita de JSON para um diretório temporário,
    evitando qualquer contato com os dados reais do usuário."""
    monkeypatch.setattr(data_manager, "BASE_DIR", str(tmp_path))
    return tmp_path


def test_formatar_pace_valor_normal():
    assert data_manager.formatar_pace(5.5) == "5:30"


def test_formatar_pace_zero_ou_negativo():
    assert data_manager.formatar_pace(0) == "0:00"
    assert data_manager.formatar_pace(-1) == "0:00"


def test_formatar_pace_none():
    assert data_manager.formatar_pace(None) == "0:00"


def test_parse_pace_com_dois_pontos():
    assert data_manager.parse_pace("5:30") == 5.5


def test_parse_pace_zero_string():
    assert data_manager.parse_pace("0:00") == 0.0


def test_parse_pace_vazio_ou_none():
    assert data_manager.parse_pace("") == 0.0
    assert data_manager.parse_pace(None) == 0.0


def test_parse_pace_numero_simples():
    assert data_manager.parse_pace("5.5") == 5.5


def test_parse_pace_invalido():
    assert data_manager.parse_pace("abc") == 0.0


def test_formatar_tempo_menos_de_uma_hora():
    assert data_manager.formatar_tempo(23.5) == "23:30"


def test_formatar_tempo_com_horas():
    assert data_manager.formatar_tempo(95) == "1:35:00"


def test_formatar_tempo_zero_ou_negativo():
    assert data_manager.formatar_tempo(0) == "0:00"
    assert data_manager.formatar_tempo(-5) == "0:00"


def test_carregar_historico_arquivo_inexistente():
    assert data_manager.carregar_historico() == []


def test_adicionar_e_carregar_corrida():
    corrida = data_manager.adicionar_corrida(
        distancia=5, tempo=25, pace_valor=5.0,
        data="2026-01-01", tipo="Treino", notas="teste",
    )
    assert corrida == {
        "distancia": 5.0,
        "tempo": 25.0,
        "pace": "5:00",
        "data": "2026-01-01",
        "tipo": "Treino",
        "notas": "teste",
    }

    historico = data_manager.carregar_historico()
    assert historico == [corrida]


def test_deletar_corrida():
    data_manager.adicionar_corrida(5, 25, 5.0, data="2026-01-01")
    data_manager.adicionar_corrida(10, 50, 5.0, data="2026-01-02")

    removida = data_manager.deletar_corrida(0)
    assert removida["data"] == "2026-01-01"

    restante = data_manager.carregar_historico()
    assert len(restante) == 1
    assert restante[0]["data"] == "2026-01-02"


def test_deletar_corrida_indice_invalido():
    data_manager.adicionar_corrida(5, 25, 5.0, data="2026-01-01")
    assert data_manager.deletar_corrida(99) is None
    assert len(data_manager.carregar_historico()) == 1


def test_carregar_historico_preenche_campos_ausentes(isolar_arquivos):
    caminho = isolar_arquivos / "historico.json"
    caminho.write_text(
        json.dumps([{"distancia": 5, "tempo": 25, "pace": "5:00"}]),
        encoding="utf-8",
    )

    historico = data_manager.carregar_historico()
    assert historico[0]["tipo"] == "Treino"
    assert historico[0]["notas"] == ""
    assert "data" in historico[0]

    persistido = json.loads(caminho.read_text(encoding="utf-8"))
    assert persistido[0]["tipo"] == "Treino"


def test_carregar_config_padrao_quando_ausente():
    assert data_manager.carregar_config() == {"ia_ativada": False, "modelo": "llama3.2:1b"}


def test_salvar_e_carregar_config():
    data_manager.salvar_config({"ia_ativada": True, "modelo": "llama3.2:3b"})
    assert data_manager.carregar_config() == {"ia_ativada": True, "modelo": "llama3.2:3b"}


def test_carregar_conhecimento_arquivo_inexistente():
    assert data_manager.carregar_conhecimento() == {}


def test_carregar_conversas_arquivo_inexistente():
    assert data_manager.carregar_conversas() == []


def test_salvar_e_carregar_conversa():
    data_manager.salvar_conversa("oi", "olá! como posso ajudar?")
    conversas = data_manager.carregar_conversas()
    assert len(conversas) == 1
    assert conversas[0]["pergunta"] == "oi"
    assert conversas[0]["resposta"] == "olá! como posso ajudar?"
    assert "data" in conversas[0]
