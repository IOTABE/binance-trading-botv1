#!/bin/bash

echo "🚀 Setup Rápido do Bot de Trading"
echo "================================="
echo ""
echo "📋 Passo 1: Criar API Keys no Testnet"
echo "🔗 Abra: https://testnet.binance.vision/"
echo ""
echo "📝 Instruções:"
echo "1. Faça login com sua conta Binance"
echo "2. Vá em 'API Key' no menu superior"
echo "3. Clique em 'Create API Key'"
echo "4. Dê um nome (ex: 'bot-trading')"
echo "5. Configure as permissões:"
echo "   ✅ Enable Reading"
echo "   ✅ Enable Spot & Margin Trading" 
echo "   ❌ Enable Withdrawals (deixe DESMARCADO)"
echo "6. Deixe IP restriction em branco (ou adicione seu IP)"
echo "7. Copie a API Key e Secret"
echo ""
echo "⏳ Pressione Enter quando tiver criado as chaves..."
read

echo ""
echo "🔑 Digite sua API Key do Testnet:"
read -r API_KEY

echo ""
echo "🔐 Digite seu API Secret do Testnet:"
read -r -s API_SECRET

# Criar arquivo .env
cat > .env << EOF
# Configurações da API Binance - TESTNET
API_KEY=$API_KEY
API_SECRET=$API_SECRET
TESTNET=True

# Configurações de risco
RISK_REWARD_RATIO=4.0
STOP_LOSS_RATIO=3.0
CAPITAL_PROTECTION_THRESHOLD=0.85
MAX_DAILY_LOSS=0.05
MAX_RISK_PER_TRADE=0.02

# Configurações de trading
TIMEFRAMES=15m,1h,4h
MIN_VOLUME_USDT=1000000
MAX_POSITIONS=3

# Parâmetros de indicadores técnicos
RSI_PERIOD=14
MACD_FAST=12
MACD_SLOW=26
MACD_SIGNAL=9
BB_PERIOD=20
BB_STD=2.0

# Configurações de análise
MIN_CONFIDENCE=0.6
MAX_SPREAD=0.5

# Configurações do ambiente
DEBUG_MODE=False

# Configurações do servidor web
WEB_HOST=0.0.0.0
WEB_PORT=5000
EOF

echo ""
echo "✅ Arquivo .env criado!"
echo "🧪 Testando conexão..."

python test_api.py