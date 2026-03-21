import { useState } from 'react';
import './App.css';
import ExecutionHistory from './style/ExecutionHistory.jsx';
import FloatingLines from './style/FloatingLines.jsx';
import Header from './style/Header.jsx';
import HomePage from './style/HomePage.jsx';
import TestRunner from './style/TestRunner.jsx';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const handleNavigate = (page) => {
    setCurrentPage(page);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage />;
      case 'runner':
        return <TestRunner />;
      case 'history':
        return <ExecutionHistory />;
      default:
        return <HomePage />;
    }
  };

  return (
    <>
      {/* Full-viewport background canvas */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: 0,
        background: '#0a0a0f',
      }}>
        <FloatingLines
          enabledWaves={['top', 'middle', 'bottom']}
          lineCount={5}
          lineDistance={5}
          bendRadius={5}
          bendStrength={-0.5}
          interactive={true}
          parallax={true}
        />
      </div>

      {/* Header — sits above the canvas */}
      <Header currentPage={currentPage} onNavigate={handleNavigate} />

      {/* Page content sits above the background */}
      <div style={{ position: 'relative', zIndex: 1, paddingTop: '80px' }}>
        {renderPage()}
      </div>
    </>
  );
}

export default App;
