from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
import uuid

from models.user import User
from models.course import Course
from utils.auth import get_current_user
from utils.openrouter import generate_course_with_ai
from utils.payment import get_remaining_courses

# Pydantic models for requests and responses
from pydantic import BaseModel

class Module(BaseModel):
    title: str
    steps: List[str]
    example: Optional[str] = ""

class CourseRequest(BaseModel):
    topic: str
    experience_level: str
    available_time: str

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

# Create router
router = APIRouter()

@router.post("/generate-course", response_model=CourseResponse)
async def generate_course(request: CourseRequest, current_user: User = Depends(get_current_user)):
    """Generate a course with AI"""
    # Check remaining courses based on subscription
    remaining_courses = await get_remaining_courses(current_user)
    
    if remaining_courses == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have reached your course limit for your subscription tier"
        )
    
    # Generate the course with AI
    course_content = await generate_course_with_ai(
        topic=request.topic,
        experience_level=request.experience_level,
        available_time=request.available_time
    )
    
    return course_content

@router.post("/save-course")
async def save_course(course_data: SavedCourseRequest, current_user: User = Depends(get_current_user)):
    """Save a generated course"""
    # Check remaining courses based on subscription
    remaining_courses = await get_remaining_courses(current_user)
    
    if remaining_courses == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have reached your course limit for your subscription tier"
        )
    
    # Create and save new course
    new_course = Course(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title=course_data.title,
        prompt=course_data.prompt,
        content=course_data.content,
        experience_level=course_data.experience_level,
        available_time=course_data.available_time
    )
    
    await new_course.insert()
    
    return {"id": new_course.id, "message": "Course saved successfully"}

@router.get("/courses")
async def get_courses(current_user: User = Depends(get_current_user)):
    """Get all courses for the current user"""
    # Find all courses for the user
    courses = await Course.find(Course.user_id == current_user.id).to_list()
    
    # Format the response
    course_list = [
        {
            "id": course.id,
            "title": course.title,
            "experience_level": course.experience_level,
            "available_time": course.available_time,
            "created_at": course.created_at.isoformat()
        }
        for course in courses
    ]
    
    return course_list

@router.get("/courses/{course_id}")
async def get_course(course_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific course by ID"""
    # Find the course
    course = await Course.find_one(Course.id == course_id, Course.user_id == current_user.id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or access denied"
        )
    
    # Format the response
    return {
        "id": course.id,
        "title": course.title,
        "content": course.content,
        "experience_level": course.experience_level,
        "available_time": course.available_time,
        "created_at": course.created_at.isoformat()
    }

@router.delete("/courses/{course_id}")
async def delete_course(course_id: str, current_user: User = Depends(get_current_user)):
    """Delete a course"""
    # Find the course
    course = await Course.find_one(Course.id == course_id, Course.user_id == current_user.id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or access denied"
        )
    
    # Delete the course
    await course.delete()
    
    return {"success": True}

@router.post("/replace-topic")
async def replace_topic(request: TopicReplacementRequest, current_user: User = Depends(get_current_user)):
    """Replace a specific topic in a course with AI-generated content"""
    # Find the course
    course = await Course.find_one(Course.id == request.course_id, Course.user_id == current_user.id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or access denied"
        )
    
    # Generate a new section with AI
    prompt = f"Rewrite the following section in a {request.experience_level} level for {course.title}: {request.current_topic}"
    
    # Basic generation for this example
    # In a real implementation, you'd want to call a more specialized AI function
    response = await generate_course_with_ai(
        topic=f"Rewrite section: {request.current_topic}",
        experience_level=request.experience_level,
        available_time="N/A"
    )
    
    # Return the generated content
    # In a real implementation, you might want to update the course content directly
    return {
        "original": request.current_topic,
        "replacement": response.get("summary", "Failed to generate replacement"),
        "success": True
    }

@router.post("/replace-module")
async def replace_module(request: ModuleReplacementRequest, current_user: User = Depends(get_current_user)):
    """Replace a specific module in a course with AI-generated content"""
    # Find the course
    course = await Course.find_one(Course.id == request.course_id, Course.user_id == current_user.id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or access denied"
        )
    
    # Generate a new module with AI
    prompt = f"Rewrite the following module in a {request.experience_level} level for {course.title}: {request.current_module_title}"
    
    # Basic generation for this example
    # In a real implementation, you'd want to call a more specialized AI function
    response = await generate_course_with_ai(
        topic=f"Rewrite module: {request.current_module_title}",
        experience_level=request.experience_level,
        available_time="N/A"
    )
    
    # Extract just the first module from the response
    if response and "modules" in response and len(response["modules"]) > 0:
        new_module = response["modules"][0]
    else:
        new_module = {
            "title": f"Revised: {request.current_module_title}",
            "steps": ["Failed to generate new module content"],
            "example": ""
        }
    
    # Return the generated content
    # In a real implementation, you might want to update the course content directly
    return {
        "original_title": request.current_module_title,
        "new_module": new_module,
        "success": True
    } 