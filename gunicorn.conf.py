import multiprocessing
import os

# Configurações do servidor
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "eventlet"
worker_connections = 1000
timeout = 300
keepalive = 2

# Configurações de log
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# Configurações do daemon
daemon = False
pidfile = "bot.pid"

# Configurações do Reload
reload = True
reload_extra_files = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/config/settings.py"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/web/templates/base.html"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/web/templates/dashboard.html"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/web/templates/positions.html"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/web/templates/trading.html")
]

# Configurações do WebSocket
websocket_ping_interval = 25
websocket_ping_timeout = 60

# Configurações de SSL/TLS (comente se não estiver usando HTTPS)
# keyfile = "config/ssl/privkey.pem"
# certfile = "config/ssl/fullchain.pem"
