import React from 'react';
import { useFileUpload } from './hooks/useFileUpload';
import { TableEditor } from './components/TableEditor';
import { RowContextMenu, ColumnContextMenu } from './components/ContextMenus';
import { Lightbulb } from 'lucide-react';

const FileUpload: React.FC = () => {
  const {
    file,
    loading,
    localPreview,
    hasChanges,
    editingCell,
    editValue,
    contextMenu,
    columnContextMenu,
    editingColumnName,
    columnNameValue,
    setEditValue,
    setColumnNameValue,
    handleFileChange,
    handleUpload,
    startEditing,
    saveEdit,
    cancelEdit,
    showContextMenu,
    showColumnContextMenu,
    addRow,
    deleteRow,
    startEditingRowName,
    saveRowName,
    cancelRowNameEdit,
    addColumn,
    deleteColumn,
    startEditingColumnName,
    saveColumnName,
    cancelColumnNameEdit,
    saveChangesToContext,
    clearData,
  } = useFileUpload();

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-gray-900 dark:text-white">
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
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 dark:file:bg-blue-900/50 file:text-blue-700 dark:file:text-blue-300 hover:file:bg-blue-100"
        />
      </div>

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition disabled:opacity-50 btn-relief"
      >
        {loading ? 'Subiendo...' : 'Subir y procesar'}
      </button>

      {localPreview && (
        <div className="mt-6">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold text-lg text-gray-900 dark:text-white">Vista previa (editable)</h3>
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
              <button
                onClick={clearData}
                className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 text-sm font-medium flex items-center gap-1 btn-ghost px-2 py-1 rounded-md"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Limpiar datos
              </button>
            </div>
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            <strong>Archivo:</strong> {localPreview.filename} | <strong>Filas:</strong> {localPreview.rows}
            {hasChanges && <span className="text-orange-600 ml-2"><strong>(Cambios sin guardar)</strong></span>}
          </p>

          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
            <Lightbulb className="w-3 h-3 inline mr-1" /> Haz clic en cualquier celda para editarla | Click derecho en fila/columna para opciones
          </p>

          <TableEditor
            localPreview={localPreview}
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

export default FileUpload;
