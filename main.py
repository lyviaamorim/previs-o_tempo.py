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