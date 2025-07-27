#!/bin/bash

# Criar diretórios de log se não existirem
mkdir -p logs

# Definir variáveis de ambiente
export PYTHONPATH=$PYTHONPATH:$(pwd)
export FLASK_APP=src.app:create_app
export FLASK_ENV=production

# Verificar dependências
echo "Verificando dependências..."
pip install -r requirements.txt

# Iniciar o servidor Gunicorn com configuração específica
echo "Iniciando servidor..."
gunicorn -c gunicorn.conf.py wsgi:app
