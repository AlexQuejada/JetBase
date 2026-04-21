import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useData } from '../context/DataContext';

const FileMerge: React.FC = () => {
    const { processedData, setProcessedData, clearProcessedData } = useData();
    const [files, setFiles] = useState<FileList | null>(null);
    const [preview, setPreview] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [operation, setOperation] = useState('clean');
    const [keyColumns, setKeyColumns] = useState('');
    const [fillValue, setFillValue] = useState('');
    const [caseSensitive, setCaseSensitive] = useState(false);
    const [normalizeAccents, setNormalizeAccents] = useState(true);
    const [normalizeWhitespace, setNormalizeWhitespace] = useState(true);
    const [keep, setKeep] = useState('first');
    const [downloadFormat, setDownloadFormat] = useState('csv');
    const [hasChanges, setHasChanges] = useState(false);

    // Estado para edición inline
    const [editingCell, setEditingCell] = useState<{ row: number; col: string } | null>(null);
    const [editValue, setEditValue] = useState('');

    // Al montar, solo mostramos datos si vienen del módulo de merge
    useEffect(() => {
        if (processedData && processedData.source === 'merge') {
            setPreview({
                files_processed: processedData.filename.split(',').length,
                original_rows: processedData.original_rows,
                transformed_rows: processedData.transformed_rows,
                columns: processedData.columns,
                preview: processedData.preview,
                message: 'Datos cargados desde sesión anterior',
            });
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFiles(e.target.files);
        }
    };

    // Funciones para edición inline
    const startEditing = (rowIdx: number, col: string, value: any) => {
        setEditingCell({ row: rowIdx, col });
        setEditValue(value?.toString() || '');
    };

    const saveEdit = () => {
        if (!editingCell || !preview) return;

        const newPreview = [...preview.preview];
        newPreview[editingCell.row] = {
            ...newPreview[editingCell.row],
            [editingCell.col]: editValue
        };

        setPreview({
            ...preview,
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
        if (!preview || !hasChanges) return;

        setProcessedData({
            filename: preview.files.map((f: any) => f.filename).join(', '),
            columns: preview.columns,
            preview: preview.preview,
            transformed_rows: preview.preview.length,
            original_rows: preview.original_rows,
            columnTypes: processedData?.columnTypes || {},
            source: 'merge',
        });
        setHasChanges(false);
    };

    const handleMerge = async () => {
        if (!files || files.length < 2) {
            alert('Selecciona al menos 2 archivos para combinar');
            return;
        }

        setLoading(true);
        const formData = new FormData();

        // Agregar todos los archivos
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        // Agregar parámetros
        console.log('>>> DEBUG: operation =', operation);
        console.log('>>> DEBUG: keyColumns =', keyColumns);
        console.log('>>> DEBUG: keep =', keep);
        formData.append('operation', operation);
        if (fillValue) formData.append('fill_value', fillValue);
        if (keyColumns) formData.append('key_columns', keyColumns);
        formData.append('case_sensitive', String(caseSensitive));
        formData.append('normalize_accents', String(normalizeAccents));
        formData.append('normalize_whitespace', String(normalizeWhitespace));
        formData.append('keep', keep);
        formData.append('merge_mode', 'union');

        try {
            const res = await axios.post('http://localhost:8000/api/v1/data/merge', formData);
            setPreview(res.data);
            console.log('Archivos combinados:', res.data);

            // Guardar datos procesados en el contexto para el dashboard
            setProcessedData({
                filename: res.data.files.map((f: any) => f.filename).join(', '),
                columns: res.data.columns,
                preview: res.data.preview,
                transformed_rows: res.data.transformed_rows,
                original_rows: res.data.original_rows,
                columnTypes: Object.fromEntries(
                    res.data.columns.map((col: string) => [col, 'unknown'])
                ),
                source: 'merge',
            });
        } catch (err) {
            console.error('Error al combinar:', err);
            alert('Error al combinar los archivos');
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = async () => {
        if (!files || files.length < 2) {
            alert('Selecciona al menos 2 archivos');
            return;
        }

        setLoading(true);
        const formData = new FormData();

        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        formData.append('operation', operation);
        if (fillValue) formData.append('fill_value', fillValue);
        if (keyColumns) formData.append('key_columns', keyColumns);
        formData.append('case_sensitive', String(caseSensitive));
        formData.append('normalize_accents', String(normalizeAccents));
        formData.append('normalize_whitespace', String(normalizeWhitespace));
        formData.append('keep', keep);
        formData.append('merge_mode', 'union');
        formData.append('download_format', downloadFormat);

        try {
            const res = await axios.post('http://localhost:8000/api/v1/data/merge/download', formData, {
                responseType: 'blob'
            });

            // Crear link de descarga
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            const contentDisposition = res.headers['content-disposition'];
            const filename = contentDisposition?.split('filename=')[1]?.replace(/"/g, '') || `merged.${downloadFormat === 'excel' ? 'xlsx' : 'csv'}`;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Error al descargar:', err);
            alert('Error al descargar el archivo');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">🔗 Combinar múltiples archivos</h2>

            {/* Selector de archivos */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Selecciona archivos (CSV o Excel)
                </label>
                <input
                    type="file"
                    multiple
                    accept=".csv,.xlsx,.xls"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                {files && (
                    <p className="text-sm text-gray-500 mt-1">
                        {files.length} archivo(s) seleccionado(s)
                    </p>
                )}
            </div>

            {/* Parámetros de limpieza */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Operación</label>
                    <select
                        value={operation}
                        onChange={(e) => setOperation(e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                        <option value="clean">Solo limpiar (normalizar)</option>
                        <option value="dropna">Eliminar nulos</option>
                        <option value="fillna">Rellenar nulos</option>
                        <option value="drop_duplicates">Eliminar duplicados</option>
                    </select>
                </div>

                {operation === 'fillna' && (
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Valor para rellenar</label>
                        <input
                            type="text"
                            value={fillValue}
                            onChange={(e) => setFillValue(e.target.value)}
                            placeholder="Ej: DESCONOCIDO"
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        />
                    </div>
                )}

                {operation === 'drop_duplicates' && (
                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Columnas clave (separadas por coma)
                        </label>
                        <input
                            type="text"
                            value={keyColumns}
                            onChange={(e) => setKeyColumns(e.target.value)}
                            placeholder="Ej: email,cliente_id"
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        />
                    </div>
                )}

                {operation === 'drop_duplicates' && (
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Conservar</label>
                        <select
                            value={keep}
                            onChange={(e) => setKeep(e.target.value)}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        >
                            <option value="first">Primera ocurrencia</option>
                            <option value="last">Última ocurrencia</option>
                            <option value="false">Eliminar todas</option>
                        </select>
                    </div>
                )}
            </div>

            {/* Opciones de normalización */}
            <div className="flex flex-wrap gap-4 mb-4">
                <label className="flex items-center gap-2">
                    <input
                        type="checkbox"
                        checked={!caseSensitive}
                        onChange={(e) => setCaseSensitive(!e.target.checked)}
                        className="rounded border-gray-300"
                    />
                    <span className="text-sm">Ignorar mayúsculas/minúsculas</span>
                </label>
                <label className="flex items-center gap-2">
                    <input
                        type="checkbox"
                        checked={normalizeAccents}
                        onChange={(e) => setNormalizeAccents(e.target.checked)}
                        className="rounded border-gray-300"
                    />
                    <span className="text-sm">Normalizar acentos (é → e)</span>
                </label>
                <label className="flex items-center gap-2">
                    <input
                        type="checkbox"
                        checked={normalizeWhitespace}
                        onChange={(e) => setNormalizeWhitespace(e.target.checked)}
                        className="rounded border-gray-300"
                    />
                    <span className="text-sm">Normalizar espacios</span>
                </label>
            </div>

            {/* Botón de acción */}
            <button
                onClick={handleMerge}
                disabled={!files || files.length < 2 || loading}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition disabled:opacity-50"
            >
                {loading ? 'Combinando...' : 'Combinar archivos'}
            </button>

            {/* Resultado */}
            {preview && (
                <div className="mt-6">
                    <div className="flex flex-wrap items-center justify-between mb-4">
                        <h3 className="font-semibold text-lg">Resultado combinado (editable)</h3>
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
                                    setPreview(null);
                                    setFiles(null);
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
                    <div className="flex flex-wrap items-center justify-between mb-4">
                        <div className="flex gap-2 items-center">
                            <select
                                value={downloadFormat}
                                onChange={(e) => setDownloadFormat(e.target.value)}
                                className="text-sm rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            >
                                <option value="csv">CSV</option>
                                <option value="excel">Excel</option>
                            </select>
                            <button
                                onClick={handleDownload}
                                disabled={loading}
                                className="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700 transition disabled:opacity-50"
                            >
                                {loading ? 'Descargando...' : 'Descargar archivo'}
                            </button>
                        </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                        <strong>Archivos procesados:</strong> {preview.files_processed} |
                        <strong> Filas originales:</strong> {preview.original_rows} |
                        <strong> Filas finales:</strong> {preview.transformed_rows}
                        {hasChanges && <span className="text-orange-600 ml-2"><strong>(Cambios sin guardar)</strong></span>}
                    </p>
                    <p className="text-sm text-green-600 mb-2">{preview.message}</p>
                    <p className="text-xs text-gray-500 mb-2">💡 Haz clic en cualquier celda para editarla</p>
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
                                {preview.preview?.map((row: any, rowIdx: number) => (
                                    <tr key={rowIdx} className="hover:bg-gray-50">
                                        {preview.columns.map((col: string) => {
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
                        {preview.transformed_rows > preview.preview?.length && (
                            <p className="text-sm text-gray-500 mt-2">
                                Mostrando {preview.preview?.length} de {preview.transformed_rows} filas
                            </p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default FileMerge;