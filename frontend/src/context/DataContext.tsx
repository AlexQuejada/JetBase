import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface ProcessedData {
  filename: string;
  columns: string[];
  preview: any[];
  transformed_rows: number;
  original_rows: number;
  columnTypes?: Record<string, string>;
  rawData?: string; // CSV content para re-procesar si es necesario
}

interface DataContextType {
  processedData: ProcessedData | null;
  setProcessedData: (data: ProcessedData | null) => void;
  clearProcessedData: () => void;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const DataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [processedData, setProcessedData] = useState<ProcessedData | null>(null);

  const clearProcessedData = () => {
    setProcessedData(null);
  };

  return (
    <DataContext.Provider value={{ processedData, setProcessedData, clearProcessedData }}>
      {children}
    </DataContext.Provider>
  );
};

export const useData = (): DataContextType => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useData debe usarse dentro de un DataProvider');
  }
  return context;
};
