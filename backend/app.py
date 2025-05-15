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
    roadmap: List[str]
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
        "5. 🗺️ Mapa de aprendizaje\n"
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
        '  "roadmap": ["..."],\n'
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
        "max_tokens": 2000
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        if response.status_code != 200:
            # Log more detailed error information
            error_detail = f"Status code: {response.status_code}, Response: {response.text}"
            print(f"OpenRouter API error: {error_detail}")
            raise HTTPException(status_code=response.status_code, detail=error_detail)

        # Log successful response
        print(f"OpenRouter API response status: {response.status_code}")
        
        ai_response = response.json()
        print(f"OpenRouter API response: {json.dumps(ai_response, indent=2)}")
        
        content = ai_response["choices"][0]["message"]["content"]

        try:
            parsed = json.loads(content)
            for mod in parsed.get("modules", []):
                mod.setdefault("steps", [])
                mod.setdefault("example", "")
            # Cerrar la conexión a la base de datos antes de retornar la respuesta
            if 'conn' in locals() and conn:
                conn.close()
            return CourseResponse(**parsed)
        except json.JSONDecodeError:
            lines = content.split('\n')
            
            title = next((line.replace("Título:", "").strip() for line in lines if line.lower().startswith("título:")), request.topic)
            objective = next((line.replace("Objetivo:", "").strip() for line in lines if line.lower().startswith("objetivo:")), f"Aprender {request.topic}")
            summary = next((line.replace("Resumen:", "").strip() for line in lines if line.lower().startswith("resumen:")), "")

            prerequisites = extract_list("Conceptos previos:", lines)
            definitions = extract_list("Definiciones clave:", lines)
            roadmap = extract_list("Mapa de aprendizaje:", lines)
            faqs = extract_list("Preguntas frecuentes:", lines)
            errors = extract_list("Errores comunes:", lines)
            downloads = extract_list("Recursos descargables:", lines)
            resources = extract_list("Recursos adicionales:", lines)

            modules = []
            current_module = None
            for line in lines:
                if re.match(r"^m[oó]dulo \d+", line.lower()):
                    if current_module:
                        modules.append(current_module)
                    current_module = {"title": line.strip(), "steps": [], "example": ""}
                elif current_module:
                    if "ejemplo" in line.lower():
                        current_module["example"] = line.split(":", 1)[1].strip()
                    elif line.strip().startswith("-") or line.strip().startswith("•"):
                        current_module["steps"].append(line.strip("-• ").strip())
            if current_module:
                modules.append(current_module)

            # Cerrar la conexión a la base de datos antes de retornar la respuesta
            if 'conn' in locals() and conn:
                conn.close()

            return CourseResponse(
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

    except Exception as e:
        # Add more detailed error logging
        import traceback
        error_trace = traceback.format_exc()
        print(f"Exception in generate_course: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=str(e))

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 