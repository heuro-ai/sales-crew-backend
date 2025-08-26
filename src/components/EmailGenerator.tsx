import React, { useState } from 'react';
import { Copy, Mail, Send, CheckCircle, TrendingUp, User, Building } from 'lucide-react';
import { CompanyAnalysis, GeneratedEmail } from '../types';
import { toast } from 'react-hot-toast';

interface EmailGeneratorProps {
  analysis: CompanyAnalysis | null;
  generatedEmail: GeneratedEmail | null;
  onGenerateEmail: (
    companyName: string,
    decisionMaker: string, 
    position: string,
    situation: string,
    productDescription: string
  ) => void;
  loading: {
    generation: boolean;
  };
}

export const EmailGenerator: React.FC<EmailGeneratorProps> = ({
  analysis,
  generatedEmail,
  onGenerateEmail,
  loading
}) => {
  const [companyName, setCompanyName] = useState('');
  const [decisionMaker, setDecisionMaker] = useState('');
  const [position, setPosition] = useState('');
  const [situation, setSituation] = useState('initial-outreach');
  const [productDescription, setProductDescription] = useState('');

  const handleGenerateEmail = (e: React.FormEvent) => {
    e.preventDefault();
    if (companyName && decisionMaker && position && productDescription) {
      onGenerateEmail(companyName, decisionMaker, position, situation, productDescription);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const situationOptions = [
    { value: 'initial-outreach', label: 'Initial Outreach' },
    { value: 'follow-up', label: 'Follow Up' },
    { value: 'referral', label: 'Referral Introduction' },
    { value: 'event-follow-up', label: 'Event Follow Up' },
    { value: 'content-engagement', label: 'Content Engagement' }
  ];

  return (
    <div className="space-y-6">
      {/* Company Analysis Results */}
      {analysis && (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100">
          <div className="p-6 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
              Company Analysis
            </h3>
          </div>
          
          <div className="p-6 space-y-6">
            {/* Company Overview */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <Building className="w-4 h-4 mr-2 text-blue-600" />
                  Company Insights
                </h4>
                <div className="space-y-3 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Recent News:</span>
                    <p className="text-gray-600 mt-1">{analysis.company_analysis.recent_news}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Financial Health:</span>
                    <p className="text-gray-600 mt-1">{analysis.company_analysis.financial_health}</p>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <User className="w-4 h-4 mr-2 text-green-600" />
                  Decision Maker Profile
                </h4>
                <div className="space-y-3 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Communication Style:</span>
                    <p className="text-gray-600 mt-1">{analysis.decision_maker_profile.communication_style}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Personality Type:</span>
                    <p className="text-gray-600 mt-1">{analysis.decision_maker_profile.personality_type}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Challenges and Priorities */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Key Challenges</h4>
                <ul className="space-y-2">
                  {analysis.company_analysis.verified_challenges.map((challenge, idx) => (
                    <li key={idx} className="flex items-start text-sm text-gray-600">
                      <div className="w-1.5 h-1.5 bg-red-400 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                      {challenge}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Strategic Priorities</h4>
                <ul className="space-y-2">
                  {analysis.company_analysis.strategic_priorities.map((priority, idx) => (
                    <li key={idx} className="flex items-start text-sm text-gray-600">
                      <div className="w-1.5 h-1.5 bg-green-400 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                      {priority}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Persuasion Levers */}
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Persuasion Strategy</h4>
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-blue-800 mb-3">
                  <strong>Product Fit:</strong> {analysis.synergy_points.product_fit}
                </p>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h5 className="font-medium text-blue-900 mb-2">Key Levers:</h5>
                    <ul className="space-y-1">
                      {analysis.synergy_points.persuasion_levers.map((lever, idx) => (
                        <li key={idx} className="text-xs text-blue-700">• {lever}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h5 className="font-medium text-blue-900 mb-2">Urgency Factors:</h5>
                    <ul className="space-y-1">
                      {analysis.synergy_points.urgency_factors.map((factor, idx) => (
                        <li key={idx} className="text-xs text-blue-700">• {factor}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Email Generation Form */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <div className="flex items-center mb-4">
          <Mail className="w-5 h-5 text-purple-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Generate Personalized Email</h3>
        </div>
        
        <form onSubmit={handleGenerateEmail} className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Name
              </label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="TechCorp"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Decision Maker
              </label>
              <input
                type="text"
                value={decisionMaker}
                onChange={(e) => setDecisionMaker(e.target.value)}
                placeholder="John Smith"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>
          </div>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Position
              </label>
              <input
                type="text"
                value={position}
                onChange={(e) => setPosition(e.target.value)}
                placeholder="VP of Sales"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Situation Type
              </label>
              <select
                value={situation}
                onChange={(e) => setSituation(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                {situationOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Product Description
            </label>
            <textarea
              value={productDescription}
              onChange={(e) => setProductDescription(e.target.value)}
              placeholder="AI-powered sales automation platform that helps sales teams increase productivity by 40%..."
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading.generation}
            className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading.generation ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Generating Email...
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <Send className="w-4 h-4 mr-2" />
                Generate Email
              </div>
            )}
          </button>
        </form>
      </div>

      {/* Generated Email */}
      {generatedEmail && (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100">
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
                Generated Email
              </h3>
              <button
                onClick={() => copyToClipboard(`Subject: ${generatedEmail.subject}\n\n${generatedEmail.body.replace(/<[^>]*>/g, '')}`)}
                className="text-blue-600 hover:text-blue-800 transition-colors flex items-center text-sm"
              >
                <Copy className="w-4 h-4 mr-1" />
                Copy Email
              </button>
            </div>
          </div>
          
          <div className="p-6 space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">Subject Line:</label>
                <button
                  onClick={() => copyToClipboard(generatedEmail.subject)}
                  className="text-blue-600 hover:text-blue-800 transition-colors"
                >
                  <Copy className="w-3 h-3" />
                </button>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 text-sm font-medium text-gray-900">
                {generatedEmail.subject}
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">Email Body:</label>
                <button
                  onClick={() => copyToClipboard(generatedEmail.body.replace(/<[^>]*>/g, ''))}
                  className="text-blue-600 hover:text-blue-800 transition-colors"
                >
                  <Copy className="w-3 h-3" />
                </button>
              </div>
              <div 
                className="bg-gray-50 rounded-lg p-4 text-sm text-gray-800 whitespace-pre-wrap"
                dangerouslySetInnerHTML={{ __html: generatedEmail.body }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};