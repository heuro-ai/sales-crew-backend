import React, { useState } from 'react';
import { Mail, User, Building2, Sparkles, Copy, Send, Loader } from 'lucide-react';
import { CompanyAnalysis, GeneratedEmail } from '../types';
import { apiService } from '../services/api';
import { toast } from 'react-hot-toast';

export const EmailGeneration: React.FC = () => {
  const [formData, setFormData] = useState({
    companyName: '',
    decisionMaker: '',
    position: '',
    situation: 'initial-outreach',
    productDescription: ''
  });
  const [loading, setLoading] = useState({
    analysis: false,
    generation: false,
    sending: false
  });
  const [analysis, setAnalysis] = useState<CompanyAnalysis | null>(null);
  const [generatedEmail, setGeneratedEmail] = useState<GeneratedEmail | null>(null);
  const [recipientEmail, setRecipientEmail] = useState('');

  const situationOptions = [
    { value: 'initial-outreach', label: 'Initial Outreach' },
    { value: 'follow-up', label: 'Follow Up' },
    { value: 'referral', label: 'Referral Introduction' },
    { value: 'event-follow-up', label: 'Event Follow Up' },
    { value: 'content-engagement', label: 'Content Engagement' }
  ];

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAnalyzeCompany = async () => {
    if (!formData.companyName || !formData.decisionMaker || !formData.position) {
      toast.error('Please fill in company name, decision maker, and position');
      return;
    }

    setLoading(prev => ({ ...prev, analysis: true }));
    try {
      const analysisResult = await apiService.getCompanyAnalysis(
        formData.companyName,
        formData.decisionMaker,
        formData.position,
        formData.productDescription || 'AI-powered sales solutions'
      );
      setAnalysis(analysisResult);
      
      // Update dashboard stats
      const stats = JSON.parse(localStorage.getItem('dashboardStats') || '{}');
      stats.companiesAnalyzed = (stats.companiesAnalyzed || 0) + 1;
      localStorage.setItem('dashboardStats', JSON.stringify(stats));
      
      toast.success('Company analysis completed!');
    } catch (error) {
      console.error('Analysis failed:', error);
      toast.error(error instanceof Error ? error.message : 'Analysis failed');
    } finally {
      setLoading(prev => ({ ...prev, analysis: false }));
    }
  };

  const handleGenerateEmail = async () => {
    if (!formData.companyName || !formData.decisionMaker || !formData.position) {
      toast.error('Please fill in required fields');
      return;
    }

    setLoading(prev => ({ ...prev, generation: true }));
    try {
      const email = await apiService.generateEmail(
        formData.companyName,
        formData.decisionMaker,
        formData.position,
        formData.situation,
        formData.productDescription || 'AI-powered sales solutions',
        analysis || undefined
      );
      setGeneratedEmail(email);
      
      // Update dashboard stats
      const stats = JSON.parse(localStorage.getItem('dashboardStats') || '{}');
      stats.emailsGenerated = (stats.emailsGenerated || 0) + 1;
      localStorage.setItem('dashboardStats', JSON.stringify(stats));
      
      toast.success('Email generated successfully!');
    } catch (error) {
      console.error('Email generation failed:', error);
      toast.error(error instanceof Error ? error.message : 'Email generation failed');
    } finally {
      setLoading(prev => ({ ...prev, generation: false }));
    }
  };

  const handleSendEmail = async () => {
    if (!generatedEmail || !recipientEmail) {
      toast.error('Please generate an email and enter recipient address');
      return;
    }

    setLoading(prev => ({ ...prev, sending: true }));
    try {
      const result = await apiService.sendEmail({
        to_email: recipientEmail,
        subject: generatedEmail.subject,
        body: generatedEmail.body
      });
      
      if (result.success) {
        toast.success('Email sent successfully!');
        setRecipientEmail('');
      } else {
        toast.error(result.message || 'Failed to send email');
      }
    } catch (error) {
      console.error('Email sending failed:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to send email');
    } finally {
      setLoading(prev => ({ ...prev, sending: false }));
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Email Generation</h1>
        <p className="text-gray-600">Generate personalized outreach emails using AI analysis</p>
      </div>

      {/* Input Form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center mb-4">
          <Sparkles className="w-5 h-5 text-purple-600 mr-2" />
          <h2 className="text-lg font-semibold text-gray-900">Email Parameters</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Company Name *
            </label>
            <div className="relative">
              <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={formData.companyName}
                onChange={(e) => handleInputChange('companyName', e.target.value)}
                placeholder="Microsoft"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Decision Maker *
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={formData.decisionMaker}
                onChange={(e) => handleInputChange('decisionMaker', e.target.value)}
                placeholder="Satya Nadella"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Position *
            </label>
            <input
              type="text"
              value={formData.position}
              onChange={(e) => handleInputChange('position', e.target.value)}
              placeholder="CEO"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Situation Type
            </label>
            <select
              value={formData.situation}
              onChange={(e) => handleInputChange('situation', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {situationOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Product Description
          </label>
          <textarea
            value={formData.productDescription}
            onChange={(e) => handleInputChange('productDescription', e.target.value)}
            placeholder="AI-powered sales automation platform that helps sales teams increase productivity by 40%..."
            rows={3}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
          />
        </div>

        <div className="flex space-x-3">
          <button
            onClick={handleAnalyzeCompany}
            disabled={loading.analysis || !formData.companyName || !formData.decisionMaker}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading.analysis ? (
              <div className="flex items-center">
                <Loader className="animate-spin w-4 h-4 mr-2" />
                Analyzing...
              </div>
            ) : (
              'Analyze Company'
            )}
          </button>

          <button
            onClick={handleGenerateEmail}
            disabled={loading.generation || !formData.companyName || !formData.decisionMaker}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading.generation ? (
              <div className="flex items-center">
                <Loader className="animate-spin w-4 h-4 mr-2" />
                Generating...
              </div>
            ) : (
              'Generate Email'
            )}
          </button>
        </div>
      </div>

      {/* Company Analysis Results */}
      {analysis && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Company Analysis</h3>
          
          <div className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Recent News</h4>
                <p className="text-sm text-blue-800">{analysis.company_analysis.recent_news}</p>
              </div>
              
              <div className="p-4 bg-green-50 rounded-lg">
                <h4 className="font-medium text-green-900 mb-2">Financial Health</h4>
                <p className="text-sm text-green-800">{analysis.company_analysis.financial_health}</p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Key Challenges</h4>
                <ul className="space-y-1">
                  {analysis.company_analysis.verified_challenges.map((challenge, idx) => (
                    <li key={idx} className="text-sm text-gray-600 flex items-start">
                      <span className="w-1.5 h-1.5 bg-red-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                      {challenge}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Strategic Priorities</h4>
                <ul className="space-y-1">
                  {analysis.company_analysis.strategic_priorities.map((priority, idx) => (
                    <li key={idx} className="text-sm text-gray-600 flex items-start">
                      <span className="w-1.5 h-1.5 bg-green-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                      {priority}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Generated Email */}
      {generatedEmail && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Generated Email</h3>
            <button
              onClick={() => copyToClipboard(`Subject: ${generatedEmail.subject}\n\n${generatedEmail.body.replace(/<[^>]*>/g, '')}`)}
              className="text-blue-600 hover:text-blue-800 transition-colors flex items-center text-sm"
            >
              <Copy className="w-4 h-4 mr-1" />
              Copy All
            </button>
          </div>
          
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">Subject:</label>
                <button
                  onClick={() => copyToClipboard(generatedEmail.subject)}
                  className="text-blue-600 hover:text-blue-800 transition-colors"
                >
                  <Copy className="w-3 h-3" />
                </button>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 font-medium text-gray-900">
                {generatedEmail.subject}
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">Body:</label>
                <button
                  onClick={() => copyToClipboard(generatedEmail.body.replace(/<[^>]*>/g, ''))}
                  className="text-blue-600 hover:text-blue-800 transition-colors"
                >
                  <Copy className="w-3 h-3" />
                </button>
              </div>
              <div 
                className="bg-gray-50 rounded-lg p-4 text-gray-800 whitespace-pre-wrap"
                dangerouslySetInnerHTML={{ __html: generatedEmail.body }}
              />
            </div>
          </div>

          {/* Send Email Section */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <h4 className="font-medium text-gray-900 mb-3">Send Email</h4>
            <div className="flex space-x-3">
              <div className="flex-1">
                <input
                  type="email"
                  value={recipientEmail}
                  onChange={(e) => setRecipientEmail(e.target.value)}
                  placeholder="recipient@company.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
              <button
                onClick={handleSendEmail}
                disabled={loading.sending || !recipientEmail}
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center"
              >
                {loading.sending ? (
                  <Loader className="animate-spin w-4 h-4 mr-2" />
                ) : (
                  <Send className="w-4 h-4 mr-2" />
                )}
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};