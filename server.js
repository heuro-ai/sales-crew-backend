const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = 8000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Company search endpoint
app.post('/search-companies', (req, res) => {
  const { query, filters } = req.body;
  
  // Mock company data for demo
  const mockCompanies = [
    {
      id: 1,
      name: 'TechCorp Solutions',
      domain: 'techcorp.com',
      industry: 'Technology',
      size: '50-100 employees',
      location: 'San Francisco, CA',
      description: 'Leading software development company'
    },
    {
      id: 2,
      name: 'DataFlow Systems',
      domain: 'dataflow.io',
      industry: 'Data Analytics',
      size: '100-250 employees', 
      location: 'New York, NY',
      description: 'Enterprise data solutions provider'
    },
    {
      id: 3,
      name: 'CloudTech Innovations',
      domain: 'cloudtech.com',
      industry: 'Cloud Services',
      size: '25-50 employees',
      location: 'Austin, TX',
      description: 'Cloud infrastructure and services'
    }
  ];

  // Filter based on query if provided
  let results = mockCompanies;
  if (query) {
    results = mockCompanies.filter(company => 
      company.name.toLowerCase().includes(query.toLowerCase()) ||
      company.industry.toLowerCase().includes(query.toLowerCase())
    );
  }

  res.json({
    companies: results,
    total: results.length,
    query: query || ''
  });
});

// Email verification endpoint
app.post('/verify-email', (req, res) => {
  const { email } = req.body;
  
  if (!email) {
    return res.status(400).json({ error: 'Email is required' });
  }

  // Mock email verification
  const isValid = email.includes('@') && email.includes('.');
  const deliverable = Math.random() > 0.3; // 70% chance of being deliverable

  res.json({
    email: email,
    valid: isValid,
    deliverable: deliverable,
    risk: deliverable ? 'low' : 'high',
    provider: email.split('@')[1] || 'unknown'
  });
});

// Email generation endpoint
app.post('/generate-email', (req, res) => {
  const { companyName, recipientName, tone, purpose } = req.body;
  
  // Mock email generation
  const templates = {
    professional: `Dear ${recipientName || 'Hiring Manager'},

I hope this email finds you well. I wanted to reach out regarding potential collaboration opportunities between our companies.

${companyName || 'Your company'} has caught our attention due to your innovative approach in the industry. We believe there could be significant synergies between our organizations.

I would welcome the opportunity to discuss how we might work together to achieve mutual success.

Best regards,
Sales Team`,
    
    casual: `Hi ${recipientName || 'there'}!

Hope you're having a great day! I came across ${companyName || 'your company'} and was really impressed by what you're doing.

I think there might be some cool opportunities for us to collaborate. Would love to chat about it sometime!

Looking forward to hearing from you!

Cheers,
Sales Team`,
    
    urgent: `Dear ${recipientName || 'Decision Maker'},

I hope this message reaches you at the right time. We have an exciting opportunity that could significantly benefit ${companyName || 'your organization'}.

Time-sensitive partnerships like this don't come around often, and I believe ${companyName || 'your company'} would be an ideal fit.

Could we schedule a brief call this week to discuss?

Best regards,
Sales Team`
  };

  const selectedTemplate = templates[tone] || templates.professional;

  res.json({
    subject: `Partnership Opportunity for ${companyName || 'Your Company'}`,
    body: selectedTemplate,
    tone: tone || 'professional',
    estimatedReadTime: '2 minutes'
  });
});

// Analytics endpoint
app.get('/analytics', (req, res) => {
  res.json({
    totalSearches: Math.floor(Math.random() * 1000) + 500,
    emailsVerified: Math.floor(Math.random() * 800) + 300,
    emailsGenerated: Math.floor(Math.random() * 600) + 200,
    successRate: 85.4
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Sales AI Agent Backend running on http://localhost:${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
});