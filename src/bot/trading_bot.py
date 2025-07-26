import sys
import decimal
import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from threading import Thread, Event
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

# Adicionar o diretório pai ao path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Imports dos módulos locais
from models.signal import MarketSignal
from models.position import Position
from models.enums import SignalStrength
from analysis.technical_analyzer import TechnicalAnalyzer
from risk.risk_manager import RiskManager
from data.market_data import MarketDataProvider

logger = logging.getLogger(__name__)

class BinanceTradingBot:
    def _get_min_notional(self, symbol: str) -> float:
        """Obtém o valor mínimo de notional exigido para o símbolo."""
        try:
            info = self.client.get_symbol_info(symbol)
            for f in info['filters']:
                if f['filterType'] == 'MIN_NOTIONAL':
                    return float(f['minNotional'])
        except Exception as e:
            logger.error(f"Erro ao buscar MIN_NOTIONAL do símbolo {symbol}: {e}")
        return 0.0
    def _get_lot_size_info(self, symbol: str):
        """Obtém stepSize, minQty e maxQty do símbolo."""
        try:
            info = self.client.get_symbol_info(symbol)
            for f in info['filters']:
                if f['filterType'] == 'LOT_SIZE':
                    step_size = float(f['stepSize'])
                    min_qty = float(f['minQty'])
                    max_qty = float(f['maxQty'])
                    precision = abs(decimal.Decimal(str(step_size)).as_tuple().exponent)
                    return step_size, min_qty, max_qty, precision
        except Exception as e:
            logger.error(f"Erro ao buscar LOT_SIZE do símbolo {symbol}: {e}")
        return 1e-6, 1e-6, 1e6, 6  # valores padrão
    """Bot de trading automatizado para Binance"""
    
    def __init__(self, config):
        self.config = config
        self.client = None
        self.is_running = False
        self.stop_event = Event()
        
        # Componentes principais
        self.technical_analyzer = TechnicalAnalyzer(config)
        self.risk_manager = RiskManager(config, self)
        self.market_data = None
        
        # Estado do bot
        self.symbols_to_analyze = []
        self.last_analysis_time = {}
        self.execution_errors = []
        
        # Inicializar cliente Binance
        self._initialize_client()
        
    def _initialize_client(self):
        """Inicializa o cliente da Binance"""
        try:
            if not self.config.api_key or not self.config.api_secret:
                raise ValueError("API Key e Secret são obrigatórios")
            
            self.client = Client(
                api_key=self.config.api_key,
                api_secret=self.config.api_secret,
                testnet=getattr(self.config, 'testnet', True)  # Usar testnet por padrão
            )
            
            # Testar conexão
            account_info = self.client.get_account()
            logger.info("✅ Cliente Binance inicializado com sucesso")
            
            # Inicializar market data provider
            self.market_data = MarketDataProvider(self.client, self.config)
            
            # Atualizar informações de capital
            self._update_capital_info()
            
        except Exception as e:
            logger.error(f"❌ Erro inicializando cliente Binance: {e}")
            raise
    
    def _update_capital_info(self):
        """Atualiza informações de capital"""
        try:
            account = self.client.get_account()
            usdt_balance = 0
            
            for balance in account['balances']:
                if balance['asset'] == 'USDT':
                    usdt_balance = float(balance['free'])
                    break
            
            self.risk_manager.update_capital(usdt_balance, usdt_balance)
            logger.info(f"Capital atualizado: {usdt_balance:.2f} USDT")
            
        except Exception as e:
            logger.error(f"Erro atualizando capital: {e}")
    
    def start(self):
        """Inicia o bot de trading"""
        try:
            if self.is_running:
                logger.warning("Bot já está rodando")
                return
            
            logger.info("🚀 Iniciando Bot de Trading...")
            self.is_running = True
            self.stop_event.clear()
            
            # Obter símbolos para análise
            self._update_symbols_list()
            
            # Thread principal do bot
            bot_thread = Thread(target=self._main_loop, daemon=True)
            bot_thread.start()
            
            logger.info("✅ Bot iniciado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro iniciando bot: {e}")
            self.is_running = False
            raise
    
    def stop(self):
        """Para o bot de trading"""
        logger.info("🛑 Parando Bot de Trading...")
        self.is_running = False
        self.stop_event.set()
        logger.info("✅ Bot parado")
    
    def run(self):
        """Executa o bot de forma síncrona (bloqueia até ser interrompido)"""
        try:
            logger.info("🤖 Iniciando Bot de Trading (modo síncrono)")
            
            # Iniciar o bot
            self.start()
            
            # Manter o programa rodando até ser interrompido
            logger.info("▶️ Bot rodando... Pressione Ctrl+C para parar")
            
            while self.is_running:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("\n🛑 Interrupção detectada...")
                    break
            
        except Exception as e:
            logger.error(f"❌ Erro executando bot: {e}")
            raise
        finally:
            # Garantir que o bot seja parado
            if self.is_running:
                self.stop()
            logger.info("🏁 Execução finalizada")
    
    def _main_loop(self):
        """Loop principal do bot"""
        logger.info("🔄 Iniciando loop principal do bot")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                logger.info("📊 Executando ciclo de análise...")
                
                # Atualizar informações de capital
                self._update_capital_info()
                
                # Verificar posições existentes
                self._monitor_positions()
                
                # Verificar proteção de capital
                self._check_risk_protection()
                
                # Procurar novos sinais se possível abrir posições
                if self.risk_manager.can_open_position():
                    logger.info("🔍 Procurando novos sinais de trading...")
                    self._scan_for_signals()
                else:
                    logger.info("⏸️ Máximo de posições atingido ou proteção ativa")
                
                logger.info(f"⏰ Aguardando próximo ciclo (60 segundos)...")
                
                # Aguardar antes da próxima iteração
                if self.stop_event.wait(60):  # 1 minuto entre ciclos
                    break
                    
            except Exception as e:
                logger.error(f"❌ Erro no loop principal: {e}")
                logger.info("⏳ Aguardando 30 segundos antes de tentar novamente...")
                time.sleep(30)  # Aguardar 30s em caso de erro
        
        logger.info("🏁 Loop principal finalizado")
    
    def _update_symbols_list(self):
        """Atualiza lista de símbolos para análise"""
        try:
            if not self.market_data:
                logger.warning("Market data provider não inicializado")
                return
            
            # Obter símbolos USDT com volume suficiente
            symbols = self.market_data.get_top_volume_symbols(
                quote_asset='USDT',
                min_volume=self.config.min_volume_usdt,
                limit=50
            )
            
            self.symbols_to_analyze = symbols
            logger.info(f"📈 Símbolos para análise: {len(symbols)} ({', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''})")
            
        except Exception as e:
            logger.error(f"❌ Erro atualizando lista de símbolos: {e}")
            # Usar símbolos padrão em caso de erro
            self.symbols_to_analyze = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']
            logger.info(f"📈 Usando símbolos padrão: {self.symbols_to_analyze}")
    
    def _scan_for_signals(self):
        """Escaneia símbolos em busca de sinais de trading"""
        signals_found = 0
        
        for symbol in self.symbols_to_analyze:
            try:
                # Verificar se já analisou recentemente
                if self._should_skip_analysis(symbol):
                    continue
                
                logger.debug(f"🔍 Analisando {symbol}...")
                
                # Analisar símbolo
                signal = self._analyze_symbol(symbol)
                
                if signal and self.risk_manager.can_open_position(signal):
                    # Executar ordem
                    if self._execute_signal(signal):
                        logger.info(f"✅ Sinal executado para {symbol}")
                        signals_found += 1
                        break  # Uma posição por ciclo
                
                # Atualizar tempo da última análise
                self.last_analysis_time[symbol] = datetime.now()
                
            except Exception as e:
                logger.error(f"❌ Erro analisando {symbol}: {e}")
        
        if signals_found == 0:
            logger.info("📊 Nenhum sinal de trading encontrado neste ciclo")
    
    def _should_skip_analysis(self, symbol: str) -> bool:
        """Verifica se deve pular a análise de um símbolo"""
        if symbol not in self.last_analysis_time:
            return False
        
        # Analisar no máximo a cada 5 minutos
        time_diff = datetime.now() - self.last_analysis_time[symbol]
        return time_diff.total_seconds() < 300
    
    def _analyze_symbol(self, symbol: str) -> Optional[MarketSignal]:
        """Analisa um símbolo específico"""
        try:
            # Obter dados de múltiplos timeframes
            klines_data = {}
            
            for timeframe in self.config.timeframes:
                klines = self.client.get_klines(
                    symbol=symbol,
                    interval=timeframe,
                    limit=100
                )
                klines_data[timeframe] = klines
            
            # Análise técnica
            signal = self.technical_analyzer.analyze_symbol(symbol, klines_data)
            
            if signal:
                logger.info(f"📊 Sinal encontrado para {symbol}: {signal.strength.name} (confiança: {signal.confidence:.2%})")
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de {symbol}: {e}")
            return None
    
    def _execute_signal(self, signal: MarketSignal) -> bool:
        """Executa um sinal de trading"""
        try:
            logger.info(f"🎯 Executando sinal para {signal.symbol}")
            
            # Calcular tamanho da posição
            position_size = self.risk_manager._calculate_position_size(signal)
            step_size, min_qty, max_qty, precision = self._get_lot_size_info(signal.symbol)
            # Ajustar para múltiplo de step_size e dentro dos limites
            position_size = max(min_qty, min(position_size, max_qty))
            # Arredondar para múltiplo de step_size
            position_size = float(decimal.Decimal(str(position_size)).quantize(decimal.Decimal(str(step_size))))
            # Formatar quantity como string decimal simples
            quantity_str = format(position_size, f'.{precision}f').rstrip('0').rstrip('.')

            # Verificar notional mínimo
            min_notional = self._get_min_notional(signal.symbol)
            # Usar preço de mercado para cálculo do notional
            try:
                ticker = self.client.get_symbol_ticker(symbol=signal.symbol)
                market_price = float(ticker['price'])
            except Exception:
                market_price = signal.entry_price
            notional = position_size * market_price
            if notional < min_notional:
                logger.warning(f"❌ Notional ({notional}) menor que o mínimo ({min_notional}) para {signal.symbol}")
                return False

            if position_size < min_qty or position_size > max_qty or position_size <= 0:
                logger.warning(f"❌ Tamanho de posição inválido para {signal.symbol}: {position_size}")
                return False

            # No testnet, simular execução da ordem
            if self.config.testnet:
                logger.info(f"🧪 TESTNET: Simulando ordem de compra para {signal.symbol}")
                logger.info(f"   Quantidade: {position_size}")
                logger.info(f"   Preço estimado: {signal.entry_price}")

                # Simular ordem executada
                success = self.risk_manager.add_position(
                    symbol=signal.symbol,
                    side='BUY',
                    size=position_size,
                    entry_price=signal.entry_price,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit,
                    risk_amount=signal.risk_amount
                )

                if success:
                    signal.execute()
                    logger.info(f"✅ Posição simulada criada para {signal.symbol}")

                return success

            else:
                # Executar ordem real
                order = self.client.order_market_buy(
                    symbol=signal.symbol,
                    quantity=quantity_str
                )

                if order['status'] == 'FILLED':
                    # Registrar posição
                    executed_price = float(order['fills'][0]['price']) if order['fills'] else signal.entry_price

                    success = self.risk_manager.add_position(
                        symbol=signal.symbol,
                        side='BUY',
                        size=position_size,
                        entry_price=executed_price,
                        stop_loss=signal.stop_loss,
                        take_profit=signal.take_profit,
                        risk_amount=signal.risk_amount
                    )

                    if success:
                        # Configurar stop loss e take profit
                        self._set_stop_loss_take_profit(signal.symbol, signal.stop_loss, signal.take_profit)
                        signal.execute()
                        return True

                return False
            
        except BinanceAPIException as e:
            logger.error(f"❌ Erro da API Binance executando {signal.symbol}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro executando sinal {signal.symbol}: {e}")
            return False
    
    def _set_stop_loss_take_profit(self, symbol: str, stop_loss: float, take_profit: float):
        """Configura stop loss e take profit"""
        try:
            position = self.risk_manager.positions.get(symbol)
            if not position:
                return
            
            if self.config.testnet:
                logger.info(f"🧪 TESTNET: SL/TP configurados para {symbol} (SL: {stop_loss}, TP: {take_profit})")
                return
            
            # Stop Loss Order (apenas em produção)
            self.client.order_oco_sell(
                symbol=symbol,
                quantity=position.size,
                price=str(take_profit),  # Take Profit
                stopPrice=str(stop_loss * 1.01),  # Stop Price
                stopLimitPrice=str(stop_loss),  # Stop Loss
                stopLimitTimeInForce='GTC'
            )
            
            logger.info(f"✅ Stop Loss e Take Profit configurados para {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Erro configurando SL/TP para {symbol}: {e}")
    
    def _monitor_positions(self):
        """Monitora posições abertas"""
        if not self.risk_manager.positions:
            return
        
        logger.debug(f"👁️ Monitorando {len(self.risk_manager.positions)} posições...")
        
        for symbol in list(self.risk_manager.positions.keys()):
            try:
                # Obter preço atual
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
                
                # Atualizar PnL
                self.risk_manager.update_position_pnl(symbol, current_price)
                
                # Verificar se deve fechar
                should_close, reason = self.risk_manager.should_close_position(symbol)
                
                if should_close:
                    self._close_position(symbol, reason)
                
            except Exception as e:
                logger.error(f"❌ Erro monitorando posição {symbol}: {e}")
    
    def _check_risk_protection(self):
        """Verifica proteção de risco"""
        positions_to_close = self.risk_manager.check_capital_protection()
        
        for symbol in positions_to_close:
            self._close_position(symbol, "Proteção de capital")
    
    def _close_position(self, symbol: str, reason: str):
        """Encerrar uma posição"""
        try:
            position = self.risk_manager.positions.get(symbol)
            if position:
                self.logger.info(f"Encerrando posição em {symbol} por {reason}")
                order = self.exchange.create_market_sell_order(symbol, position.amount)
                self.logger.info(f"Posição encerrada: {order}")
                del self.risk_manager.positions[symbol]
                
                # Emitir atualização via WebSocket
                if hasattr(self, 'app') and hasattr(self.app, 'socketio'):
                    positions = list(self.risk_manager.positions.values())
                    daily_pnl = sum(pos.unrealized_pnl for pos in positions)
                    self.app.socketio.emit('update_positions', {
                        'positions': [pos.to_dict() for pos in positions],
                        'active_positions': len(positions),
                        'daily_pnl': daily_pnl
                    })
        except Exception as e:
            self.logger.error(f"Erro ao encerrar posição: {e}")
            raise e
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do bot"""
        return {
            'is_running': self.is_running,
            'positions': self.risk_manager.get_positions_summary(),
            'symbols_analyzed': len(self.symbols_to_analyze),
            'last_update': datetime.now().isoformat(),
            'errors': self.execution_errors[-10:],  # Últimos 10 erros
            'config': {
                'testnet': self.config.testnet,
                'max_positions': self.config.max_positions,
                'timeframes': self.config.timeframes
            }
        }
    
    def get_balance(self) -> float:
        """Retorna saldo atual"""
        return self.risk_manager.available_capital

# Alias para compatibilidade
TradingBot = BinanceTradingBot