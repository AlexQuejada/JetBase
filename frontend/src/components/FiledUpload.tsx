import React, { useState } from 'react';
import axios from 'axios';

const FileUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

const handleUpload = async () => {
  if (!file) return;

  setLoading(true);
  const formData = new FormData();
  formData.append('file', file);

  // Elegir el endpoint según el tipo de archivo
  let endpoint = '';
  if (file.name.endsWith('.csv')) {
    endpoint = 'http://localhost:8000/api/v1/data/upload/csv';
  } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
    endpoint = 'http://localhost:8000/api/v1/data/upload/excel';
  } else {
    alert('Formato no soportado. Use CSV o Excel');
    setLoading(false);
    return;
  }

  try {
    const res = await axios.post(endpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    setPreview(res.data);
    console.log('Archivo subido:', res.data);
  } catch (err) {
    console.error('Error al subir:', err);
    alert('Error al subir el archivo');
  } finally {
    setLoading(false);
  }
};

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2>Subir Archivo</h2>
      <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? 'Subiendo...' : 'Subir y procesar'}
      </button>

      {preview && (
        <div style={{ marginTop: '20px' }}>
          <h3>Vista previa</h3>
          <p><strong>Archivo:</strong> {preview.filename}</p>
          <p><strong>Filas:</strong> {preview.rows}</p>
          <p><strong>Columnas:</strong> {preview.columns.join(', ')}</p>
          
          <h4>Primeras filas:</h4>
          <table style={{ borderCollapse: 'collapse', width: '100%' }}>
            <thead>
              <tr>
                {preview.columns.map((col: string) => (
                  <th key={col} style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview.preview.slice(0, 5).map((row: any, idx: number) => (
                <tr key={idx}>
                  {preview.columns.map((col: string) => (
                    <td key={col} style={{ border: '1px solid #ddd', padding: '8px' }}>
                      {row[col]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default FileUpload;