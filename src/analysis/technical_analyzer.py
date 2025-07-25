from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from .indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_stochastic, calculate_atr, calculate_volume_profile,
    calculate_support_resistance
)
from ..models.signal import MarketSignal
from ..models.enums import SignalStrength
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Analisador técnico avançado"""
    
    def __init__(self, config):
        self.config = config
        # Parâmetros padrão para indicadores
        self.rsi_period = getattr(config, 'rsi_period', 14)
        self.macd_fast = getattr(config, 'macd_fast', 12)
        self.macd_slow = getattr(config, 'macd_slow', 26)
        self.macd_signal = getattr(config, 'macd_signal', 9)
        self.bb_period = getattr(config, 'bb_period', 20)
        self.bb_std = getattr(config, 'bb_std', 2)
        
    def analyze_symbol(self, symbol: str, klines_data: dict) -> Optional[MarketSignal]:
        """Análise técnica completa de um símbolo"""
        try:
            combined_signal = self._multi_timeframe_analysis(symbol, klines_data)
            
            if combined_signal['strength'].value >= SignalStrength.MODERATE.value:
                entry_price = combined_signal['entry_price']
                risk_amount = combined_signal['risk_amount']
                
                stop_loss = entry_price - (risk_amount * self.config.stop_loss_ratio)
                take_profit = entry_price + (risk_amount * self.config.risk_reward_ratio)
                
                return MarketSignal(
                    symbol=symbol,
                    strength=combined_signal['strength'],
                    confidence=combined_signal['confidence'],
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    risk_amount=risk_amount,
                    analysis_data=combined_signal['analysis'],
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erro na análise técnica de {symbol}: {e}")
            return None
    
    def _multi_timeframe_analysis(self, symbol: str, klines_data: dict) -> dict:
        """Análise em múltiplos timeframes"""
        timeframe_scores = {}
        
        for timeframe in self.config.timeframes:
            if timeframe in klines_data:
                df = self._prepare_dataframe(klines_data[timeframe])
                score = self._calculate_signal_strength(df)
                timeframe_scores[timeframe] = score
        
        weights = {'15m': 0.2, '1h': 0.3, '4h': 0.5}
        total_score = 0
        total_weight = 0
        
        for tf, score in timeframe_scores.items():
            if tf in weights:
                total_score += score['score'] * weights[tf]
                total_weight += weights[tf]
        
        if total_weight > 0:
            final_score = total_score / total_weight
            strength = self._score_to_strength(final_score)
            
            main_df = self._prepare_dataframe(klines_data['1h'])
            entry_price = main_df['close'].iloc[-1]
            risk_amount = self._calculate_risk_amount(main_df)
            
            return {
                'strength': strength,
                'confidence': final_score,
                'entry_price': entry_price,
                'risk_amount': risk_amount,
                'analysis': timeframe_scores
            }
        
        return {'strength': SignalStrength.VERY_WEAK, 'confidence': 0}
    
    def _prepare_dataframe(self, klines: List) -> pd.DataFrame:
        """Prepara DataFrame com dados OHLCV"""
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col])
        
        return df
    
    def _calculate_signal_strength(self, df: pd.DataFrame) -> dict:
        """Calcula força do sinal baseado em indicadores técnicos"""
        if len(df) < 50:  # Dados insuficientes
            return {'score': 0.0, 'signals': {}}
        
        signals = {}
        
        # Indicadores principais
        signals['rsi'] = calculate_rsi(df, self.rsi_period)
        signals['macd'] = calculate_macd(df, self.macd_fast, self.macd_slow, self.macd_signal)
        signals['bb'] = calculate_bollinger_bands(df, self.bb_period, self.bb_std)
        
        # Indicadores auxiliares
        signals['stochastic'] = calculate_stochastic(df)['score']
        signals['volume'] = calculate_volume_profile(df)['score']
        
        # Análise de suporte e resistência
        sr_analysis = calculate_support_resistance(df)
        signals['support_resistance'] = self._evaluate_support_resistance(df, sr_analysis)
        
        # Pesos para cada indicador
        weights = {
            'rsi': 0.25,
            'macd': 0.25,
            'bb': 0.20,
            'stochastic': 0.15,
            'volume': 0.10,
            'support_resistance': 0.05
        }
        
        # Cálculo da pontuação ponderada
        weighted_score = 0
        total_weight = 0
        
        for indicator, score in signals.items():
            if indicator in weights:
                weighted_score += score * weights[indicator]
                total_weight += weights[indicator]
        
        final_score = weighted_score / total_weight if total_weight > 0 else 0
        
        return {
            'score': final_score,
            'signals': signals
        }
    
    def _evaluate_support_resistance(self, df: pd.DataFrame, sr_data: dict) -> float:
        """Avalia sinal baseado em suporte e resistência"""
        current_price = df['close'].iloc[-1]
        support_distance = sr_data['support_distance']
        resistance_distance = sr_data['resistance_distance']
        
        # Se próximo do suporte, sinal de compra
        if support_distance < 0.02:  # 2% do suporte
            return 0.7
        # Se próximo da resistência, sinal de venda
        elif resistance_distance < 0.02:  # 2% da resistência
            return 0.3
        else:
            return 0.5
    
    def _score_to_strength(self, score: float) -> SignalStrength:
        """Converte score numérico em força do sinal"""
        if score >= 0.8:
            return SignalStrength.VERY_STRONG
        elif score >= 0.65:
            return SignalStrength.STRONG
        elif score >= 0.5:
            return SignalStrength.MODERATE
        elif score >= 0.35:
            return SignalStrength.WEAK
        else:
            return SignalStrength.VERY_WEAK
    
    def _calculate_risk_amount(self, df: pd.DataFrame) -> float:
        """Calcula o valor de risco baseado na volatilidade do mercado"""
        try:
            # Usar ATR para calcular volatilidade
            atr = calculate_atr(df)
            current_price = df['close'].iloc[-1]
            
            # Risco baseado em % do ATR
            risk_percentage = atr / current_price
            
            # Limitar o risco entre 1% e 5%
            risk_amount = max(0.01, min(0.05, risk_percentage)) * current_price
            
            return risk_amount
            
        except Exception as e:
            logger.error(f"Erro no cálculo do risco: {e}")
            # Fallback: 2% do preço atual
            return df['close'].iloc[-1] * 0.02