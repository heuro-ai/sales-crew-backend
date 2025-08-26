import React from 'react';
import { ExternalLink, CheckCircle, XCircle, Mail } from 'lucide-react';
import { SearchResult, EmailVerification } from '../types';

interface SearchResultsProps {
  searchResults: SearchResult[];
  emailVerification: EmailVerification | null;
  onAnalyzeCompany: (companyName: string, personName: string, position: string) => void;
  loading: {
    analysis: boolean;
  };
}

export const SearchResults: React.FC<SearchResultsProps> = ({ 
  searchResults, 
  emailVerification, 
  onAnalyzeCompany,
  loading 
}) => {
  const extractPersonAndCompany = (title: string) => {
    // Simple extraction logic - in reality, this would be more sophisticated
    const match = title.match(/^([^-]+) - ([^-]+) at ([^-]+)/);
    if (match) {
      return {
        person: match[1].trim(),
        position: match[2].trim(),
        company: match[3].trim()
      };
    }
    return {
      person: 'John Doe',
      position: 'Decision Maker',
      company: 'TechCorp'
    };
  };

  if (searchResults.length === 0 && !emailVerification) {
    return (
      <div className="text-center py-12 text-gray-500">
        <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <Mail className="w-8 h-8 text-gray-400" />
        </div>
        <p>Search for companies or verify emails to see results here</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Email Verification Results */}
      {emailVerification && (
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Mail className="w-5 h-5 mr-2 text-blue-600" />
            Email Verification Result
          </h3>
          
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              {emailVerification.isValid ? (
                <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
              ) : (
                <XCircle className="w-5 h-5 text-red-600 mr-3" />
              )}
              <div>
                <p className="font-medium text-gray-900">{emailVerification.email}</p>
                <p className="text-sm text-gray-600">{emailVerification.status}</p>
              </div>
            </div>
            
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              emailVerification.isValid 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {emailVerification.isValid ? 'Valid' : 'Invalid'}
            </span>
          </div>
        </div>
      )}

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100">
          <div className="p-6 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900">
              Search Results ({searchResults.length})
            </h3>
          </div>
          
          <div className="divide-y divide-gray-100">
            {searchResults.map((result, index) => {
              const { person, position, company } = extractPersonAndCompany(result.title);
              
              return (
                <div key={index} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex justify-between items-start mb-3">
                    <h4 className="text-base font-medium text-gray-900 flex items-center">
                      {result.title}
                      <a
                        href={result.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-2 text-blue-600 hover:text-blue-800 transition-colors"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </h4>
                  </div>
                  
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {result.snippet}
                  </p>
                  
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => onAnalyzeCompany(company, person, position)}
                      disabled={loading.analysis}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {loading.analysis ? (
                        <div className="flex items-center">
                          <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-2"></div>
                          Analyzing...
                        </div>
                      ) : (
                        'Analyze Company'
                      )}
                    </button>
                    
                    <span className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg text-xs">
                      {company}
                    </span>
                    <span className="bg-blue-100 text-blue-700 px-3 py-2 rounded-lg text-xs">
                      {position}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};