import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

# Adicionar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from models.position import Position
from models.signal import MarketSignal
from models.enums import SignalStrength
import logging

logger = logging.getLogger(__name__)

class RiskManager:
    """Gerenciador de risco para operações de trading"""
    
    def __init__(self, config, bot_instance=None):
        self.config = config
        self.bot_instance = bot_instance
        self.total_capital = 0
        self.available_capital = 0
        self.positions: Dict[str, Position] = {}
        self.daily_trades = 0
        self.daily_pnl = 0
        self.daily_start_capital = 0
        self.max_daily_loss = getattr(config, 'max_daily_loss', 0.05)
        self.max_positions = getattr(config, 'max_positions', 3)
        self.max_risk_per_trade = getattr(config, 'max_risk_per_trade', 0.02)
        self.capital_protection_threshold = getattr(config, 'capital_protection_threshold', 0.85)

    def add_position(self, symbol: str, side: str, size: float, entry_price: float, 
                     stop_loss: float, take_profit: float, risk_amount: float) -> bool:
        """Adiciona uma nova posição"""
        try:
            position = Position(
                symbol=symbol,
                side=side,
                size=size,
                entry_price=entry_price,
                current_price=entry_price,
                unrealized_pnl=0,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_amount=risk_amount,
                timestamp=datetime.now()
            )
            
            self.positions[symbol] = position
            self.daily_trades += 1
            
            logger.info(f"✅ Posição adicionada: {symbol}")
            logger.info(f"   Tamanho: {size}")
            logger.info(f"   Preço de entrada: {entry_price}")
            logger.info(f"   Stop Loss: {stop_loss}")
            logger.info(f"   Take Profit: {take_profit}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro adicionando posição {symbol}: {e}")
            return False

    def update_capital(self, total: float, available: float):
        """Atualiza informações de capital"""
        if self.daily_start_capital == 0:
            self.daily_start_capital = total
            
        self.total_capital = total
        self.available_capital = available

    def can_open_position(self, signal: Optional[MarketSignal] = None) -> bool:
        """Verifica se pode abrir uma nova posição"""
        try:
            # Verificar limite de posições
            if len(self.positions) >= self.max_positions:
                logger.warning(f"Limite de posições atingido: {len(self.positions)}/{self.max_positions}")
                return False
            
            # Verificar perda diária máxima
            if self._check_daily_loss_limit():
                logger.warning("Limite de perda diária atingido")
                return False
            
            # Se não há sinal específico, só verificar limites gerais
            if signal is None:
                return len(self.positions) < self.max_positions
            
            # Verificar se o sinal ainda é válido
            if not signal.is_valid():
                logger.warning(f"Sinal para {signal.symbol} expirado")
                return False
            
            # Calcular tamanho da posição
            position_size = self._calculate_position_size(signal)
            if position_size <= 0:
                logger.warning(f"Tamanho de posição inválido para {signal.symbol}")
                return False
            
            # Verificar capital disponível
            required_capital = position_size * signal.entry_price
            if required_capital > self.available_capital:
                logger.warning(f"Capital insuficiente: {required_capital:.2f} > {self.available_capital:.2f}")
                return False
            
            # Verificar se já existe posição para o símbolo
            if signal.symbol in self.positions:
                logger.warning(f"Posição já existe para {signal.symbol}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro verificando possibilidade de posição: {e}")
            return False

    def _calculate_position_size(self, signal: MarketSignal) -> float:
        """Calcula o tamanho da posição baseado no risco"""
        try:
            # Capital mínimo por trade (1% do disponível ou $10)
            min_entry_usdt = max(10, self.available_capital * 0.01)
            
            # Calcular risco por preço
            price_risk = abs(signal.entry_price - signal.stop_loss)
            
            if price_risk <= 0:
                logger.warning("Risco de preço inválido")
                return 0
            
            # Risco máximo por trade (2% do capital disponível)
            max_risk_usdt = self.available_capital * self.max_risk_per_trade
            
            # Tamanho baseado no risco
            position_size_risk = max_risk_usdt / price_risk
            
            # Tamanho mínimo baseado no valor mínimo
            position_size_min = min_entry_usdt / signal.entry_price
            
            # Tamanho máximo (10% do capital disponível)
            max_position_usdt = self.available_capital * 0.1
            max_position_size = max_position_usdt / signal.entry_price
            
            # Retornar o menor entre os tamanhos calculados
            final_size = min(max(position_size_risk, position_size_min), max_position_size)
            
            logger.info(f"Tamanho calculado para {signal.symbol}: {final_size:.6f}")
            return final_size
            
        except Exception as e:
            logger.error(f"Erro calculando tamanho da posição: {e}")
            return 0

    def _check_daily_loss_limit(self) -> bool:
        """Verifica se o limite de perda diária foi atingido"""
        if self.daily_start_capital == 0:
            return False
        
        current_loss_ratio = abs(self.daily_pnl) / self.daily_start_capital
        return current_loss_ratio >= self.max_daily_loss

    def check_capital_protection(self) -> List[str]:
        """Verifica proteção de capital e retorna posições para fechar"""
        positions_to_close = []
        
        try:
            for symbol, position in self.positions.items():
                # Verificar perda individual da posição
                if position.unrealized_pnl < 0:
                    loss_ratio = abs(position.unrealized_pnl) / self.total_capital
                    
                    # Se a perda da posição excede o limite de proteção de capital
                    if loss_ratio >= (1 - self.capital_protection_threshold):
                        positions_to_close.append(symbol)
                        logger.warning(f"🚨 Proteção de capital acionada para {symbol}: {loss_ratio:.2%}")
            
            # Verificar perda total do dia
            if self._check_daily_loss_limit():
                # Fechar todas as posições em perda
                for symbol, position in self.positions.items():
                    if position.unrealized_pnl < 0 and symbol not in positions_to_close:
                        positions_to_close.append(symbol)
                        logger.warning(f"🚨 Limite diário atingido - fechando {symbol}")
        
        except Exception as e:
            logger.error(f"Erro na verificação de proteção de capital: {e}")
        
        return positions_to_close

    def remove_position(self, symbol: str, realized_pnl: float = 0):
        """Remove uma posição e atualiza estatísticas"""
        if symbol in self.positions:
            position = self.positions[symbol]
            position.close_position(position.current_price, realized_pnl)
            
            # Atualizar PnL diário
            self.daily_pnl += realized_pnl
            
            del self.positions[symbol]
            logger.info(f"Posição {symbol} removida. PnL realizado: {realized_pnl:.2f}")

    def update_position_pnl(self, symbol: str, current_price: float):
        """Atualiza o PnL de uma posição específica"""
        if symbol in self.positions:
            position = self.positions[symbol]
            position.update_price(current_price)
            
            logger.debug(f"PnL atualizado para {symbol}: {position.unrealized_pnl:.2f}")

    def get_total_unrealized_pnl(self) -> float:
        """Retorna o PnL total não realizado"""
        return sum(position.unrealized_pnl for position in self.positions.values())

    def get_total_risk_amount(self) -> float:
        """Retorna o valor total em risco"""
        return sum(position.risk_amount for position in self.positions.values())

    def get_positions_summary(self) -> Dict:
        """Retorna resumo das posições"""
        return {
            'total_positions': len(self.positions),
            'max_positions': self.max_positions,
            'total_unrealized_pnl': self.get_total_unrealized_pnl(),
            'total_risk': self.get_total_risk_amount(),
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'available_capital': self.available_capital,
            'positions': [pos.to_dict() for pos in self.positions.values()]
        }

    def should_close_position(self, symbol: str) -> tuple[bool, str]:
        """Verifica se uma posição deve ser fechada"""
        if symbol not in self.positions:
            return False, "Posição não encontrada"
        
        position = self.positions[symbol]
        
        # Verificar stop loss
        if position.should_close_by_stop_loss():
            return True, "Stop Loss acionado"
        
        # Verificar take profit
        if position.should_close_by_take_profit():
            return True, "Take Profit acionado"
        
        return False, "Posição mantida"

    def reset_daily_stats(self):
        """Reseta estatísticas diárias"""
        self.daily_trades = 0
        self.daily_pnl = 0
        self.daily_start_capital = self.total_capital
        logger.info("Estatísticas diárias resetadas")