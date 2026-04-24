import React from 'react';

interface OperationControlsProps {
  operation: string;
  keyColumns: string;
  fillValue: string;
  keep: string;
  caseSensitive: boolean;
  normalizeAccents: boolean;
  normalizeWhitespace: boolean;
  onOperationChange: (value: string) => void;
  onKeyColumnsChange: (value: string) => void;
  onFillValueChange: (value: string) => void;
  onKeepChange: (value: string) => void;
  onCaseSensitiveChange: (value: boolean) => void;
  onNormalizeAccentsChange: (value: boolean) => void;
  onNormalizeWhitespaceChange: (value: boolean) => void;
}

export const OperationControls: React.FC<OperationControlsProps> = ({
  operation, keyColumns, fillValue, keep, caseSensitive, normalizeAccents, normalizeWhitespace,
  onOperationChange, onKeyColumnsChange, onFillValueChange, onKeepChange,
  onCaseSensitiveChange, onNormalizeAccentsChange, onNormalizeWhitespaceChange,
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">Operación</label>
        <select
          value={operation}
          onChange={(e) => onOperationChange(e.target.value)}
          className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 dark:text-white text-gray-700 shadow-sm focus:border-blue-500 focus:ring-blue-500 focus:ring-offset-0 dark:focus:ring-blue-500 dark:focus:border-blue-500 px-2 py-1.5"
        >
          <option value="clean">Solo limpiar (normalizar)</option>
          <option value="dropna">Eliminar nulos</option>
          <option value="fillna">Rellenar nulos</option>
          <option value="drop_duplicates">Eliminar duplicados</option>
        </select>
      </div>

      {operation === 'fillna' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">Valor para rellenar</label>
          <input
            type="text"
            value={fillValue}
            onChange={(e) => onFillValueChange(e.target.value)}
            placeholder="Ej: DESCONOCIDO"
            className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 dark:text-white text-gray-700 shadow-sm focus:border-blue-500 focus:ring-blue-500 focus:ring-offset-0 dark:focus:ring-blue-500 dark:focus:border-blue-500 px-2 py-1.5"
          />
        </div>
      )}

      {operation === 'drop_duplicates' && (
        <>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">Columnas clave (separadas por coma)</label>
            <input
              type="text"
              value={keyColumns}
              onChange={(e) => onKeyColumnsChange(e.target.value)}
              placeholder="Ej: email,cliente_id"
              className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 dark:text-white text-gray-700 shadow-sm focus:border-blue-500 focus:ring-blue-500 focus:ring-offset-0 dark:focus:ring-blue-500 dark:focus:border-blue-500 px-2 py-1.5"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">Conservar</label>
            <select
              value={keep}
              onChange={(e) => onKeepChange(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 dark:text-white text-gray-700 shadow-sm focus:border-blue-500 focus:ring-blue-500 focus:ring-offset-0 dark:focus:ring-blue-500 dark:focus:border-blue-500 px-2 py-1.5"
            >
              <option value="first">Primera ocurrencia</option>
              <option value="last">Última ocurrencia</option>
              <option value="false">Eliminar todas</option>
            </select>
          </div>
        </>
      )}
    </div>
  );
};

interface NormalizationOptionsProps {
  caseSensitive: boolean;
  normalizeAccents: boolean;
  normalizeWhitespace: boolean;
  onCaseSensitiveChange: (value: boolean) => void;
  onNormalizeAccentsChange: (value: boolean) => void;
  onNormalizeWhitespaceChange: (value: boolean) => void;
}

export const NormalizationOptions: React.FC<NormalizationOptionsProps> = ({
  caseSensitive, normalizeAccents, normalizeWhitespace,
  onCaseSensitiveChange, onNormalizeAccentsChange, onNormalizeWhitespaceChange,
}) => {
  return (
    <div className="flex flex-wrap gap-4 mb-4">
      <label className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={!caseSensitive}
          onChange={(e) => onCaseSensitiveChange(!e.target.checked)}
          className="rounded border-gray-300 dark:border-gray-600"
        />
        <span className="text-sm text-gray-700 dark:text-gray-200">Ignorar mayúsculas/minúsculas</span>
      </label>
      <label className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={normalizeAccents}
          onChange={(e) => onNormalizeAccentsChange(e.target.checked)}
          className="rounded border-gray-300 dark:border-gray-600"
        />
        <span className="text-sm text-gray-700 dark:text-gray-200">Normalizar acentos (é → e)</span>
      </label>
      <label className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={normalizeWhitespace}
          onChange={(e) => onNormalizeWhitespaceChange(e.target.checked)}
          className="rounded border-gray-300 dark:border-gray-600"
        />
        <span className="text-sm text-gray-700 dark:text-gray-200">Normalizar espacios</span>
      </label>
    </div>
  );
};
