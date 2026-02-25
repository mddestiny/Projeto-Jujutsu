import os
import sys
from app import app, db

# Remove database files
db_paths = ['database.db', 'instance/database.db']
for path in db_paths:
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"✓ Deletado: {path}")
        except Exception as e:
            print(f"✗ Erro ao deletar {path}: {e}")

# Create new database
with app.app_context():
    db.create_all()
    print("✓ Banco de dados criado com sucesso!")
