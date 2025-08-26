# Sales AI Agent - Complete Frontend & Backend Solution

A modern, responsive sales AI agent platform with advanced lead generation, email verification, company analysis, and personalized email generation capabilities.

## 🚀 Features

### Backend (Python FastAPI)
- **Google Search Integration**: Find decision makers and companies using advanced search queries
- **Email Verification**: Validate email addresses with high accuracy using multiple verification services
- **Company Analysis**: AI-powered analysis of companies and decision makers using Perplexity API
- **Email Generation**: Create personalized outreach emails using PDF templates and AI
- **Email Sending**: Automated email delivery with SMTP configuration
- **PDF Template Processing**: Extract and use email templates from PDF documents

### Frontend (React + TypeScript + Tailwind CSS)
- **Dashboard**: Real-time analytics and system monitoring
- **Company Search**: Interactive search interface with predefined queries
- **Email Verification**: Bulk email validation with history tracking
- **Email Generation**: AI-powered personalized email creation
- **Responsive Design**: Mobile-first design with clean, professional UI
- **Error Handling**: Comprehensive error handling and loading states

## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Perplexity API**: AI-powered company and person analysis  
- **Google Search API**: Lead discovery and research
- **MailTester API**: Email verification service
- **PyPDF2**: PDF template processing
- **FAISS**: Vector similarity search for templates
- **Sentence Transformers**: Text embeddings for semantic search

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Hot Toast**: Beautiful notifications
- **Lucide Icons**: Consistent icon set

## 📋 Prerequisites

### Backend Requirements
- Python 3.8+
- Virtual environment (recommended)
- API Keys for:
  - Perplexity API
  - RapidAPI (for search)
  - MailTester API (for email verification)

### Frontend Requirements
- Node.js 16+
- npm or yarn

## 🚦 Getting Started

### Backend Setup

1. **Clone and setup Python environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment variables:**
Create a `.env` file in the root directory:
```env
# API Keys
PERPLEXITY_API_KEY=your_perplexity_api_key
RAPIDAPI_KEY=your_rapidapi_key
MAILTESTER_API_KEY=your_mailtester_api_key

# Email Configuration
EMAIL_USERNAME=your_email@domain.com
EMAIL_PASSWORD=your_email_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Database (optional)
DATABASE_URL=your_database_url

# Encryption (optional)
ENCRYPTION_KEY=your_encryption_key
ENCRYPTION_IV=your_encryption_iv
```

3. **Run the backend server:**
```bash
python app.py
```
The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies:**
```bash
npm install
```

2. **Start the development server:**
```bash
npm run dev
```
The frontend will be available at `http://localhost:5173`

## 📁 Project Structure

```
sales-ai-agent/
├── backend/
│   ├── app.py                 # Main FastAPI application
│   ├── email_verifier.py      # Email verification logic
│   ├── email_proposal.py      # AI email generation
│   ├── info_gather.py         # Company analysis
│   ├── google_api.py          # Search functionality
│   ├── dom.py                 # Domain identification & email sending
│   ├── config.py              # Configuration management
│   └── requirements.txt       # Python dependencies
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx      # Main dashboard
│   │   ├── CompanySearch.tsx  # Search interface
│   │   ├── EmailVerification.tsx # Email validation
│   │   ├── EmailGeneration.tsx   # Email creation
│   │   └── Navigation.tsx     # Navigation component
│   ├── services/
│   │   └── api.ts            # API service layer
│   ├── types/
│   │   └── index.ts          # TypeScript definitions
│   └── App.tsx               # Main React component
└── package.json              # Node.js dependencies
```

## 🔧 API Endpoints

### Search & Discovery
- `POST /search` - Search for companies and decision makers
- `POST /verify-email` - Verify email addresses
- `POST /analyze-company` - Get AI-powered company analysis

### Email Operations
- `POST /generate-email` - Generate personalized emails
- `POST /send-email` - Send emails via SMTP
- `GET /health` - Health check endpoint

## 🎯 Usage Examples

### 1. Company Search
```javascript
const results = await apiService.searchCompanies(
  'VP Sales at SaaS companies site:linkedin.com', 
  10
);
```

### 2. Email Verification
```javascript
const verification = await apiService.verifyEmail(
  'John', 
  'Doe', 
  'company.com'
);
```

### 3. Company Analysis
```javascript
const analysis = await apiService.getCompanyAnalysis(
  'Microsoft',
  'Satya Nadella', 
  'CEO',
  'AI-powered solutions'
);
```

### 4. Email Generation
```javascript
const email = await apiService.generateEmail(
  'Microsoft',
  'Satya Nadella',
  'CEO', 
  'initial-outreach',
  'AI automation platform',
  analysisData
);
```

## 🔐 Security Features

- **Environment Variables**: Secure API key management
- **Input Validation**: Comprehensive input sanitization
- **Error Handling**: Proper error responses without exposing sensitive data
- **CORS Configuration**: Secure cross-origin requests

## 📊 Dashboard Features

- **Real-time Stats**: Track searches, verifications, and email generation
- **System Health**: Monitor backend API status
- **Activity History**: View recent operations
- **Quick Actions**: Fast access to main features

## 🎨 UI/UX Features

- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Loading States**: Clear feedback during API operations
- **Error Handling**: User-friendly error messages
- **Copy to Clipboard**: Easy content copying
- **Toast Notifications**: Real-time operation feedback
- **Professional Theme**: Clean, modern interface suitable for business use

## 🚀 Deployment

### Backend Deployment
- Compatible with any Python hosting service (Heroku, DigitalOcean, AWS)
- Requires environment variable configuration
- Supports database integration for production use

### Frontend Deployment
- Build for production: `npm run build`
- Deploy to Netlify, Vercel, or any static hosting service
- Update API base URL for production environment

## 📈 Performance Optimizations

- **Lazy Loading**: Components loaded on demand
- **API Caching**: Intelligent request caching
- **Debounced Inputs**: Optimized user input handling
- **Vector Search**: Fast template matching using FAISS
- **Concurrent Processing**: Parallel email verification

## 🧪 Testing

Run the application in development mode to test all endpoints:

1. Start backend: `python app.py`
2. Start frontend: `npm run dev`
3. Use the web interface to test all features
4. Check browser developer tools for API responses
5. Verify email sending functionality with test emails

## 📝 License

This project is ready for commercial use and can be deployed as an MVP or production application.

## 🤝 Support

The codebase is fully documented and ready for:
- Demo presentations
- MVP validation
- Production deployment
- Feature extensions
- Team collaboration

---

**Built for modern sales teams who want to leverage AI for better lead generation and outreach automation.**