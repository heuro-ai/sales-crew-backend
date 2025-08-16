import ast
from fastapi import FastAPI, HTTPException, Form, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, String, TIMESTAMP, create_engine, text, ForeignKey, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from typing import List, Dict
import uuid
from datetime import datetime, timedelta
from email_verifier import find_valid_email
from google_api import google_search
from info_gather import get_company_and_person_info
import requests
import os
import dns.resolver
import json
import re
from fastapi.middleware.cors import CORSMiddleware
from Crypto.Cipher import AES
from base64 import b64decode
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from dotenv import load_dotenv
import random
from passlib.context import CryptContext
import jwt
from typing import Optional
from email_proposal import EmailProposalSystem
import razorpay
import smtplib
#import time module
import time
import urllib.parse
import asyncio
import asyncpg
import httpx

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
secret_key = os.getenv('ENCRYPTION_KEY')

# Razorpay setup
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

Base = declarative_base()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

pdf_paths = {
            "email": "email-template.pdf",
            "followup": "followup-template.pdf",
            "breakup": "breakup-template.pdf"
        }

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_unique_uuid(db: Session, table, column):
    while True:
        new_uuid = str(uuid.uuid4())
        exists = db.query(table).filter(column == new_uuid).first()
        if not exists:
            return new_uuid

# Email Tracking Model
class EmailStatus(Base):
    __tablename__ = "email_status"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'))  # Add user_id field
    dm_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    company_id = Column(String, ForeignKey('generated_companies.id', ondelete='CASCADE')) 
    dm_position = Column(String, nullable=False)
    email_id = Column(String, nullable=False)
    email_subject = Column(String, nullable=False)
    email_body = Column(String, nullable=False)
    email_type = Column(String) 
    status = Column(String, default="Not Responded")
    open_count = Column(Integer, default=0)
    date_sent = Column(TIMESTAMP, default=datetime.utcnow)
    date_opened = Column(TIMESTAMP)
    sender_name = Column(String, nullable=False)
    sender_company = Column(String, nullable=False)
    sender_position = Column(String, nullable=False)
    sender_email = Column(String)
    product_id = Column(String, ForeignKey('product_details.product_id', ondelete='CASCADE'))

# Follow-up Email Model
class FollowupStatus(Base):
    __tablename__ = "followup_status"
    followup_id = Column(String, ForeignKey('email_status.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'))  # Add user_id field
    email_uid = Column(String, nullable=False)
    followup_date = Column(TIMESTAMP, nullable=False)
    followup_status = Column(String, nullable=False)
    body = Column(String)
    subject = Column(String)
    open_count = Column(Integer, default=0)
    followup_sent_count = Column(Integer)
    company_name = Column(String, nullable=False)
    recipient_name = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    sender_name = Column(String, nullable=False)
    sender_company = Column(String, nullable=False)
    sender_position = Column(String, nullable=False)
    sender_email = Column(String)
    followup_threshold = Column(Integer)
    followup_type = Column(String)


# Product Details Model
class ProductDetails(Base):
    __tablename__ = "product_details"
    product_id = Column(String, primary_key=True, default='product_'+str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'))  # Add user_id field
    product_name = Column(String, nullable=False)
    preloading_status = Column(Boolean, default=False)  # New field
    existing_customers = Column(String, nullable=True)
    product_description = Column(String, nullable=True)
    target_min_emp_count = Column(Integer, nullable=True)
    target_max_emp_count = Column(Integer, nullable=True)
    target_industries = Column(String, nullable=True)
    target_geo_loc = Column(String, nullable=True)
    target_business_model = Column(String, nullable=True)
    addressing_pain_points = Column(String, nullable=True)

# User Model
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    company_name = Column(String)  # Change to list
    position = Column(String)  # Change to dictionary
    otp = Column(Integer)
    product_limit = Column(Integer, default=1)
    company_limit = Column(Integer, default=10)
    is_verified = Column(Boolean, default=False)  # New field

# Generated Company Model
class GeneratedCompany(Base):
    __tablename__ = "generated_companies"
    id = Column(String, primary_key=True, default='generatedCompany_'+str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'))
    product_id = Column(String, ForeignKey('product_details.product_id', ondelete='CASCADE'))
    company_name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    domain = Column(String, nullable=True)
    status = Column(String, default="Decision Maker Found")
    personality_type = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    body = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    decision_maker_name = Column(String, nullable=True)  # New field
    decision_maker_email = Column(String, nullable=True)  # New field
    decision_maker_position = Column(String, nullable=True)  # New field
    failed_company = Column(Boolean, default=False)  # New field

# Subscription Model
class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(String, primary_key=True, default='subscription_' + str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'))
    plan_name = Column(String, nullable=False)
    start_date = Column(TIMESTAMP, default=datetime.utcnow)
    end_date = Column(TIMESTAMP, nullable=False)
    status = Column(String, default="Active")

Base.metadata.create_all(bind=engine)

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
USERNAME = os.environ.get('EMAIL_USERNAME')
PASSWORD = os.environ.get('EMAIL_PASSWORD')


# FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://lead-stream.heuro.in",  # Correct URL without trailing slash
        "https://sales-ai-agent-crm-fgbna0ghdrhxb5hp.centralindia-01.azurewebsites.net",
        "https://leadagent.in",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class EmailData(BaseModel):
    recipient_name: str
    company_name: str
    company_id: str
    dm_position: str
    recipient: str
    subject: str
    body: str
    sender_name: str
    sender_company: str
    sender_position: str
    product_id: str

class FollowupData(BaseModel):
    email_uid: str
    body: str = None
    subject: str = None
    followup_sent_count: int = 0
    recipient_name: str = None
    company_name: str = None
    sender_name: str = None
    sender_company: str = None
    sender_position: str = None
    recipient: str = None

class ProductRequest(BaseModel):
    user_id: Optional[str] = None
    product_id: Optional[str] = None
    product_name: str
    existing_customers: List[str] = None
    product_description: str = None
    target_min_emp_count: Optional[int] = None
    target_max_emp_count: Optional[int] = None
    target_industries: List[str] = None
    target_geo_loc: List[str] = None
    sender_position: Optional[str] = None
    sender_company: Optional[str] = None
    target_business_model: List[str] = None
    addressing_pain_points: List[str] = None
    limit: int = 5

class DecisionMakerRequest(BaseModel):
    company_name: str
    domain_name: str
    industry: str

class EmailProposalRequest(BaseModel):
    product_description: str
    company_name: str
    decision_maker: str
    decision_maker_position: str
    sender_name: str
    sender_position: str
    sender_company: str

class ReminderRequest(BaseModel):
    type: str
    sender_name: str
    sender_position: str
    sender_company: str

class TrackedEmail(BaseModel):
    id: str

class UserCreate(BaseModel):
    id: str = None
    password: str = Field(..., min_length=6)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    company_name: List[str] = Field(..., min_items=1)  # Change to list
    position: Dict[str, List[str]] = Field(..., min_items=1)  # Change to dictionary with list of positions as values
    otp: int = None
    product_limit: int = 1
    user_company_limit: int = 10

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: int

class PositionEditRequest(BaseModel):
    company_name: str
    position: List[str]

class CompanyEditRequest(BaseModel):
    company_name: str
    new_company_name: Optional[str] = None
    position: Dict[str, List[str]] = None

class GeneratedCompanyRequest(BaseModel):
    product_id: str
    companies: List[Dict[str, Optional[str]]]  # Allow Optional[str] for decision maker fields

class GeneratedCompanyUpdateRequest(BaseModel):
    company_id: str
    status: str
    decision_maker_name: Optional[str] = None  # New field
    personality_type: Optional[str] = None  # New field
    linkedin_url: Optional[str] = None  # New field
    decision_maker_email: Optional[str] = None  # New field
    subject: Optional[str] = None  # New field
    body: Optional[str] = None  # New field
    decision_maker_position: Optional[str] = None  # New field
    failed_company: Optional[bool] = False  # New field
    domain_name: Optional[str] = None

class SubscriptionRequest(BaseModel):
    plan_name: str
    duration_days: int
    amount: float

class PaymentSuccess(BaseModel):
    order_id: str
    payment_id: str
    signature: str

class PaymentFailure(BaseModel):
    order_id: str

# OpenAI and Perplexity Configuration
API_KEY = os.getenv("PERPLEXITY_API_KEY")
BASE_URL = "https://api.perplexity.ai/chat/completions"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def decrypt_password(encrypted_password: str) -> str:
    secret_key = os.environ.get("ENCRYPTION_KEY")
    iv = os.environ.get("ENCRYPTION_IV")
    print("SECRET KEY", secret_key)
    print("IV", iv)
    if not secret_key or not iv:
        raise ValueError("ENCRYPTION_KEY or ENCRYPTION_IV environment variable is not set")
    
    print("ENCRYPTED PASSWORD from func", encrypted_password)
    
    ciphertext = b64decode(encrypted_password)
    derived_key = b64decode(secret_key)
    cipher = AES.new(derived_key, AES.MODE_CBC, iv.encode('utf-8'))
    decrypted_data = cipher.decrypt(ciphertext)
    return unpad(decrypted_data, 16).decode("utf-8")

def identify_smtp_server(email: str) -> tuple:
    # Extract the domain from the email address.
    try:
        domain = email.split('@')[-1].lower()
    except IndexError:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Mapping from substrings (found in MX records) to SMTP server settings.
    # For example, if the MX record contains 'google.com' then we assume the provider is Gmail.
    known_mx_map = {
        'google.com': ('smtp.gmail.com', 587),
        'yahoo.com': ('smtp.mail.yahoo.com', 587),
        'outlook.com': ('smtp.office365.com', 587),
        'hotmail.com': ('smtp.office365.com', 587),
        'hostinger.com': ('smtp.hostinger.com', 587),
        # You can add additional keys as needed.
    }
    
    # Attempt to retrieve the MX records for the domain.
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Unable to resolve MX record for domain '{domain}': {e}"
        )
    
    # Check each MX record against the known keys.
    for mx in mx_records:
        mx_name = str(mx.exchange).rstrip('.').lower()
        for key, smtp_info in known_mx_map.items():
            if key in mx_name:
                return smtp_info
    
    # If no known key is found in the MX records, return a default SMTP server.
    return ("smtpout.secureserver.net", 587)

@app.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    otp = random.randint(100000, 999999)
    user_id = 'user_' + generate_unique_uuid(db, User, User.id)  # Generate a unique UUID for the user ID
    new_user = User(
        id=user_id,  # Set the user ID
        username=user.email.split('@')[0],  # Use the email prefix as the username
        password=hash_password(decrypt_password(user.password)),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        company_name=json.dumps(user.company_name),  # Convert list to JSON string
        position=json.dumps(user.position),  # Convert dictionary with list of strings to JSON string
        otp=otp,
        is_verified=False  # Set is_verified to False initially
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send OTP email
    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL_USERNAME')
    msg['To'] = user.email
    msg['Subject'] = "Your OTP Code"
    body = f"""<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>OTP Verification - Lead Stream</title>
                </head>
                <body style="background-color: rgb(89,227,167); margin: 0; padding: 20px; font-family: Arial, sans-serif; text-align: center;">

                    <!-- Wrapper Table to Center Everything -->
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                        <tr>
                            <td align="center">

                                <!-- Logo Row (Placed Above the Container) -->
                                <table role="presentation" width="360px" cellspacing="0" cellpadding="0" border="0">
                                    <tr>
                                        <td align="left" style="padding-bottom: 15px;">
                                            <img src="https://twingenfuelfiles.blob.core.windows.net/lead-stream/heuro.png" alt="Heuro Logo" width="80">
                                        </td>
                                    </tr>
                                </table>

                                <!-- Email Container -->
                                <table role="presentation" width="360px" cellspacing="0" cellpadding="0" border="0" style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 20px; text-align: center;">
                                    
                                    <!-- Title -->
                                    <tr>
                                        <td style="font-size: 22px; font-weight: bold; color: #2c3e50; padding-bottom: 10px;">
                                            Lead Stream OTP Verification
                                        </td>
                                    </tr>

                                    <!-- Message -->
                                    <tr>
                                        <td style="font-size: 14px; color: #7f8c8d; padding-bottom: 20px;">
                                            Please use the following code to verify your account:
                                        </td>
                                    </tr>

                                    <!-- OTP Code -->
                                    <tr>
                                        <td style="font-size: 30px; font-weight: bold; color: #4ca1af; letter-spacing: 2px; padding: 10px; border: 2px solid #4ca1af; border-radius: 5px; display: inline-block;">
                                            {otp}
                                        </td>
                                    </tr>

                                    <!-- Expiry Notice -->
                                    <tr>
                                        <td style="font-size: 14px; color: #7f8c8d; padding-top: 20px;">
                                            This code will expire in 10 minutes.
                                        </td>
                                    </tr>

                                    <!-- Footer -->
                                    <tr>
                                        <td style="font-size: 12px; color: #95a5a6; padding-top: 20px;">
                                            Lead Stream is a product of <a href="https://heuro.in" target="_blank" style="color: #4ca1af; text-decoration: none;">heuro.in</a>
                                        </td>
                                    </tr>

                                </table>
                                
                            </td>
                        </tr>
                    </table>

                </body>
                </html>
                """

    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT')) as server:
            server.starttls()
            server.login(os.getenv('EMAIL_USERNAME'), os.getenv('EMAIL_PASSWORD'))
            server.sendmail(os.getenv('EMAIL_USERNAME'), user.email, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")

    return {"message": "User registered successfully. Please verify your email with the OTP sent."}

@app.post("/login/")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    # convert object to dict
    if not db_user or not verify_password(decrypt_password(user.password), db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not db_user.is_verified:
        raise HTTPException(status_code=400, detail="Please verify your email with the OTP sent before logging in.")
    access_token = create_access_token(data={"name": db_user.username, "user_id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/verify_otp/")
def verify_otp(request: VerifyOtpRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email, User.otp == request.otp).first()
    print("USER: ", user)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    user.otp = 0  # Clear the OTP after successful verification
    user.is_verified = True  # Set is_verified to True
    db.commit()
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/user")
def get_user(user_id: str, db: Session = Depends(get_db)):
    try:
        # extract First Name, Last Name, email, company name, position
        user = db.query(User).filter(User.id == user_id).first()
        print(user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "company_name": json.loads(user.company_name),  # Convert JSON string to list
            "product_limit": user.product_limit,
            "company_limit": user.company_limit,
            "position": json.loads(user.position)  # Convert JSON string to dictionary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {e}")

@app.post("/potential-companies")
async def start_process(background_tasks: BackgroundTasks, request: ProductRequest, db: Session = Depends(get_db)):
    background_tasks.add_task(get_potential_companies, request, db)
    return {"message": "Companies generation process started"}
def get_potential_companies(request: ProductRequest, db: Session = Depends(get_db)):
    try:
        if not API_KEY:
            raise HTTPException(status_code=500, detail="API Key not configured")
        
        existing_customers = request.existing_customers
        print("Starting potential companies generation")
        potential_dms = []

        db = SessionLocal()
        product_item = db.query(ProductDetails).filter(ProductDetails.product_id == request.product_id).first()
        if not product_item:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_item.preloading_status = True
        db.commit()
        
        while len(potential_dms) < request.limit:
            try:
                prompt = f"""
    Given the detailed product information and Ideal Client Profile (ICP) provided below, analyze and identify:
    1. The top {request.limit} companies that demonstrate a strong potential to become customers of {request.product_name}. Each identified company must strictly satisfy the specified target criteria—including employee count, industry, geographical location, and business model—and show clear indicators of being a viable future customer for this product. Exclude any companies listed in the 'Existing Customers' from this list.
    2. Craft the output potential companies with the limit of {request.limit} that are defined as companies with a significant market presence, a long track record of success, and stable growth. These companies should also meet the target criteria for employee count, industry, geographical location, and business model.

    ### Product Information:
    - **Product Name**: {request.product_name} ( This is the name of the product )
    - **Product Description**: {request.product_description or 'N/A'} ( Thsi is what the product does )
    - **Existing Customers**: {', '.join(existing_customers) if existing_customers else 'N/A'} (  These are the companies that are already maybe using the product )
    - **Target Industries**: {', '.join(request.target_industries) if request.target_industries else 'N/A'} ( These are the industries that the product is targeting, so Identify companies in these industries )
    - **Target Employee Count**: {request.target_min_emp_count or 'N/A'} to {request.target_max_emp_count or 'N/A'} ( These is the range of employees in the company, so identify companies in this employee count range )
    - **Target Geographical Locations**: {', '.join(request.target_geo_loc) if request.target_geo_loc else 'N/A'} ( These are the locations where the companies should be located, so identify companies with mix of these locations )
    - **Target Business Models**: {', '.join(request.target_business_model) if request.target_business_model else 'N/A'} ( These are the business models that the product is targeting, so identify companies with these business models )
    - **Addressing Pain Points**: {', '.join(request.addressing_pain_points) if request.addressing_pain_points else 'N/A'} ( These are the pain points that the product is addressing, so identify companies with these pain points )

    ### Chain-of-Thought Instructions (Internal Use Only):
    Employ a chain-of-thought method to thoroughly analyze the provided information and determine:
    - The companies with strong potential to become customers of {request.product_name}, ensuring they meet all specified criteria and strictly are not part of Existing Customers: {existing_customers}.
    - The companies that are well established customers, characterized by a significant market presence, long operational history, and stable growth, while also meeting the target criteria.
    **Do not include any internal reasoning or chain-of-thought details in the final output.**

    ### Instructions:
    - **Data Accuracy**: Ensure all company details, especially domain names, are accurate and verified through reliable sources. Avoid assumptions or unverifiable information.
    - **Web Browsing**: Utilize official company websites, reputable business directories, and recent news articles to gather current and precise information. Provide companies that have a valid domain.
    - **Exclusions**: For the list of potential customers, strictly exclude companies listed under 'Existing Customers'.

    ### Output Format: ( provide only a single JSON with the below keys alone as output without any additional text or content )
    - name: Company name
    - industry: Industry type
    - domain: Company's domain name (ensure accuracy; exclude 'www.', 'http://', or 'https://')

    Ensure that the output strictly adheres to this format and includes only companies that meet all specified criteria. If certain details cannot be verified, omit those companies from the list. Provide only the JSON as output without any additional text or content.
    """

                payload = {
                    "model": "sonar",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                }
                response = requests.post(
                    BASE_URL,
                    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                usage = data.get("usage", {})
                print("Potential companies generated")
                print(f"Input tokens: {usage.get('prompt_tokens', 'N/A') * 0.0000002}")
                print(f"Output tokens: {usage.get('completion_tokens', 'N/A') * 0.0000002}")
                print(f"Total tokens: {usage.get('total_tokens', 'N/A')}")
            except requests.exceptions.RequestException as e:
                raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")

            if not data or "choices" not in data or not data["choices"]:
                raise HTTPException(status_code=500, detail="Invalid response from API")

            formatted_response = format_response(data)

            print("Getting potential Decision Makers")

            i=0

            for company in formatted_response:
                comp_name = company['name']
                industry = company['industry']
                domain = company['domain']
                existing_customers.append(comp_name)
                print("Req", existing_customers)
                ref_request = DecisionMakerRequest(company_name=comp_name, domain_name=domain, industry=industry)
                
                try:
                    potential_dm = get_potential_decision_makers(request=ref_request)
                    
                    # Always add the company to potential_dms, even if no decision maker is found
                    if potential_dm['decision_maker_email']:
                        potential_dm['status'] = "Decision Maker Found"
                        curr_user = db.query(User).filter(User.id == request.user_id).first()
                        email_proposal_req = EmailProposalRequest(
                            product_description=request.product_description,
                            company_name=comp_name,
                            decision_maker=potential_dm['decision_maker_name'],
                            decision_maker_position=potential_dm['decision_maker_position'],
                            sender_name=curr_user.first_name + ' ' + curr_user.last_name,
                            sender_position=request.sender_position,
                            sender_company=request.sender_company
                        )
                        generated_proposal = get_email_proposal(email_proposal_req)
                        print(f"{i} Generated Proposal: ", generated_proposal)
                        i+=1
                        potential_dm['status'] = "Mail Drafted"
                        potential_dm['personality_type'] = generated_proposal['personality_type']
                        potential_dm['subject'] = generated_proposal['subject']
                        potential_dm['body'] = generated_proposal['body']
                    else:
                        potential_dm['status'] = "No Decision Maker Found"
                        potential_dm['personality_type'] = None
                        potential_dm['subject'] = None
                        potential_dm['body'] = None
                    
                    potential_dms.append(potential_dm)
                    if len(potential_dms) == request.limit:
                        print("Potential companies fetched and formatted: ", potential_dms)
                        break
                        
                except Exception as e:
                    print(f"Error processing company {comp_name}: {e}")
                    # Add company with error status
                    error_company = {
                        'name': comp_name,
                        'decision_maker_name': None,
                        'decision_maker_email': None,
                        'decision_maker_position': None,
                        'linkedin_url': None,
                        'domain': domain,
                        'industry': industry,
                        'status': 'Error Processing',
                        'personality_type': None,
                        'subject': None,
                        'body': None
                    }
                    potential_dms.append(error_company)
                    if len(potential_dms) == request.limit:
                        break

        print("Potential companies fetched and formatted: ", potential_dms)

        # Check if we have any companies to process
        if not potential_dms:
            print("No companies were processed successfully")
            # Update product status and return
            product_item = db.query(ProductDetails).filter(ProductDetails.product_id == request.product_id).first()
            if product_item:
                product_item.preloading_status = False
                db.commit()
            return []

        # Clean and validate the data structure before creating GeneratedCompanyRequest
        print("Raw potential_dms data structure:")
        for i, company in enumerate(potential_dms):
            print(f"Company {i}: {company}")
            for key, value in company.items():
                print(f"  {key}: {value} (type: {type(value)})")
        
        cleaned_companies = []
        for company in potential_dms:
            # Create a completely clean company object with all fields properly handled
            cleaned_company = {}
            
            # Handle all possible field names and ensure they're strings or None
            for key, value in company.items():
                if isinstance(value, list):
                    # If it's a list, take the first non-empty value or None
                    if value and len(value) > 0:
                        cleaned_company[key] = str(value[0])
                    else:
                        cleaned_company[key] = None
                elif isinstance(value, (str, int, float)):
                    # If it's a basic type, convert to string
                    cleaned_company[key] = str(value)
                elif value is None:
                    # If it's None, keep it as None
                    cleaned_company[key] = None
                else:
                    # For any other type, convert to string representation
                    cleaned_company[key] = str(value)
            
            # Ensure all required fields exist
            required_fields = ['name', 'decision_maker_name', 'decision_maker_position', 'decision_maker_email', 
                             'linkedin_url', 'domain', 'industry', 'status', 'personality_type', 'subject', 'body']
            
            for field in required_fields:
                if field not in cleaned_company:
                    cleaned_company[field] = None
            
            cleaned_companies.append(cleaned_company)
            print(f"Cleaned company {len(cleaned_companies)}: {cleaned_company}")

        print("About to create GeneratedCompanyRequest with cleaned data...")
        req = GeneratedCompanyRequest(product_id=request.product_id, companies=cleaned_companies)
        print("GeneratedCompanyRequest created successfully!")

        add_generated_company = add_generated_companies(req, request.user_id)

        # send a notification message telling the user that the companies have been generated
        db = SessionLocal()
        user_mail = db.query(User).filter(User.id == request.user_id).first().email
        smtp_server, smtp_port = identify_smtp_server(user_mail)

        html_body = f"""<!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1">
                            <title>Companies Generated</title>
                        </head>
                        <body style="background-color: rgb(89,227,167); margin: 0; padding: 20px; font-family: Arial, sans-serif; text-align: center;">

                            <!-- Wrapper Table to Center Everything -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td align="center">

                                        <!-- Logo Row (Placed Above the Container) -->
                                        <table role="presentation" width="360px" cellspacing="0" cellpadding="0" border="0">
                                            <tr>
                                                <td align="left" style="padding-bottom: 15px;">
                                                    <img src="https://twingenfuelfiles.blob.core.windows.net/lead-stream/heuro.png" alt="Heuro Logo" width="80">
                                                </td>
                                            </tr>
                                        </table>

                                        <!-- Email Container -->
                                        <table role="presentation" width="360px" cellspacing="0" cellpadding="0" border="0" style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 20px; text-align: center;">
                                            
                                            <!-- Title -->
                                            <tr>
                                                <td style="font-size: 22px; font-weight: bold; color: #2c3e50; padding-bottom: 10px;">
                                                    Companies Generated
                                                </td>
                                            </tr>

                                            <!-- Message -->
                                            <tr>
                                                <td style="font-size: 14px; color: #7f8c8d; padding-bottom: 20px;">
                                                    The potential companies have been generated successfully. Please check your dashboard for more details.
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size: 14px; color: #7f8c8d; padding-bottom: 20px;">
                                                    <a href="https://leadagent.in/generate" target="_blank" style="color: #4ca1af; text-decoration: none;">Leadagent</a>
                                                </td>
                                            </tr>
                                            <!-- Footer -->
                                            <tr>
                                            <td style="font-size: 12px; color: #95a5a6; padding-top: 20px;">
                                                Lead Stream is a product of 
                                                <a href="https://heuro.in" target="_blank" style="color: #4ca1af; text-decoration: none;">
                                                heuro.in
                                                </a>
                                                <br>
                                                <a href="tel:+919655612306" style="color: #4ca1af; text-decoration: none;">
                                                +91 96556 12306
                                                </a>
                                                <br>
                                                <a href="mailto:dharani96556@gmail.com" style="color: #4ca1af; text-decoration: none;">
                                                dharani96556@gmail.com
                                                </a>
                                            </td>
                                            </tr>

                                        </table>
                                        
                                    </td>
                                </tr>
                            </table>

                        </body>
                        </html>
                        """
        
        send_notification_email(user_mail, "Companies Generated", html_body)

        product_item = db.query(ProductDetails).filter(ProductDetails.product_id == request.product_id).first()
        product_item.preloading_status = False
        db.commit()

    
        return potential_dms
    
    except Exception as e:
        db = SessionLocal()
        user_mail = db.query(User).filter(User.id == request.user_id).first().email
        smtp_server, smtp_port = identify_smtp_server(user_mail)

        html_body = f"""<!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1">
                            <title>Error Generating Companies</title>
                        </head>
                        <body style="background-color: rgb(89,227,167); margin: 0; padding: 20px; font-family: Arial, sans-serif; text-align: center;">

                            <!-- Wrapper Table to Center Everything -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td align="center">

                                        <!-- Logo Row (Placed Above the Container) -->
                                        <table role="presentation" width="360px" cellspacing="0" cellpadding="0" border="0">
                                            <tr>
                                                <td align="left" style="padding-bottom: 15px;">
                                                    <img src="https://twingenfuelfiles.blob.core.windows.net/lead-stream/heuro.png" alt="Heuro Logo" width="80">
                                                </td>
                                            </tr>
                                        </table>

                                        <!-- Email Container -->
                                        <table role="presentation" width="360px" cellspacing="0" cellpadding="0" border="0" style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 20px; text-align: center;">
                                            
                                            <!-- Title -->
                                            <tr>
                                                <td style="font-size: 22px; font-weight: bold; color: #2c3e50; padding-bottom: 10px;">
                                                    Error Generating Companies
                                                </td>
                                            </tr>

                                            <!-- Message -->
                                            <tr>
                                                <td style="font-size: 14px; color: #7f8c8d; padding-bottom: 20px;">
                                                    There was an error generating potential companies. Please try again or contact support if the issue persists.
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size: 14px; color: #7f8c8d; padding-bottom: 20px;">
                                                    <a href="tel:+919655612306" style="color: #4ca1af; text-decoration: none;">+91 96556 12306</a>
                                                    <a href="mailto:dharani96556@gmail.com" style="color: #4ca1af; text-decoration: none;">dharani96556@gmail.com</a>
                                                </td>
                                            </tr>

                                            <!-- Footer -->
                                            <tr>
                                                <td style="font-size: 12px; color: #95a5a6; padding-top: 20px;">
                                                    Lead Stream is a product of <a href="https://heuro.in" target="_blank" style="color: #4ca1af; text-decoration: none;">heuro.in</a>
                                                </td>
                                            </tr>

                                        </table>
                                        
                                    </td>
                                </tr>
                            </table>

                        </body>
                        </html>
                        """
        
        send_notification_email(user_mail, "Error Generating Companies", html_body)
        
        product_item = db.query(ProductDetails).filter(ProductDetails.product_id == request.product_id).first()
        product_item.preloading_status = False
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error generating potential companies: {e}")

# @app.post("/potential-decision-makers")
def get_potential_decision_makers(request: DecisionMakerRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key not configured")
    
    print("Fetching decision makers for ", request.company_name)
    comp_name = request.company_name
    api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = os.getenv('SEARCH_ENGINE_ID')
    domain_search_engine_id = os.getenv('DOMAIN_SEARCH_ENGINE_ID')

    query = f"{request.company_name} {request.industry}"
    print("QUERY: ", query)
    result = google_search(query, limit=3)
    # result = google_search(api_key, domain_search_engine_id, query, limit=3)
    # domain_docs = [item.get('link').split('//')[-1].split('/')[0].replace('www.', '') for item in result.get('items', [])]

    if not result:
        print("No search results found for domain search")
        domain_docs = []
    else:
        domain_docs = [item.get('url', '').split('//')[-1].split('/')[0].replace('www.', '') for item in result if item.get('url')]

    # print("DOMAIN DOCS: ", domain_docs)

    # domain may be in the form of https://www.example.com or https://example.com
    domain = request.domain_name
    # print(domain_docs)

    positions = ['CEO', 'Founder']
    results = []
    for i in positions:
        query = f"Current {i} at {domain} site:linkedin.com"
        try:
            result = google_search(query, limit=3)
            # result = google_search(api_key, search_engine_id, query, limit=3)  # Set limit to 5
            # Process results
            ref_res = []
            # for item in result.get('items', []):
            if result:
                for item in result:
                    title = item.get('title')
                    snippet = item.get('description')
                    print(f'Title: {title}\nSnippet: {snippet}\n')
                    ref_res.append({'title': title, 'snippet': snippet})
            results.append({i: ref_res})
        except Exception as e:
            print(f"Error searching for {i} position: {e}")
            results.append({i: []})

    print("Results fetched ", results)

    scrapped_docs = []

    # Process results
    for item in results:
        for key, value in item.items():
            for i in value:
                scrapped_docs.append({'name': i['title'], 'position': key})

    if not scrapped_docs:
        print("No decision makers found for the company, returning default data")
        # Return a default company structure instead of raising an exception
        return {
            'name': request.company_name,
            'decision_maker_name': None,
            'decision_maker_email': None,
            'decision_maker_position': None,
            'linkedin_url': None,
            'domain': request.domain_name,
            'industry': request.industry,
            'status': 'No Decision Maker Found'
        }

    # print("Scrapped CEO, Co-CEO and VP of the company ", comp_name, " from LinkedIn: ", scrapped_docs)
    
    print("Decision makers details fetched for ", comp_name)

    prompt = f"""
                Given:  
                - Company: {comp_name}  
                - Initial Domain Claim: {domain}  
                - Domain Validation Documents: {domain_docs}  
                - LinkedIn Profiles: {scrapped_docs}  
                Execute:  
                1. **Identify Decision Makers**  
                - Select 1 profile with highest business decision authority using hierarchy:  
                    CEO/CFO/COO > President/VP > Director > Department Head  
                - Exclude technical/operational roles (e.g., IT Manager, HR Lead)  
                2. **Validate/Correct Domain**  
                - Compare {domain} with keywords in {domain_docs}  
                - If mismatch: Extract dominant industry from documents  
                - If unclear: Retain original {domain}  
                3. **Output Fields**
                - Get the Name and Role of the identified person
                - Replace them in the output json
                Output **ONLY** this JSON ( Replace with person's name and title in the respective field ):  
                ( Provide person name as the key and role as the value in the JSON, also add a key called domain with value as the validated domain or original domain. )
                ( Do not include any additional text or content in the output )"""

    payload = {
        "model": "sonar-reasoning-pro",
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }


    try:
        response = requests.post(
            BASE_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload,
        )
        data = response.json()
        usage = data.get("usage", {})
        print(f"Input tokens: {usage.get('prompt_tokens', 'N/A') * 0.000005}")
        print(f"Output tokens: {usage.get('completion_tokens', 'N/A') * 0.000008}")
        print(f"Total tokens: {usage.get('total_tokens', 'N/A')}")
        response.raise_for_status()
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")
    
    api_response = format_response(response.json())

    print("Decision makers found and formatted for ", comp_name)

    company = {'name': comp_name, 'decision_maker_name': None, 'decision_maker_email': None, 'decision_maker_position': None, 'linkedin_url': None, 'domain': api_response['domain'], 'industry': request.industry}

    dm_names = []
    dm_positions = []
    linkedin_urls = []

    for key, value in api_response.items():
            
        if key.strip(' ')[2] != 'linkedin' and key.strip() != 'domain':
            company['decision_maker_name'] = key
            company['decision_maker_position'] = value

            first_name = None
            last_name = None
            middle_name = None

            if len(key.split(' ')) == 2:
                first_name, last_name = key.split(' ')
            elif len(key.split(' ')) == 3:
                first_name, middle_name, last_name = key.split(' ')
            elif len(key.split(' ')) == 1:
                first_name = key

            ref = find_valid_email(first_name, last_name, company['domain'])
            # print(ref)
            valid_email, status = ref
            print("Valid email:", valid_email)
            if valid_email:
                linkedin_url_query = f"{key} {value} of {request.company_name} site:linkedin.com"
                linkedin_url = google_search(linkedin_url_query, limit=1)
                # linkedin_url = google_search(api_key, search_engine_id, linkedin_url_query, limit=1)
                # print("Linkedin URL: ", linkedin_url)
                if linkedin_url and len(linkedin_url) > 0:                  
                    company['linkedin_url'] = linkedin_url[0]['url']
                else:
                    company['linkedin_url'] = f'https://linkedin.com/pub/dir/{first_name}/{last_name}'
                company['decision_maker_email'] = valid_email
                company['status'] = status
                break
            else:
                linkedin_url = google_search(f"{key} {value} of {request.company_name} site:linkedin.com", limit=1)
                # linkedin_url = google_search(api_key, search_engine_id, f"{key} {value} of {request.company_name} site:linkedin.com", limit=1)
                # print("Linkedin URL: ", linkedin_url)
                # find for a key in linkedin_url
                if linkedin_url and len(linkedin_url) > 0:                  
                    company['linkedin_url'] = linkedin_url[0]['url']
                else:
                    company['linkedin_url'] = f'https://linkedin.com/pub/dir/{first_name}/{last_name}'
                company['decision_maker_email'] = None
                company['decision_maker_name'] = key  # Keep as string, not list
                company['decision_maker_position'] = value  # Keep as string, not list
                company['status'] = status
                print("Appended")
            
    print(f"Final company structure before return: {company}")
    return company


@app.get("/product_loading_status")
async def get_product_loading_status(user_id: str, product_id: str, db: Session = Depends(get_db)):
    try:
        conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
        row = await conn.fetchrow("SELECT preloading_status FROM product_details WHERE product_id = $1", product_id)
        await conn.close()
        if row:
            return {"product_id": product_id, "preloading_status": row["preloading_status"]}
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Callback function called when a notification is received from PostgreSQL.
def notify_callback(connection, pid, channel, payload):
    try:
        # Parse the JSON payload from PostgreSQL
        data = json.loads(payload)
        product_id = data.get("product_id")
        preloading_status = data.get("preloading_status")
        # Schedule the sending of notifications as an asyncio task.
    except Exception as e:
        print("Error parsing payload:", e)

# Background task that connects to PostgreSQL and listens for notifications.
async def listen_to_db():
    try:
        conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
        # Listen on the "preloading_status_change" channel
        await conn.add_listener('preloading_status_change', notify_callback)
        # Keep the task running indefinitely.
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print("Error in listen_to_db:", e)

# Startup event: launch the background listener.
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(listen_to_db())

# @app.post("/email-proposal")
def get_email_proposal(request: EmailProposalRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key not configured")
    
    print("Fetching email for ", request.decision_maker)
    company_name = request.company_name
    ref_dm = request.decision_maker

    print("Finding the type of Decision maker")

    #find the datatype of decision_maker['decision_maker']
    if type(ref_dm) == str:
        print("True")
        dm_pos = request.decision_maker_position
        # domain = decision_maker['domain']

        response = get_company_and_person_info(request.decision_maker, ref_dm, dm_pos, request.product_description)

        print("Information fetched for ", ref_dm," from the company ", company_name,":", response)

        req_info = format_response(response)

        print("Information fetched for ", ref_dm)

        query = "Personalised Email proposal based on Target Company and Decision Maker"

        situation = "email"
        
        proposal_system = EmailProposalSystem(pdf_paths)
        
        # Mock request data
        mock_request = {
            "product_description": request.product_description,
            "sender_name": request.sender_name,
            "sender_position": request.sender_position,
            "sender_company": request.sender_company
        }
        
        
        # Generate email
        response = proposal_system.generate_email(
            query=query,
            situation=situation,
            company_name=company_name,
            decision_maker=ref_dm,
            decision_maker_position=dm_pos,
            req_info=json.dumps(req_info),
            **mock_request
        )

        response, decision_maker_context = response
        
        # print the generated email
        print(format_response(response))

        response = format_response(response)

        print("Email template generated for", ref_dm)

        response['personality_type'] = decision_maker_context

        return response

def format_response(response):
    # Get the raw content from the API response.
    json_string = response["choices"][0]["message"]["content"].strip()
    
    # First, try to extract JSON content between ```json and ```
    match = re.search(r'```json\s*(.*?)\s*```', json_string, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
    else:
        # If no code block markers, use the full response
        candidate = json_string

    # Remove single-line comments (// ...) from the candidate.
    # This uses MULTILINE mode so that any line that starts with // (or has them after some whitespace) is removed.
    candidate = re.sub(r'(?m)^\s*//.*$', '', candidate)
    # Also remove inline comments that start with // and continue until the end of the line.
    candidate = re.sub(r'(?m)([^:])//.*$', r'\1', candidate)

    # Optionally, remove trailing commas (if any) before closing brackets/braces.
    candidate = re.sub(r',\s*([}\]])', r'\1', candidate)

    try:
        # First attempt: try to parse the candidate as JSON.
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        # If the error message indicates control characters, try escaping them
        if "Invalid control character" in str(e):
            fixed_candidate = re.sub(r'(?<!\\)(\n)', r'\\n', candidate)
            try:
                return json.loads(fixed_candidate)
            except (json.JSONDecodeError, ValueError) as e2:
                print(f"Error parsing JSON after fixing control characters: {e2}")
        else:
            # You can add further fixes here if needed.
            pass

        print("Problematic response:", candidate)
        raise HTTPException(status_code=500, detail="Invalid response format from API")


@app.post("/send_email")
async def send_email(email: EmailData, user_id: str, user_email: str, encrypted_password: str, db: Session = Depends(get_db)):
    recipient_name = email.recipient_name
    company_name = email.company_name
    dm_position = email.dm_position
    recipient = email.recipient
    subject = email.subject
    body = email.body.replace('\n', '<br>')  # Replace \n with <br> for line breaks
    # email_type = email.email_type/
    sender_name = email.sender_name
    sender_company = email.sender_company
    sender_position = email.sender_position
    sender_email = user_email
    product_id = email.product_id
    company_id = email.company_id

    encrypted_pass = urllib.parse.unquote(encrypted_password)

    # Debugging: Print the encrypted password received
    print(f"Received Encrypted Password: {encrypted_pass}")

    # Decrypt the password
    try:
        decrypted_password = decrypt_password(encrypted_pass)
        print(f"Decrypted Password: {decrypted_password}")  # Debugging: Print the decrypted password
    except Exception as e:
        print(f"Decryption Error: {e}")  # Debugging: Print the decryption error
        raise HTTPException(status_code=400, detail="Invalid encrypted password")

    # Generate unique tracking ID
    tracking_id = 'tracking_' + generate_unique_uuid(db, EmailStatus, EmailStatus.id)

    # Save tracking info in the database
    try:
        db = SessionLocal()
        new_email = EmailStatus(
            id=tracking_id,
            user_id=user_id,  # Set the user_id
            dm_name=recipient_name,
            company_name=company_name,
            company_id=company_id,
            dm_position=dm_position,
            email_id=recipient,
            email_subject=subject,
            email_body=body,
            # email_type=email_type,
            product_id=product_id,
            sender_name=sender_name,
            sender_company=sender_company,
            sender_position=sender_position,
            sender_email=sender_email,
            status="Not Responded",
        )
        db.add(new_email)
        db.commit()
    except Exception as e:
        print(f"Database Error: {e}")  # Debugging: Print the database error
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        db.close()

    # Identify SMTP server
    smtp_server, smtp_port = identify_smtp_server(user_email)
    print(f"Identified SMTP Server: {smtp_server}, Port: {smtp_port}")  # Debugging: Print the identified SMTP server

    # Email content with tracking pixel
    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Email Notification</title>
</head>
<body style="background-color: rgb(89,227,167); font-family: Arial, sans-serif; margin: 0; padding: 20px; text-align: center;">

    <!-- Outer Table (Centers Content) -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center">

                <!-- Email Container -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); padding: 20px; text-align: center;">
                    
                    <!-- Email Body Content -->
                    <tr>
                        <td style="font-size: 16px; color: #333; line-height: 1.6; padding-bottom: 20px; text-align: left;">
                            {body}
                        </td>
                    </tr>

                    <!-- Tracking Pixel (Hidden) -->
                    <tr>
                        <td>
                            <img src="https://sales-ai-agent-backend-e3h0gzfxduabejdz.centralindia-01.azurewebsites.net/track/{tracking_id}" width="3" height="3" alt="tracking pixel" style="display: none;">
                        </td>
                    </tr>

                    <!-- Action Buttons -->
                    <tr>
                        <td style="padding-top: 20px;">
                            <a href="https://sales-ai-agent-backend-e3h0gzfxduabejdz.centralindia-01.azurewebsites.net/track-response/{tracking_id}/interested"
                                style="display: inline-block; background: rgb(89,227,167); color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 5px; font-size: 16px; margin-right: 10px;">
                                Interested
                            </a>
                            <a href="https://sales-ai-agent-backend-e3h0gzfxduabejdz.centralindia-01.azurewebsites.net/track-response/{tracking_id}/not-interested"
                                style="display: inline-block; background: #e74c3c; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 5px; font-size: 16px;">
                                Not Interested
                            </a>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
"""

    # Send email
    msg = MIMEMultipart()
    msg['From'] = user_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user_email, decrypted_password)
            server.sendmail(user_email, recipient, msg.as_string())
        
        # Send notification email to the sender
        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Email Confirmation - Lead Stream</title>
</head>
<body style="background-color: rgb(89,227,167); font-family: Arial, sans-serif; padding: 20px; margin: 0; text-align: center;">

    <!-- Outer Table to Center Content -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center">

                <!-- Logo -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td align="left" style="padding-bottom: 20px;">
                            <img src="https://twingenfuelfiles.blob.core.windows.net/lead-stream/heuro.png" alt="Heuro Logo" width="75">
                        </td>
                    </tr>
                </table>

                <!-- Email Content -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0" 
                    style="background: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); padding: 20px; text-align: left;">
                    
                    <tr>
                        <td style="font-size: 16px; color: #333; padding: 10px 20px; line-height: 1.6;">
                            <p>Hi {sender_name},</p>
                            <p>Your email to <strong>{recipient}</strong> has been sent successfully.</p>
                            <p><strong>Subject:</strong> {subject}</p>
                            <p><strong>Body:</strong></p>
                            <p>{body}</p>
                            <p>Thank you for using Lead Stream!</p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
"""

        send_notification_email(sender_email, "Email Sent Notification", html_body)

        return {"message": "Email sent!"}
    except Exception as e:
        print(f"Email Sending Error: {e}")  # Debugging: Print the email sending error
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")

def send_notification_email(to_email: str, subject: str, body: str, smtp_server: str = SMTP_SERVER):
    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL_USERNAME')
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(os.getenv('EMAIL_USERNAME'), os.getenv('EMAIL_PASSWORD'))
            server.sendmail(os.getenv('EMAIL_USERNAME'), to_email, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")

@app.get("/track/{tracking_id}")
async def track(tracking_id: str):
    # Update the email status to "Not Responded" in the database
    db = SessionLocal()
    email_entry = db.query(EmailStatus).filter(EmailStatus.id == tracking_id).first()
    followup_entry = db.query(FollowupStatus).filter(FollowupStatus.followup_id == tracking_id).first()

    if email_entry and (email_entry.status != "Interested" or email_entry.status != "Not Interested"):
        email_entry.status = "Opened but Not Responded"
        email_entry.open_count += 1
        db.commit()
    
    if followup_entry and (followup_entry.followup_status != "Interested" or followup_entry.followup_status != "Not Interested"):
        followup_entry.followup_status = "Opened but Not Responded"
        followup_entry.open_count += 1
        db.commit()

    if not(email_entry or followup_entry):
        raise HTTPException(status_code=404, detail="Tracking ID not found")

        
    # Send notification email to the sender
    html_body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <title>Lead Stream Notification</title>
        </head>
        <body style="background-color: rgb(89,227,167); font-family: Arial, sans-serif; padding: 20px; margin: 0; text-align: center;">

        <!-- Outer Table to Center Content -->
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
            <tr>
                <td align="center">

                    <!-- Logo -->
                    <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0">
                        <tr>
                            <td align="left" style="padding-bottom: 20px;">
                                <img src="https://twingenfuelfiles.blob.core.windows.net/lead-stream/heuro.png" alt="Heuro Logo" width="75">
                            </td>
                        </tr>
                    </table>

                    <!-- Email Content -->
                    <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0" 
                        style="background: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); padding: 20px; text-align: left;">
                        
                        <tr>
                            <td style="font-size: 16px; color: #333; padding: 10px 20px; line-height: 1.6;">
                                <p>Hi {email_entry.sender_name},</p>
                                <p><strong>Lead Stream has a new notification for you!</strong></p>
                                <p>{email_entry.dm_name} <b>has opened your {'followup' if followup_entry else 'email'}</b> but has not yet responded.</p>
                                <p>Here is the email that was sent to <strong>{email_entry.email_id}</strong>:</p>
                                <p><strong>Subject:</strong> {email_entry.email_subject}</p>
                                <p><strong>Body:</strong> {email_entry.email_body}</p>
                                <p>Please check the email and take the necessary action.</p>
                                <p>Thank you for using Lead Stream!</p>
                            </td>
                        </tr>

                    </table>

                </td>
            </tr>
        </table>

        </body>
        </html>
        """

    send_notification_email(email_entry.sender_email, "New Notification from Lead Stream!", html_body)

    print(f"Email with Tracking ID: {tracking_id} has been opened.")
    
    db.close()

@app.get("/track-response/{tracking_id}/{response}")
async def track_response(tracking_id: str, response: str):
    # Update the email status to "Opened" in the database
    db = SessionLocal()
    email_entry = db.query(EmailStatus).filter(EmailStatus.id == tracking_id).first()
    followup_entry = db.query(FollowupStatus).filter(FollowupStatus.followup_id == tracking_id).first()

    if email_entry and response == "interested":
        email_entry.status = "Interested"
        db.commit()
        print(f"Email with Tracking ID: {tracking_id} has been opened and interested")
        #return a html page with a thank you message
        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lead Stream Notification</title>
</head>
<body style="background-color: rgb(89,227,167); font-family: Arial, sans-serif; padding: 20px; margin: 0; text-align: center;">

    <!-- Outer Table to Center Content -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center">

                <!-- Logo -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td align="left" style="padding-bottom: 20px;">
                            <img src="https://twingenfuelfiles.blob.core.windows.net/lead-stream/heuro.png" alt="Heuro Logo" width="75">
                        </td>
                    </tr>
                </table>

                <!-- Email Content -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0" 
                    style="background: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); padding: 20px; text-align: left;">
                    
                    <tr>
                        <td style="font-size: 16px; color: #333; padding: 10px 20px; line-height: 1.6;">
                            <p>Hi {email_entry.sender_name},</p>
                            <p><strong>Lead Stream has a new notification for you!</strong></p>
                            <p>{email_entry.dm_name} has opened and <b>is showing interest</b> to your product <b>via mail</b></p>
                            <p>Here is the email that was sent to <strong>{email_entry.email_id}</strong>:</p>
                            <p><strong>Subject:</strong> {email_entry.email_subject}</p>
                            <p><strong>Body:</strong> {email_entry.email_body}</p>
                            <p>Please check the email and take the necessary action.</p>
                            <p>Thank you for using Lead Stream!</p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
"""

        send_notification_email(email_entry.sender_email, "Hurray! You have a new lead", html_body)

        print(f"Email with Tracking ID: {tracking_id} has been opened and interested.")
        db.close()

        return FileResponse("interested.html")
    
    if email_entry and response == "not-interested":
        email_entry.status = "Not Interested"
        db.commit()
        print(f"Email with Tracking ID: {tracking_id} has been opened but not interested")
        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lead Stream Notification</title>
</head>
<body style="background-color: rgb(89,227,167); font-family: Arial, sans-serif; padding: 20px; margin: 0; text-align: center;">

    <!-- Outer Table to Center Content -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center">

                <!-- Logo -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td align="left" style="padding-bottom: 20px;">
                            <img src="https://twingenfuelfiles.blob.core.windows.net/lead-stream/heuro.png" alt="Heuro Logo" width="75">
                        </td>
                    </tr>
                </table>

                <!-- Email Content -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0" 
                    style="background: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); padding: 20px; text-align: left;">
                    
                    <tr>
                        <td style="font-size: 16px; color: #333; padding: 10px 20px; line-height: 1.6;">
                            <p>Hi {email_entry.sender_name},</p>
                            <p><strong>Lead Stream has a new notification for you!</strong></p>
                            <p>Unfortunately, {email_entry.dm_name} has opened and <b>is not interested</b> to your product at this time <b>via mail</b></p>
                            <p>Here is the email that was sent to <strong>{email_entry.email_id}</strong>:</p>
                            <p><strong>Subject:</strong> {email_entry.email_subject}</p>
                            <p><strong>Body:</strong> {email_entry.email_body}</p>
                            <p>Thank you for using Lead Stream!</p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
"""

        send_notification_email(email_entry.sender_email, "New Notification from Lead Stream!", html_body)

        print(f"Email with Tracking ID: {tracking_id} has been opened and interested.")
        db.close()

        return FileResponse("not-interested.html")
    
    if followup_entry and response == "interested":
        followup_entry.followup_status = "Interested"
        db.commit()
        print(f"Followup with Tracking ID: {tracking_id} has been opened and interested")
        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lead Stream Notification</title>
</head>
<body style="background-color: rgb(89,227,167); font-family: Arial, sans-serif; padding: 20px; margin: 0; text-align: center;">

    <!-- Outer Table to Center Content -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center">

                <!-- Logo -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td align="left" style="padding-bottom: 20px;">
                            <img src="https://twingenfuelfiles.blob.core.windows.net/lead-stream/heuro.png" alt="Heuro Logo" width="75">
                        </td>
                    </tr>
                </table>

                <!-- Email Content -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0" 
                    style="background: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); padding: 20px; text-align: left;">
                    
                    <tr>
                        <td style="font-size: 16px; color: #333; padding: 10px 20px; line-height: 1.6;">
                            <p>Hi {email_entry.sender_name},</p>
                            <p><strong>Lead Stream has a new notification for you!</strong></p>
                            <p>{email_entry.dm_name} has opened and <b>is showing interest</b> to your product <b>via followup</b></p>
                            <p>Here is the email that was sent to <strong>{email_entry.email_id}</strong>:</p>
                            <p><strong>Subject:</strong> {email_entry.email_subject}</p>
                            <p><strong>Body:</strong> {email_entry.email_body}</p>
                            <p>Please check the email and take the necessary action.</p>
                            <p>Thank you for using Lead Stream!</p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
"""

        send_notification_email(email_entry.sender_email, "Hurray! You have a new Lead", html_body)

        print(f"Email with Tracking ID: {tracking_id} has been opened and interested.")
        db.close()
        return FileResponse("interested.html")
    
    if followup_entry and response == 'not-interested':
        followup_entry.followup_status = "Not Interested"
        db.commit()
        print(f"Followup with Tracking ID: {tracking_id} has been opened and not interested")
        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lead Stream Notification</title>
</head>
<body style="background-color: rgb(89,227,167); font-family: Arial, sans-serif; padding: 20px; margin: 0; text-align: center;">

    <!-- Outer Table to Center Content -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center">

                <!-- Logo -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td align="left" style="padding-bottom: 20px;">
                            <img src="https://twingenfuelfiles.blob.core.windows.net/lead-stream/heuro.png" alt="Heuro Logo" width="75">
                        </td>
                    </tr>
                </table>

                <!-- Email Content -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0" 
                    style="background: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); padding: 20px; text-align: left;">
                    
                    <tr>
                        <td style="font-size: 16px; color: #333; padding: 10px 20px; line-height: 1.6;">
                            <p>Hi {email_entry.sender_name},</p>
                            <p><strong>Lead Stream has a new notification for you!</strong></p>
                            <p>Unfortunately, {email_entry.dm_name} has opened and <b>is not interested</b> to your product at this time <b>via followup</b></p>
                            <p>Here is the email that was sent to <strong>{email_entry.email_id}</strong>:</p>
                            <p><strong>Subject:</strong> {email_entry.email_subject}</p>
                            <p><strong>Body:</strong> {email_entry.email_body}</p>
                            <p>Please check the email and take the necessary action.</p>
                            <p>Thank you for using Lead Stream!</p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
"""

        send_notification_email(email_entry.sender_email, "New Notification from Lead Stream!", html_body)

        print(f"Followup with Tracking ID: {tracking_id} has been opened and interested.")
        db.close()
        return FileResponse("not-interested.html")

    else:
        db.close()

@app.post("/email-reminder")
def get_email_reminder(tracking_id: str, user_id: str, request: ReminderRequest, db: Session = Depends(get_db)):
    email = db.query(EmailStatus).filter(EmailStatus.id == tracking_id, EmailStatus.user_id == user_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found or you do not have permission to send a reminder for this email")
    
    company_name = email.company_name
    decision_maker = email.dm_name
    body = email.email_body
    product_description = db.query(ProductDetails).filter(ProductDetails.product_id == email.product_id).first().product_description
    dm_pos = email.dm_position
    response = get_company_and_person_info(decision_maker, decision_maker, dm_pos, product_description)

    print("Information fetched for ", decision_maker," from the company ", company_name,":", response)

    req_info = format_response(response)

    query = f"Personalised {request.type[0].upper() + request.type[1:]} proposal based on Target Company and Decision Maker"

    situation = request.type

    proposal_system = EmailProposalSystem(pdf_paths)
        
    # Mock request data
    mock_request = {
        "product_description": request.product_description,
        "sender_name": request.sender_name,
        "sender_position": request.sender_position,
        "sender_company": request.sender_company
    }
    
    
    # Generate email
    response = proposal_system.generate_email(
        query=query,
        situation=situation,
        company_name=company_name,
        decision_maker=decision_maker,
        decision_maker_position=dm_pos,
        req_info=json.dumps(req_info),
        **mock_request
    )

    formatted_response = format_response(response)

    subject = formatted_response.get("subject")
    body = formatted_response.get("body")

    # Send notification email to the sender
    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lead Stream - Reminder Sent</title>
</head>
<body style="background-color: rgb(89,227,167); font-family: Arial, sans-serif; padding: 20px; margin: 0; text-align: center;">

    <!-- Outer Table to Center Content -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center">

                <!-- Logo -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td align="left" style="padding-bottom: 20px;">
                            <img src="https://twingenfuelfiles.blob.core.windows.net/lead-stream/heuro.png" alt="Heuro Logo" width="75">
                        </td>
                    </tr>
                </table>

                <!-- Email Content -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0" 
                    style="background: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); padding: 20px; text-align: left;">
                    
                    <tr>
                        <td style="font-size: 16px; color: #333; padding: 10px 20px; line-height: 1.6;">
                            <p>Hi {email.sender_name},</p>
                            <p>Reminder has been sent to <strong>{email.email_id}</strong>.</p>
                            <p><strong>Subject:</strong> {subject}</p>
                            <p><strong>Body:</strong> {body}</p>
                            <p>Thank you for using Lead Stream!</p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
"""

    send_notification_email(email.sender_email, "Reminder Email Sent from Lead Stream!", html_body)

    return {"subject": subject, "body": body}

@app.post('/update-followup')
def update_followup(followup_id: str, followup_field: str, field_value: str):
    db = SessionLocal()
    followup = db.query(FollowupStatus).filter(FollowupStatus.followup_id == followup_id).first()
    if not followup:
        raise HTTPException(status_code=404, detail="Followup not found")

    setattr(followup, followup_field, field_value)
    db.commit()
    db.close()
    return {"message": "Followup updated successfully"}


@app.post("/send_followup_email")
async def send_followup_email(user_id: str, user_email: str, encrypted_password: str, followup: FollowupData, db: Session = Depends(get_db)):
    db = SessionLocal()
    try:
        followup_data = db.query(FollowupStatus).filter(FollowupStatus.email_uid == followup.email_uid, FollowupStatus.user_id == user_id).first()
        if not followup_data:
            # insert a followup mail
            new_followup = FollowupStatus(
                followup_id=followup_data.followup_id,
                user_id=user_id,  # Set the user_id
                email_uid=followup.email_uid,
                followup_date=datetime.utcnow(),
                followup_status="Not Responded",
                body=followup.body,
                subject=followup.subject,
                followup_sent_count=1,
                recipient_name=followup.recipient_name,
                company_name=followup.company_name,
                sender_name=followup.sender_name,
                sender_company=followup.sender_company,
                sender_position=followup.sender_position,
                sender_email=user_email,
                sender_threshold=2,
                recipient=followup.recipient,
                followup_type="Followup Mail"
            )
            db.add(new_followup)
            db.commit()
        
        else:
            # update the followup mail
            followup_data.followup_date = datetime.utcnow()
            followup_data.followup_status = "Not Responded"
            followup_data.body = followup.body
            followup_data.subject = followup.subject
            followup_data.followup_sent_count += 1
            db.commit()

        # Decrypt the password
        decrypted_password = decrypt_password(encrypted_password)

        # Identify SMTP server
        smtp_server = identify_smtp_server(user_email)

        # Send follow-up email
        msg = MIMEMultipart()
        msg['From'] = user_email
        msg['To'] = followup.recipient
        msg['Subject'] = followup.subject
        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Followup Notification</title>
</head>
<body style="background-color: rgb(89,227,167); font-family: Arial, sans-serif; margin: 0; padding: 20px; text-align: center;">

    <!-- Outer Table (Centers Content) -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center">

                <!-- Email Container -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); padding: 20px; text-align: center;">
                    
                    <!-- Email Body Content -->
                    <tr>
                        <td style="font-size: 16px; color: #333; line-height: 1.6; padding-bottom: 20px; text-align: left;">
                            {followup.body}
                        </td>
                    </tr>

                    <!-- Tracking Pixel (Hidden) -->
                    <tr>
                        <td>
                            <img src="https://sales-ai-agent-backend-e3h0gzfxduabejdz.centralindia-01.azurewebsites.net/track/{followup_data.followup_id}" width="3" height="3" alt="tracking pixel" style="display: none;">
                        </td>
                    </tr>

                    <!-- Action Buttons -->
                    <tr>
                        <td style="padding-top: 20px;">
                            <a href="https://sales-ai-agent-backend-e3h0gzfxduabejdz.centralindia-01.azurewebsites.net/track-response/{followup_data.followup_id}/interested"
                                style="display: inline-block; background: rgb(89,227,167); color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 5px; font-size: 16px; margin-right: 10px;">
                                Interested
                            </a>
                            <a href="https://sales-ai-agent-backend-e3h0gzfxduabejdz.centralindia-01.azurewebsites.net/track-response/{followup_data.followup_id}/not-interested"
                                style="display: inline-block; background: #e74c3c; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 5px; font-size: 16px;">
                                Not Interested
                            </a>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
"""
        msg.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP(smtp_server, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(user_email, decrypted_password)
                server.sendmail(user_email, followup.recipient, msg.as_string())

            # Send notification email to the sender
            html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Follow-Up Email Sent - Lead Stream</title>
</head>
<body style="background-color: rgb(89,227,167); font-family: Arial, sans-serif; padding: 20px; margin: 0; text-align: center;">

    <!-- Outer Table to Center Content -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center">

                <!-- Logo -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td align="left" style="padding-bottom: 20px;">
                            <img src="https://twingenfuelfiles.blob.core.windows.net/lead-stream/heuro.png" alt="Heuro Logo" width="75">
                        </td>
                    </tr>
                </table>

                <!-- Email Content -->
                <table role="presentation" width="600px" cellspacing="0" cellpadding="0" border="0" 
                    style="background: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); padding: 20px; text-align: left;">
                    
                    <tr>
                        <td style="font-size: 16px; color: #333; padding: 10px 20px; line-height: 1.6;">
                            <p>Hi {followup.sender_name},</p>
                            <p>Your follow-up email to <strong>{followup.recipient}</strong> has been sent successfully.</p>
                            <p><strong>Subject:</strong> {followup.subject}</p>
                            <p><strong>Body:</strong> {followup.body}</p>
                            <p>Thank you for using Lead Stream!</p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
"""

            send_notification_email(user_email, "Follow-up Email Sent Notification", html_body)

            return {"message": "Follow-up email sent!"}
        except Exception as e:
            db.commit()
            return {"message": "Follow-up email sent!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error sending follow-up email: {e}")
    finally:
        db.close()

@app.get("/status")
def status(user_id: str, db: Session = Depends(get_db)):
    # Fetch tracked emails
    tracked_emails = db.query(EmailStatus).filter(EmailStatus.user_id == user_id).all()
    return {
        "tracked_emails": [
            {
                "id": email.id,
                "email_id": email.email_id,
                "email_subject": email.email_subject,
                "email_body": email.email_body,
                "email_datesent": email.date_sent,
                "status": email.status,
            }
            for email in tracked_emails
        ]
    } 

@app.get("/fetch-mail-status")
def fetch_mail_status(user_id: str, db: Session = Depends(get_db)):
    email_statuses = db.query(EmailStatus).filter(EmailStatus.user_id == user_id).all()
    product_details = {product.product_id: product.product_name for product in db.query(ProductDetails).all()}
    followup = {followup.email_uid: {"status": followup.followup_status,
                                     "followup_id": followup.followup_id,
                                     "date_sent": followup.followup_date, 
                                     "followup_sent_count": followup.followup_sent_count, 
                                     "open_count": followup.open_count,
                                     "sender_name": followup.sender_name,
                                     "sender_company": followup.sender_company,
                                     "sender_position": followup.sender_position,
                                     "sender_email": followup.sender_email,
                                     "followup_threshold": followup.followup_threshold
                                     } for followup in db.query(FollowupStatus).filter(FollowupStatus.user_id == user_id).all()}
    db.close()
    
    result = []
    for email in email_statuses:
        followup_data = followup.get(email.id, "No Followup")
        result.append({
            "id": email.id,
            "followup_id": followup_data['followup_id'] if followup_data != "No Followup" else None,
            "dm_name": email.dm_name,
            "company_name": email.company_name,
            "company_id": email.company_id,
            "dm_position": email.dm_position,
            "email_id": email.email_id,
            "followup_open_count": followup_data['open_count'] if followup_data != "No Followup" else 0,
            "email_open_count": email.open_count,
            "email_subject": email.email_subject,
            "sender_name": followup_data['sender_name'] if followup_data != "No Followup" else email.sender_name,
            "sender_company": followup_data['sender_company'] if followup_data != "No Followup" else email.sender_company,
            "sender_position": followup_data['sender_position'] if followup_data != "No Followup" else email.sender_position,
            "sender_email": followup_data['sender_email'] if followup_data != "No Followup" else email.sender_email,
            "followup_threshold": followup_data['followup_threshold'] if followup_data != "No Followup" else 0,
            "email_body": email.email_body,
            "followup_sent_count": followup_data['followup_sent_count'] if followup_data != "No Followup" else 0,
            "status": followup_data['status'] if followup_data != "No Followup" else email.status,
            "date_sent": followup_data['date_sent'] if followup_data != "No Followup" else email.date_sent,
            "product_id": email.product_id,
            "product_name": product_details.get(email.product_id, "Unknown")
        })
    
    return result

@app.get("/email-status-check")
def check_email_status(tracking_id: str, user_id: str, db: Session = Depends(get_db)):
    current_time = datetime.utcnow()

    # Open the session
    db = SessionLocal()
    try:
        email = db.query(EmailStatus).filter(EmailStatus.id == tracking_id, EmailStatus.user_id == user_id).first()
        print("Email: ", email)
        followup = db.query(FollowupStatus).filter(FollowupStatus.email_uid == tracking_id).first()
        print("Followup: ", followup)

        if not email:
            return {"error": "Email with the provided tracking ID not found or you do not have permission to check the status of this email"}

        if followup:
            date_sent = followup.followup_date
            status = followup.followup_status
        else:
            date_sent = email.date_sent
            status = email.status

        time_difference = current_time - date_sent
        days_difference = time_difference.days

        if followup:
            if days_difference > followup.followup_threshold and status != "Not Interested":
                status = "Send Reminder"
                if followup:
                    followup.followup_status = "Send Reminder"
                    db.commit()
                else:
                    email.status = "Send Reminder"
                    db.commit()
                return {
                    "email_id": email.email_id,
                    "status": f"Need to send a reminder as the email was sent {days_difference} days ago",
                    "days_since_sent": days_difference
                }
        else:
            return {
                "email_id": email.email_id,
                "status": status,
                "days_since_sent": days_difference
            }
    finally:
        # Ensure the session is closed after the operation
        db.close()

@app.delete("/delete-entity/{id}")
def delete_entity(id: str, user_id: str, db: Session = Depends(get_db)):
    email_entry = db.query(EmailStatus).filter(EmailStatus.id == id, EmailStatus.user_id == user_id).first()
    if not email_entry:
        raise HTTPException(status_code=404, detail="Entity not found or you do not have permission to delete this entity")
    db.delete(email_entry)
    db.commit()
    return {"message": "Entity deleted successfully"}

@app.post("/add_product")
def add_product(user_id: str, request: ProductRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the user has reached the product limit
    if user.product_limit <= 0:
        raise HTTPException(status_code=400, detail="Product limit reached. Please upgrade your plan to add more products")
    
    product_name = request.product_name

    # Check if the product name already exists
    product = db.query(ProductDetails).filter(ProductDetails.product_name == product_name, ProductDetails.user_id == user_id).first()
    if product:
        raise HTTPException(status_code=400, detail="Product with the same name already exists")

    try:
        new_product = ProductDetails(
            user_id=user_id,  # Set the user_id
            product_id='product_'+ generate_unique_uuid(db, ProductDetails, ProductDetails.product_id),
            product_name=request.product_name,
            existing_customers=request.existing_customers,
            product_description=request.product_description,
            target_min_emp_count=request.target_min_emp_count,
            target_max_emp_count=request.target_max_emp_count,
            target_industries=request.target_industries,
            target_geo_loc=request.target_geo_loc,
            target_business_model=request.target_business_model,
            addressing_pain_points=request.addressing_pain_points
        )
        db.add(new_product)
        user.product_limit -= 1
        db.commit()
        return {"message": "Product added successfully", "product_id": new_product.product_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding product: {e}")
    finally:
        db.close()

@app.get("/get_products")
def get_products(user_id: str, db: Session = Depends(get_db)):
    try:
        products = db.query(ProductDetails).filter(ProductDetails.user_id == user_id).all()
        return [
            {
                "product_id": product.product_id,
                "product_name": product.product_name,
                "existing_customers": product.existing_customers,
                "product_description": product.product_description,
                "target_min_emp_count": product.target_min_emp_count,
                "target_max_emp_count": product.target_max_emp_count,
                "target_industries": product.target_industries,
                "target_geo_loc": product.target_geo_loc,
                "target_business_model": product.target_business_model,
                "addressing_pain_points": product.addressing_pain_points,
            }
            for product in products
        ]
    finally:
        db.close()

@app.get("/get_single_product/{product_id}")
def get_existing_customers(product_id: str, user_id: str, db: Session = Depends(get_db)):
    product = db.query(ProductDetails).filter(ProductDetails.product_id == product_id, ProductDetails.user_id == user_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or you do not have permission to view this product")

    # return the updated product details
    return {
        "product_id": product.product_id,
        "product_name": product.product_name,
        "preloading_status": product.preloading_status,
        "existing_customers": product.existing_customers,
        "product_description": product.product_description,
        "target_min_emp_count": product.target_min_emp_count,
        "target_max_emp_count": product.target_max_emp_count,
        "target_industries": product.target_industries,
        "target_geo_loc": product.target_geo_loc,
        "target_business_model": product.target_business_model,
        "addressing_pain_points": product.addressing_pain_points
    }

@app.put("/update_product/{product_id}")
def update_product(product_id: str, user_id: str, request: ProductRequest, db: Session = Depends(get_db)):
    product = db.query(ProductDetails).filter(ProductDetails.product_id == product_id, ProductDetails.user_id == user_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or you do not have permission to update this product")

    # Update the product details
    product.product_name = request.product_name
    product.existing_customers = request.existing_customers
    product.product_description = request.product_description
    product.target_min_emp_count = request.target_min_emp_count
    product.target_max_emp_count = request.target_max_emp_count
    product.target_industries = request.target_industries
    product.target_geo_loc = request.target_geo_loc
    product.target_business_model = request.target_business_model
    product.addressing_pain_points = request.addressing_pain_points

    db.commit()

    # Return the updated product details
    return {
        "product_id": product.product_id,
        "product_name": product.product_name,
        "existing_customers": product.existing_customers,
        "product_description": product.product_description,
        "target_min_emp_count": product.target_min_emp_count,
        "target_max_emp_count": product.target_max_emp_count,
        "target_industries": product.target_industries,
        "target_geo_loc": product.target_geo_loc,
        "target_business_model": product.target_business_model,
        "addressing_pain_points": product.addressing_pain_points
    }

@app.post("/add_company/")
def add_company(user_id: str, request: CompanyEditRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # user.company_name is a list present as string in the database so we need to convert it to a list
    
    company_names = json.loads(user.company_name)
    positions = request.position
    
    if request.company_name not in company_names:
        company_names.append(request.company_name)

    user.company_name = json.dumps(company_names)
    user.position = json.dumps(positions)

    
    db.commit()
    return {"message": "Company and positions added successfully"}

@app.put("/edit_company/")
def edit_company(user_id: str, request: CompanyEditRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # replace the company name with the new company name in the company_name list and position dictionary
    company_names = json.loads(user.company_name)
    positions = user.position

    if request.company_name not in company_names:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company_names[company_names.index(request.company_name)] = request.new_company_name

    user.company_name = json.dumps(company_names)
    user.position = json.dumps(positions)

    db.commit()
    return {"message": "Company updated successfully"}

@app.delete("/remove_company/")
def remove_company(user_id: str, company_name: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    company_names = json.loads(user.company_name)
    positions = json.loads(user.position)
    
    if company_name not in company_names:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company_names.remove(company_name)
    positions = {k: v for k, v in positions.items() if k != company_name}
        
    
    user.company_name = json.dumps(company_names)
    user.position = json.dumps(positions)
    
    db.commit()
    return {"message": "Company removed successfully"}


@app.put("/edit_positions/")
def edit_positions(user_id: str, request: PositionEditRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    company_name = request.company_name
    position = request.position

    positions = json.loads(user.position)

    if company_name not in positions:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Update the positions for the company
    positions[company_name] = position

    if positions[company_name] == []:
        # remove the company from the company_name list
        company_names = json.loads(user.company_name)
        company_names.remove(company_name)
        user.company_name = json.dumps(company_names)
        # remove the company from the positions dictionary
        positions.pop(company_name, None)
   
    user.position = json.dumps(positions)

    db.commit()
    return {"message": "Position updated successfully"}

# @app.post("/add_generated_companies/")
def add_generated_companies(request: GeneratedCompanyRequest, user_id: str, db: Session = Depends(get_db)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # product = db.query(ProductDetails).filter(ProductDetails.product_id == request.product_id, ProductDetails.user_id == user_id).first()
    # if not product:
    #     raise HTTPException(status_code=404, detail="Product not found or you do not have permission to add companies for this product")

    # update the company_limit in users table
    if user.company_limit < len(request.companies):
        raise HTTPException(status_code=400, detail="Company limit exceeded")
    else:
        user.company_limit = user.company_limit - len(request.companies)
    
    try:
        for company in request.companies:
            new_company = GeneratedCompany(
                id='generatedCompany_' + generate_unique_uuid(db, GeneratedCompany, GeneratedCompany.id),  # Ensure unique ID
                user_id=user_id,
                product_id=request.product_id,
                company_name=company["name"],
                industry=company.get("industry"),
                subject=company.get("subject"),  # Allow null
                body=company.get("body"),  # Allow null
                personality_type=company.get("personality_type"),  # Allow null
                domain=company.get("domain"),
                status=company.get("status"),
                decision_maker_name=company.get("decision_maker_name"),  # Allow null
                decision_maker_email=company.get("decision_maker_email"),  # Allow null
                decision_maker_position=company.get("decision_maker_position"),  # Allow null
                linkedin_url = company.get("linkedin_url"),  # New field
            )
            db.add(new_company)
        db.commit()
        return db.query(GeneratedCompany).filter(GeneratedCompany.user_id == user_id, GeneratedCompany.product_id == request.product_id).all()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding generated companies: {e}")
    finally:
        db.close()

@app.get("/get_generated_companies/")
def get_generated_companies(user_id: str, product_id: str, db: Session = Depends(get_db)):
    try:
        companies = db.query(GeneratedCompany).filter(GeneratedCompany.user_id == user_id, GeneratedCompany.product_id == product_id).all()
        return [
            {
                "id": company.id,
                "name": company.company_name,
                "industry": company.industry,
                "domain": company.domain,
                "status": company.status,
                "personality_type": company.personality_type,
                "linkedin_url": company.linkedin_url,  # New field
                "decision_maker": company.decision_maker_name,  # New field
                "subject": company.subject,  # New field
                "body": company.body,  # New field
                "decision_maker_mail": company.decision_maker_email,  # New field
                "decision_maker_position": company.decision_maker_position,  # New field
                "failed_company": company.failed_company
            }
            for company in companies
        ]
    finally:
        db.close()

@app.put("/update_generated_company_status/")
def update_generated_company_status(request: GeneratedCompanyUpdateRequest, user_id: str, db: Session = Depends(get_db)):
    company = db.query(GeneratedCompany).filter(GeneratedCompany.id == request.company_id, GeneratedCompany.user_id == user_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found or you do not have permission to update this company")
    
    company.status = request.status
    if request.decision_maker_name:
        company.decision_maker_name = request.decision_maker_name  # New field
    if request.personality_type:
        company.personality_type = request.personality_type  # New field
    if request.linkedin_url:
        company.linkedin_url = request.linkedin_url  # New field
    if request.decision_maker_email:
        company.decision_maker_email = request.decision_maker_email  # New field
    if request.decision_maker_position:
        company.decision_maker_position = request.decision_maker_position  # New field
    if request.subject:
        company.subject = request.subject  # New field
    if request.body:
        company.body = request.body  # New field
    if request.domain_name:
        company.domain = request.domain_name
    if request.failed_company == True:
        if company.failed_company == False:
            user = db.query(User).filter(User.id == user_id).first()
            user.company_limit = user.company_limit + 1
            company.failed_company = True
    if request.failed_company == False:
        if company.failed_company == True:
            user = db.query(User).filter(User.id == user_id).first()
            user.company_limit = user.company_limit - 1
            company.failed_company = False

    db.commit()
    return {"message": "Company status updated successfully"}

@app.post("/subscribe/{user_id}")
def subscribe_user(request: SubscriptionRequest, user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create Razorpay order
    razorpay_order = razorpay_client.order.create({
        "amount": int(request.amount * 100),  # amount in paise
        "currency": "INR",
        "payment_capture": "1"
    })

    end_date = datetime.utcnow() + timedelta(days=request.duration_days)
    new_subscription = Subscription(
        user_id=user_id,
        plan_name=request.plan_name,
        end_date=end_date,
        status="Pending",
        id=razorpay_order["id"]
    )
    db.add(new_subscription)
    db.commit()
    return {
        "message": "Subscription initiated successfully",
        # "order_id": razorpay_order["order_id"],
        "subscription_id": razorpay_order["id"],
        "amount": razorpay_order["amount"],
        "currency": razorpay_order["currency"]
    }

@app.post("/payment-success")
def payment_success(payment: PaymentSuccess, db: Session = Depends(get_db)):
    # Verify the payment signature
    params_dict = {
        'razorpay_order_id': payment.order_id,
        'razorpay_payment_id': payment.payment_id,
        'razorpay_signature': payment.signature
    }
    try:
        razorpay_client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    # Fetch payment details from Razorpay
    payment_details = razorpay_client.payment.fetch(payment.payment_id)

    # Update the subscription status
    subscription = db.query(Subscription).filter(Subscription.id == payment.order_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.status = "Active"
    db.commit()
    return {"message": "Payment verified and subscription activated"}

@app.post("/payment-failure")
def payment_failure(payment: PaymentFailure, db: Session = Depends(get_db)):
    # Update the subscription status
    subscription = db.query(Subscription).filter(Subscription.id == payment.order_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.status = "Failed"
    db.commit()
    return {"message": "Payment failed and subscription updated"}


@app.put("/cancel_subscription/{subscription_id}")
def cancel_subscription(subscription_id: str, user_id: str, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id, Subscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found or you do not have permission to cancel this subscription")

    subscription.status = "Cancelled"
    db.commit()
    return {"message": "Subscription cancelled successfully"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
