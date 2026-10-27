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
