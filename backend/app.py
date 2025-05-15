from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests
import json
import sqlite3
import os
import re
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import uuid

# Importar el servicio de pagos
try:
    from payment_service import create_payment_link, verify_payment, approve_simulated_payment, SIMULATION_MODE
    PAYMENT_ENABLED = True
except ImportError:
    # Si no existe el módulo de pagos, se desactiva la funcionalidad
    PAYMENT_ENABLED = False
    print("WARNING: Payment service not available")

# Database setup
DB_PATH = "courses.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Add new columns to users table if they don't exist
    try:
        # Check if subscription_tier column exists
        cursor.execute("SELECT subscription_tier FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # Add subscription_tier column
        cursor.execute("ALTER TABLE users ADD COLUMN subscription_tier TEXT DEFAULT 'free'")
        print("Added subscription_tier column to users table")
    
    try:
        # Check if subscription_end_date column exists
        cursor.execute("SELECT subscription_end_date FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # Add subscription_end_date column
        cursor.execute("ALTER TABLE users ADD COLUMN subscription_end_date TIMESTAMP")
        print("Added subscription_end_date column to users table")
    
    # Create courses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        prompt TEXT NOT NULL,
        content TEXT NOT NULL,
        experience_level TEXT NOT NULL,
        available_time TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create subscription_tiers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscription_tiers (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        price REAL NOT NULL,
        course_limit INTEGER NOT NULL,
        description TEXT NOT NULL
    )
    ''')
    
    # Insert default subscription tiers if they don't exist
    cursor.execute("SELECT COUNT(*) FROM subscription_tiers")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO subscription_tiers (id, name, price, course_limit, description)
        VALUES 
            ('tier_free', 'Free', 0, 1, 'Access to 1 course only'),
            ('tier_pro', 'Pro', 19.90, 5, 'Ideal para usuarios regulares'),
            ('tier_unlimited', 'Unlimited', 24.90, -1, 'Perfecto para uso intensivo')
        ''')
        print("Inserted default subscription tiers")
    else:
        # Actualizar los planes para que coincidan con el frontend
        cursor.execute("DELETE FROM subscription_tiers WHERE id NOT IN ('tier_free', 'tier_pro', 'tier_unlimited')")
        cursor.execute("UPDATE subscription_tiers SET price = 19.90, course_limit = 5, description = 'Ideal para usuarios regulares' WHERE id = 'tier_pro'")
        cursor.execute("UPDATE subscription_tiers SET price = 24.90, course_limit = -1, description = 'Perfecto para uso intensivo' WHERE id = 'tier_unlimited'")
        print("Updated subscription tiers")
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Auth setup
SECRET_KEY = "your-super-secret-key-replace-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Course Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API config
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Data models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    id: str
    username: str
    email: str
    created_at: str
    subscription_tier: str
    subscription_end_date: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class SubscriptionTier(BaseModel):
    id: str
    name: str
    price: float
    course_limit: int
    description: str

class SubscriptionUpdate(BaseModel):
    tier_id: str

class CourseRequest(BaseModel):
    topic: str
    experience_level: str
    available_time: str

class Module(BaseModel):
    title: str
    steps: List[str]
    example: Optional[str] = ""

class CourseResponse(BaseModel):
    title: str
    objective: str
    prerequisites: List[str]
    definitions: List[str]
    roadmap: Dict[str, List[str]]
    modules: List[Module]
    resources: List[str]
    faqs: List[str]
    errors: List[str]
    downloads: List[str]
    summary: str

class SavedCourseRequest(BaseModel):
    title: str
    prompt: str
    content: Dict[str, Any]
    experience_level: str
    available_time: str

class TopicReplacementRequest(BaseModel):
    course_id: str
    section: str
    current_topic: str
    experience_level: str

class ModuleReplacementRequest(BaseModel):
    course_id: str
    module_index: int
    current_module_title: str
    experience_level: str

# Helper functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return user
    return None

def authenticate_user(username, password):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["password_hash"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Ensure we're only selecting columns that definitely exist
    cursor.execute("SELECT id, username, email, created_at FROM users WHERE username = ?", (token_data.username,))
    user = cursor.fetchone()
    
    # Now check and fetch subscription data if available
    try:
        cursor.execute("SELECT subscription_tier, subscription_end_date FROM users WHERE id = ?", (user["id"],))
        subscription = cursor.fetchone()
        if subscription:
            # Add subscription data to user dict
            user_dict = dict(user)
            user_dict["subscription_tier"] = subscription["subscription_tier"] 
            user_dict["subscription_end_date"] = subscription["subscription_end_date"]
            user = user_dict
    except sqlite3.OperationalError:
        # Columns don't exist yet, which is fine
        pass
    
    conn.close()
    
    if user is None:
        raise credentials_exception
    
    return user

def extract_list(label: str, lines: list[str]) -> list[str]:
    result = []
    capture = False
    for line in lines:
        if label.lower() in line.lower():
            capture = True
            continue
        if capture:
            if line.strip() == "" or re.match(r"^\w+:", line):  # termina al detectar nueva sección
                break
            if line.strip().startswith("-") or line.strip().startswith("•"):
                result.append(line.strip("-• ").strip())
    return result

# Routes
@app.post("/register", response_model=User)
async def register(user_data: UserCreate):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if username already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (user_data.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    
    # Asegurar que las columnas de suscripción existen
    try:
        cursor.execute("SELECT subscription_tier FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN subscription_tier TEXT DEFAULT 'free'")
        cursor.execute("ALTER TABLE users ADD COLUMN subscription_end_date TIMESTAMP")
    
    # Insertar usuario con tier gratuito por defecto
    cursor.execute(
        "INSERT INTO users (id, username, email, password_hash, subscription_tier) VALUES (?, ?, ?, ?, ?)",
        (user_id, user_data.username, user_data.email, hashed_password, "free")
    )
    
    conn.commit()
    
    # Fetch the newly created user
    cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    
    # Crear el objeto de respuesta con los campos básicos
    user_response = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "created_at": user_row["created_at"],
        "subscription_tier": "free",
        "subscription_end_date": None
    }
    
    conn.close()
    
    return user_response

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    # Convert sqlite3.Row to dict and provide default values if fields don't exist
    user_dict = dict(current_user)
    
    return {
        "id": user_dict["id"],
        "username": user_dict["username"],
        "email": user_dict["email"],
        "created_at": user_dict["created_at"],
        "subscription_tier": user_dict.get("subscription_tier", "free"),
        "subscription_end_date": user_dict.get("subscription_end_date")
    }

@app.post("/generate-course", response_model=CourseResponse)
async def generate_course(request: CourseRequest, current_user: dict = Depends(get_current_user)):
    if not request.topic or len(request.topic.strip()) < 3:
        raise HTTPException(status_code=400, detail="Course topic must have at least 3 characters")

    # Log the request parameters for debugging
    print(f"Generating course for topic: '{request.topic}', experience: {request.experience_level}, time: {request.available_time}")

    # Check subscription status and course limit
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get course count
    cursor.execute("SELECT COUNT(*) as count FROM courses WHERE user_id = ?", (current_user["id"],))
    course_count = dict(cursor.fetchone())["count"]
    
    # Default values for free tier
    subscription_tier = "free"
    subscription_end_date = None
    course_limit = 1
    
    # Try to get subscription data (might not exist yet)
    try:
        # Get user's subscription tier
        cursor.execute("SELECT subscription_tier, subscription_end_date FROM users WHERE id = ?", (current_user["id"],))
        subscription_row = cursor.fetchone()
        if subscription_row:
            subscription = dict(subscription_row)
            subscription_tier = subscription.get("subscription_tier", "free")
            subscription_end_date = subscription.get("subscription_end_date")
            
            # Get tier details
            cursor.execute("SELECT * FROM subscription_tiers WHERE name = ? COLLATE NOCASE", (subscription_tier,))
            tier_row = cursor.fetchone()
            if tier_row:
                tier = dict(tier_row)
                course_limit = tier.get("course_limit", 1)
    except sqlite3.OperationalError:
        # Subscription columns don't exist yet, use defaults
        pass
    
    # Check if subscription is active
    is_active = True
    if subscription_end_date:
        end_date = datetime.fromisoformat(subscription_end_date)
        is_active = end_date > datetime.utcnow()
    
    # If subscription is inactive, revert to free tier
    if not is_active:
        course_limit = 1
    
    # Check if user can create more courses
    if course_limit != -1 and course_count >= course_limit:
        # Obtenemos todos los planes disponibles para mostrar al usuario
        cursor.execute("SELECT * FROM subscription_tiers WHERE name <> 'Free' ORDER BY price")
        available_plans = [dict(row) for row in cursor.fetchall()]
        # Cerramos la conexión antes de lanzar la excepción
        conn.close()
        
        raise HTTPException(
            status_code=403, 
            detail={
                "message": f"Has alcanzado el límite de cursos para tu plan actual ({subscription_tier})",
                "title": "Límite de plan alcanzado",
                "description": "Para crear más cursos, actualiza a un plan premium",
                "current_tier": subscription_tier,
                "course_limit": course_limit,
                "course_count": course_count,
                "need_upgrade": True,
                "available_plans": available_plans,
                "show_plans_modal": True
            }
        )
    
    # Si llegamos aquí, el usuario puede crear más cursos
    prompt = (
        f"Actúa como un experto en educación digital y diseño instruccional. Crea un curso completo, profesional y bien estructurado sobre el tema: '{request.topic}'\n\n"
        f"Nivel de experiencia del usuario: {request.experience_level}\n"
        f"Tiempo disponible: {request.available_time}\n\n"
        "La respuesta debe estar en español, con enfoque práctico, ideal para personas ocupadas que desean aprender de manera rápida pero profunda. NO des una respuesta genérica de IA; debe sentirse como un curso visual moderno y real.\n\n"
        "📘 Formato del curso (estructura completa):\n\n"
        "1. 🎓 Título atractivo y profesional\n"
        "2. 🎯 Objetivo del curso\n"
        "3. 🧠 Conceptos previos\n"
        "4. 📌 Definiciones clave\n"
        "5. 🗺️ Mapa de aprendizaje (IMPORTANTE: Debes estructurar el mapa con formato de secciones, con cada sección conteniendo varios temas específicos. Ejemplo: '1. Fundamentos: [tema1, tema2, tema3]', '2. Nivel intermedio: [tema1, tema2]', etc.)\n"
        "6. 📚 Módulos con título, pasos y ejemplo\n"
        "7. 🌐 Recursos adicionales sugeridos\n"
        "8. ❓ Preguntas frecuentes\n"
        "9. ⚠️ Errores comunes\n"
        "10. 📦 Recursos descargables\n"
        "11. 🧾 Resumen final\n\n"
        "Devuelve la respuesta en formato JSON con la siguiente estructura:\n"
        "{\n"
        '  "title": "string",\n'
        '  "objective": "string",\n'
        '  "prerequisites": ["..."],\n'
        '  "definitions": ["..."],\n'
        '  "roadmap": {"sección1": ["tema1", "tema2"], "sección2": ["tema1", "tema2"]},\n'
        '  "modules": [{"title": "...", "steps": ["..."], "example": "..."}],\n'
        '  "resources": ["..."],\n'
        '  "faqs": ["..."],\n'
        '  "errors": ["..."],\n'
        '  "downloads": ["..."],\n'
        '  "summary": "string"\n'
        "}"
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "stream": False,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1500  # Reducir tokens para asegurarnos de no exceder límites
    }

    try:
        print("Sending request to OpenRouter API...")
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        print(f"OpenRouter API response status: {response.status_code}")
        
        if response.status_code != 200:
            # Log more detailed error information
            error_detail = f"Status code: {response.status_code}, Response: {response.text}"
            print(f"OpenRouter API error: {error_detail}")
            
            # Cerrar la conexión a la base de datos antes de retornar la respuesta
            if 'conn' in locals() and conn:
                conn.close()
                
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Error en la generación del curso: {error_detail}"
            )

        ai_response = response.json()
        if "choices" not in ai_response or not ai_response["choices"]:
            print("Error: No choices in API response")
            print(f"Full response: {json.dumps(ai_response, indent=2)}")
            
            # Cerrar la conexión a la base de datos antes de retornar la respuesta
            if 'conn' in locals() and conn:
                conn.close()
                
            raise HTTPException(status_code=500, detail="La API no devolvió resultados válidos")
            
        print("API response received successfully")
        content = ai_response["choices"][0]["message"]["content"]
        print(f"Content length: {len(content)} characters")
        
        # Guardar el contenido en un archivo para depuración
        with open("last_course_response.txt", "w", encoding="utf-8") as f:
            f.write(content)
            
        print("Content saved to last_course_response.txt for debugging")

        try:
            print("Parsing JSON response...")
            parsed = json.loads(content)
            print("JSON parsed successfully")
            
            # Asegurarnos de que roadmap sea un diccionario
            if "roadmap" in parsed and isinstance(parsed["roadmap"], list):
                print("Converting roadmap from list to dictionary")
                # Convertir array a diccionario si viene en formato antiguo
                parsed["roadmap"] = {"Ruta de aprendizaje": parsed["roadmap"]}
                
            # Asegurarnos de que todos los módulos tengan los campos requeridos
            print(f"Processing {len(parsed.get('modules', []))} modules")
            for mod in parsed.get("modules", []):
                mod.setdefault("steps", [])
                mod.setdefault("example", "")
                
            # Cerrar la conexión a la base de datos antes de retornar la respuesta
            if 'conn' in locals() and conn:
                conn.close()
                
            # Validar que todas las propiedades requeridas estén presentes
            required_props = ["title", "objective", "prerequisites", "definitions", "roadmap", "modules", "resources", "faqs", "errors", "downloads", "summary"]
            missing_props = [prop for prop in required_props if prop not in parsed]
            
            if missing_props:
                print(f"Missing properties in response: {missing_props}")
                for prop in missing_props:
                    parsed[prop] = [] if prop in ["prerequisites", "definitions", "modules", "resources", "faqs", "errors", "downloads"] else ""
                    if prop == "roadmap":
                        parsed[prop] = {"General": []}
            
            print("Creating CourseResponse object")
            response_obj = CourseResponse(**parsed)
            print("CourseResponse created successfully")
            return response_obj
        except json.JSONDecodeError:
            print("Error decoding JSON, falling back to text processing")
            lines = content.split('\n')
            
            print("Extracting title and objective")
            title = next((line.replace("Título:", "").strip() for line in lines if line.lower().startswith("título:")), request.topic)
            objective = next((line.replace("Objetivo:", "").strip() for line in lines if line.lower().startswith("objetivo:")), f"Aprender {request.topic}")
            summary = next((line.replace("Resumen:", "").strip() for line in lines if line.lower().startswith("resumen:")), "")

            print("Extracting prerequisites and definitions")
            prerequisites = extract_list("Conceptos previos:", lines)
            definitions = extract_list("Definiciones clave:", lines)
            
            print("Processing roadmap")
            # Extraer mapa de aprendizaje y procesarlo como un diccionario de secciones
            roadmap_items = extract_list("Mapa de aprendizaje:", lines)
            roadmap = {}
            current_section = "General"
            roadmap[current_section] = []
            
            # Intentar convertir los elementos del roadmap en secciones
            for item in roadmap_items:
                # Verificar si es un título de sección (contiene ":" al final)
                if ":" in item:
                    parts = item.split(":", 1)
                    current_section = parts[0].strip()
                    items = parts[1].strip().split(",")
                    roadmap[current_section] = [i.strip() for i in items if i.strip()]
                else:
                    # Si no es una sección, añadir al último grupo
                    roadmap[current_section].append(item)
            
            # Si no pudimos extraer secciones correctamente, usar un formato simple
            if len(roadmap) == 1 and len(roadmap["General"]) == len(roadmap_items):
                roadmap = {"Ruta de aprendizaje": roadmap_items}
                
            print("Extracting FAQs, errors, downloads, and resources")
            faqs = extract_list("Preguntas frecuentes:", lines)
            errors = extract_list("Errores comunes:", lines)
            downloads = extract_list("Recursos descargables:", lines)
            resources = extract_list("Recursos adicionales:", lines)

            print("Extracting modules")
            modules = []
            current_module = None
            for line in lines:
                if re.match(r"^m[oó]dulo \d+", line.lower()):
                    if current_module:
                        modules.append(current_module)
                    current_module = {"title": line.strip(), "steps": [], "example": ""}
                elif current_module:
                    if "ejemplo" in line.lower():
                        current_module["example"] = line.split(":", 1)[1].strip() if ":" in line else ""
                    elif line.strip().startswith("-") or line.strip().startswith("•"):
                        current_module["steps"].append(line.strip("-• ").strip())
            if current_module:
                modules.append(current_module)
                
            print(f"Extracted {len(modules)} modules")
            
            # Si no se encontraron módulos, crear uno por defecto
            if not modules:
                print("No modules found, creating default module")
                modules = [{
                    "title": f"Módulo 1: Introducción a {request.topic}",
                    "steps": ["Conocer los conceptos básicos", "Realizar ejercicios prácticos", "Revisar los recursos adicionales"],
                    "example": ""
                }]

            # Cerrar la conexión a la base de datos antes de retornar la respuesta
            if 'conn' in locals() and conn:
                conn.close()

            print("Creating CourseResponse object from text parse")
            response_obj = CourseResponse(
                title=title,
                objective=objective,
                prerequisites=prerequisites,
                definitions=definitions,
                roadmap=roadmap,
                modules=modules,
                resources=resources,
                faqs=faqs,
                errors=errors,
                downloads=downloads,
                summary=summary
            )
            print("CourseResponse created successfully from text parse")
            return response_obj

    except Exception as e:
        # Add more detailed error logging
        import traceback
        error_trace = traceback.format_exc()
        print(f"Exception in generate_course: {str(e)}")
        print(f"Traceback: {error_trace}")
        
        # Intentar proporcionar un error más específico y útil
        error_message = str(e)
        if "validation error" in error_message.lower():
            error_message = "Error de validación en los datos del curso. Los datos no tienen el formato esperado."
        elif "roadmap" in error_message.lower():
            error_message = "Error en el formato de la hoja de ruta del curso. Intenta de nuevo."
        elif "unexpected keyword argument" in error_message.lower():
            error_message = "Error en la estructura de datos del curso. Algunos campos no son válidos."
        elif "not a valid value" in error_message.lower():
            error_message = "Uno de los valores devueltos por la API no es válido. Intenta de nuevo."
        elif "TypeError" in error_message or "NoneType" in error_message:
            error_message = "Error de tipo de datos en la respuesta. Intenta de nuevo con un tema diferente."
        elif "IndexError" in error_message:
            error_message = "Error en el procesamiento de la respuesta. Intenta de nuevo con un tema más específico."
        elif "KeyError" in error_message:
            error_message = "Error en la estructura de datos. Falta alguna propiedad requerida."
        
        # Crear una respuesta predeterminada como fallback para casos extremos
        try:
            if 'conn' in locals() and conn:
                conn.close()
                
            # Proporcionar un curso mínimo fallback
            fallback_response = CourseResponse(
                title=f"Curso sobre {request.topic}",
                objective=f"Aprender sobre {request.topic}",
                prerequisites=[],
                definitions=[],
                roadmap={"Fundamentos": [f"Conceptos básicos de {request.topic}", f"Introducción a {request.topic}"]},
                modules=[{
                    "title": f"Módulo 1: Introducción a {request.topic}",
                    "steps": ["Conocer los conceptos básicos", "Realizar ejercicios prácticos"],
                    "example": ""
                }],
                resources=[],
                faqs=[],
                errors=[],
                downloads=[],
                summary=f"Este curso te enseñará los fundamentos de {request.topic}."
            )
            
            # Agregar mensaje de error indicando que este es un curso de fallback
            print("Returning fallback course due to error")
            return fallback_response
            
        except Exception as inner_e:
            print(f"Error creating fallback response: {str(inner_e)}")
            # Cerrar la conexión si está abierta
            if 'conn' in locals() and conn:
                conn.close()
                
            raise HTTPException(status_code=500, detail=error_message)

@app.post("/save-course")
async def save_course(course_data: SavedCourseRequest, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    course_id = str(uuid.uuid4())
    
    cursor.execute(
        "INSERT INTO courses (id, user_id, title, prompt, content, experience_level, available_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            course_id,
            current_user["id"],
            course_data.title,
            course_data.prompt,
            json.dumps(course_data.content),
            course_data.experience_level,
            course_data.available_time
        )
    )
    
    conn.commit()
    conn.close()
    
    return {"id": course_id, "message": "Course saved successfully"}

@app.get("/courses")
async def get_courses(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, title, experience_level, available_time, created_at FROM courses WHERE user_id = ? ORDER BY created_at DESC",
        (current_user["id"],)
    )
    
    courses = cursor.fetchall()
    
    conn.close()
    
    return [dict(course) for course in courses]

@app.get("/courses/{course_id}")
async def get_course(course_id: str, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM courses WHERE id = ? AND user_id = ?",
        (course_id, current_user["id"])
    )
    
    course = cursor.fetchone()
    
    conn.close()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course_dict = dict(course)
    course_dict["content"] = json.loads(course_dict["content"])
    
    return course_dict

@app.delete("/courses/{course_id}")
async def delete_course(course_id: str, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM courses WHERE id = ? AND user_id = ?",
        (course_id, current_user["id"])
    )
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Course not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Course deleted successfully"}

@app.get("/subscription-tiers")
async def get_subscription_tiers():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM subscription_tiers ORDER BY price")
    tiers = cursor.fetchall()
    
    conn.close()
    
    return [dict(tier) for tier in tiers]

@app.post("/subscribe")
async def subscribe(subscription: SubscriptionUpdate, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Verify tier exists
    cursor.execute("SELECT * FROM subscription_tiers WHERE id = ?", (subscription.tier_id,))
    tier_row = cursor.fetchone()
    
    if not tier_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Subscription tier not found")
    
    tier = dict(tier_row)
    
    # In a real application, here you would process the payment
    # For now, we'll just update the user's subscription
    
    # Calculate subscription end date (30 days from now)
    end_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    try:
        # Try to update user's subscription
        cursor.execute(
            "UPDATE users SET subscription_tier = ?, subscription_end_date = ? WHERE id = ?",
            (tier["name"].lower(), end_date, current_user["id"])
        )
    except sqlite3.OperationalError:
        # Columns might not exist, try to add them
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN subscription_tier TEXT DEFAULT 'free'")
            cursor.execute("ALTER TABLE users ADD COLUMN subscription_end_date TIMESTAMP")
            
            # Now try the update again
            cursor.execute(
                "UPDATE users SET subscription_tier = ?, subscription_end_date = ? WHERE id = ?",
                (tier["name"].lower(), end_date, current_user["id"])
            )
        except Exception as e:
            conn.close()
            raise HTTPException(status_code=500, detail=f"Failed to update subscription: {str(e)}")
    
    conn.commit()
    conn.close()
    
    return {"message": f"Subscribed to {tier['name']} plan", "end_date": end_date}

@app.get("/subscription-status")
async def get_subscription_status(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get course count
    cursor.execute("SELECT COUNT(*) as count FROM courses WHERE user_id = ?", (current_user["id"],))
    course_count = dict(cursor.fetchone())["count"]
    
    # Default values
    subscription_tier = "free"
    subscription_end_date = None
    tier = {"id": "tier_free", "name": "Free", "price": 0.0, "course_limit": 1, "description": "Access to 1 course only"}
    
    # Try to get subscription data (might not exist yet)
    try:
        # Get user's current tier
        cursor.execute("SELECT subscription_tier, subscription_end_date FROM users WHERE id = ?", (current_user["id"],))
        subscription_row = cursor.fetchone()
        if subscription_row:
            subscription = dict(subscription_row)
            subscription_tier = subscription.get("subscription_tier", "free")
            subscription_end_date = subscription.get("subscription_end_date")
            
            # Get tier details
            cursor.execute("SELECT * FROM subscription_tiers WHERE name = ? COLLATE NOCASE", (subscription_tier,))
            tier_row = cursor.fetchone()
            if tier_row:
                tier = dict(tier_row)
    except sqlite3.OperationalError:
        # Subscription columns don't exist yet, use defaults
        pass
    
    conn.close()
    
    # Check if subscription is active
    is_active = True
    if subscription_end_date:
        end_date = datetime.fromisoformat(subscription_end_date)
        is_active = end_date > datetime.utcnow()
    
    return {
        "tier": tier,
        "course_count": course_count,
        "is_active": is_active,
        "end_date": subscription_end_date,
        "can_create_course": (tier["course_limit"] == -1 or course_count < tier["course_limit"])
    }

@app.post("/create-payment")
async def create_payment(subscription: SubscriptionUpdate, current_user: dict = Depends(get_current_user)):
    if not PAYMENT_ENABLED:
        raise HTTPException(status_code=501, detail="Payment service not available")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Verificar que el plan existe
    cursor.execute("SELECT * FROM subscription_tiers WHERE id = ?", (subscription.tier_id,))
    tier_row = cursor.fetchone()
    
    if not tier_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Subscription tier not found")
    
    tier = dict(tier_row)
    
    # Obtener precio según el plan
    price = 0
    if tier["name"].lower() == "pro":
        price = 19900
    elif tier["name"].lower() == "unlimited":
        price = 24900
    
    # Crear el enlace de pago
    payment_result = create_payment_link(
        user_id=current_user["id"],
        plan_id=tier["id"],
        plan_name=tier["name"],
        amount=price
    )
    
    conn.close()
    
    if payment_result["success"]:
        # Guardar la referencia de pago en una tabla de transacciones (opcional)
        # ...
        
        return {
            "payment_url": payment_result["payment_url"],
            "reference": payment_result["reference"]
        }
    else:
        raise HTTPException(status_code=500, detail=payment_result["error"])

@app.post("/verify-payment")
async def check_payment(payment_data: dict, current_user: dict = Depends(get_current_user)):
    if not PAYMENT_ENABLED:
        raise HTTPException(status_code=501, detail="Payment service not available")
    
    reference = payment_data.get("reference")
    if not reference:
        raise HTTPException(status_code=400, detail="Payment reference is required")
    
    # Verificar el estado del pago
    verification = verify_payment(reference)
    
    if verification["success"] and verification["status"] == "APPROVED":
        # Actualizar la suscripción del usuario
        # Extraer el ID del plan de la referencia (plan_TIER_ID_USER_ID_TIMESTAMP)
        try:
            tier_id = reference.split("_")[1]
            
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Obtener información del plan
            cursor.execute("SELECT * FROM subscription_tiers WHERE id = ?", (tier_id,))
            tier = dict(cursor.fetchone())
            
            # Calcular fecha de expiración (30 días)
            end_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
            
            # Actualizar suscripción
            cursor.execute(
                "UPDATE users SET subscription_tier = ?, subscription_end_date = ? WHERE id = ?",
                (tier["name"].lower(), end_date, current_user["id"])
            )
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": f"Pago verificado y suscripción actualizada al plan {tier['name']}",
                "plan": tier["name"],
                "expiration_date": end_date
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al actualizar la suscripción: {str(e)}")
    
    return {
        "success": False,
        "status": verification.get("status", "UNKNOWN"),
        "message": "El pago no ha sido aprobado o no se ha completado"
    }

@app.post("/approve-simulated-payment")
async def manual_approve_payment(payment_data: dict, current_user: dict = Depends(get_current_user)):
    """
    Endpoint para aprobar manualmente un pago simulado (solo en modo desarrollo)
    """
    if not PAYMENT_ENABLED:
        raise HTTPException(status_code=501, detail="Payment service not available")
    
    if not SIMULATION_MODE:
        raise HTTPException(status_code=403, detail="This endpoint is only available in simulation mode")
    
    reference = payment_data.get("reference")
    if not reference:
        raise HTTPException(status_code=400, detail="Payment reference is required")
    
    # Aprobar el pago simulado
    result = approve_simulated_payment(reference)
    
    if result["success"]:
        # Actualizar la suscripción del usuario
        try:
            tier_id = reference.split("_")[1]
            
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Obtener información del plan
            cursor.execute("SELECT * FROM subscription_tiers WHERE id = ?", (tier_id,))
            tier = dict(cursor.fetchone())
            
            # Calcular fecha de expiración (30 días)
            end_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
            
            # Actualizar suscripción
            cursor.execute(
                "UPDATE users SET subscription_tier = ?, subscription_end_date = ? WHERE id = ?",
                (tier["name"].lower(), end_date, current_user["id"])
            )
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": f"Pago simulado aprobado y suscripción actualizada al plan {tier['name']}",
                "plan": tier["name"],
                "expiration_date": end_date
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al actualizar la suscripción: {str(e)}")
    
    return {
        "success": False,
        "message": result.get("error", "No se pudo aprobar el pago simulado")
    }

@app.post("/replace-topic")
async def replace_topic(request: TopicReplacementRequest, current_user: dict = Depends(get_current_user)):
    """
    Endpoint para reemplazar un tema que el usuario ya conoce por uno nuevo
    """
    # Verificar que el curso pertenezca al usuario
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM courses WHERE id = ? AND user_id = ?",
        (request.course_id, current_user["id"])
    )
    
    course = cursor.fetchone()
    conn.close()
    
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado o no pertenece al usuario")
    
    # Preparar el prompt para generar un tema de reemplazo
    prompt = (
        f"Actúa como un experto en educación y diseño instruccional. El usuario ya conoce el tema: '{request.current_topic}' "
        f"que forma parte de la sección '{request.section}' de un curso. "
        f"Nivel de experiencia del usuario: {request.experience_level}\n\n"
        "Necesito que generes UN SOLO tema alternativo relacionado pero diferente que pueda reemplazarlo en el plan de estudio. "
        "El tema debe ser del mismo nivel de complejidad y mantener la coherencia con la sección general. "
        "SOLO proporciona el nuevo tema, sin explicaciones adicionales, en máximo 15 palabras, sin numeración ni viñetas."
    )
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "stream": False,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 100
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error en la API: {response.text}")
        
        ai_response = response.json()
        new_topic = ai_response["choices"][0]["message"]["content"].strip()
        
        # Limpieza adicional para asegurar formato adecuado
        new_topic = new_topic.replace("\"", "").replace("'", "")
        new_topic = re.sub(r"^\d+\.\s*", "", new_topic)  # Eliminar numeración inicial si existe
        new_topic = re.sub(r"^[•\-]\s*", "", new_topic)  # Eliminar viñetas si existen
        
        return {"replacement_topic": new_topic}
    
    except Exception as e:
        print(f"Error al generar tema de reemplazo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"No se pudo generar un tema de reemplazo: {str(e)}")

@app.post("/replace-module")
async def replace_module(request: ModuleReplacementRequest, current_user: dict = Depends(get_current_user)):
    """
    Endpoint para reemplazar un módulo que el usuario ya conoce por uno nuevo
    """
    # Verificar que el curso pertenezca al usuario
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM courses WHERE id = ? AND user_id = ?",
        (request.course_id, current_user["id"])
    )
    
    course = cursor.fetchone()
    conn.close()
    
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado o no pertenece al usuario")
    
    # Preparar el prompt para generar un módulo de reemplazo
    prompt = (
        f"Actúa como un experto en educación y diseño instruccional. Estás diseñando un curso sobre el tema principal relacionado con el módulo: '{request.current_module_title}'. "
        f"El usuario ha indicado que ya conoce el contenido de este módulo específico y necesita un módulo alternativo sobre un tema estrechamente relacionado. "
        f"Nivel de experiencia del usuario: {request.experience_level}.\n\n"
        "INSTRUCCIONES IMPORTANTES:\n"
        "1. El nuevo módulo debe mantener relación directa con el tema principal del módulo original.\n"
        "2. Debe cubrir un aspecto diferente pero complementario al módulo original.\n"
        "3. Mantener el mismo idioma (español) que el título del módulo original.\n"
        "4. El nivel de complejidad debe ser similar al del módulo original.\n"
        "5. Los pasos deben ser concretos y específicos, no genéricos.\n"
        "6. El ejemplo debe ser práctico y directamente relacionado con los pasos descritos.\n\n"
        "Responde con un objeto JSON con exactamente esta estructura:\n"
        "{\n"
        '  "title": "Título específico y descriptivo del nuevo módulo",\n'
        '  "steps": ["Paso 1 específico", "Paso 2 específico", "Paso 3 específico", "Paso 4 específico"],\n'
        '  "example": "Un ejemplo práctico relacionado con los pasos (25-50 palabras)"\n'
        "}\n\n"
        "RECUERDA: Mantener coherencia temática con el módulo original, usar español, y proporcionar contenido específico y útil."
    )
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "stream": False,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        print(f"Solicitando reemplazo de módulo: {request.current_module_title}")
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error en la API: {response.text}")
        
        ai_response = response.json()
        content = ai_response["choices"][0]["message"]["content"].strip()
        
        # Limpieza de la respuesta
        content = re.sub(r"^```json\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        
        try:
            # Intentar analizar el JSON
            new_module = json.loads(content)
            
            # Verificar que tenga la estructura esperada
            if "title" not in new_module:
                new_module["title"] = f"Módulo alternativo a {request.current_module_title}"
            if "steps" not in new_module or not new_module["steps"]:
                new_module["steps"] = ["Conocer los conceptos básicos", "Realizar ejercicios prácticos"]
            if "example" not in new_module:
                new_module["example"] = ""
                
            return {"replacement_module": new_module}
            
        except json.JSONDecodeError:
            # Si no es un JSON válido, intentar extraer información útil
            print(f"Error decodificando JSON de módulo reemplazado: {content}")
            
            # Crear un módulo de respaldo
            module_title = request.current_module_title.lower()
            fallback_module = {}
            
            # Intentar extraer el tema principal del título
            if "gramática" in module_title:
                fallback_module = {
                    "title": "Uso práctico de la gramática en contextos cotidianos",
                    "steps": [
                        "Identificar errores gramaticales comunes en conversaciones",
                        "Aplicar reglas gramaticales en la redacción de correos electrónicos",
                        "Practicar la gramática mediante ejercicios de reformulación",
                        "Adaptar el lenguaje a diferentes contextos formales e informales"
                    ],
                    "example": "Analiza cómo cambia el significado en: 'Los estudiantes que aprobaron el examen fueron premiados' vs 'Los estudiantes, que aprobaron el examen, fueron premiados'."
                }
            elif "inglés" in module_title or "ingles" in module_title:
                fallback_module = {
                    "title": "Expresiones idiomáticas en inglés para conversaciones naturales",
                    "steps": [
                        "Reconocer expresiones idiomáticas comunes en inglés",
                        "Comprender el significado figurado vs. literal",
                        "Practicar el uso contextual de modismos",
                        "Incorporar expresiones en conversaciones cotidianas"
                    ],
                    "example": "En lugar de decir 'It's raining a lot', un hablante nativo diría 'It's raining cats and dogs', que literalmente significa 'llueven gatos y perros' pero se usa para expresar lluvia intensa."
                }
            elif "programación" in module_title or "programacion" in module_title or "python" in module_title:
                fallback_module = {
                    "title": "Depuración efectiva de código y manejo de errores",
                    "steps": [
                        "Identificar tipos comunes de errores (sintaxis, lógica, tiempo de ejecución)",
                        "Utilizar técnicas de depuración sistemática",
                        "Implementar manejo de excepciones adecuado",
                        "Aplicar pruebas unitarias para prevenir errores"
                    ],
                    "example": "En lugar de usar print() para depurar, utiliza un depurador como pdb en Python: import pdb; pdb.set_trace() para examinar variables en tiempo de ejecución."
                }
            else:
                # Fallback genérico pero más específico que el anterior
                fallback_module = {
                    "title": f"Aplicaciones prácticas: {request.current_module_title}",
                    "steps": [
                        f"Identificar situaciones reales donde aplicar los conocimientos de {request.current_module_title}",
                        "Resolver problemas prácticos usando las técnicas aprendidas",
                        "Adaptar los conceptos teóricos a diferentes contextos",
                        "Evaluar y mejorar resultados mediante análisis crítico"
                    ],
                    "example": f"Frente a un problema real, aplica los conceptos de {request.current_module_title} siguiendo estos pasos: 1) Identifica el problema, 2) Analiza posibles soluciones, 3) Implementa la mejor alternativa, 4) Evalúa el resultado."
                }
            
            return {"replacement_module": fallback_module}
    
    except Exception as e:
        print(f"Error al generar módulo de reemplazo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"No se pudo generar un módulo de reemplazo: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 