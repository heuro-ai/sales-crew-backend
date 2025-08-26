import { Lead, EmailVerification, CompanyAnalysis, GeneratedEmail, SearchFilters, AIInsight, PsychographicProfile } from '../types';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-url.com/api' 
  : 'http://localhost:8000';

class APIService {
  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Lead search and discovery
  async searchLeads(query: string, filters?: SearchFilters, limit: number = 10): Promise<Lead[]> {
    const searchParams = new URLSearchParams({
      q: query,
      limit: limit.toString(),
      ...(filters?.industry && { industry: filters.industry }),
      ...(filters?.company_size && { company_size: filters.company_size }),
      ...(filters?.location && { location: filters.location }),
      ...(filters?.position_level && { position_level: filters.position_level }),
    });

    return this.makeRequest<Lead[]>(`/leads/search?${searchParams}`);
  }

  // Get psychographic analysis for a lead
  async getLeadPsychographics(leadId: string): Promise<PsychographicProfile> {
    return this.makeRequest<PsychographicProfile>(`/leads/${leadId}/psychographics`);
  }

  // Verify email address
  async verifyEmail(firstName: string, lastName: string, domain: string): Promise<EmailVerification> {
    return this.makeRequest<EmailVerification>('/leads/verify-email', {
      method: 'POST',
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        domain: domain,
      }),
    });
  }

  // Get company analysis
  async getCompanyAnalysis(
    companyName: string,
    personName: string,
    position: string,
    productDescription: string
  ): Promise<CompanyAnalysis> {
    return this.makeRequest<CompanyAnalysis>('/leads/analyze-company', {
      method: 'POST',
      body: JSON.stringify({
        company_name: companyName,
        person_name: personName,
        position: position,
        product_description: productDescription,
      }),
    });
  }

  // Generate personalized email
  async generateEmail(
    companyName: string,
    decisionMaker: string,
    position: string,
    situation: string,
    productDescription: string,
    analysis?: CompanyAnalysis
  ): Promise<GeneratedEmail> {
    return this.makeRequest<GeneratedEmail>('/leads/generate-email', {
      method: 'POST',
      body: JSON.stringify({
        company_name: companyName,
        decision_maker: decisionMaker,
        position: position,
        situation: situation,
        product_description: productDescription,
        req_info: analysis ? JSON.stringify(analysis) : undefined,
      }),
    });
  }

  // Get AI insights for leads
  async getAIInsights(leads: Lead[]): Promise<AIInsight[]> {
    return this.makeRequest<AIInsight[]>('/leads/ai-insights', {
      method: 'POST',
      body: JSON.stringify({ leads }),
    });
  }

  // Save lead to favorites/CRM
  async saveLead(leadId: string): Promise<{ success: boolean }> {
    return this.makeRequest<{ success: boolean }>(`/leads/${leadId}/save`, {
      method: 'POST',
    });
  }

  // Export leads data
  async exportLeads(leadIds: string[], format: 'csv' | 'xlsx' = 'csv'): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/leads/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lead_ids: leadIds, format }),
    });

    return response.blob();
  }
}

export const apiService = new APIService();