from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    """Classe para gerenciar configurações do projeto."""
    
    def __init__(self):
        # API Binance
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv("API_SECRET")
        
        # Configurações de risco
        self.risk_reward_ratio = float(os.getenv("RISK_REWARD_RATIO", "4.0"))
        self.stop_loss_ratio = float(os.getenv("STOP_LOSS_RATIO", "3.0"))
        self.capital_protection_threshold = float(os.getenv("CAPITAL_PROTECTION_THRESHOLD", "0.85"))
        self.max_daily_loss = float(os.getenv("MAX_DAILY_LOSS", "0.05"))
        self.max_risk_per_trade = float(os.getenv("MAX_RISK_PER_TRADE", "0.02"))
        
        # Configurações de trading
        self.timeframes = os.getenv("TIMEFRAMES", "15m,1h,4h").split(",")
        self.min_volume_usdt = float(os.getenv("MIN_VOLUME_USDT", "1000000"))
        self.max_positions = int(os.getenv("MAX_POSITIONS", "3"))
        
        # Parâmetros de indicadores técnicos
        self.rsi_period = int(os.getenv("RSI_PERIOD", "14"))
        self.macd_fast = int(os.getenv("MACD_FAST", "12"))
        self.macd_slow = int(os.getenv("MACD_SLOW", "26"))
        self.macd_signal = int(os.getenv("MACD_SIGNAL", "9"))
        self.bb_period = int(os.getenv("BB_PERIOD", "20"))
        self.bb_std = float(os.getenv("BB_STD", "2.0"))
        
        # Configurações de análise
        self.min_confidence = float(os.getenv("MIN_CONFIDENCE", "0.6"))
        self.max_spread = float(os.getenv("MAX_SPREAD", "0.5"))
        
        # Configurações do ambiente
        self.testnet = os.getenv("TESTNET", "True").lower() == "true"
        self.debug_mode = os.getenv("DEBUG_MODE", "False").lower() == "true"
        
        # Configurações do servidor web
        self.web_host = os.getenv("WEB_HOST", "0.0.0.0")
        self.web_port = int(os.getenv("WEB_PORT", "5000"))
        
    def validate(self):
        """Valida se todas as configurações necessárias estão presentes"""
        errors = []
        
        if not self.api_key:
            errors.append("API_KEY não configurada")
        
        if not self.api_secret:
            errors.append("API_SECRET não configurada")
        
        if self.risk_reward_ratio <= 0:
            errors.append("RISK_REWARD_RATIO deve ser maior que 0")
        
        if self.max_positions <= 0:
            errors.append("MAX_POSITIONS deve ser maior que 0")
        
        if errors:
            raise ValueError("Configurações inválidas: " + ", ".join(errors))
        
        return True
    
    def to_dict(self):
        """Retorna configurações como dicionário (mascarando dados sensíveis)"""
        return {
            'api_key': self.api_key[:8] + '...' if self.api_key else None,
            'api_secret': '***' if self.api_secret else None,
            'risk_reward_ratio': self.risk_reward_ratio,
            'stop_loss_ratio': self.stop_loss_ratio,
            'capital_protection_threshold': self.capital_protection_threshold,
            'max_daily_loss': self.max_daily_loss,
            'max_risk_per_trade': self.max_risk_per_trade,
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
            'testnet': self.testnet,
            'debug_mode': self.debug_mode,
            'web_host': self.web_host,
            'web_port': self.web_port
        }
