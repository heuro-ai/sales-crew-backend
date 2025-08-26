import React, { useState, useCallback } from 'react';
import { Search, Filter, Sparkles, Target, Users, MapPin } from 'lucide-react';
import { SearchFilters, AIInsight } from '../types';
import { toast } from 'react-hot-toast';

interface LeadFinderProps {
  onSearch: (query: string, filters?: SearchFilters) => void;
  onAIAssist: (query: string) => void;
  loading: boolean;
  aiInsights?: AIInsight[];
}

export const LeadFinder: React.FC<LeadFinderProps> = ({
  onSearch,
  onAIAssist,
  loading,
  aiInsights = []
}) => {
  const [query, setQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({});

  const handleSearch = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }
    onSearch(query, filters);
  }, [query, filters, onSearch]);

  const handleAIAssist = useCallback(() => {
    if (!query.trim()) {
      toast.error('Enter a query first for AI assistance');
      return;
    }
    onAIAssist(query);
  }, [query, onAIAssist]);

  const clearFilters = () => {
    setFilters({});
    setShowFilters(false);
  };

  const industryOptions = [
    'Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail',
    'Education', 'Real Estate', 'Consulting', 'Marketing', 'SaaS'
  ];

  const companySizeOptions = [
    '1-10', '11-50', '51-200', '201-500', '501-1000', '1001-5000', '5000+'
  ];

  const positionLevelOptions = [
    'C-Level', 'VP', 'Director', 'Manager', 'Senior', 'Lead', 'Individual Contributor'
  ];

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-xl">
            <Target className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Lead Finder</h2>
            <p className="text-sm text-gray-600">Discover high-quality prospects with AI precision</p>
          </div>
        </div>
        
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`p-2 rounded-lg transition-colors ${
            showFilters ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
          } hover:bg-blue-50`}
        >
          <Filter className="w-5 h-5" />
        </button>
      </div>

      {/* AI Insights */}
      {aiInsights.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
            <Sparkles className="w-4 h-4 mr-2 text-purple-600" />
            AI Insights
          </h3>
          <div className="space-y-2">
            {aiInsights.slice(0, 2).map((insight, index) => (
              <div key={index} className={`p-3 rounded-lg text-sm ${
                insight.type === 'suggestion' ? 'bg-blue-50 border border-blue-200' :
                insight.type === 'warning' ? 'bg-yellow-50 border border-yellow-200' :
                'bg-green-50 border border-green-200'
              }`}>
                <div className="flex items-center justify-between">
                  <span className="font-medium">{insight.title}</span>
                  <span className="text-xs text-gray-500">{insight.confidence}% confidence</span>
                </div>
                <p className="text-gray-600 mt-1">{insight.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Search Form */}
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for leads: 'VP of Sales at SaaS companies in San Francisco'"
            className="w-full pl-12 pr-32 py-4 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors text-gray-900 placeholder-gray-500"
          />
          <button
            type="button"
            onClick={handleAIAssist}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center text-sm font-medium"
          >
            <Sparkles className="w-4 h-4 mr-1" />
            AI Assist
          </button>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="bg-gray-50 rounded-xl p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">Advanced Filters</h3>
              <button
                type="button"
                onClick={clearFilters}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Clear all
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Industry</label>
                <select
                  value={filters.industry || ''}
                  onChange={(e) => setFilters({ ...filters, industry: e.target.value || undefined })}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Any industry</option>
                  {industryOptions.map(industry => (
                    <option key={industry} value={industry}>{industry}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Company Size</label>
                <select
                  value={filters.company_size || ''}
                  onChange={(e) => setFilters({ ...filters, company_size: e.target.value || undefined })}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Any size</option>
                  {companySizeOptions.map(size => (
                    <option key={size} value={size}>{size} employees</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Position Level</label>
                <select
                  value={filters.position_level || ''}
                  onChange={(e) => setFilters({ ...filters, position_level: e.target.value || undefined })}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Any level</option>
                  {positionLevelOptions.map(level => (
                    <option key={level} value={level}>{level}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPin className="w-4 h-4 inline mr-1" />
                  Location
                </label>
                <input
                  type="text"
                  value={filters.location || ''}
                  onChange={(e) => setFilters({ ...filters, location: e.target.value || undefined })}
                  placeholder="e.g., San Francisco"
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
              Finding Perfect Leads...
            </div>
          ) : (
            <div className="flex items-center justify-center">
              <Users className="w-5 h-5 mr-2" />
              Discover Leads
            </div>
          )}
        </button>
      </form>

      {/* Quick Search Suggestions */}
      <div className="mt-4">
        <p className="text-xs text-gray-500 mb-2">Quick searches:</p>
        <div className="flex flex-wrap gap-2">
          {[
            'CEO at tech startups',
            'VP Sales at SaaS companies',
            'Marketing Director at B2B',
            'CTO at AI companies'
          ].map((suggestion, index) => (
            <button
              key={index}
              onClick={() => setQuery(suggestion)}
              className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full hover:bg-gray-200 transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};