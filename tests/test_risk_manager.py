from src.risk.risk_manager import RiskManager
from src.models.signal import MarketSignal
from src.models.position import Position
import unittest

class TestRiskManager(unittest.TestCase):

    def setUp(self):
        config = {
            'max_positions': 3,
            'capital_protection_threshold': 0.85,
            'max_daily_loss': 0.05
        }
        self.risk_manager = RiskManager(config)

    def test_add_position(self):
        self.risk_manager.add_position(
            symbol='BTCUSDT',
            side='BUY',
            size=0.1,
            entry_price=50000,
            stop_loss=49000,
            take_profit=55000,
            risk_amount=1000
        )
        self.assertIn('BTCUSDT', self.risk_manager.positions)

    def test_remove_position(self):
        self.risk_manager.add_position(
            symbol='BTCUSDT',
            side='BUY',
            size=0.1,
            entry_price=50000,
            stop_loss=49000,
            take_profit=55000,
            risk_amount=1000
        )
        self.risk_manager.remove_position('BTCUSDT')
        self.assertNotIn('BTCUSDT', self.risk_manager.positions)

    def test_can_open_position(self):
        self.risk_manager.add_position(
            symbol='BTCUSDT',
            side='BUY',
            size=0.1,
            entry_price=50000,
            stop_loss=49000,
            take_profit=55000,
            risk_amount=1000
        )
        self.assertFalse(self.risk_manager.can_open_position(None))

    def test_check_capital_protection(self):
        self.risk_manager.add_position(
            symbol='BTCUSDT',
            side='BUY',
            size=0.1,
            entry_price=50000,
            stop_loss=49000,
            take_profit=55000,
            risk_amount=1000
        )
        self.risk_manager.update_position_pnl('BTCUSDT', 48000)  # Simulate a loss
        positions_to_close = self.risk_manager.check_capital_protection()
        self.assertIn('BTCUSDT', positions_to_close)

if __name__ == '__main__':
    unittest.main()