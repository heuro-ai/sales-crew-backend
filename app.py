from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sales AI Agent API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class SearchResult(BaseModel):
    title: str
    snippet: str
    link: str

class EmailVerificationRequest(BaseModel):
    first_name: str
    last_name: str
    domain: str

class EmailVerification(BaseModel):
    email: str
    isValid: bool
    status: str

class CompanyAnalysisRequest(BaseModel):
    company_name: str
    person_name: str
    position: str
    product_description: str

class CompanyAnalysis(BaseModel):
    company_analysis: dict
    decision_maker_profile: dict
    synergy_points: dict

class EmailGenerationRequest(BaseModel):
    company_name: str
    decision_maker: str
    decision_maker_position: str
    situation: str

class EmailContent(BaseModel):
    subject: str
    html_content: str
    plain_content: str

# API endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Sales AI Agent API"}

@app.post("/search", response_model=List[SearchResult])
async def search_companies(request: SearchRequest):
    # Mock implementation - replace with actual search logic
    mock_results = [
        {
            "title": f"Company Result {i+1} for '{request.query}'",
            "snippet": f"This is a mock search result {i+1} for the query '{request.query}'. Replace with actual search implementation.",
            "link": f"https://example.com/company-{i+1}"
        }
        for i in range(min(request.limit, 5))
    ]
    return mock_results

@app.post("/verify-email", response_model=EmailVerification)
async def verify_email(request: EmailVerificationRequest):
    # Mock implementation - replace with actual email verification logic
    email = f"{request.first_name.lower()}.{request.last_name.lower()}@{request.domain}"
    return {
        "email": email,
        "isValid": True,  # Mock - always return valid for demo
        "status": "verified"
    }

@app.post("/analyze-company", response_model=CompanyAnalysis)
async def analyze_company(request: CompanyAnalysisRequest):
    # Mock implementation - replace with actual AI analysis
    return {
        "company_analysis": {
            "industry": "Technology",
            "size": "Mid-size",
            "revenue": "$50M-100M",
            "growth_stage": "Scaling"
        },
        "decision_maker_profile": {
            "role": request.position,
            "responsibilities": ["Strategic planning", "Technology adoption"],
            "pain_points": ["Scaling challenges", "Cost optimization"]
        },
        "synergy_points": {
            "opportunities": ["Process automation", "Efficiency improvements"],
            "value_props": ["Cost savings", "Time efficiency"]
        }
    }

@app.post("/generate-email", response_model=EmailContent)
async def generate_email(request: EmailGenerationRequest):
    # Mock implementation - replace with actual AI email generation
    subject = f"Partnership Opportunity with {request.company_name}"
    html_content = f"""
    <html>
    <body>
        <p>Dear {request.decision_maker},</p>
        <p>I hope this email finds you well. As {request.decision_maker_position} at {request.company_name}, 
        you're likely facing {request.situation} challenges.</p>
        <p>I'd love to discuss how our solution can help address these challenges and drive growth for {request.company_name}.</p>
        <p>Would you be available for a brief 15-minute call next week?</p>
        <p>Best regards,<br/>Sales Team</p>
    </body>
    </html>
    """
    plain_content = f"""
    Dear {request.decision_maker},
    
    I hope this email finds you well. As {request.decision_maker_position} at {request.company_name}, 
    you're likely facing {request.situation} challenges.
    
    I'd love to discuss how our solution can help address these challenges and drive growth for {request.company_name}.
    
    Would you be available for a brief 15-minute call next week?
    
    Best regards,
    Sales Team
    """
    
    return {
        "subject": subject,
        "html_content": html_content,
        "plain_content": plain_content
    }

@app.post("/send-email")
async def send_email(email_data: dict):
    # Mock implementation - replace with actual email sending logic
    logger.info(f"Mock sending email to: {email_data.get('to', 'unknown')}")
    return {"status": "sent", "message": "Email sent successfully (mock)"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)