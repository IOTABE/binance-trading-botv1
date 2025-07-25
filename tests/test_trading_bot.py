import unittest
from src.bot.trading_bot import BinanceTradingBot
from src.bot.config import TradingConfig

class TestBinanceTradingBot(unittest.TestCase):

    def setUp(self):
        config = TradingConfig(api_key='test_api_key', api_secret='test_api_secret')
        self.bot = BinanceTradingBot(config)

    def test_initialization(self):
        self.assertIsNotNone(self.bot.client)
        self.assertEqual(self.bot.config.api_key, 'test_api_key')
        self.assertEqual(self.bot.config.api_secret, 'test_api_secret')

    def test_start_stop(self):
        self.assertFalse(self.bot.running)
        self.bot.start()
        self.assertTrue(self.bot.running)
        self.bot.stop()
        self.assertFalse(self.bot.running)

    def test_capital_initialization(self):
        self.bot._initialize_capital()
        self.assertGreaterEqual(self.bot.risk_manager.total_capital, 0)
        self.assertGreaterEqual(self.bot.risk_manager.available_capital, 0)

if __name__ == '__main__':
    unittest.main()