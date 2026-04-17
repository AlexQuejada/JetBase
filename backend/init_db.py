import sys
import os

# Agregar la carpeta backend al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from app.models.uploaded_file import Base

print("🚀 Conectando a la base de datos...")
print(f"📍 URL: {engine.url}")

print("\n📦 Creando tablas...")
Base.metadata.create_all(bind=engine)

print("✅ Tablas creadas exitosamente.")
print("   - uploaded_files")