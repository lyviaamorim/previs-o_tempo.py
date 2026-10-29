# Checkpoint 5 — Previsão do Tempo

**FIAP — Análise e Desenvolvimento de Sistemas**
**Disciplina:** Computational Thinking using Python

## Integrantes

* Lyvia Correa de Amorim — RM 569851
* Yasmin Souza Silva Martins — RM 572102

## Sobre o projeto

Este projeto foi desenvolvido para o Checkpoint 5 da FIAP e tem como objetivo consumir dados meteorológicos de APIs públicas, processar as informações em Python e armazenar os resultados em um banco de dados Oracle.

O programa permite pesquisar cidades brasileiras, consultar a previsão do tempo para os próximos dias e manter um histórico das coletas realizadas.

## Tecnologias utilizadas

* Python 3.8 ou superior
* API Open-Meteo Geocoding
* API Open-Meteo Forecast
* Biblioteca Requests
* Biblioteca oracledb
* Oracle SQL
* Git e GitHub

## Funcionalidades

* Pesquisa de cidades brasileiras por nome.
* Consulta de latitude e longitude por meio da Geocoding API.
* Consulta da previsão do tempo para sete dias.
* Cálculo da temperatura média e da amplitude térmica.
* Classificação dos dias conforme a temperatura média.
* Classificação da precipitação diária.
* Limpeza e padronização dos dados.
* Criação da tabela `TB_PREVISAO_TEMPO` no Oracle, caso ela ainda não exista.
* Armazenamento dos registros com controle de transações.
* Consulta do histórico de previsões.
* Comparação das previsões entre diferentes coletas.

## Instalação

É necessário ter Python 3.8 ou superior, acesso à internet e credenciais válidas para o Oracle da FIAP.

### 1. Clonar o repositório

```bash
git clone https://github.com/lyviaamorim/previs-o_tempo.py.git
```

Entre na pasta do projeto:

```bash
cd previs-o_tempo.py
```

### 2. Instalar as dependências

Execute no terminal:

```bash
python -m pip install -r requirements.txt
```

### 3. Configurar o acesso ao Oracle

O programa precisa de credenciais válidas do banco Oracle da FIAP.

No Windows PowerShell, configure as variáveis de ambiente antes de executar o programa:

```powershell
$env:ORACLE_USER = "SEU_RM"
$env:ORACLE_PASSWORD = "SUA_SENHA"
$env:ORACLE_DSN = "oracle.fiap.com.br:1521/ORCL"
```

Substitua `SEU_RM` e `SUA_SENHA` pelos seus dados reais. Não publique sua senha no GitHub.

O acesso ao banco pode depender da conexão à rede ou à VPN da FIAP.

### 4. Executar o programa

No terminal, execute:

```bash
python main.py
```

Digite o nome de uma cidade brasileira quando solicitado.

O programa consultará as APIs, processará a previsão e tentará salvar os registros no Oracle. Depois, permitirá pesquisar outras cidades e exibirá os dados armazenados e a comparação entre coletas.

## Banco de dados

O programa utiliza a tabela `TB_PREVISAO_TEMPO`, criada automaticamente caso não exista.

A tabela armazena informações como:

* Cidade e estado.
* Data da previsão e data da coleta.
* Temperaturas máxima, mínima e média.
* Amplitude térmica.
* Precipitação em milímetros.
* Classificação do dia e da chuva.

A chave primária composta permite manter o histórico das coletas.

## APIs utilizadas

**Geocoding API:** pesquisa a cidade e retorna informações geográficas.

**Forecast API:** utiliza as coordenadas para obter a previsão meteorológica diária.

As APIs são disponibilizadas pela Open-Meteo e não exigem chave de acesso para o uso realizado neste projeto.

## Tratamento de erros

O programa trata falhas de conexão, timeout, respostas HTTP inesperadas, cidades não encontradas e erros relacionados ao acesso ao banco de dados.

As operações de inserção utilizam `commit()` para confirmar as alterações e `rollback()` para desfazê-las em caso de falha.

## Versionamento

O código-fonte é versionado com Git e hospedado no GitHub.

**Repositório:** https://github.com/lyviaamorim/previs-o_tempo.py
