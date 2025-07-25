# Binance Trading Bot

Este projeto é um robô de trading desenvolvido para operar na Binance, utilizando análise técnica para identificar oportunidades de compra e venda. O bot é configurável e permite a personalização de diversos parâmetros de trading.

## Estrutura do Projeto

A estrutura do projeto é organizada da seguinte forma:

```
binance-trading-bot
├── src
│   ├── __init__.py
│   ├── bot
│   │   ├── __init__.py
│   │   ├── trading_bot.py         # Classe principal do robô de trading
│   │   └── config.py              # Configurações do robô
│   ├── analysis
│   │   ├── __init__.py
│   │   ├── technical_analyzer.py   # Análise técnica dos símbolos de mercado
│   │   └── indicators.py           # Cálculo de indicadores técnicos
│   ├── risk
│   │   ├── __init__.py
│   │   └── risk_manager.py         # Gerenciamento de risco e posições
│   ├── models
│   │   ├── __init__.py
│   │   ├── position.py             # Representação de uma posição ativa
│   │   ├── signal.py               # Representação de um sinal de mercado
│   │   └── enums.py                # Enumeração de força de sinal
│   └── utils
│       ├── __init__.py
│       └── logger.py               # Configuração de logging
├── tests
│   ├── __init__.py
│   ├── test_trading_bot.py         # Testes para o robô de trading
│   ├── test_analyzer.py            # Testes para o analisador técnico
│   └── test_risk_manager.py        # Testes para o gerenciador de risco
├── config
│   └── settings.py                 # Configurações adicionais
├── logs
│   └── .gitkeep                    # Mantém o diretório de logs no controle de versão
├── requirements.txt                # Dependências do projeto
├── .env.example                    # Exemplo de arquivo de variáveis de ambiente
├── .gitignore                      # Arquivos a serem ignorados pelo Git
├── main.py                         # Ponto de entrada do aplicativo
└── README.md                       # Documentação do projeto
```

## Instalação

1. Clone o repositório:
   ```
   git clone <URL_DO_REPOSITORIO>
   cd binance-trading-bot
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Configure suas credenciais da API da Binance no arquivo `.env` baseado no `.env.example`.

## Uso

Para iniciar o robô de trading, execute o seguinte comando:
```
python main.py
```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto está licenciado sob a MIT License. Veja o arquivo LICENSE para mais detalhes.