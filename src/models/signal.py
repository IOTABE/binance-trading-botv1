from datetime import datetime
from typing import Dict, Any, Optional
from .enums import SignalStrength

class MarketSignal:
    """Modelo para sinais de mercado"""
    
    def __init__(self, symbol: str, strength: SignalStrength, confidence: float,
                 entry_price: float, stop_loss: float, take_profit: float,
                 risk_amount: float, analysis_data: Optional[Dict[str, Any]] = None,
                 timestamp: Optional[datetime] = None):
        self.symbol = symbol
        self.strength = strength
        self.confidence = confidence
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.risk_amount = risk_amount
        self.analysis_data = analysis_data or {}
        self.timestamp = timestamp or datetime.now()
        self.is_executed = False
        
    def execute(self):
        """Marca o sinal como executado"""
        self.is_executed = True
    
    def is_valid(self) -> bool:
        """Verifica se o sinal ainda é válido (não muito antigo)"""
        if not self.timestamp:
            return False
        
        # Sinal válido por 5 minutos
        time_diff = datetime.now() - self.timestamp
        return time_diff.total_seconds() < 300
    
    def get_risk_reward_ratio(self) -> float:
        """Calcula a relação risco/recompensa"""
        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.take_profit - self.entry_price)
        
        if risk > 0:
            return reward / risk
        return 0
    
    def to_dict(self) -> dict:
        """Converte sinal para dicionário"""
        return {
            'symbol': self.symbol,
            'strength': self.strength.name,
            'strength_value': self.strength.value,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'risk_amount': self.risk_amount,
            'risk_reward_ratio': self.get_risk_reward_ratio(),
            'analysis_data': self.analysis_data,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_executed': self.is_executed,
            'is_valid': self.is_valid()
        }
    
    def __str__(self) -> str:
        return f"Signal({self.symbol}, {self.strength.name}, {self.confidence:.2f})"