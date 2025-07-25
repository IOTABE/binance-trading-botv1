from typing import List, Dict, Any
from binance.client import Client
import logging

logger = logging.getLogger(__name__)

class MarketDataProvider:
    """Provedor de dados de mercado da Binance"""
    
    def __init__(self, client: Client, config):
        self.client = client
        self.config = config
    
    def get_top_volume_symbols(self, quote_asset: str = 'USDT', 
                              min_volume: float = 1000000, 
                              limit: int = 50) -> List[str]:
        """Retorna símbolos com maior volume"""
        try:
            # Obter estatísticas de 24h
            tickers = self.client.get_ticker()
            
            # Filtrar por quote asset e volume mínimo
            filtered_symbols = []
            
            for ticker in tickers:
                symbol = ticker['symbol']
                
                # Verificar se termina com o quote asset
                if not symbol.endswith(quote_asset):
                    continue
                
                # Verificar volume mínimo
                volume_usdt = float(ticker['quoteVolume'])
                if volume_usdt < min_volume:
                    continue
                
                # Verificar se não é um símbolo especial (DOWN, UP, BEAR, BULL)
                if any(keyword in symbol for keyword in ['DOWN', 'UP', 'BEAR', 'BULL']):
                    continue
                
                filtered_symbols.append({
                    'symbol': symbol,
                    'volume': volume_usdt,
                    'price_change_percent': float(ticker['priceChangePercent'])
                })
            
            # Ordenar por volume (maior primeiro)
            filtered_symbols.sort(key=lambda x: x['volume'], reverse=True)
            
            # Retornar apenas os símbolos (não os dados completos)
            top_symbols = [item['symbol'] for item in filtered_symbols[:limit]]
            
            logger.info(f"Encontrados {len(top_symbols)} símbolos com volume > {min_volume}")
            return top_symbols
            
        except Exception as e:
            logger.error(f"Erro obtendo símbolos por volume: {e}")
            return []
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List:
        """Obter dados de candlestick"""
        try:
            return self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Erro obtendo klines para {symbol}: {e}")
            return []