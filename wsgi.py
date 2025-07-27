import os
import sys

# Adicionar o diretório raiz do projeto ao PYTHONPATH
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from src.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()