class TradingConfig:
    """Configurações do robô de trading"""
    
    def __init__(self, api_key: str, api_secret: str, risk_reward_ratio: float = 4.0,
                 stop_loss_ratio: float = 3.0, capital_protection_threshold: float = 0.85,
                 max_daily_loss: float = 0.05, timeframes: list = None,
                 min_volume_usdt: float = 1000000, max_positions: int = 3,
                 rsi_period: int = 14, rsi_oversold: float = 30.0,
                 rsi_overbought: float = 70.0, macd_fast: int = 12,
                 macd_slow: int = 26, macd_signal: int = 9,
                 bb_period: int = 20, bb_std: float = 2.0,
                 sma_short: int = 20, sma_long: int = 50,
                 ichimoku_conversion: int = 9, ichimoku_base: int = 26,
                 ichimoku_span_b: int = 52):
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.risk_reward_ratio = risk_reward_ratio
        self.stop_loss_ratio = stop_loss_ratio
        self.capital_protection_threshold = capital_protection_threshold
        self.max_daily_loss = max_daily_loss
        self.timeframes = timeframes if timeframes is not None else ['15m', '1h', '4h']
        self.min_volume_usdt = min_volume_usdt
        self.max_positions = max_positions
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.sma_short = sma_short
        self.sma_long = sma_long
        self.ichimoku_conversion = ichimoku_conversion
        self.ichimoku_base = ichimoku_base
        self.ichimoku_span_b = ichimoku_span_b

    def __post_init__(self):
        """Valida as configurações após a inicialização"""
        if not self.api_key or not self.api_secret:
            raise ValueError("API key and secret must be provided.")
        if self.risk_reward_ratio <= 0:
            raise ValueError("Risk/Reward ratio must be greater than 0.")
        if self.stop_loss_ratio <= 0:
            raise ValueError("Stop Loss ratio must be greater than 0.")
        if self.max_positions <= 0:
            raise ValueError("Max positions must be greater than 0.")
        if not (0 < self.rsi_oversold < 50):
            raise ValueError("RSI oversold value must be between 0 and 50.")
        if not (50 < self.rsi_overbought < 100):
            raise ValueError("RSI overbought value must be between 50 and 100.")
        if self.macd_fast >= self.macd_slow:
            raise ValueError("MACD fast period must be less than slow period.")