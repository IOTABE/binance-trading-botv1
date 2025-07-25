import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> float:
    """Calcula o RSI (Relative Strength Index)"""
    try:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        # Converter RSI para score (0-1)
        if current_rsi > 70:  # Sobrecomprado
            return 0.2
        elif current_rsi < 30:  # Sobrevendido
            return 0.8
        elif 45 <= current_rsi <= 55:  # Neutro
            return 0.5
        else:
            return 0.6  # Tendência moderada
            
    except Exception:
        return 0.5

def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> float:
    """Calcula o MACD (Moving Average Convergence Divergence)"""
    try:
        exp1 = df['close'].ewm(span=fast).mean()
        exp2 = df['close'].ewm(span=slow).mean()
        
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        # Analisar últimos valores
        current_histogram = histogram.iloc[-1]
        prev_histogram = histogram.iloc[-2]
        
        # Score baseado na direção do histograma
        if current_histogram > prev_histogram and current_histogram > 0:
            return 0.8  # Sinal forte de compra
        elif current_histogram > prev_histogram and current_histogram < 0:
            return 0.7  # Sinal moderado de compra
        elif current_histogram < prev_histogram and current_histogram < 0:
            return 0.2  # Sinal forte de venda
        elif current_histogram < prev_histogram and current_histogram > 0:
            return 0.3  # Sinal moderado de venda
        else:
            return 0.5  # Neutro
            
    except Exception:
        return 0.5

def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> float:
    """Calcula as Bandas de Bollinger"""
    try:
        rolling_mean = df['close'].rolling(window=period).mean()
        rolling_std = df['close'].rolling(window=period).std()
        
        upper_band = rolling_mean + (rolling_std * std_dev)
        lower_band = rolling_mean - (rolling_std * std_dev)
        
        current_price = df['close'].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_middle = rolling_mean.iloc[-1]
        
        # Posição relativa nas bandas
        band_width = current_upper - current_lower
        position = (current_price - current_lower) / band_width
        
        if position > 0.8:  # Próximo da banda superior
            return 0.3  # Sinal de venda
        elif position < 0.2:  # Próximo da banda inferior
            return 0.7  # Sinal de compra
        else:
            return 0.5  # Neutro
            
    except Exception:
        return 0.5

def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict:
    """Calcula o Oscilador Estocástico"""
    try:
        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()
        
        k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        current_k = k_percent.iloc[-1]
        current_d = d_percent.iloc[-1]
        
        # Score baseado nos níveis do estocástico
        if current_k > 80 and current_d > 80:
            score = 0.2  # Sobrecomprado
        elif current_k < 20 and current_d < 20:
            score = 0.8  # Sobrevendido
        else:
            score = 0.5  # Neutro
        
        return {'score': score, 'k': current_k, 'd': current_d}
        
    except Exception:
        return {'score': 0.5, 'k': 50, 'd': 50}

def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
    """Calcula o ATR (Average True Range)"""
    try:
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr.iloc[-1]
        
    except Exception:
        return 0.01  # Valor padrão

def calculate_volume_profile(df: pd.DataFrame) -> Dict:
    """Análise do perfil de volume"""
    try:
        # Volume médio dos últimos 20 períodos
        avg_volume = df['volume'].rolling(window=20).mean()
        current_volume = df['volume'].iloc[-1]
        
        volume_ratio = current_volume / avg_volume.iloc[-1] if avg_volume.iloc[-1] > 0 else 1
        
        # Score baseado no volume
        if volume_ratio > 1.5:
            score = 0.7  # Alto volume, sinal positivo
        elif volume_ratio < 0.5:
            score = 0.3  # Baixo volume, sinal negativo
        else:
            score = 0.5  # Volume normal
        
        return {'score': score, 'volume_ratio': volume_ratio}
        
    except Exception:
        return {'score': 0.5, 'volume_ratio': 1.0}

def calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> Dict:
    """Identifica níveis de suporte e resistência"""
    try:
        # Calcular máximas e mínimas locais
        highs = df['high'].rolling(window=window, center=True).max()
        lows = df['low'].rolling(window=window, center=True).min()
        
        current_price = df['close'].iloc[-1]
        
        # Encontrar níveis de resistência (máximas acima do preço atual)
        resistance_levels = highs[highs > current_price].dropna()
        nearest_resistance = resistance_levels.min() if not resistance_levels.empty else current_price * 1.1
        
        # Encontrar níveis de suporte (mínimas abaixo do preço atual)
        support_levels = lows[lows < current_price].dropna()
        nearest_support = support_levels.max() if not support_levels.empty else current_price * 0.9
        
        # Calcular distâncias percentuais
        resistance_distance = abs(nearest_resistance - current_price) / current_price
        support_distance = abs(current_price - nearest_support) / current_price
        
        return {
            'nearest_resistance': nearest_resistance,
            'nearest_support': nearest_support,
            'resistance_distance': resistance_distance,
            'support_distance': support_distance
        }
        
    except Exception:
        current_price = df['close'].iloc[-1]
        return {
            'nearest_resistance': current_price * 1.05,
            'nearest_support': current_price * 0.95,
            'resistance_distance': 0.05,
            'support_distance': 0.05
        }

def calculate_moving_averages(df: pd.DataFrame) -> Dict:
    """Calcula médias móveis"""
    try:
        ma_9 = df['close'].rolling(window=9).mean()
        ma_21 = df['close'].rolling(window=21).mean()
        ma_50 = df['close'].rolling(window=50).mean()
        
        current_price = df['close'].iloc[-1]
        
        return {
            'ma_9': ma_9.iloc[-1],
            'ma_21': ma_21.iloc[-1],
            'ma_50': ma_50.iloc[-1],
            'price_above_ma_9': current_price > ma_9.iloc[-1],
            'price_above_ma_21': current_price > ma_21.iloc[-1],
            'price_above_ma_50': current_price > ma_50.iloc[-1],
            'ma_9_above_ma_21': ma_9.iloc[-1] > ma_21.iloc[-1],
            'ma_21_above_ma_50': ma_21.iloc[-1] > ma_50.iloc[-1]
        }
        
    except Exception:
        current_price = df['close'].iloc[-1]
        return {
            'ma_9': current_price,
            'ma_21': current_price,
            'ma_50': current_price,
            'price_above_ma_9': True,
            'price_above_ma_21': True,
            'price_above_ma_50': True,
            'ma_9_above_ma_21': True,
            'ma_21_above_ma_50': True
        }