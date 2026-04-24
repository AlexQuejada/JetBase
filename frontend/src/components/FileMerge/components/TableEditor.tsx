import React from 'react';
import { PreviewData, EditingCell } from '../types';
import { ZoomableTable } from '../../common/ZoomableTable';

interface TableEditorProps {
  preview: PreviewData;
  editingCell: EditingCell | null;
  editValue: string;
  editingColumnName: number | null;
  columnNameValue: string;
  onEditValueChange: (value: string) => void;
  onColumnNameChange: (value: string) => void;
  onStartEditing: (rowIdx: number, col: string, value: any) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  onStartEditingColumnName: (colIdx: number) => void;
  onSaveColumnName: () => void;
  onCancelColumnName: () => void;
  onShowRowContextMenu: (e: React.MouseEvent, rowIdx: number) => void;
  onShowColumnContextMenu: (e: React.MouseEvent, colIdx: number, colName: string) => void;
}

export const TableEditor: React.FC<TableEditorProps> = ({
  preview, editingCell, editValue, editingColumnName, columnNameValue,
  onEditValueChange, onColumnNameChange, onStartEditing, onSaveEdit, onCancelEdit,
  onStartEditingColumnName, onSaveColumnName, onCancelColumnName,
  onShowRowContextMenu, onShowColumnContextMenu,
}) => {
  const visibleColumns = preview.columns.filter((c: string) => c !== '_row_name');

  return (
    <ZoomableTable>
      <table className="min-w-full border text-sm">
        <thead className="bg-gray-100 dark:bg-gray-700">
          <tr>
            {visibleColumns.map((col: string) => {
              const realColIdx = preview.columns.indexOf(col);
              const isEditing = editingColumnName === realColIdx;
              return (
                <th
                  key={col}
                  onContextMenu={(e) => onShowColumnContextMenu(e, realColIdx, col)}
                  className="border px-3 py-2 text-left select-none text-gray-700 dark:text-gray-200"
                >
                  {isEditing ? (
                    <div className="flex items-center gap-1">
                      <input
                        type="text"
                        value={columnNameValue}
                        onChange={(e) => onColumnNameChange(e.target.value)}
                        onKeyDown={(e) => { if (e.key === 'Enter') onSaveColumnName(); if (e.key === 'Escape') onCancelColumnName(); }}
                        autoFocus
                        className="w-full px-1 py-0.5 border border-blue-400 rounded text-sm font-semibold dark:bg-gray-800 dark:text-white"
                      />
                      <button onClick={onSaveColumnName} className="text-green-600 hover:text-green-800 p-0.5">✓</button>
                      <button onClick={onCancelColumnName} className="text-red-600 hover:text-red-800 p-0.5">✕</button>
                    </div>
                  ) : (
                    <div
                      onClick={() => onStartEditingColumnName(realColIdx)}
                      className="cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/50 px-1 py-0.5 rounded min-h-[24px]"
                      title="Clic para renombrar, click derecho para opciones"
                    >
                      {col}
                    </div>
                  )}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {preview.preview?.map((row: any, rowIdx: number) => (
            <tr key={rowIdx} className="hover:bg-gray-50 dark:hover:bg-gray-700/50" onContextMenu={(e) => onShowRowContextMenu(e, rowIdx)}>
              {visibleColumns.map((col: string) => {
                const isEditing = editingCell?.row === rowIdx && editingCell?.col === col;
                return (
                  <td key={col} className="border px-2 py-1 text-gray-600 dark:text-gray-300">
                    {isEditing ? (
                      <div className="flex items-center gap-1">
                        <input
                          type="text"
                          value={editValue}
                          onChange={(e) => onEditValueChange(e.target.value)}
                          onKeyDown={(e) => { if (e.key === 'Enter') onSaveEdit(); if (e.key === 'Escape') onCancelEdit(); }}
                          autoFocus
                          className="w-full px-1 py-0.5 border border-blue-400 rounded text-sm dark:bg-gray-800 dark:text-white"
                        />
                        <button onClick={onSaveEdit} className="text-green-600 hover:text-green-800 p-0.5">✓</button>
                        <button onClick={onCancelEdit} className="text-red-600 hover:text-red-800 p-0.5">✕</button>
                      </div>
                    ) : (
                      <div
                        onClick={() => onStartEditing(rowIdx, col, row[col])}
                        className="cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/50 px-1 py-0.5 rounded min-h-[24px]"
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
    </ZoomableTable>
  );
};
