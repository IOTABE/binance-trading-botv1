from src.analysis.technical_analyzer import TechnicalAnalyzer
from src.models.signal import MarketSignal
from src.models.enums import SignalStrength
import unittest

class TestTechnicalAnalyzer(unittest.TestCase):

    def setUp(self):
        self.config = {
            'rsi_period': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'bb_period': 20,
            'bb_std': 2.0,
            'timeframes': ['1h', '4h', '15m']
        }
        self.analyzer = TechnicalAnalyzer(self.config)

    def test_analyze_symbol_strong_signal(self):
        # Mock data for a strong signal
        mock_data = {
            '1h': [],  # Add appropriate mock data
            '4h': [],  # Add appropriate mock data
            '15m': []  # Add appropriate mock data
        }
        signal = self.analyzer.analyze_symbol('BTCUSDT', mock_data)
        self.assertIsNotNone(signal)
        self.assertEqual(signal.strength, SignalStrength.STRONG)

    def test_analyze_symbol_weak_signal(self):
        # Mock data for a weak signal
        mock_data = {
            '1h': [],  # Add appropriate mock data
            '4h': [],  # Add appropriate mock data
            '15m': []  # Add appropriate mock data
        }
        signal = self.analyzer.analyze_symbol('BTCUSDT', mock_data)
        self.assertIsNotNone(signal)
        self.assertEqual(signal.strength, SignalStrength.WEAK)

    def test_analyze_symbol_no_signal(self):
        # Mock data for no signal
        mock_data = {
            '1h': [],  # Add appropriate mock data
            '4h': [],  # Add appropriate mock data
            '15m': []  # Add appropriate mock data
        }
        signal = self.analyzer.analyze_symbol('BTCUSDT', mock_data)
        self.assertIsNone(signal)

if __name__ == '__main__':
    unittest.main()