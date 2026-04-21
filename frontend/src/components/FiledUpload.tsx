import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useData } from '../context/DataContext';

const FileUpload: React.FC = () => {
  const { processedData, setProcessedData, clearProcessedData } = useData();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  // Estado local solo para datos nuevos, si hay en contexto los mostramos
  const [localPreview, setLocalPreview] = useState<any>(null);
  const [hasChanges, setHasChanges] = useState(false);

  // Estado para edición inline
  const [editingCell, setEditingCell] = useState<{ row: number; col: string } | null>(null);
  const [editValue, setEditValue] = useState('');

  // Al montar, solo mostramos datos si vienen del módulo de archivo único
  useEffect(() => {
    if (processedData && processedData.source === 'single') {
      setLocalPreview({
        filename: processedData.filename,
        columns: processedData.columns,
        preview: processedData.preview,
        rows: processedData.transformed_rows || processedData.original_rows,
      });
    }
  }, [processedData]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setHasChanges(false);
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
      setLocalPreview(res.data);

      // Guardar en el contexto para persistencia entre pestañas
      setProcessedData({
        filename: res.data.filename,
        columns: res.data.columns,
        preview: res.data.preview,
        transformed_rows: res.data.rows,
        original_rows: res.data.rows,
        columnTypes: res.data.column_types,
        source: 'single',
      });
    } catch (err) {
      console.error(err);
      alert('Error al subir el archivo');
    } finally {
      setLoading(false);
    }
  };

  // Funciones para edición inline
  const startEditing = (rowIdx: number, col: string, value: any) => {
    setEditingCell({ row: rowIdx, col });
    setEditValue(value?.toString() || '');
  };

  const saveEdit = () => {
    if (!editingCell || !localPreview) return;

    const newPreview = [...localPreview.preview];
    newPreview[editingCell.row] = {
      ...newPreview[editingCell.row],
      [editingCell.col]: editValue
    };

    setLocalPreview({
      ...localPreview,
      preview: newPreview
    });
    setHasChanges(true);
    setEditingCell(null);
  };

  const cancelEdit = () => {
    setEditingCell(null);
    setEditValue('');
  };

  const saveChangesToContext = () => {
    if (!localPreview || !hasChanges) return;

    setProcessedData({
      filename: localPreview.filename,
      columns: localPreview.columns,
      preview: localPreview.preview,
      transformed_rows: localPreview.preview.length,
      original_rows: localPreview.preview.length,
      columnTypes: processedData?.columnTypes || {},
      source: 'single',
    });
    setHasChanges(false);
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

      {localPreview && (
        <div className="mt-6">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold text-lg">Vista previa (editable)</h3>
            <div className="flex items-center gap-3">
              {hasChanges && (
                <button
                  onClick={saveChangesToContext}
                  className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition flex items-center gap-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Guardar cambios
                </button>
              )}
              <button
                onClick={() => {
                  clearProcessedData();
                  setLocalPreview(null);
                  setFile(null);
                  setHasChanges(false);
                }}
                className="text-red-600 hover:text-red-800 text-sm font-medium flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Limpiar datos
              </button>
            </div>
          </div>
          <p className="text-sm text-gray-600 mb-2">
            <strong>Archivo:</strong> {localPreview.filename} | <strong>Filas:</strong> {localPreview.rows}
            {hasChanges && <span className="text-orange-600 ml-2"><strong>(Cambios sin guardar)</strong></span>}
          </p>
          <p className="text-xs text-gray-500 mb-2">💡 Haz clic en cualquier celda para editarla</p>
          <div className="overflow-x-auto">
            <table className="min-w-full border text-sm">
              <thead className="bg-gray-100">
                <tr>
                  {localPreview.columns?.map((col: string) => (
                    <th key={col} className="border px-3 py-2 text-left">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {localPreview.preview?.map((row: any, rowIdx: number) => (
                  <tr key={rowIdx} className="hover:bg-gray-50">
                    {localPreview.columns.map((col: string) => {
                      const isEditing = editingCell?.row === rowIdx && editingCell?.col === col;
                      return (
                        <td key={col} className="border px-2 py-1">
                          {isEditing ? (
                            <div className="flex items-center gap-1">
                              <input
                                type="text"
                                value={editValue}
                                onChange={(e) => setEditValue(e.target.value)}
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') saveEdit();
                                  if (e.key === 'Escape') cancelEdit();
                                }}
                                autoFocus
                                className="w-full px-1 py-0.5 border border-blue-400 rounded text-sm"
                              />
                              <button
                                onClick={saveEdit}
                                className="text-green-600 hover:text-green-800 p-0.5"
                                title="Guardar"
                              >
                                ✓
                              </button>
                              <button
                                onClick={cancelEdit}
                                className="text-red-600 hover:text-red-800 p-0.5"
                                title="Cancelar"
                              >
                                ✕
                              </button>
                            </div>
                          ) : (
                            <div
                              onClick={() => startEditing(rowIdx, col, row[col])}
                              className="cursor-pointer hover:bg-blue-50 px-1 py-0.5 rounded min-h-[24px]"
                              title="Clic para editar"
                            >
                              {row[col]}
                            </div>
                          )}
                        </td>
                      );
                    })}
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