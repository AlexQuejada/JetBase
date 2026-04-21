# 🚀 Flintrex

**Plataforma de transformación y visualización de datos.**  
Conecta, limpia y visualiza datos desde CSV, Excel o SQL en un dashboard interactivo.

---

## 🎯 ¿Qué problema resuelve?

Muchos negocios tienen datos dispersos en archivos y bases de datos.  
Flintrex permite unificarlos, transformarlos y visualizarlos sin necesidad de herramientas caras o conocimiento técnico avanzado.

---

## 🧱 Stack tecnológico

| Capa | Tecnología |
| :--- | :--- |
| **Backend API** | Python + FastAPI |
| **Procesamiento de datos** | Pandas, NumPy |
| **Frontend** | React + TypeScript + TailwindCSS |
| **Base de datos** | PostgreSQL |
| **Contenedores** | Docker + Docker Compose |
| **Control de versiones** | Git + GitHub |

---

## 📁 Estructura del proyecto

Flintrex/
├── backend/
│ ├── app/
│ │ ├── api/ # Endpoints (REST)
│ │ ├── core/ # Configuración, seguridad
│ │ ├── models/ # Modelos de datos
│ │ ├── schemas/ # Validación (Pydantic)
│ │ ├── services/ # Lógica de negocio
│ │ └── utils/ # Utilidades
│ ├── tests/ # Pruebas unitarias
│ ├── requirements.txt
│ └── main.py
├── frontend/ # React app (próximamente)
├── docker-compose.yml
├── .env
├── .gitignore
└── README.md

## 🚀 Estado del proyecto

🟢 **Fase 1 - Base y configuración** (completada)  
🟡 **Fase 2 - Endpoints y procesamiento con pandas** (en curso)  
⚪ **Fase 3 - Frontend y dashboards** (próxima)  
⚪ **Fase 4 - Base de datos y usuarios** (futuro)  

---

## 🧪 Cómo correr el proyecto (local)

### 1. Clonar el repositorio

git clone https://github.com/TU_USUARIO/Flintrex.git
cd Flintrex

2. Crear y activar entorno virtual

python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

3. Instalar dependencias

pip install -r backend/requirements.txt

4. Correr el servidor

cd backend
uvicorn main:app --reload --port 8000

5. Verificar

Abrir http://localhost:8000/docs → Documentación automática de la API.

Autor
Alex Quejada
=======
# 🚀 Flintrex

**Plataforma de transformación y visualización de datos.**  
Conecta, limpia y visualiza datos desde CSV, Excel o SQL en un dashboard interactivo.

---

## 🎯 ¿Qué problema resuelve?

Muchos negocios tienen datos dispersos en archivos y bases de datos.  
Flintrex permite unificarlos, transformarlos y visualizarlos sin necesidad de herramientas caras o conocimiento técnico avanzado.

---

## 🧱 Stack tecnológico

| Capa | Tecnología |
| :--- | :--- |
| **Backend API** | Python + FastAPI |
| **Procesamiento de datos** | Pandas, NumPy |
| **Frontend** | React + TypeScript + TailwindCSS |
| **Base de datos** | PostgreSQL |
| **Contenedores** | Docker + Docker Compose |
| **Control de versiones** | Git + GitHub |

---

## 📁 Estructura del proyecto

Flintrex/

├── backend/

│ ├── app/

│ │ ├── api/ # Endpoints (REST)

│ │ ├── core/ # Configuración, seguridad

│ │ ├── models/ # Modelos de datos

│ │ ├── schemas/ # Validación (Pydantic)

│ │ ├── services/ # Lógica de negocio

│ │ └── utils/ # Utilidades

│ ├── tests/ # Pruebas unitarias

│ ├── requirements.txt

│ └── main.py

├── frontend/ # React app (próximamente)

├── docker-compose.yml

├── .env

├── .gitignore

└── README.md

## 🚀 Estado del proyecto

🟢 **Fase 1 - Base y configuración** (completada)  
🟡 **Fase 2 - Endpoints y procesamiento con pandas** (en curso)  
⚪ **Fase 3 - Frontend y dashboards** (próxima)  
⚪ **Fase 4 - Base de datos y usuarios** (futuro)  

---

## 🧪 Cómo correr el proyecto (local)

### 1. Clonar el repositorio

git clone https://github.com/TU_USUARIO/Flintrex.git
cd Flintrex

2. Crear y activar entorno virtual

python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

3. Instalar dependencias

pip install -r backend/requirements.txt

4. Correr el servidor

cd backend
uvicorn main:app --reload --port 8000

5. Verificar

Abrir http://localhost:8000/docs → Documentación automática de la API.

Autor
Alex Quejada

