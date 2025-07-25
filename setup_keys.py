#!/usr/bin/env python3
"""
Configurador interativo de API Keys
"""
import os
from dotenv import load_dotenv

def setup_api_keys():
    """Configura API Keys interativamente"""
    
    print("🔧 Configurador de API Keys Binance")
    print("="*40)
    print()
    
    print("📋 Escolha uma opção:")
    print("1. 🧪 Testnet (para testes - dinheiro falso)")
    print("2. 🏦 Mainnet (produção - dinheiro real)")
    print()
    
    choice = input("Digite sua escolha (1 ou 2): ").strip()
    
    if choice == "1":
        print("\n🧪 Configurando TESTNET")
        print("🔗 Crie suas chaves em: https://testnet.binance.vision/")
        testnet = True
    elif choice == "2":
        print("\n🏦 Configurando MAINNET")
        print("⚠️  ATENÇÃO: Use apenas dinheiro que pode perder!")
        print("🔗 Crie suas chaves em: https://www.binance.com/en/my/settings/api-management")
        testnet = False
    else:
        print("❌ Opção inválida!")
        return False
    
    print("\n📝 Instruções para criar API Key:")
    print("1. Acesse o link acima")
    print("2. Faça login na sua conta")
    print("3. Vá em 'API Key' (ou 'API Management')")
    print("4. Clique em 'Create API Key'")
    print("5. Configure as permissões:")
    print("   ✅ Enable Reading")
    print("   ✅ Enable Spot & Margin Trading")
    print("   ❌ Enable Withdrawals (DESMARCADO)")
    print("6. IP Restriction: deixe em branco ou adicione seu IP")
    print("7. Copie API Key e Secret")
    
    input("\n⏳ Pressione Enter quando tiver criado as chaves...")
    
    print("\n🔑 Cole sua API Key:")
    api_key = input("> ").strip()
    
    if not api_key:
        print("❌ API Key não pode estar vazia!")
        return False
    
    print("\n🔐 Cole seu API Secret:")
    api_secret = input("> ").strip()
    
    if not api_secret:
        print("❌ API Secret não pode estar vazio!")
        return False
    
    # Criar arquivo .env
    env_content = f"""# Configurações da API Binance
API_KEY={api_key}
API_SECRET={api_secret}
TESTNET={str(testnet)}

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
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ Arquivo .env criado com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro criando .env: {e}")
        return False
    
    # Testar conexão
    print("\n🧪 Testando conexão...")
    os.system("python test_api.py")
    
    return True

if __name__ == "__main__":
    success = setup_api_keys()
    if success:
        print("\n🎉 Configuração concluída!")
        print("🚀 Execute: python main.py")
    else:
        print("\n❌ Configuração falhou. Tente novamente.")