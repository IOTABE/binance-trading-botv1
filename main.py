import sys
import os
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from config.trading_config import TradingConfig
    from src.bot.trading_bot import BinanceTradingBot
except ImportError as e:
    print(f"❌ Erro importando módulos: {e}")
    print("💡 Certifique-se de que todos os arquivos estão no lugar correto")
    sys.exit(1)

def main():
    """Função principal para executar o bot"""
    try:
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger = logging.getLogger(__name__)
        
        # Obter chaves da API do ambiente
        api_key = os.getenv('API_KEY')
        api_secret = os.getenv('API_SECRET')
        
        if not api_key or not api_secret:
            logger.error("❌ API_KEY e API_SECRET devem estar configurados no arquivo .env")
            logger.info("📝 Crie um arquivo .env na raiz do projeto com:")
            logger.info("   API_KEY=sua_chave_api_binance")
            logger.info("   API_SECRET=seu_secret_api_binance")
            return
        
        # Mascarar chaves no log
        masked_key = api_key[:8] + "..." if len(api_key) > 8 else "***"
        logger.info(f"🔑 API Key carregada: {masked_key}")
        
        # Carregar configurações
        logger.info("⚙️ Carregando configurações...")
        config = TradingConfig(api_key=api_key, api_secret=api_secret)
        
        logger.info("🚀 Iniciando Bot de Trading...")
        logger.info(f"📊 Timeframes: {config.timeframes}")
        logger.info(f"💰 Máximo de posições: {config.max_positions}")
        logger.info(f"📈 Risk/Reward: {config.risk_reward_ratio}")
        logger.info(f"🛡️ Modo Testnet: {config.testnet}")
        
        # Iniciar o bot de trading
        trading_bot = BinanceTradingBot(config)
        logger.info("🤖 Bot criado com sucesso")
        
        # Executar o bot
        trading_bot.run()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Interrompido pelo usuário")
        if 'trading_bot' in locals():
            trading_bot.stop()
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        logger.exception("Detalhes do erro:")
        sys.exit(1)

if __name__ == "__main__":
    main()