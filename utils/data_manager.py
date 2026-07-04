import json
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _caminho(nome_arquivo):
    return os.path.join(BASE_DIR, nome_arquivo)


def formatar_pace(pace):
    if pace is None or pace <= 0:
        return "0:00"
    minutos = int(pace)
    segundos = int((pace - minutos) * 60)
    return f"{minutos}:{segundos:02d}"


def formatar_tempo(minutos):
    if minutos is None or minutos <= 0:
        return "0:00"
    total_segundos = int(round(minutos * 60))
    horas = total_segundos // 3600
    mins = (total_segundos % 3600) // 60
    segs = total_segundos % 60
    if horas > 0:
        return f"{horas}:{mins:02d}:{segs:02d}"
    return f"{mins}:{segs:02d}"


def parse_pace(pace_str):
    if not pace_str or pace_str == "0:00":
        return 0.0
    try:
        if ":" in str(pace_str):
            partes = str(pace_str).split(":")
            return int(partes[0]) + int(partes[1]) / 60
        return float(pace_str)
    except (ValueError, IndexError):
        return 0.0


def carregar_historico():
    caminho = _caminho("historico.json")
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            historico = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        historico = []

    modificado = False
    hoje = datetime.now()
    for i, corrida in enumerate(historico):
        if "data" not in corrida:
            dias_atras = (len(historico) - i) * 3
            data_sintetica = hoje - timedelta(days=dias_atras)
            corrida["data"] = data_sintetica.strftime("%Y-%m-%d")
            modificado = True
        if "tipo" not in corrida:
            corrida["tipo"] = "Treino"
            modificado = True
        if "notas" not in corrida:
            corrida["notas"] = ""
            modificado = True

    if modificado:
        salvar_historico(historico)

    return historico


def salvar_historico(historico):
    caminho = _caminho("historico.json")
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
    except OSError:
        pass


def adicionar_corrida(distancia, tempo, pace_valor, data=None, tipo="Treino", notas=""):
    historico = carregar_historico()
    corrida = {
        "distancia": round(distancia, 2),
        "tempo": round(tempo, 2),
        "pace": formatar_pace(pace_valor),
        "data": data or datetime.now().strftime("%Y-%m-%d"),
        "tipo": tipo,
        "notas": notas,
    }
    historico.append(corrida)
    salvar_historico(historico)
    return corrida


def deletar_corrida(index):
    historico = carregar_historico()
    if 0 <= index < len(historico):
        removida = historico.pop(index)
        salvar_historico(historico)
        return removida
    return None


def carregar_conhecimento():
    caminho = _caminho("conhecimento.json")
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def carregar_conversas():
    caminho = _caminho("conversas.json")
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def salvar_conversa(pergunta, resposta):
    caminho = _caminho("conversas.json")
    conversas = carregar_conversas()
    conversas.append({
        "pergunta": pergunta,
        "resposta": resposta,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(conversas, f, indent=4, ensure_ascii=False)
    except OSError:
        pass


def carregar_config():
    caminho = _caminho("config.json")
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"ia_ativada": False, "modelo": "llama3.2:1b"}


def salvar_config(config):
    caminho = _caminho("config.json")
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except OSError:
        pass
