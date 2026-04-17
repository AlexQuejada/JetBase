import React from 'react';
import FileUpload from './components/FiledUpload';


function App() {
  return (
    <div className="App">
      <header style={{ textAlign: 'center', padding: '20px', background: '#282c34', color: 'white' }}>
        <h1>🚀 JetBase</h1>
        <p>Plataforma de transformación y visualización de datos</p>
      </header>
      <main style={{ padding: '20px' }}>
        <FileUpload />
      </main>
    </div>
  );
}

export default App;


