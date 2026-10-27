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