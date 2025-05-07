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

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

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
    user = get_user(username=token_data.username)
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
    
    cursor.execute(
        "INSERT INTO users (id, username, email, password_hash) VALUES (?, ?, ?, ?)",
        (user_id, user_data.username, user_data.email, hashed_password)
    )
    
    conn.commit()
    
    # Fetch the newly created user
    cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "created_at": user[3]
    }

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
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "created_at": current_user["created_at"]
    }

@app.post("/generate-course", response_model=CourseResponse)
async def generate_course(request: CourseRequest, current_user: dict = Depends(get_current_user)):
    if not request.topic or len(request.topic.strip()) < 3:
        raise HTTPException(status_code=400, detail="Course topic must have at least 3 characters")

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
            raise HTTPException(status_code=response.status_code, detail=response.text)

        ai_response = response.json()
        content = ai_response["choices"][0]["message"]["content"]

        try:
            parsed = json.loads(content)
            for mod in parsed.get("modules", []):
                mod.setdefault("steps", [])
                mod.setdefault("example", "")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 