import json
import urllib.error
import urllib.request

import pytest

import ai_client


@pytest.fixture(autouse=True)
def isolar_config(tmp_path, monkeypatch):
    monkeypatch.setattr(ai_client, "CAMINHO_CONFIG", str(tmp_path / "config.json"))


class FakeResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._payload


def test_carregar_config_padrao_quando_ausente():
    assert ai_client.carregar_config() == {"ia_ativada": False, "modelo": "llama3.2:1b"}


def test_salvar_e_carregar_config():
    ai_client.salvar_config({"ia_ativada": True, "modelo": "llama3.2:3b"})
    assert ai_client.carregar_config() == {"ia_ativada": True, "modelo": "llama3.2:3b"}


def test_disponivel_true_quando_servidor_responde(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=3: FakeResponse({}))
    cliente = ai_client.AIClient()
    assert cliente.disponivel() is True


def test_disponivel_false_quando_servidor_offline(monkeypatch):
    def levantar_erro(req, timeout=3):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", levantar_erro)
    cliente = ai_client.AIClient()
    assert cliente.disponivel() is False


def test_ia_ativada_depende_do_config_e_disponibilidade(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=3: FakeResponse({}))

    ai_client.salvar_config({"ia_ativada": False, "modelo": "llama3.2:1b"})
    assert ai_client.AIClient().ia_ativada() is False

    ai_client.salvar_config({"ia_ativada": True, "modelo": "llama3.2:1b"})
    assert ai_client.AIClient().ia_ativada() is True


def test_responder_retorna_conteudo_da_mensagem(monkeypatch):
    resposta_esperada = {"message": {"content": "Olá! Como posso ajudar no seu treino?"}}
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=60: FakeResponse(resposta_esperada))

    cliente = ai_client.AIClient()
    assert cliente.responder("oi") == "Olá! Como posso ajudar no seu treino?"


def test_responder_inclui_historico_recente_na_requisicao(monkeypatch):
    capturado = {}

    def fake_urlopen(req, timeout=60):
        capturado["body"] = json.loads(req.data.decode("utf-8"))
        return FakeResponse({"message": {"content": "ok"}})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    historico_recente = [{"pergunta": "qual meu pace?", "resposta": "5:30 min/km"}]
    cliente = ai_client.AIClient()
    cliente.responder("e minha distância total?", historico_recente=historico_recente)

    mensagens = capturado["body"]["messages"]
    assert mensagens[0]["role"] == "system"
    assert {"role": "user", "content": "qual meu pace?"} in mensagens
    assert {"role": "assistant", "content": "5:30 min/km"} in mensagens
    assert mensagens[-1] == {"role": "user", "content": "e minha distância total?"}


def test_responder_trata_erro_de_conexao(monkeypatch):
    def levantar_erro(req, timeout=60):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", levantar_erro)
    cliente = ai_client.AIClient()
    assert cliente.responder("oi").startswith("Erro ao consultar IA:")
