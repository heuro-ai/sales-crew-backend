// Mock API service for demonstration purposes
// In production, replace with actual API endpoints

export interface SearchResult {
  title: string;
  snippet: string;
  link: string;
}

export interface EmailVerification {
  email: string;
  isValid: boolean;
  status: string;
}

export interface CompanyAnalysis {
  company_analysis: {
    recent_news: string;
    financial_health: string;
    verified_challenges: string[];
    strategic_priorities: string[];
  };
  decision_maker_profile: {
    communication_style: string;
    personality_indicators: string;
    personality_type: string;
    key_achievements: string;
    recent_activities: string;
  };
  synergy_points: {
    product_fit: string;
    persuasion_levers: string[];
    urgency_factors: string[];
  };
}

export interface GeneratedEmail {
  subject: string;
  body: string;
}

// Mock data for demonstration
const mockSearchResults: SearchResult[] = [
  {
    title: "John Smith - VP of Sales at TechCorp - LinkedIn",
    snippet: "Experienced VP of Sales with 10+ years leading high-performing sales teams at Fortune 500 companies. Currently driving revenue growth at TechCorp...",
    link: "https://www.linkedin.com/in/johnsmith-techcorp"
  },
  {
    title: "Sarah Johnson - Chief Technology Officer at InnovateAI",
    snippet: "Visionary CTO leading AI transformation initiatives. Expert in machine learning, cloud architecture, and digital transformation...",
    link: "https://www.linkedin.com/in/sarahjohnson-innovateai"
  },
  {
    title: "Michael Chen - Director of Operations at GrowthCorp",
    snippet: "Operations leader specializing in process optimization and operational efficiency. Currently implementing digital transformation...",
    link: "https://www.linkedin.com/in/michaelchen-growthcorp"
  }
];

const mockCompanyAnalysis: CompanyAnalysis = {
  company_analysis: {
    recent_news: "TechCorp recently announced a $50M Series C funding round to expand their AI capabilities and enter new markets. The company has shown 45% YoY growth and is actively hiring across all departments.",
    financial_health: "Strong financial position with consistent revenue growth, healthy cash flow, and recent successful funding round. Company is in expansion mode with solid fundamentals.",
    verified_challenges: [
      "Scaling operational efficiency as team grows rapidly",
      "Need for advanced AI tools to maintain competitive edge", 
      "Managing increased customer support demands"
    ],
    strategic_priorities: [
      "AI integration across all business processes",
      "Market expansion to European regions",
      "Building scalable customer success operations"
    ]
  },
  decision_maker_profile: {
    communication_style: "Data-driven and results-focused",
    personality_indicators: "Strategic thinker, values efficiency, prefers concrete ROI metrics",
    personality_type: "ENTJ - The Executive",
    key_achievements: "Led 300% revenue growth over 3 years, built award-winning sales team, recognized as 'Sales Leader of the Year'",
    recent_activities: "Speaking at SaaS Summit 2024, recently posted about AI adoption in sales processes, active in sales leadership communities"
  },
  synergy_points: {
    product_fit: "Your AI solutions directly address their operational scaling challenges and AI integration priorities",
    persuasion_levers: [
      "Demonstrate ROI with concrete metrics and case studies",
      "Show how solution accelerates their AI transformation goals",
      "Emphasize operational efficiency gains during rapid growth"
    ],
    urgency_factors: [
      "Current rapid scaling creating operational bottlenecks",
      "Competitive pressure requiring AI adoption",
      "Window of opportunity with new funding for strategic investments"
    ]
  }
};

// Simulated API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const apiService = {
  // Search for companies and decision makers
  searchCompanies: async (query: string, limit: number = 5): Promise<SearchResult[]> => {
    await delay(1500); // Simulate API call
    
    // Filter mock results based on query
    const filtered = mockSearchResults.filter(result => 
      result.title.toLowerCase().includes(query.toLowerCase()) ||
      result.snippet.toLowerCase().includes(query.toLowerCase())
    );
    
    return filtered.slice(0, limit);
  },

  // Verify email address
  verifyEmail: async (firstName: string, lastName: string, domain: string): Promise<EmailVerification> => {
    await delay(2000); // Simulate API call
    
    // Generate most likely email format
    const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@${domain.toLowerCase()}`;
    
    // Simulate verification logic
    const commonDomains = ['gmail.com', 'outlook.com', 'yahoo.com', 'company.com'];
    const isCommonDomain = commonDomains.some(d => domain.toLowerCase().includes(d.split('.')[0]));
    
    return {
      email,
      isValid: Math.random() > 0.3, // 70% success rate for demo
      status: isCommonDomain ? 'Verified' : 'Deliverable'
    };
  },

  // Get company and decision maker analysis
  getCompanyAnalysis: async (
    companyName: string,
    personName: string,
    position: string,
    productDescription: string
  ): Promise<CompanyAnalysis> => {
    await delay(3000); // Simulate longer AI processing
    
    // Return customized mock data
    return {
      ...mockCompanyAnalysis,
      company_analysis: {
        ...mockCompanyAnalysis.company_analysis,
        recent_news: `${companyName} recently announced significant growth initiatives and is actively seeking solutions to enhance ${position.toLowerCase()} operations...`
      }
    };
  },

  // Generate personalized email
  generateEmail: async (
    companyName: string,
    decisionMaker: string,
    position: string,
    situation: string,
    productDescription: string,
    analysis?: CompanyAnalysis
  ): Promise<GeneratedEmail> => {
    await delay(2500); // Simulate AI email generation
    
    const subjects = [
      `${decisionMaker}, quick question about ${companyName}'s AI initiatives`,
      `Helping ${companyName} scale operations efficiently`,
      `${decisionMaker}, thought this might interest you for ${companyName}`,
      `Quick solution for ${companyName}'s growth challenges`
    ];
    
    const emailBody = `
      <p>Hi ${decisionMaker},</p>
      
      <p>I noticed ${companyName}'s recent growth and expansion initiatives. As ${position}, you're likely focused on ${analysis?.company_analysis.strategic_priorities[0] || 'operational efficiency'}.</p>
      
      <p>We've helped similar companies like yours:</p>
      <ul>
        <li>Reduce operational overhead by 35%</li>
        <li>Accelerate AI implementation timelines</li>
        <li>Scale efficiently during rapid growth phases</li>
      </ul>
      
      <p>Given your background in ${analysis?.decision_maker_profile.key_achievements || 'driving results'}, I thought this might be relevant for ${companyName}'s current priorities.</p>
      
      <p>Worth a quick 10-minute call this week to explore how this could specifically benefit ${companyName}?</p>
      
      <p>Best regards,<br>
      Alex Thompson<br>
      Senior Solutions Consultant<br>
      AI Growth Solutions</p>
    `;
    
    return {
      subject: subjects[Math.floor(Math.random() * subjects.length)],
      body: emailBody.trim()
    };
  }
};