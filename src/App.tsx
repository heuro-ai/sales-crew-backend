import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { Navigation } from './components/Navigation';
import { Dashboard } from './components/Dashboard';
import { CompanySearch } from './components/CompanySearch';
import { EmailVerification } from './components/EmailVerification';
import { EmailGeneration } from './components/EmailGeneration';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'search':
        return <CompanySearch />;
      case 'verify':
        return <EmailVerification />;
      case 'generate':
        return <EmailGeneration />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster 
        position="top-right" 
        toastOptions={{
          duration: 4000,
          style: {
            background: '#333',
            color: '#fff',
          },
          success: {
            style: {
              background: '#10B981',
            },
          },
          error: {
            style: {
              background: '#EF4444',
            },
          },
        }}
      />
      
      {/* Navigation */}
      <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderCurrentPage()}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Sales AI Agent - Advanced Lead Generation & Email Automation Platform
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Built with FastAPI backend and React frontend • Ready for production deployment
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;