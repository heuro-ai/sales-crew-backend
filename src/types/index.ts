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

export interface Lead {
  id: string;
  name: string;
  position: string;
  company: string;
  email?: string;
  verified?: boolean;
  source: string;
}

export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}