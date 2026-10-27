"""
Checkpoint 5 - Computational Thinking using Python (FIAP)
Pipeline de Integração e Persistência de Dados: Previsão do Tempo

APIs consumidas (gratuitas e sem chave):
  1. Open-Meteo Geocoding API -> nome da cidade -> latitude/longitude
  2. Open-Meteo Forecast API  -> latitude/longitude -> previsão de 7 dias

Integrantes do grupo:
  - Lyvia Correa de Amorim RM:569851
  - Yasmin Souza Silva Martins RM:572102
"""

import os
from datetime import datetime

import oracledb
import requests

# ---------------------------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------------------------
URL_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
URL_FORECAST = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_SEGUNDOS = 10

# Credenciais do Oracle .
# Preencha aqui OU defina as variáveis de ambiente ORACLE_USER, ORACLE_PASSWORD
# e ORACLE_DSN. NUNCA envie a senha real para o Git.
ORACLE_USER = os.getenv("ORACLE_USER",)
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD",)
ORACLE_DSN = os.getenv("ORACLE_DSN", "oracle.----.com.br:XXXX/ORCL")

# ---------------------------------------------------------------------------
# PASSO 2 - CONSUMO DAS APIs (requests)
# ---------------------------------------------------------------------------
def fazer_requisicao(url, parametros):
    """
    Faz um GET na URL informada e trata erros de conexão e de status HTTP.
    Retorna o JSON (dict) em caso de sucesso, ou None em caso de erro.
    """
    try:
        resposta = requests.get(url, params=parametros, timeout=TIMEOUT_SEGUNDOS)
    except requests.exceptions.Timeout:
        print("[ERRO] A API demorou demais para responder (timeout).")
        return None
    except requests.exceptions.ConnectionError:
        print("[ERRO] Falha de conexão. Verifique sua internet.")
        return None
    except requests.exceptions.RequestException as erro:
        print(f"[ERRO] Erro inesperado na requisição: {erro}")
        return None

    # Tratamento dos códigos de status HTTP
    if resposta.status_code == 200:
        try:
            return resposta.json()
        except ValueError:
            print("[ERRO] A resposta da API não é um JSON válido.")
            return None
    elif resposta.status_code == 400:
        print("[ERRO 400] Requisição inválida. Verifique os parâmetros enviados.")
    elif resposta.status_code == 404:
        print("[ERRO 404] Endpoint não encontrado.")
    elif resposta.status_code == 429:
        print("[ERRO 429] Muitas requisições. Aguarde um pouco e tente de novo.")
    elif resposta.status_code >= 500:
        print(f"[ERRO {resposta.status_code}] Erro interno no servidor da API.")
    else:
        print(f"[ERRO {resposta.status_code}] Resposta inesperada da API.")
    return None


def buscar_cidade(nome_cidade):
    """
    API 1 (Geocoding): procura a cidade pelo nome e devolve um dict com
    nome oficial, estado, latitude, longitude e timezone.
    Retorna None se a cidade não for encontrada ou se houver erro.
    """
    parametros = {
        "name": nome_cidade,
        "count": 1,
        "language": "pt",
        "countryCode": "BR",
        "format": "json",
    }
    dados = fazer_requisicao(URL_GEOCODING, parametros)
    if dados is None:
        return None

    # Quando a cidade não existe, a API responde 200 mas SEM a chave "results"
    if "results" not in dados or not dados["results"]:
        print(f"[AVISO] Cidade '{nome_cidade}' não encontrada.")
        return None

    resultado = dados["results"][0]
    return {
        "nome": resultado.get("name"),
        "estado": resultado.get("admin1"),
        "latitude": resultado.get("latitude"),
        "longitude": resultado.get("longitude"),
        "timezone": resultado.get("timezone", "America/Sao_Paulo"),
    }


def buscar_previsao(latitude, longitude, timezone):
    """
    API 2 (Forecast): recebe as coordenadas e devolve uma lista com a previsão
    de cada dia (data, temperatura máxima, mínima e precipitação total).
    Retorna None se houver erro.
    """
    parametros = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": timezone,
    }
    dados = fazer_requisicao(URL_FORECAST, parametros)
    if dados is None:
        return None

    if "daily" not in dados:
        print("[ERRO] A resposta da previsão não trouxe os dados diários.")
        return None

    diario = dados["daily"]
    previsao = []
    for i in range(len(diario["time"])):
        previsao.append({
            "data": diario["time"][i],
            "temp_max": diario["temperature_2m_max"][i],
            "temp_min": diario["temperature_2m_min"][i],
            "precipitacao": diario["precipitation_sum"][i],
        })
    return previsao



# ---------------------------------------------------------------------------
# PASSO 3 - TRANSFORMAÇÕES EM MEMÓRIA
# ---------------------------------------------------------------------------
def calcular_metricas(temp_max, temp_min):
    """
    TRANSFORMAÇÃO 1 (cálculo): temperatura média e amplitude térmica do dia.
      média     = (máxima + mínima) / 2
      amplitude = máxima - mínima
    """
    temp_media = round((temp_max + temp_min) / 2, 1)
    amplitude = round(temp_max - temp_min, 1)
    return temp_media, amplitude


def classificar_dia(temp_media):
    """
    TRANSFORMAÇÃO 2 (categorização): classifica o dia pela temperatura média.
      abaixo de 15 °C        -> Frio
      de 15 °C até 22 °C     -> Agradável  (exclusive 22)
      de 22 °C até 28 °C     -> Quente     (exclusive 28)
      28 °C ou mais          -> Muito quente
    """
    if temp_media < 15:
        return "Frio"
    elif temp_media < 22:
        return "Agradável"
    elif temp_media < 28:
        return "Quente"
    return "Muito quente"


def classificar_chuva(precipitacao_mm):
    """
    TRANSFORMAÇÃO 3 (categorização): classifica a chuva pelo total diário em mm.
      0 mm               -> Sem chuva
      até 5 mm           -> Fraca
      acima de 5 até 25  -> Moderada
      acima de 25 mm     -> Forte
    """
    if precipitacao_mm == 0:
        return "Sem chuva"
    elif precipitacao_mm <= 5:
        return "Fraca"
    elif precipitacao_mm <= 25:
        return "Moderada"
    return "Forte"


def padronizar_texto(texto):
    """
    TRANSFORMAÇÃO 4a (limpeza): remove espaços extras e deixa em MAIÚSCULAS,
    para o mesmo nome sempre ficar igual na chave primária do banco.
    """
    if not texto:
        return "NÃO INFORMADO"
    return " ".join(texto.split()).upper()


def converter_data(data_texto):
    """
    TRANSFORMAÇÃO 4b (formatação): converte 'AAAA-MM-DD' (texto da API)
    para um objeto date do Python, que o Oracle grava na coluna DATE.
    """
    return datetime.strptime(data_texto, "%Y-%m-%d").date()


def transformar_previsao(cidade, previsao):
    """
    Aplica todas as transformações e devolve a lista de registros
    prontos para inserir no Oracle (um dict por dia).
    """
    data_coleta = datetime.now()
    registros = []

    for dia in previsao:
        # Ignora dias com dados incompletos (a API pode devolver None)
        if dia["temp_max"] is None or dia["temp_min"] is None:
            continue

        # Chuva ausente é tratada como 0 mm
        chuva = dia["precipitacao"] if dia["precipitacao"] is not None else 0.0

        temp_media, amplitude = calcular_metricas(dia["temp_max"], dia["temp_min"])

        registros.append({
            "cidade": padronizar_texto(cidade["nome"]),
            "estado": padronizar_texto(cidade["estado"]),
            "latitude": cidade["latitude"],
            "longitude": cidade["longitude"],
            "data_previsao": converter_data(dia["data"]),
            "temp_max": dia["temp_max"],
            "temp_min": dia["temp_min"],
            "temp_media": temp_media,
            "amplitude": amplitude,
            "precipitacao": chuva,
            "classificacao_dia": classificar_dia(temp_media),
            "classificacao_chuva": classificar_chuva(chuva),
            "data_coleta": data_coleta,
        })
    return registros



# ---------------------------------------------------------------------------
# PASSO 4 - PERSISTÊNCIA NO ORACLE (oracledb)
# ---------------------------------------------------------------------------
SQL_CREATE_TABLE = """
CREATE TABLE TB_PREVISAO_TEMPO (
    CIDADE              VARCHAR2(100)  NOT NULL,
    DATA_PREVISAO       DATE           NOT NULL,
    ESTADO              VARCHAR2(100),
    LATITUDE            NUMBER(9,5),
    LONGITUDE           NUMBER(9,5),
    TEMP_MAX            NUMBER(4,1),
    TEMP_MIN            NUMBER(4,1),
    TEMP_MEDIA          NUMBER(4,1),
    AMPLITUDE_TERMICA   NUMBER(4,1),
    PRECIPITACAO_MM     NUMBER(6,1),
    CLASSIFICACAO_DIA   VARCHAR2(20),
    CLASSIFICACAO_CHUVA VARCHAR2(20),
    DATA_COLETA         TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT PK_PREVISAO_TEMPO PRIMARY KEY (CIDADE, DATA_PREVISAO, DATA_COLETA)
)
"""

# Cada execução grava uma NOVA coleta (DATA_COLETA faz parte da PK), então a
# previsão antiga do mesmo dia é mantida e o histórico não é perdido.
SQL_INSERT = """
INSERT INTO TB_PREVISAO_TEMPO
    (CIDADE, DATA_PREVISAO, ESTADO, LATITUDE, LONGITUDE, TEMP_MAX, TEMP_MIN,
     TEMP_MEDIA, AMPLITUDE_TERMICA, PRECIPITACAO_MM, CLASSIFICACAO_DIA,
     CLASSIFICACAO_CHUVA, DATA_COLETA)
VALUES
    (:cidade, :data_previsao, :estado, :latitude, :longitude, :temp_max,
     :temp_min, :temp_media, :amplitude, :precipitacao, :classificacao_dia,
     :classificacao_chuva, :data_coleta)
"""

SQL_SELECT = """
SELECT CIDADE, ESTADO, DATA_PREVISAO, DATA_COLETA, TEMP_MEDIA,
       PRECIPITACAO_MM, CLASSIFICACAO_DIA, CLASSIFICACAO_CHUVA
  FROM TB_PREVISAO_TEMPO
 ORDER BY CIDADE, DATA_PREVISAO, DATA_COLETA
"""

# Compara cada coleta com a coleta anterior do MESMO dia e cidade (função LAG)
SQL_EVOLUCAO = """
SELECT CIDADE, DATA_PREVISAO, DATA_COLETA,
       TEMP_MEDIA,
       TEMP_MEDIA - LAG(TEMP_MEDIA) OVER (
           PARTITION BY CIDADE, DATA_PREVISAO ORDER BY DATA_COLETA) AS VAR_TEMP,
       PRECIPITACAO_MM,
       PRECIPITACAO_MM - LAG(PRECIPITACAO_MM) OVER (
           PARTITION BY CIDADE, DATA_PREVISAO ORDER BY DATA_COLETA) AS VAR_CHUVA
  FROM TB_PREVISAO_TEMPO
 ORDER BY CIDADE, DATA_PREVISAO, DATA_COLETA
"""


def conectar_oracle():
    """Abre a conexão com o Oracle da FIAP. Retorna a conexão ou None se falhar."""
    try:
        conexao = oracledb.connect(
            user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN
        )
        print("[OK] Conectado ao Oracle.")
        return conexao
    except oracledb.Error as erro:
        # Usuário/senha inválidos, serviço inexistente, etc.
        print(f"[ERRO] Não foi possível conectar ao Oracle: {erro}")
        return None
    except OSError as erro:
        # Host não encontrado, sem rede/VPN, porta bloqueada, etc.
        print(f"[ERRO] Falha de rede ao acessar o Oracle (host/DSN, VPN ou internet): {erro}")
        return None


def criar_tabela(conexao):
    """Cria a tabela TB_PREVISAO_TEMPO. Se ela já existir (ORA-00955), segue em frente."""
    try:
        with conexao.cursor() as cursor:
            cursor.execute(SQL_CREATE_TABLE)
        print("[OK] Tabela TB_PREVISAO_TEMPO criada.")
    except oracledb.DatabaseError as erro:
        codigo = erro.args[0].code
        if codigo == 955:
            print("[OK] Tabela TB_PREVISAO_TEMPO já existe.")
        else:
            print(f"[ERRO] Falha ao criar a tabela: {erro}")
            raise


def inserir_previsao(conexao, registros):
    """
    Grava os registros transformados em uma única transação.
    Se qualquer comando falhar, rollback() desfaz tudo; se der certo, commit().
    """
    if not registros:
        print("[AVISO] Nenhum registro para inserir.")
        return False

    try:
        with conexao.cursor() as cursor:
            cursor.executemany(SQL_INSERT, registros)
        conexao.commit()
        print(f"[OK] {len(registros)} registros gravados (commit realizado).")
        return True
    except oracledb.Error as erro:
        conexao.rollback()
        print(f"[ERRO] Falha ao inserir. Rollback executado: {erro}")
        return False