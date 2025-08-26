import React, { useState } from 'react';
import { 
  User, Building, Mail, ExternalLink, Star, Bookmark, 
  CheckCircle, XCircle, Brain, TrendingUp, MessageSquare,
  MoreHorizontal, Download, Eye
} from 'lucide-react';
import { Lead, PsychographicProfile } from '../types';
import { toast } from 'react-hot-toast';

interface LeadCardProps {
  lead: Lead;
  onViewDetails: (lead: Lead) => void;
  onVerifyEmail: (lead: Lead) => void;
  onSaveLead: (leadId: string) => void;
  onGenerateEmail: (lead: Lead) => void;
  saved?: boolean;
  loading?: {
    verify?: boolean;
    save?: boolean;
    email?: boolean;
  };
}

export const LeadCard: React.FC<LeadCardProps> = ({
  lead,
  onViewDetails,
  onVerifyEmail,
  onSaveLead,
  onGenerateEmail,
  saved = false,
  loading = {}
}) => {
  const [showMenu, setShowMenu] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getVerificationStatus = () => {
    if (lead.verified === undefined) return null;
    return lead.verified ? (
      <div className="flex items-center text-green-600 text-xs">
        <CheckCircle className="w-3 h-3 mr-1" />
        Verified
      </div>
    ) : (
      <div className="flex items-center text-red-600 text-xs">
        <XCircle className="w-3 h-3 mr-1" />
        Unverified
      </div>
    );
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard!`);
  };

  const handleMenuAction = (action: string) => {
    setShowMenu(false);
    
    switch (action) {
      case 'details':
        onViewDetails(lead);
        break;
      case 'verify':
        onVerifyEmail(lead);
        break;
      case 'save':
        onSaveLead(lead.id);
        break;
      case 'email':
        onGenerateEmail(lead);
        break;
      default:
        break;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
      {/* Header */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-3 rounded-xl">
              <User className="w-6 h-6 text-white" />
            </div>
            
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-1">
                <h3 className="font-bold text-gray-900 text-lg">{lead.name}</h3>
                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getScoreColor(lead.score)}`}>
                  {lead.score}% Match
                </span>
              </div>
              
              <p className="text-gray-600 font-medium">{lead.position}</p>
              
              <div className="flex items-center text-gray-500 text-sm mt-1">
                <Building className="w-4 h-4 mr-1" />
                <span>{lead.company}</span>
                {lead.linkedin && (
                  <a
                    href={lead.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </div>
            </div>
          </div>
          
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <MoreHorizontal className="w-5 h-5 text-gray-600" />
            </button>
            
            {showMenu && (
              <div className="absolute right-0 top-10 bg-white rounded-lg shadow-xl border border-gray-200 py-1 z-10 w-48">
                <button
                  onClick={() => handleMenuAction('details')}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  View Details
                </button>
                <button
                  onClick={() => handleMenuAction('verify')}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  disabled={loading.verify}
                >
                  <Mail className="w-4 h-4 mr-2" />
                  Verify Email
                </button>
                <button
                  onClick={() => handleMenuAction('save')}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  disabled={loading.save}
                >
                  <Bookmark className="w-4 h-4 mr-2" />
                  {saved ? 'Saved' : 'Save Lead'}
                </button>
                <button
                  onClick={() => handleMenuAction('email')}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  disabled={loading.email}
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Generate Email
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {lead.email ? (
              <button
                onClick={() => copyToClipboard(lead.email!, 'Email')}
                className="flex items-center text-gray-600 hover:text-blue-600 transition-colors"
              >
                <Mail className="w-4 h-4 mr-2" />
                <span className="text-sm font-mono">{lead.email}</span>
              </button>
            ) : (
              <span className="flex items-center text-gray-400 text-sm">
                <Mail className="w-4 h-4 mr-2" />
                Email not found
              </span>
            )}
          </div>
          {getVerificationStatus()}
        </div>
      </div>

      {/* Psychographic Preview */}
      {lead.psychographics && (
        <div className="px-6 py-4 border-b border-gray-100">
          <div className="flex items-center mb-3">
            <Brain className="w-4 h-4 text-purple-600 mr-2" />
            <span className="text-sm font-semibold text-gray-900">Psychographic Profile</span>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-600">Personality Type:</span>
              <span className="font-medium text-gray-900">{lead.psychographics.personality_type}</span>
            </div>
            
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-600">Communication Style:</span>
              <span className="font-medium text-gray-900">{lead.psychographics.communication_style}</span>
            </div>
            
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-600">Urgency Level:</span>
              <span className={`font-medium px-2 py-1 rounded-full ${
                lead.psychographics.urgency_level === 'high' ? 'bg-red-100 text-red-800' :
                lead.psychographics.urgency_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-green-100 text-green-800'
              }`}>
                {lead.psychographics.urgency_level}
              </span>
            </div>
          </div>
          
          <button
            onClick={() => onViewDetails(lead)}
            className="mt-3 text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center"
          >
            View full profile
            <ExternalLink className="w-3 h-3 ml-1" />
          </button>
        </div>
      )}

      {/* Action Buttons */}
      <div className="px-6 py-4">
        <div className="flex space-x-2">
          <button
            onClick={() => onVerifyEmail(lead)}
            disabled={loading.verify || lead.verified}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium flex items-center justify-center"
          >
            {loading.verify ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <>
                <Mail className="w-4 h-4 mr-2" />
                {lead.verified ? 'Verified' : 'Verify'}
              </>
            )}
          </button>
          
          <button
            onClick={() => onGenerateEmail(lead)}
            disabled={loading.email}
            className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium flex items-center justify-center"
          >
            {loading.email ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <>
                <MessageSquare className="w-4 h-4 mr-2" />
                Generate Email
              </>
            )}
          </button>
          
          <button
            onClick={() => onSaveLead(lead.id)}
            disabled={loading.save}
            className={`p-2 rounded-lg transition-colors ${
              saved 
                ? 'bg-green-100 text-green-600' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {loading.save ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
            ) : (
              <Star className={`w-4 h-4 ${saved ? 'fill-current' : ''}`} />
            )}
          </button>
        </div>
      </div>

      {/* Source Badge */}
      <div className="px-6 pb-4">
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
          Source: {lead.source}
        </span>
      </div>
    </div>
  );
};