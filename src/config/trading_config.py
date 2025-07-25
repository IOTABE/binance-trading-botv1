from dataclasses import dataclass
from typing import List
from .settings import Settings

@dataclass
class TradingConfig:
    """Configuração para o bot de trading"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Carregar configurações do arquivo settings
        settings = Settings()
        
        # Configurações de risco
        self.risk_reward_ratio = settings.risk_reward_ratio
        self.stop_loss_ratio = settings.stop_loss_ratio
        self.capital_protection_threshold = settings.capital_protection_threshold
        self.max_daily_loss = settings.max_daily_loss
        
        # Configurações de trading
        self.timeframes = settings.timeframes
        self.min_volume_usdt = settings.min_volume_usdt
        self.max_positions = settings.max_positions
        
        # Parâmetros de indicadores técnicos
        self.rsi_period = settings.rsi_period
        self.macd_fast = settings.macd_fast
        self.macd_slow = settings.macd_slow
        self.macd_signal = settings.macd_signal
        self.bb_period = settings.bb_period
        self.bb_std = settings.bb_std
        
        # Configurações de análise
        self.min_confidence = getattr(settings, 'min_confidence', 0.6)
        self.max_spread = getattr(settings, 'max_spread', 0.5)
        
        # Configurações de risco por trade
        self.max_risk_per_trade = getattr(settings, 'max_risk_per_trade', 0.02)
        
        # Configurações do ambiente
        self.testnet = getattr(settings, 'testnet', True)
        self.debug_mode = getattr(settings, 'debug_mode', False)
    
    @classmethod
    def from_settings(cls, settings: Settings = None):
        """Cria configuração a partir do arquivo de settings"""
        if settings is None:
            settings = Settings()
        
        return cls(
            api_key=settings.api_key,
            api_secret=settings.api_secret
        )
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'api_key': self.api_key[:8] + '...' if self.api_key else None,  # Mascarar chave
            'api_secret': '***' if self.api_secret else None,  # Mascarar secret
            'risk_reward_ratio': self.risk_reward_ratio,
            'stop_loss_ratio': self.stop_loss_ratio,
            'capital_protection_threshold': self.capital_protection_threshold,
            'max_daily_loss': self.max_daily_loss,
            'timeframes': self.timeframes,
            'min_volume_usdt': self.min_volume_usdt,
            'max_positions': self.max_positions,
            'rsi_period': self.rsi_period,
            'macd_fast': self.macd_fast,
            'macd_slow': self.macd_slow,
            'macd_signal': self.macd_signal,
            'bb_period': self.bb_period,
            'bb_std': self.bb_std,
            'min_confidence': self.min_confidence,
            'max_spread': self.max_spread,
            'max_risk_per_trade': self.max_risk_per_trade,
            'testnet': self.testnet,
            'debug_mode': self.debug_mode
        }