export interface Lead {
  id: string;
  company: string;
  name: string;
  position: string;
  email?: string;
  verified?: boolean;
  domain: string;
  linkedin?: string;
  psychographics?: PsychographicProfile;
  score: number;
  source: string;
}

export interface PsychographicProfile {
  communication_style: string;
  personality_type: string;
  personality_indicators: string;
  motivations: string[];
  pain_points: string[];
  behavioral_traits: string[];
  decision_factors: string[];
  urgency_level: 'low' | 'medium' | 'high';
  influence_style: string;
}

export interface SearchResult {
  title: string;
  snippet: string;
  link: string;
}

export interface EmailVerification {
  email: string;
  isValid: boolean;
  status: string;
  deliverability: string;
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

export interface SearchFilters {
  industry?: string;
  company_size?: string;
  location?: string;
  position_level?: string;
  keywords?: string[];
}

export interface AIInsight {
  type: 'suggestion' | 'warning' | 'opportunity';
  title: string;
  description: string;
  confidence: number;
  action?: string;
}