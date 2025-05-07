# Skills Hub

## Descripción
Skills Hub es una aplicación web que utiliza IA para generar cursos personalizados adaptados a las necesidades específicas de cada usuario. Creado por Nicolas Hurtado Amezquita

## Características
- Generación de cursos personalizados usando IA
- Autenticación de usuarios
- Guardado y gestión de cursos
- Interfaz de usuario moderna e intuitiva

## Requisitos previos
- Docker y Docker Compose instalados

## Inicio rápido con Docker

Para ejecutar toda la aplicación con un solo comando usando Docker:

```bash
# Opción 1: Usando el script
./start.sh

# Opción 2: Usando Docker Compose directamente
docker-compose up --build
```

La aplicación estará disponible en:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Desarrollo local

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend (React)
```bash
cd frontend
npm install
npm start
```

## Estructura del proyecto
```
skills-hub/
├── backend/              # API de FastAPI
│   ├── models/           # Modelos de datos
│   ├── routes/           # Endpoints de la API
│   ├── utils/            # Utilidades
│   ├── app.py            # Aplicación principal
│   └── requirements.txt  # Dependencias
├── frontend/             # Aplicación React
│   ├── public/           # Archivos estáticos
│   └── src/              # Código fuente
└── docker-compose.yml    # Configuración de Docker
```

## Notas
- Asegúrate de que los puertos 3000 y 8000 estén disponibles.
- En Windows, puede ser necesario usar `docker compose` en lugar de `docker-compose`.

## Uso

1. Regístrate para crear una cuenta nueva
2. Inicia sesión con tus credenciales
3. En el dashboard, haz clic en "Nuevo curso"
4. Completa el formulario con el tema que deseas aprender, tu nivel de experiencia y tiempo disponible
5. Espera unos momentos mientras se genera tu curso personalizado
6. Explora el contenido de tu curso, organizado en secciones fáciles de navegar
7. Todos tus cursos quedarán guardados en el dashboard para acceder a ellos cuando lo necesites

## Tecnologías utilizadas

### Backend
- FastAPI
- SQLite
- JWT para autenticación
- Mistral AI (a través de OpenRouter)

### Frontend
- React
- React Router
- Tailwind CSS
- Framer Motion para animaciones
- Axios para solicitudes HTTP

## Licencia

MIT 