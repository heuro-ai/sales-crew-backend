import React, { useState } from 'react';
import { Mail, User, Building2, CheckCircle, XCircle, Loader } from 'lucide-react';
import { EmailVerification as EmailVerificationType } from '../types';
import { apiService } from '../services/api';
import { toast } from 'react-hot-toast';

export const EmailVerification: React.FC = () => {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [domain, setDomain] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EmailVerificationType | null>(null);
  const [verificationHistory, setVerificationHistory] = useState<EmailVerificationType[]>([]);

  const handleVerification = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!firstName.trim() || !lastName.trim() || !domain.trim()) {
      toast.error('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const verification = await apiService.verifyEmail(firstName, lastName, domain);
      setResult(verification);
      
      // Add to history
      setVerificationHistory(prev => [verification, ...prev.slice(0, 9)]);
      
      // Update dashboard stats
      const stats = JSON.parse(localStorage.getItem('dashboardStats') || '{}');
      stats.emailsVerified = (stats.emailsVerified || 0) + 1;
      localStorage.setItem('dashboardStats', JSON.stringify(stats));
      
      toast.success(verification.isValid ? 'Email verified successfully!' : 'Email could not be verified');
    } catch (error) {
      console.error('Verification failed:', error);
      toast.error(error instanceof Error ? error.message : 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setFirstName('');
    setLastName('');
    setDomain('');
    setResult(null);
  };

  const copyEmail = (email: string) => {
    navigator.clipboard.writeText(email);
    toast.success('Email copied to clipboard!');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Email Verification</h1>
        <p className="text-gray-600">Verify email addresses before sending outreach campaigns</p>
      </div>

      {/* Verification Form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center mb-4">
          <Mail className="w-5 h-5 text-green-600 mr-2" />
          <h2 className="text-lg font-semibold text-gray-900">Verify Email Address</h2>
        </div>

        <form onSubmit={handleVerification} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-2">
                First Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  id="firstName"
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="John"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-2">
                Last Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  id="lastName"
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  placeholder="Smith"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
          
          <div>
            <label htmlFor="domain" className="block text-sm font-medium text-gray-700 mb-2">
              Company Domain
            </label>
            <div className="relative">
              <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                id="domain"
                type="text"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="company.com"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="flex space-x-3">
            <button
              type="submit"
              disabled={loading || !firstName.trim() || !lastName.trim() || !domain.trim()}
              className="flex-1 bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <Loader className="animate-spin w-4 h-4 mr-2" />
                  Verifying...
                </div>
              ) : (
                'Verify Email'
              )}
            </button>
            
            <button
              type="button"
              onClick={clearForm}
              className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
            >
              Clear
            </button>
          </div>
        </form>
      </div>

      {/* Verification Result */}
      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Verification Result</h3>
          
          <div className={`p-4 rounded-lg border ${result.isValid ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center">
                {result.isValid ? (
                  <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-600 mr-3" />
                )}
                <div>
                  <p className="font-medium text-gray-900">{result.email}</p>
                  <p className="text-sm text-gray-600">{result.status}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  result.isValid 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {result.isValid ? 'Valid' : 'Invalid'}
                </span>
                
                <button
                  onClick={() => copyEmail(result.email)}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Copy Email
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Verification History */}
      {verificationHistory.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Verifications</h3>
          
          <div className="space-y-3">
            {verificationHistory.map((verification, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  {verification.isValid ? (
                    <CheckCircle className="w-4 h-4 text-green-600 mr-3" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-600 mr-3" />
                  )}
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{verification.email}</p>
                    <p className="text-xs text-gray-600">{verification.status}</p>
                  </div>
                </div>
                
                <button
                  onClick={() => copyEmail(verification.email)}
                  className="text-blue-600 hover:text-blue-800 text-xs"
                >
                  Copy
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="font-semibold text-blue-900 mb-3">Email Verification Tips</h3>
        <ul className="text-sm text-blue-800 space-y-2">
          <li>• Use the exact spelling of first and last names as they appear professionally</li>
          <li>• Enter the domain without "www" or "https://" (e.g., "company.com")</li>
          <li>• Common email formats are automatically checked (john.doe, j.doe, jdoe, etc.)</li>
          <li>• Verification helps improve email deliverability rates</li>
        </ul>
      </div>
    </div>
  );
};