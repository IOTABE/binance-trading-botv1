import json
import os
from datetime import datetime
from typing import Dict, Any
from ..models.position import Position

class DataPersistence:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Usar diretório padrão
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'persistence')
        else:
            self.data_dir = data_dir
            
        # Criar diretório se não existir
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.positions_file = os.path.join(self.data_dir, 'positions.json')
        self.backup_dir = os.path.join(self.data_dir, 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)

    def save_positions(self, positions: Dict[str, Position]) -> bool:
        """Salva as posições em arquivo JSON"""
        try:
            # Criar backup do arquivo atual se existir
            if os.path.exists(self.positions_file):
                self._create_backup('positions')
            
            # Converter posições para dicionário
            positions_data = {
                'timestamp': datetime.now().isoformat(),
                'positions': {
                    symbol: pos.to_dict() for symbol, pos in positions.items()
                }
            }
            
            # Salvar em arquivo
            with open(self.positions_file, 'w') as f:
                json.dump(positions_data, f, indent=4)
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar posições: {e}")
            return False

    def load_positions(self) -> Dict[str, Position]:
        """Carrega posições do arquivo JSON"""
        try:
            if not os.path.exists(self.positions_file):
                return {}
            
            with open(self.positions_file, 'r') as f:
                data = json.load(f)
            
            # Reconstruir objetos Position
            positions = {}
            for symbol, pos_data in data['positions'].items():
                positions[symbol] = Position.from_dict(pos_data)
            
            return positions
            
        except Exception as e:
            print(f"Erro ao carregar posições: {e}")
            return {}

    def _create_backup(self, file_type: str):
        """Cria backup de um arquivo"""
        try:
            source_file = self.positions_file if file_type == 'positions' else None
            if not source_file or not os.path.exists(source_file):
                return
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(
                self.backup_dir,
                f'{file_type}_{timestamp}.json'
            )
            
            # Copiar arquivo
            with open(source_file, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
                
        except Exception as e:
            print(f"Erro ao criar backup: {e}")

    def cleanup_old_backups(self, max_backups: int = 10):
        """Remove backups antigos mantendo apenas os N mais recentes"""
        try:
            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.backup_dir, filename)
                    backups.append((filepath, os.path.getmtime(filepath)))
            
            # Ordenar por data de modificação
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Remover backups excedentes
            for filepath, _ in backups[max_backups:]:
                os.remove(filepath)
                
        except Exception as e:
            print(f"Erro ao limpar backups: {e}")
