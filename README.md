🚀 Flintrex

Flintrex es una plataforma web para limpiar, transformar y visualizar datos provenientes de múltiples fuentes como CSV, Excel o datasets inconsistentes.
Permite convertir información desordenada en datasets utilizables y dashboards interactivos, sin necesidad de herramientas complejas.

Demo

https://www.flintrex.com(en proceso de validación SSL)

Problema que resuelve

Los datos del mundo real rara vez vienen listos para usarse:

Archivos corruptos o mal estructurados
Columnas inconsistentes entre múltiples fuentes
Datos duplicados o incompletos
Procesos manuales lentos y propensos a errores

Flintrex automatiza este proceso, permitiendo:

Unificar múltiples archivos

Limpiar y normalizar datos

Detectar inconsistencias

Generar métricas y visualizaciones

✨ Características principales
Carga múltiple de archivos (CSV, Excel)

Detección automática de estructura

Unificación inteligente de columnas (ej: name, full_name, nombre)

Eliminación y manejo de duplicados

Gestión de valores nulos (drop/fill)

Edición directa de datos (inline)

Dashboard interactivo en tiempo real

Exportación a CSV, Excel, JSON y PDF

Procesamiento robusto de archivos corruptos

Trazabilidad por archivo de origen

Stack tecnológico
Capa	Tecnología

Backend API	Python + FastAPI

Procesamiento de datos	Pandas, NumPy

Frontend	React + TypeScript + TailwindCSS

Base de datos	PostgreSQL

Infraestructura	Docker + Railway

Seguridad	Rate limiting, validación de archivos

Control de versiones	Git + GitHub

📁 Estructura del proyecto

Flintrex/

├── backend/

│   ├── app/

│   │   ├── api/        # Endpoints REST

│   │   ├── core/       # Configuración y seguridad

│   │   ├── models/     # Modelos de datos

│   │   ├── schemas/    # Validación (Pydantic)

│   │   ├── services/   # Lógica de negocio

│   │   └── utils/      # Utilidades

│   ├── tests/          # Pruebas unitarias

│   ├── requirements.txt

│   └── main.py

├── frontend/           # Aplicación React

├── docker-compose.yml

├── .env.example

└── README.md

Estado del proyecto

✅ Backend robusto y desacoplado
✅ Procesamiento avanzado de datos
✅ Frontend funcional con dashboards
🟡 Deploy en producción (en validación SSL)
🔜 Sistema de usuarios y persistencia

Ejecución local

1. Clonar repositorio
git clone https://github.com/TU_USUARIO/Flintrex.git
cd Flintrex

3. Crear entorno virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

5. Instalar dependencias
pip install -r backend/requirements.txt

7. Ejecutar servidor
cd backend
uvicorn main:app --reload --port 8000

9. Acceder a la API
http://localhost:8000/docs

Consideraciones
Límite de tamaño de archivos para estabilidad

Validación de archivos corruptos o inválidos

Procesamiento optimizado para datasets grandes

Sistema preparado para escalabilidad futura

Roadmap
Autenticación de usuarios

Persistencia de proyectos

Integraciones (Google Drive, APIs externas)

Streaming para archivos grandes

Mejora de visualizaciones avanzadas

Autor

Alex Quejada
Analista y Desarrollador de Software
