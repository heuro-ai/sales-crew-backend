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
    product_description: str
    sender_name: str = "Sales Agent"
    sender_position: str = "Business Development"
    sender_company: str = "AI Sales Solutions"
    req_info: Optional[str] = None

class GeneratedEmail(BaseModel):
    subject: str
    body: str

class EmailSendRequest(BaseModel):
    to_email: str
    subject: str
    body: str

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Backend server is running"}

# Search endpoint (mock implementation)
@app.post("/search", response_model=List[SearchResult])
async def search_companies(request: SearchRequest):
    logger.info(f"Search request: {request.query}")
    
    # Mock search results for demo
    mock_results = [
        SearchResult(
            title="VP Sales at TechCorp Inc.",
            snippet="John Smith is the VP of Sales at TechCorp, leading a team of 50+ sales professionals...",
            link="https://linkedin.com/in/johnsmith"
        ),
        SearchResult(
            title="Chief Revenue Officer - DataSys Solutions",
            snippet="Sarah Johnson serves as CRO at DataSys Solutions, focusing on enterprise software sales...",
            link="https://linkedin.com/in/sarahjohnson"
        ),
        SearchResult(
            title="Sales Director at CloudTech Innovations",
            snippet="Mike Davis leads the sales division at CloudTech, specializing in cloud infrastructure...",
            link="https://linkedin.com/in/mikedavis"
        )
    ]
    
    # Return limited results based on request
    return mock_results[:request.limit]

# Email verification endpoint (mock implementation)
@app.post("/verify-email", response_model=EmailVerification)
async def verify_email(request: EmailVerificationRequest):
    logger.info(f"Email verification request: {request.first_name}.{request.last_name}@{request.domain}")
    
    # Generate mock email and verification
    email = f"{request.first_name.lower()}.{request.last_name.lower()}@{request.domain}"
    
    # Mock verification (in real implementation, this would use external service)
    is_valid = request.domain in ["gmail.com", "outlook.com", "company.com", "techcorp.com", "datasys.com"]
    
    return EmailVerification(
        email=email,
        isValid=is_valid,
        status="verified" if is_valid else "invalid"
    )

# Company analysis endpoint (mock implementation)
@app.post("/analyze-company", response_model=CompanyAnalysis)
async def analyze_company(request: CompanyAnalysisRequest):
    logger.info(f"Company analysis request: {request.company_name}")
    
    # Mock analysis data
    mock_analysis = CompanyAnalysis(
        company_analysis={
            "recent_news": f"{request.company_name} has recently announced strong Q4 results and is expanding their market presence.",
            "financial_health": "Strong financial position with consistent growth over the past 3 years.",
            "verified_challenges": ["Market competition", "Digital transformation needs", "Scaling operations"],
            "strategic_priorities": ["Customer acquisition", "Technology modernization", "Global expansion"]
        },
        decision_maker_profile={
            "communication_style": "Direct and results-oriented, prefers data-driven conversations.",
            "personality_indicators": "Strategic thinker with focus on ROI and efficiency.",
            "personality_type": "Analytical and goal-driven professional.",
            "key_achievements": "Led 40% revenue growth in previous role, known for innovative sales strategies.",
            "recent_activities": "Recently spoke at industry conference about sales automation trends."
        },
        synergy_points={
            "product_fit": f"Our {request.product_description} aligns perfectly with {request.company_name}'s digital transformation goals.",
            "persuasion_levers": ["ROI improvement", "Competitive advantage", "Operational efficiency"],
            "urgency_factors": ["Market competition", "Q1 targets", "Technology modernization timeline"]
        }
    )
    
    return mock_analysis

# Email generation endpoint (mock implementation)
@app.post("/generate-email", response_model=GeneratedEmail)
async def generate_email(request: EmailGenerationRequest):
    logger.info(f"Email generation request for {request.company_name}")
    
    # Mock personalized email generation
    subject = f"Boost {request.company_name}'s Sales Performance with {request.product_description}"
    
    body = f"""Hi {request.decision_maker},

I hope this message finds you well. I came across {request.company_name}'s recent achievements and was impressed by your strategic approach to market expansion.

As the {request.decision_maker_position}, I'm sure you're always looking for ways to drive revenue growth and improve operational efficiency. Our {request.product_description} has helped similar companies in your industry achieve:

• 40% increase in lead conversion rates
• 60% reduction in manual sales processes  
• 25% improvement in sales team productivity

I'd love to show you how we can help {request.company_name} achieve similar results. Would you be open to a brief 15-minute conversation next week to explore how this could benefit your sales organization?

Looking forward to hearing from you.

Best regards,
{request.sender_name}
{request.sender_position}
{request.sender_company}"""

    return GeneratedEmail(subject=subject, body=body)

# Email sending endpoint (mock implementation)
@app.post("/send-email")
async def send_email(request: EmailSendRequest):
    logger.info(f"Email send request to: {request.to_email}")
    
    # Mock email sending (in real implementation, this would use SMTP)
    return {"success": True, "message": f"Email sent successfully to {request.to_email}"}

if __name__ == "__main__":
    print("🚀 Starting Sales AI Agent Backend Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 Frontend should connect from: http://localhost:5173")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )