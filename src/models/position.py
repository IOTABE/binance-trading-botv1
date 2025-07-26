from datetime import datetime
from typing import Optional
from .enums import PositionSide, PositionStatus

class Position:
    """Modelo para representar uma posição de trading"""
    
    def __init__(self, symbol: str, side: str, size: float, entry_price: float,
                 current_price: float, unrealized_pnl: float = 0.0,
                 stop_loss: Optional[float] = None, take_profit: Optional[float] = None,
                 risk_amount: float = 0.0, timestamp: Optional[datetime] = None):
        self.symbol = symbol
        self.side = side
        self.size = size
        self.entry_price = entry_price
        self.current_price = current_price
        self.unrealized_pnl = unrealized_pnl
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.risk_amount = risk_amount
        self.timestamp = timestamp or datetime.now()
        self.status = PositionStatus.OPEN
        self.realized_pnl = 0.0
        
    def update_price(self, new_price: float):
        """Atualiza o preço atual e recalcula PnL"""
        self.current_price = new_price
        self.calculate_unrealized_pnl()
    
    def calculate_unrealized_pnl(self):
        """Calcula o PnL não realizado"""
        if self.side.upper() in ['BUY', 'LONG']:
            self.unrealized_pnl = (self.current_price - self.entry_price) * self.size
        else:  # SELL ou SHORT
            self.unrealized_pnl = (self.entry_price - self.current_price) * self.size
    
    def should_close_by_stop_loss(self) -> bool:
        """Verifica se deve fechar por stop loss"""
        if not self.stop_loss:
            return False
            
        if self.side.upper() in ['BUY', 'LONG']:
            return self.current_price <= self.stop_loss
        else:
            return self.current_price >= self.stop_loss
    
    def should_close_by_take_profit(self) -> bool:
        """Verifica se deve fechar por take profit"""
        if not self.take_profit:
            return False
            
        if self.side.upper() in ['BUY', 'LONG']:
            return self.current_price >= self.take_profit
        else:
            return self.current_price <= self.take_profit
    
    def close_position(self, closing_price: float, realized_pnl: float):
        """Fecha a posição"""
        self.current_price = closing_price
        self.realized_pnl = realized_pnl
        self.unrealized_pnl = 0.0
        self.status = PositionStatus.CLOSED
    
    def to_dict(self) -> dict:
        """Converte posição para dicionário"""
        return {
            'symbol': self.symbol,
            'side': self.side,
            'size': self.size,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'risk_amount': self.risk_amount,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __str__(self) -> str:
        return f"Position({self.symbol}, {self.side}, {self.size}, PnL: {self.unrealized_pnl:.2f})"
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Position':
        """Cria uma instância de Position a partir de um dicionário"""
        # Converter timestamp de string para datetime
        if data.get('timestamp'):
            timestamp = datetime.fromisoformat(data['timestamp'])
        else:
            timestamp = None
            
        # Criar instância
        position = cls(
            symbol=data['symbol'],
            side=data['side'],
            size=data['size'],
            entry_price=data['entry_price'],
            current_price=data['current_price'],
            unrealized_pnl=data['unrealized_pnl'],
            stop_loss=data.get('stop_loss'),
            take_profit=data.get('take_profit'),
            risk_amount=data.get('risk_amount', 0.0),
            timestamp=timestamp
        )
        
        # Atualizar campos adicionais
        position.realized_pnl = data.get('realized_pnl', 0.0)
        position.status = PositionStatus(data.get('status', PositionStatus.OPEN.value))
        
        return position