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
      const res = await axios.post(endpoint, formData);
      setPreview(res.data);
    } catch (err) {
      console.error(err);
      alert('Error al subir el archivo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="12" y1="18" x2="12" y2="12" />
          <line x1="9" y1="15" x2="15" y2="15" />
        </svg>
        Subir archivo
      </h2>
      <div className="mb-4">
        <input
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
      </div>
      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition disabled:opacity-50"
      >
        {loading ? 'Subiendo...' : 'Subir y procesar'}
      </button>

      {preview && (
        <div className="mt-6">
          <h3 className="font-semibold text-lg mb-2">Vista previa</h3>
          <p className="text-sm text-gray-600 mb-2">
            <strong>Archivo:</strong> {preview.filename} | <strong>Filas:</strong> {preview.rows}
          </p>
          <div className="overflow-x-auto">
            <table className="min-w-full border text-sm">
              <thead className="bg-gray-100">
                <tr>
                  {preview.columns?.map((col: string) => (
                    <th key={col} className="border px-3 py-2 text-left">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.preview?.map((row: any, idx: number) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    {preview.columns.map((col: string) => (
                      <td key={col} className="border px-3 py-2">{row[col]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;