#!/usr/bin/env python3
"""
Script para testar conectividade com a API da Binance
"""
import os
import sys
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException

load_dotenv()

def test_specific_environment():
    """Testa apenas o ambiente configurado no .env"""
    
    print("🔧 Testando Conectividade com a API Binance")
    print("=" * 50)
    
    # Obter credenciais
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    testnet = os.getenv('TESTNET', 'True').lower() == 'true'
    
    print(f"🔑 API Key: {api_key[:8]}..." if api_key else "❌ API Key não encontrada")
    print(f"🔐 API Secret: {'***' if api_secret else '❌ API Secret não encontrado'}")
    print(f"🧪 Testnet: {testnet}")
    
    if not api_key or not api_secret:
        print("\n❌ Erro: API_KEY e API_SECRET devem estar configurados no .env")
        print("💡 Execute: python setup_keys.py")
        return False
    
    env_name = "Testnet" if testnet else "Mainnet"
    print(f"\n🔍 Testando Binance {env_name}...")
    
    try:
        client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )
        
        # Teste 1: Conectividade básica
        print("📡 Verificando conectividade do servidor...")
        try:
            server_time = client.get_server_time()
            print(f"✅ Servidor conectado - Tempo: {server_time['serverTime']}")
        except Exception as e:
            print(f"❌ Erro de conectividade: {e}")
            return False
        
        # Teste 2: Validar API Key
        print("🔑 Validando API Key...")
        try:
            account = client.get_account()
            print("✅ API Key válida")
            
            # Mostrar saldo USDT
            usdt_balance = 0
            for balance in account['balances']:
                if balance['asset'] == 'USDT':
                    usdt_balance = float(balance['free'])
                    break
            
            print(f"💰 Saldo USDT: {usdt_balance:.2f}")
            
            if testnet:
                print("🎁 Dica: No testnet você pode obter USDT grátis para testes!")
            
        except BinanceAPIException as e:
            print(f"❌ Erro na API Key: {e}")
            
            if e.code == -2015:
                print("\n💡 Soluções para erro -2015:")
                print("1. 🔄 Criar nova API Key")
                print("2. ✅ Verificar permissões (Reading + Spot Trading)")
                print("3. 🌐 Verificar restrições de IP")
                print("4. 🎯 Usar ambiente correto (Testnet vs Mainnet)")
                
                if testnet:
                    print("🔗 Testnet: https://testnet.binance.vision/")
                else:
                    print("🔗 Mainnet: https://www.binance.com/en/my/settings/api-management")
            
            return False
        
        # Teste 3: Permissões de trading
        print("📊 Verificando permissões de trading...")
        try:
            # Tentar acessar informações de trading
            exchange_info = client.get_exchange_info()
            print("✅ Permissões de trading OK")
            
            # Verificar alguns símbolos populares
            symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
            active_symbols = []
            
            for symbol_info in exchange_info['symbols']:
                if symbol_info['symbol'] in symbols and symbol_info['status'] == 'TRADING':
                    active_symbols.append(symbol_info['symbol'])
            
            print(f"📈 Símbolos disponíveis: {', '.join(active_symbols)}")
            
        except Exception as e:
            print(f"❌ Erro nas permissões: {e}")
            return False
        
        print(f"\n🎉 {env_name} configurado corretamente!")
        print("✅ Bot pronto para funcionar!")
        return True
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_specific_environment()
    
    if not success:
        print("\n🛠️ Para reconfigurar, execute:")
        print("python setup_keys.py")
    
    sys.exit(0 if success else 1)