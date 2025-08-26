// API Service for Sales AI Agent Backend
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-url.com' 
  : 'http://localhost:8000';

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

export interface EmailSendRequest {
  to_email: string;
  subject: string;
  body: string;
}

class APIService {
  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        timeout: 10000, // 10 second timeout
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        console.error(`Backend server not available at ${API_BASE_URL}`);
        throw new Error('Backend server is not running. Please start the Python FastAPI server on port 8000.');
      }
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Google Search API
  async searchCompanies(query: string, limit: number = 5): Promise<SearchResult[]> {
    return this.makeRequest<SearchResult[]>('/search', {
      method: 'POST',
      body: JSON.stringify({ query, limit }),
    });
  }

  // Email Verification
  async verifyEmail(firstName: string, lastName: string, domain: string): Promise<EmailVerification> {
    return this.makeRequest<EmailVerification>('/verify-email', {
      method: 'POST',
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        domain: domain,
      }),
    });
  }

  // Company Analysis
  async getCompanyAnalysis(
    companyName: string,
    personName: string,
    position: string,
    productDescription: string
  ): Promise<CompanyAnalysis> {
    return this.makeRequest<CompanyAnalysis>('/analyze-company', {
      method: 'POST',
      body: JSON.stringify({
        company_name: companyName,
        person_name: personName,
        position: position,
        product_description: productDescription,
      }),
    });
  }

  // Email Generation
  async generateEmail(
    companyName: string,
    decisionMaker: string,
    position: string,
    situation: string,
    productDescription: string,
    analysis?: CompanyAnalysis
  ): Promise<GeneratedEmail> {
    return this.makeRequest<GeneratedEmail>('/generate-email', {
      method: 'POST',
      body: JSON.stringify({
        company_name: companyName,
        decision_maker: decisionMaker,
        decision_maker_position: position,
        situation: situation,
        product_description: productDescription,
        sender_name: 'Sales Agent',
        sender_position: 'Business Development',
        sender_company: 'AI Sales Solutions',
        req_info: analysis ? JSON.stringify(analysis) : undefined,
      }),
    });
  }

  // Send Email
  async sendEmail(emailData: EmailSendRequest): Promise<{ success: boolean; message: string }> {
    return this.makeRequest<{ success: boolean; message: string }>('/send-email', {
      method: 'POST',
      body: JSON.stringify(emailData),
    });
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; message: string }> {
    return this.makeRequest<{ status: string; message: string }>('/health');
  }
}

export const apiService = new APIService();