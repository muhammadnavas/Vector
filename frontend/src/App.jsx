import FloatingLines from './style/FloatingLines.jsx';
import Header from './style/Header.jsx';
import HomePage from './style/HomePage.jsx';
import './App.css';

function App() {
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
      <Header />

      {/* Page content sits above the background */}
      <div style={{ position: 'relative', zIndex: 1, paddingTop: '80px' }}>
        <HomePage />
      </div>
    </>
  );
}

export default App;
