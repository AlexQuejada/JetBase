import React from 'react';
import { RowContextMenuState, ColumnContextMenuState } from '../types';
import { Plus, Trash2, Pencil, Tag } from 'lucide-react';

interface RowContextMenuProps {
  contextMenu: RowContextMenuState;
  onAddRow: (position: 'above' | 'below') => void;
  onDeleteRow: () => void;
  onEditRowName: (rowIdx: number) => void;
}

export const RowContextMenu: React.FC<RowContextMenuProps> = ({
  contextMenu,
  onAddRow,
  onDeleteRow,
  onEditRowName,
}) => {
  if (!contextMenu.visible) return null;

  return (
    <div
      className="fixed bg-white border border-gray-200 shadow-lg rounded-md py-1 z-50 min-w-[180px]"
      style={{ top: contextMenu.y, left: contextMenu.x }}
    >
      <div className="px-3 py-1 text-xs text-gray-500 border-b border-gray-100">
        Fila {contextMenu.rowIdx !== null ? contextMenu.rowIdx + 1 : ''}
      </div>
      <button
        onClick={() => onAddRow('above')}
        className="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm flex items-center gap-2"
      >
        <Plus className="w-4 h-4" /> Insertar fila arriba
      </button>
      <button
        onClick={() => onAddRow('below')}
        className="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm flex items-center gap-2"
      >
        <Plus className="w-4 h-4" /> Insertar fila abajo
      </button>
      <button
        onClick={() => onEditRowName(contextMenu.rowIdx!)}
        className="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm flex items-center gap-2"
      >
        <Tag className="w-4 h-4" /> Editar nombre de fila
      </button>
      <div className="border-t border-gray-100 my-1"></div>
      <button
        onClick={onDeleteRow}
        className="w-full text-left px-3 py-2 hover:bg-red-50 text-sm text-red-600 flex items-center gap-2"
      >
        <Trash2 className="w-4 h-4" /> Eliminar fila
      </button>
    </div>
  );
};

interface ColumnContextMenuProps {
  columnContextMenu: ColumnContextMenuState;
  onAddColumn: (position: 'left' | 'right') => void;
  onDeleteColumn: () => void;
  onRenameColumn: (colIdx: number) => void;
}

export const ColumnContextMenu: React.FC<ColumnContextMenuProps> = ({
  columnContextMenu,
  onAddColumn,
  onDeleteColumn,
  onRenameColumn,
}) => {
  if (!columnContextMenu.visible) return null;

  const isRowNameCol = columnContextMenu.colName === '_row_name';

  return (
    <div
      className="fixed bg-white border border-gray-200 shadow-lg rounded-md py-1 z-50 min-w-[180px]"
      style={{ top: columnContextMenu.y, left: columnContextMenu.x }}
    >
      <div className="px-3 py-1 text-xs text-gray-500 border-b border-gray-100 truncate max-w-[250px]">
        Columna "{columnContextMenu.colName}"
      </div>
      <button
        onClick={() => onAddColumn('left')}
        className="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm flex items-center gap-2"
      >
        <Plus className="w-4 h-4" /> Insertar columna izquierda
      </button>
      <button
        onClick={() => onAddColumn('right')}
        className="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm flex items-center gap-2"
      >
        <Plus className="w-4 h-4" /> Insertar columna derecha
      </button>
      <button
        onClick={() => onRenameColumn(columnContextMenu.colIdx!)}
        className="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm flex items-center gap-2"
      >
        <Pencil className="w-4 h-4" /> Renombrar columna
      </button>
      <div className="border-t border-gray-100 my-1"></div>
      <button
        onClick={onDeleteColumn}
        disabled={isRowNameCol}
        className="w-full text-left px-3 py-2 hover:bg-red-50 text-sm text-red-600 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Trash2 className="w-4 h-4" /> Eliminar columna
      </button>
    </div>
  );
};
