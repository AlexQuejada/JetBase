import React from 'react';
import { useFileMerge } from './hooks/useFileMerge';
import { TableEditor } from './components/TableEditor';
import { RowContextMenu, ColumnContextMenu } from './components/ContextMenus';
import { OperationControls, NormalizationOptions } from './components/OperationControls';
import { Lightbulb } from 'lucide-react';

const FileMerge: React.FC = () => {
  const {
    files, preview, loading, hasChanges,
    operation, keyColumns, fillValue, caseSensitive, normalizeAccents, normalizeWhitespace, keep, downloadFormat,
    editingCell, editValue, contextMenu, columnContextMenu, editingColumnName, columnNameValue,
    setOperation, setKeyColumns, setFillValue, setCaseSensitive, setNormalizeAccents, setNormalizeWhitespace, setKeep, setDownloadFormat,
    setEditValue, setColumnNameValue,
    handleFileChange, handleMerge, handleDownload, startEditing, saveEdit, cancelEdit,
    showContextMenu, showColumnContextMenu, addRow, deleteRow, startEditingRowName, saveRowName, cancelRowNameEdit,
    addColumn, deleteColumn, startEditingColumnName, saveColumnName, cancelColumnNameEdit,
    saveChangesToContext, clearData,
  } = useFileMerge();

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Combinar múltiples archivos</h2>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">Selecciona archivos (CSV o Excel)</label>
        <input
          type="file"
          multiple
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 dark:file:bg-blue-900/50 file:text-blue-700 dark:file:text-blue-300 hover:file:bg-blue-100"
        />
        {files && <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{files.length} archivo(s) seleccionado(s)</p>}
      </div>

      <OperationControls
        operation={operation}
        keyColumns={keyColumns}
        fillValue={fillValue}
        keep={keep}
        caseSensitive={caseSensitive}
        normalizeAccents={normalizeAccents}
        normalizeWhitespace={normalizeWhitespace}
        onOperationChange={setOperation}
        onKeyColumnsChange={setKeyColumns}
        onFillValueChange={setFillValue}
        onKeepChange={setKeep}
        onCaseSensitiveChange={setCaseSensitive}
        onNormalizeAccentsChange={setNormalizeAccents}
        onNormalizeWhitespaceChange={setNormalizeWhitespace}
      />

      <NormalizationOptions
        caseSensitive={caseSensitive}
        normalizeAccents={normalizeAccents}
        normalizeWhitespace={normalizeWhitespace}
        onCaseSensitiveChange={setCaseSensitive}
        onNormalizeAccentsChange={setNormalizeAccents}
        onNormalizeWhitespaceChange={setNormalizeWhitespace}
      />

      <button
        onClick={handleMerge}
        disabled={!files || files.length < 2 || loading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition disabled:opacity-50 btn-relief"
      >
        {loading ? 'Combinando...' : 'Combinar archivos'}
      </button>

      {preview && (
        <div className="mt-6">
          <div className="flex flex-wrap items-center justify-between mb-4">
            <h3 className="font-semibold text-lg text-gray-900 dark:text-white">Resultado combinado (editable)</h3>
            <div className="flex items-center gap-3">
              {hasChanges && (
                <button
                  onClick={saveChangesToContext}
                  className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition flex items-center gap-1 btn-relief"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Guardar cambios
                </button>
              )}
                <button onClick={clearData} className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 text-sm font-medium flex items-center gap-1 btn-ghost px-2 py-1 rounded-md">
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
                className="text-sm rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 dark:text-white text-gray-700 shadow-sm focus:border-blue-500 focus:ring-blue-500 focus:ring-offset-0 dark:focus:ring-blue-500 dark:focus:border-blue-500 px-2 py-1.5"
              >
                <option value="csv">CSV</option>
                <option value="excel">Excel</option>
              </select>
              <button
                onClick={handleDownload}
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700 transition disabled:opacity-50 btn-relief"
              >
                {loading ? 'Descargando...' : 'Descargar archivo'}
              </button>
            </div>
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            <strong>Archivos procesados:</strong> {preview.files_processed} |
            <strong> Filas originales:</strong> {preview.original_rows} |
            <strong> Filas finales:</strong> {preview.transformed_rows}
            {hasChanges && <span className="text-orange-600 ml-2"><strong>(Cambios sin guardar)</strong></span>}
          </p>
          <p className="text-sm text-green-600 dark:text-green-400 mb-2">{preview.message}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2"><Lightbulb className="w-3 h-3 inline mr-1" /> Haz clic en cualquier celda para editarla | Click derecho en fila/columna para opciones</p>

          <TableEditor
            preview={preview}
            editingCell={editingCell}
            editValue={editValue}
            editingColumnName={editingColumnName}
            columnNameValue={columnNameValue}
            onEditValueChange={setEditValue}
            onColumnNameChange={setColumnNameValue}
            onStartEditing={startEditing}
            onSaveEdit={saveEdit}
            onCancelEdit={cancelEdit}
            onStartEditingColumnName={startEditingColumnName}
            onSaveColumnName={saveColumnName}
            onCancelColumnName={cancelColumnNameEdit}
            onShowRowContextMenu={showContextMenu}
            onShowColumnContextMenu={showColumnContextMenu}
          />

          <RowContextMenu
            contextMenu={contextMenu}
            onAddRow={addRow}
            onDeleteRow={deleteRow}
            onEditRowName={startEditingRowName}
          />

          <ColumnContextMenu
            columnContextMenu={columnContextMenu}
            onAddColumn={addColumn}
            onDeleteColumn={deleteColumn}
            onRenameColumn={startEditingColumnName}
          />
        </div>
      )}
    </div>
  );
};

export default FileMerge;
