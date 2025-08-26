import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { Bot, Sparkles } from 'lucide-react';
import { SearchForm } from './components/SearchForm';
import { SearchResults } from './components/SearchResults';
import { EmailGenerator } from './components/EmailGenerator';
import { apiService } from './services/api';
import { SearchResult, EmailVerification, CompanyAnalysis, GeneratedEmail } from './types';
import { toast } from 'react-hot-toast';

function App() {
  // State for search results
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [emailVerification, setEmailVerification] = useState<EmailVerification | null>(null);
  const [companyAnalysis, setCompanyAnalysis] = useState<CompanyAnalysis | null>(null);
  const [generatedEmail, setGeneratedEmail] = useState<GeneratedEmail | null>(null);

  // Loading states
  const [loading, setLoading] = useState({
    search: false,
    email: false,
    analysis: false,
    generation: false
  });

  const handleCompanySearch = async (query: string) => {
    setLoading(prev => ({ ...prev, search: true }));
    try {
      const results = await apiService.searchCompanies(query, 5);
      setSearchResults(results);
      toast.success(`Found ${results.length} results`);
    } catch (error) {
      toast.error('Failed to search companies');
      console.error('Search error:', error);
    } finally {
      setLoading(prev => ({ ...prev, search: false }));
    }
  };

  const handleEmailVerification = async (firstName: string, lastName: string, domain: string) => {
    setLoading(prev => ({ ...prev, email: true }));
    try {
      const verification = await apiService.verifyEmail(firstName, lastName, domain);
      setEmailVerification(verification);
      toast.success(verification.isValid ? 'Email verified!' : 'Email could not be verified');
    } catch (error) {
      toast.error('Failed to verify email');
      console.error('Email verification error:', error);
    } finally {
      setLoading(prev => ({ ...prev, email: false }));
    }
  };

  const handleCompanyAnalysis = async (companyName: string, personName: string, position: string) => {
    setLoading(prev => ({ ...prev, analysis: true }));
    try {
      const analysis = await apiService.getCompanyAnalysis(companyName, personName, position, 'AI-powered solutions');
      setCompanyAnalysis(analysis);
      toast.success('Company analysis complete!');
    } catch (error) {
      toast.error('Failed to analyze company');
      console.error('Analysis error:', error);
    } finally {
      setLoading(prev => ({ ...prev, analysis: false }));
    }
  };

  const handleEmailGeneration = async (
    companyName: string,
    decisionMaker: string,
    position: string,
    situation: string,
    productDescription: string
  ) => {
    setLoading(prev => ({ ...prev, generation: true }));
    try {
      const email = await apiService.generateEmail(
        companyName,
        decisionMaker,
        position,
        situation,
        productDescription,
        companyAnalysis || undefined
      );
      setGeneratedEmail(email);
      toast.success('Email generated successfully!');
    } catch (error) {
      toast.error('Failed to generate email');
      console.error('Email generation error:', error);
    } finally {
      setLoading(prev => ({ ...prev, generation: false }));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-2 rounded-lg">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Sales AI Agent</h1>
                <p className="text-sm text-gray-600">Find prospects, verify emails, and generate personalized outreach</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Sparkles className="w-4 h-4" />
              <span>Powered by AI</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Input Forms */}
          <div className="space-y-6">
            <SearchForm
              onCompanySearch={handleCompanySearch}
              onEmailVerification={handleEmailVerification}
              loading={{
                search: loading.search,
                email: loading.email
              }}
            />
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            <SearchResults
              searchResults={searchResults}
              emailVerification={emailVerification}
              onAnalyzeCompany={handleCompanyAnalysis}
              loading={{
                analysis: loading.analysis
              }}
            />
          </div>
        </div>

        {/* Email Generation Section - Full Width */}
        <div className="mt-8">
          <EmailGenerator
            analysis={companyAnalysis}
            generatedEmail={generatedEmail}
            onGenerateEmail={handleEmailGeneration}
            loading={{
              generation: loading.generation
            }}
          />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-500">
            <p className="text-sm">
              Demo application showcasing AI-powered sales intelligence and email generation.
            </p>
            <p className="text-xs mt-2">
              This is a demonstration using mock data and simulated API responses.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;