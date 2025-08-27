import express from 'express';
import cors from 'cors';

const app = express();
const PORT = 8000;

// Middleware
app.use(cors({
  origin: ["http://localhost:5173", "http://127.0.0.1:5173"],
  credentials: true
}));
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'Sales AI Agent API'
  });
});

// Search endpoint (matches FastAPI /search)
app.post('/search', (req, res) => {
  const { query, limit = 5 } = req.body;
  
  const mockResults = [
    {
      title: `Company Result 1 for '${query}'`,
      snippet: `This is a mock search result 1 for the query '${query}'. Replace with actual search implementation.`,
      link: "https://example.com/company-1"
    },
    {
      title: `Company Result 2 for '${query}'`,
      snippet: `This is a mock search result 2 for the query '${query}'. Replace with actual search implementation.`,
      link: "https://example.com/company-2"
    },
    {
      title: `Company Result 3 for '${query}'`,
      snippet: `This is a mock search result 3 for the query '${query}'. Replace with actual search implementation.`,
      link: "https://example.com/company-3"
    }
  ].slice(0, Math.min(limit, 5));

  res.json(mockResults);
});

// Email verification endpoint
app.post('/verify-email', (req, res) => {
  const { first_name, last_name, domain } = req.body;
  
  const email = `${first_name.toLowerCase()}.${last_name.toLowerCase()}@${domain}`;
  
  res.json({
    email: email,
    isValid: true,
    status: 'verified'
  });
});

// Company analysis endpoint
app.post('/analyze-company', (req, res) => {
  const { company_name, person_name, position, product_description } = req.body;
  
  res.json({
    company_analysis: {
      recent_news: `${company_name} has been expanding their operations and focusing on digital transformation initiatives.`,
      financial_health: "Strong financial position with steady growth",
      verified_challenges: ["Scaling operations", "Digital transformation", "Market competition"],
      strategic_priorities: ["Innovation", "Customer experience", "Operational efficiency"]
    },
    decision_maker_profile: {
      communication_style: "Professional and data-driven",
      personality_indicators: "Results-oriented, analytical, values efficiency",
      personality_type: "Executive/Strategic",
      key_achievements: `Leading ${company_name}'s growth initiatives`,
      recent_activities: "Focused on strategic partnerships and technology adoption"
    },
    synergy_points: {
      product_fit: `${product_description} aligns well with ${company_name}'s digital transformation goals`,
      persuasion_levers: ["ROI improvement", "Competitive advantage", "Operational efficiency"],
      urgency_factors: ["Market competition", "Digital transformation timeline", "Cost optimization"]
    }
  });
});

// Email generation endpoint
app.post('/generate-email', (req, res) => {
  const { company_name, decision_maker, decision_maker_position, situation } = req.body;
  
  const subject = `Partnership Opportunity for ${company_name}`;
  const body = `Dear ${decision_maker},

I hope this email finds you well. As ${decision_maker_position} at ${company_name}, you're likely focused on driving growth and operational excellence.

I wanted to reach out because I believe there's a significant opportunity for ${company_name} to enhance your ${situation} initiatives through our innovative solutions.

Our platform has helped similar companies achieve:
• 30% improvement in operational efficiency
• 25% reduction in operational costs
• Faster time-to-market for new initiatives

Would you be available for a brief 15-minute call next week to explore how we can support ${company_name}'s strategic objectives?

Best regards,
Sales Team`;

  res.json({
    subject: subject,
    body: body
  });
});

// Send email endpoint
app.post('/send-email', (req, res) => {
  const { to_email, subject, body } = req.body;
  
  console.log(`Mock sending email to: ${to_email}`);
  console.log(`Subject: ${subject}`);
  
  res.json({
    success: true,
    message: "Email sent successfully (mock implementation)"
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Sales AI Agent Backend running on http://localhost:${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
});