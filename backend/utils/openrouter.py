import os
import requests
import json
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

async def generate_course_with_ai(topic: str, experience_level: str, available_time: str) -> Dict[str, Any]:
    """
    Generate a complete course structure using OpenRouter AI
    """
    prompt = f"""Create a structured course about {topic} for a {experience_level} learner with {available_time} of study time available.

Your output should be a structured JSON with the following format:
{{
  "title": "Course title",
  "objective": "A concise paragraph explaining what the student will learn",
  "prerequisites": ["prerequisite 1", "prerequisite 2", ...],
  "definitions": ["concept 1: explanation", "concept 2: explanation", ...],
  "roadmap": {{"Week 1": ["topic 1", "topic 2"], "Week 2": ["topic 3", "topic 4"], ...}},
  "modules": [
    {{
      "title": "Module title",
      "steps": ["step 1", "step 2", ...],
      "example": "An example related to the module (optional)"
    }},
    ...
  ],
  "resources": ["resource 1", "resource 2", ...],
  "faqs": ["Q: question? A: answer", ...],
  "errors": ["Common error 1: How to fix it", ...],
  "downloads": ["name - URL", ...],
  "summary": "A concise summary of the entire course content"
}}

Only respond with the valid JSON, with no explanation or additional text.
Do not include any markdown formatting or code blocks, just the JSON object.
Ensure it's detailed and comprehensive but reasonable for the available time.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct:free",  # Using a more reliable free model
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000  # Reducing token count to avoid timeouts
    }

    try:
        print(f"Sending request to OpenRouter API for topic: {topic}")
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        print("Received response from OpenRouter API")
        result = response.json()
        ai_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Log response for debugging
        print(f"Response length: {len(ai_response)}")
        print(f"Response preview: {ai_response[:100]}...")
        
        # Extract JSON object from response
        json_str = extract_json_from_text(ai_response)
        if not json_str:
            print("Failed to extract JSON from response")
            raise ValueError("No valid JSON found in response")
            
        # Parse the JSON string
        course_data = json.loads(json_str)
        
        # Validate basic structure
        required_fields = [
            "title", "objective", "prerequisites", "definitions", 
            "roadmap", "modules", "resources", "faqs", "errors", 
            "downloads", "summary"
        ]
        
        # Add missing fields if needed
        for field in required_fields:
            if field not in course_data:
                if field in ["prerequisites", "definitions", "modules", "resources", "faqs", "errors", "downloads"]:
                    course_data[field] = []
                elif field == "roadmap":
                    course_data[field] = {"Basics": ["Getting Started"]}
                else:
                    course_data[field] = f"Generated {field}"
        
        print(f"Successfully generated course: {course_data.get('title', 'Unknown title')}")
        return course_data
        
    except Exception as e:
        print(f"Error generating course: {str(e)}")
        # Return a minimal structure in case of error
        return {
            "title": f"Course on {topic}",
            "objective": f"Learn about {topic} at {experience_level} level in {available_time}",
            "prerequisites": [],
            "definitions": [],
            "roadmap": {"Basics": ["Getting Started", "Core Concepts"]},
            "modules": [
                {
                    "title": f"Introduction to {topic}",
                    "steps": ["Understand the basics", "Practice with examples"],
                    "example": ""
                }
            ],
            "resources": [],
            "faqs": [],
            "errors": [f"Note: There was an error generating detailed content: {str(e)}"],
            "downloads": [],
            "summary": f"A course on {topic} for {experience_level} learners with {available_time} available."
        }

def extract_json_from_text(text: str) -> str:
    """
    Extract a JSON object from a text response, handling cases where the JSON might be
    embedded in markdown or surrounded by other text
    """
    # Clean up markdown code blocks
    text = re.sub(r'```json', '', text)
    text = re.sub(r'```', '', text)
    
    # Try to find JSON object boundaries
    json_start = text.find('{')
    json_end = text.rfind('}')
    
    if json_start >= 0 and json_end > json_start:
        # Extract the JSON string
        json_str = text[json_start:json_end+1]
        try:
            # Validate by parsing
            json.loads(json_str)
            return json_str
        except:
            # If parsing fails, log for debugging
            print(f"Failed to parse extracted JSON: {json_str[:100]}...")
    
    # If direct extraction failed, try a more aggressive approach
    try:
        # Look for structured data in any format
        print("Attempting to construct valid JSON from response")
        # Create a fallback JSON with minimal structure
        fallback_json = {
            "title": "Generated Course",
            "objective": "Learn new skills",
            "prerequisites": [],
            "definitions": [],
            "roadmap": {"Basics": ["Getting Started"]},
            "modules": [{"title": "Introduction", "steps": ["Step 1", "Step 2"], "example": ""}],
            "resources": [],
            "faqs": [],
            "errors": [],
            "downloads": [],
            "summary": "Course generated from AI"
        }
        
        # Try to extract meaningful content from the text
        if len(text) > 0:
            lines = text.split('\n')
            for line in lines:
                if "title" in line.lower() and len(line) > 10:
                    fallback_json["title"] = line.split(":", 1)[1].strip() if ":" in line else line.strip()
                    break
            
            fallback_json["summary"] = text[:100] + "..." if len(text) > 100 else text
        
        return json.dumps(fallback_json)
    except Exception as e:
        print(f"Failed to construct fallback JSON: {str(e)}")
        raise ValueError("No valid JSON found in response") 