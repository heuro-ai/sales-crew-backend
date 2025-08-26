import React, { useState } from 'react';
import { Search, Building2, ExternalLink, Loader, AlertCircle } from 'lucide-react';
import { SearchResult } from '../types';
import { apiService } from '../services/api';
import { toast } from 'react-hot-toast';

export const CompanySearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [limit, setLimit] = useState(5);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setLoading(true);
    try {
      const searchResults = await apiService.searchCompanies(query, limit);
      setResults(searchResults);
      toast.success(`Found ${searchResults.length} results`);
      
      // Update dashboard stats
      const stats = JSON.parse(localStorage.getItem('dashboardStats') || '{}');
      stats.totalSearches = (stats.totalSearches || 0) + 1;
      localStorage.setItem('dashboardStats', JSON.stringify(stats));
    } catch (error) {
      console.error('Search failed:', error);
      toast.error(error instanceof Error ? error.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const predefinedQueries = [
    'CEO at tech startups site:linkedin.com',
    'VP Sales at SaaS companies site:linkedin.com',
    'CTO at AI companies site:linkedin.com',
    'Marketing Director at B2B companies site:linkedin.com',
    'Head of Growth at fintech site:linkedin.com'
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Company & People Search</h1>
        <p className="text-gray-600">Find decision makers at target companies using AI-powered search</p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center mb-4">
          <Building2 className="w-5 h-5 text-blue-600 mr-2" />
          <h2 className="text-lg font-semibold text-gray-900">Search Parameters</h2>
        </div>

        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                id="query"
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., VP Sales at SaaS companies site:linkedin.com"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-2">
              Number of Results
            </label>
            <select
              id="limit"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={5}>5 results</option>
              <option value={10}>10 results</option>
              <option value={15}>15 results</option>
              <option value={20}>20 results</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <Loader className="animate-spin w-4 h-4 mr-2" />
                Searching...
              </div>
            ) : (
              'Search Companies'
            )}
          </button>
        </form>

        {/* Predefined Queries */}
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Search Templates:</h3>
          <div className="flex flex-wrap gap-2">
            {predefinedQueries.map((predefined, index) => (
              <button
                key={index}
                onClick={() => setQuery(predefined)}
                className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full hover:bg-gray-200 transition-colors"
              >
                {predefined}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Search Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Search Results ({results.length})
            </h3>
          </div>
          
          <div className="divide-y divide-gray-100">
            {results.map((result, index) => (
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
                
                <div className="flex items-center text-xs text-gray-500">
                  <span className="bg-gray-100 px-2 py-1 rounded">
                    {new URL(result.link).hostname}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Results */}
      {!loading && results.length === 0 && query && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
          <p className="text-gray-600">
            Try adjusting your search query or using different keywords.
          </p>
        </div>
      )}
    </div>
  );
};