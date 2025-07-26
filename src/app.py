from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import json
import threading
from datetime import datetime
from config.settings import Settings
from src.bot.trading_bot import TradingBot
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'web', 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'web', 'static'))
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

    # SocketIO para atualizações em tempo real
    socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)
    
    # Instância global do bot
    app.trading_bot = None
    app.bot_thread = None
    
    @app.route('/')
    def dashboard():
        """Dashboard principal"""
        return render_template('dashboard.html')
    
    @app.route('/trading')
    def trading():
        """Página de trading"""
        settings = Settings()
        return render_template('trading.html', settings=settings)
    
    @app.route('/positions')
    def positions():
        """Página de posições"""
        # Exemplo: obtenha as posições do seu bot
        positions = []
        if hasattr(app, 'trading_bot') and app.trading_bot:
            # Supondo que app.trading_bot.risk_manager.positions seja um dict
            positions = list(app.trading_bot.risk_manager.positions.values())
        return render_template('positions.html', positions=positions)
    
    @app.route('/api/start-bot', methods=['POST'])
    def start_bot():
        """Iniciar o bot de trading"""
        global trading_bot, bot_thread
        
        try:
            if app.trading_bot and app.trading_bot.is_running:
                return jsonify({'error': 'Bot já está rodando'}), 400
            
            settings = Settings()
            app.trading_bot = TradingBot(settings)
            
            # Executar bot em thread separada
            app.bot_thread = threading.Thread(target=app.trading_bot.run)
            app.bot_thread.daemon = True
            app.bot_thread.start()
            
            return jsonify({'message': 'Bot iniciado com sucesso'})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stop-bot', methods=['POST'])
    def stop_bot():
        """Parar o bot de trading"""
        global trading_bot
        
        try:
            if app.trading_bot:
                app.trading_bot.stop()
                return jsonify({'message': 'Bot parado com sucesso'})
            else:
                return jsonify({'error': 'Bot não está rodando'}), 400
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/status')
    def bot_status():
        """Status do bot"""
        global trading_bot
        
        if app.trading_bot:
            return jsonify({
            'running': app.trading_bot.is_running if hasattr(app.trading_bot, 'is_running') else False,
            'positions': len(app.trading_bot.positions) if hasattr(app.trading_bot, 'positions') else 0,
            'balance': app.trading_bot.get_balance() if hasattr(app.trading_bot, 'get_balance') else 0,
                'last_update': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'running': False,
                'positions': 0,
                'balance': 0,
                'last_update': datetime.now().isoformat()
            })
    
    @app.route('/api/close-position', methods=['POST'])
    def close_position():
        """Encerrar uma posição manualmente"""
        try:
            data = request.get_json()
            symbol = data.get('symbol')
            
            if not symbol:
                return jsonify({'error': 'Símbolo não informado'}), 400
                
            if not app.trading_bot:
                return jsonify({'error': 'Bot não está ativo'}), 400
            
            app.trading_bot._close_position(symbol, "Encerramento manual")
            return jsonify({'message': f'Posição {symbol} encerrada com sucesso'})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings', methods=['GET', 'POST'])
    def settings_api():
        """Gerenciar configurações"""
        settings = Settings()
        
        if request.method == 'POST':
            # Atualizar configurações (implementar conforme necessário)
            return jsonify({'message': 'Configurações atualizadas'})
        
        return jsonify({
            'risk_reward_ratio': settings.risk_reward_ratio,
            'stop_loss_ratio': settings.stop_loss_ratio,
            'capital_protection_threshold': settings.capital_protection_threshold,
            'max_daily_loss': settings.max_daily_loss,
            'timeframes': settings.timeframes,
            'min_volume_usdt': settings.min_volume_usdt,
            'max_positions': settings.max_positions
        })
    
    # SocketIO Events
    @socketio.on('connect')
    def handle_connect():
        print('Cliente conectado')
        emit('status', {'message': 'Conectado ao servidor'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Cliente desconectado')
    
    app.socketio = socketio
    return app

if __name__ == '__main__':
    app = create_app()
    app.socketio.run(app, debug=True, host='0.0.0.0', port=5000)