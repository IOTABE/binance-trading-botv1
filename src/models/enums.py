from enum import Enum

class SignalStrength(Enum):
    """Força do sinal de trading"""
    VERY_WEAK = 1
    WEAK = 2
    MODERATE = 3
    STRONG = 4
    VERY_STRONG = 5

class PositionSide(Enum):
    """Lado da posição"""
    BUY = "BUY"
    SELL = "SELL"
    LONG = "LONG"
    SHORT = "SHORT"

class OrderStatus(Enum):
    """Status da ordem"""
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    PENDING_CANCEL = "PENDING_CANCEL"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class PositionStatus(Enum):
    """Status da posição"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CLOSING = "CLOSING"