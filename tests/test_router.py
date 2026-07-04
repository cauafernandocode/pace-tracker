from router import classificar, extrair_dados_corrida


def test_classificar_calculo_distancia_e_tempo():
    assert classificar("corri 10km em 50min") == "calculo"


def test_classificar_calculo_com_horas():
    assert classificar("corri 21km em 1h30") == "calculo"


def test_classificar_comando():
    assert classificar("qual meu pace médio?") == "comando"


def test_classificar_conhecimento():
    assert classificar("o que é pace?") == "conhecimento"


def test_classificar_conhecimento_lesao():
    assert classificar("estou com uma lesão no joelho") == "conhecimento"


def test_classificar_conversa_padrao():
    assert classificar("oi, tudo bem?") == "conversa"


def test_extrair_dados_distancia_e_tempo_em_minutos():
    distancia, tempo, pace = extrair_dados_corrida("corri 10km em 50min")
    assert distancia == 10.0
    assert tempo == 50.0
    assert pace is None


def test_extrair_dados_tempo_em_horas_e_minutos():
    distancia, tempo, pace = extrair_dados_corrida("corri 21km em 1h30")
    assert distancia == 21.0
    assert tempo == 90.0


def test_extrair_dados_distancia_com_virgula():
    distancia, _, _ = extrair_dados_corrida("corri 10,5km hoje")
    assert distancia == 10.5


def test_extrair_dados_pace_com_dois_pontos():
    _, _, pace = extrair_dados_corrida("pace 5:30 e distancia 8km")
    assert pace == 5.5


def test_extrair_dados_pace_sem_separador():
    _, _, pace = extrair_dados_corrida("meu pace 6 hoje")
    assert pace == 6.0


def test_extrair_dados_sem_informacao():
    distancia, tempo, pace = extrair_dados_corrida("bom dia")
    assert distancia is None
    assert tempo is None
    assert pace is None
