import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

const STORAGE_KEY = 'flintrex_processed_data';

export interface ProcessedData {
  filename: string;
  columns: string[];
  preview: any[];
  transformed_rows: number;
  original_rows: number;
  columnTypes?: Record<string, string>;
  rawData?: string;
  source?: 'single' | 'merge';
}

interface DataContextType {
  processedData: ProcessedData | null;
  setProcessedData: (data: ProcessedData | null) => void;
  clearProcessedData: () => void;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const DataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [processedData, setProcessedDataState] = useState<ProcessedData | null>(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setProcessedDataState(parsed);
      }
    } catch (err) {
      console.error('Error loading from localStorage:', err);
    }
  }, []);

  const setProcessedData = (data: ProcessedData | null) => {
    setProcessedDataState(data);
    try {
      if (data) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    } catch (err) {
      console.error('Error saving to localStorage:', err);
    }
  };

  const clearProcessedData = () => {
    setProcessedDataState(null);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (err) {
      console.error('Error clearing localStorage:', err);
    }
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
