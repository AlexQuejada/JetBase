import React, { useRef, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

const ZOOM_STORAGE_KEY = 'flintrex_table_zoom';

interface ZoomableTableProps {
  children: React.ReactNode;
  minScale?: number;
  maxScale?: number;
  step?: number;
  externalScale?: number;
  onScaleChange?: (scale: number) => void;
}

export const ZoomableTable: React.FC<ZoomableTableProps> = ({
  children,
  minScale = 0.5,
  maxScale = 1.5,
  step = 0.1,
  externalScale,
  onScaleChange,
}) => {
  const { t } = useTranslation();
  const containerRef = useRef<HTMLDivElement>(null);

  // Load initial scale from localStorage or use external, default to 1
  const [internalScale, setInternalScale] = useState(() => {
    try {
      const stored = localStorage.getItem(ZOOM_STORAGE_KEY);
      return stored ? parseFloat(stored) : 1;
    } catch {
      return 1;
    }
  });
  const [hasOverflow, setHasOverflow] = useState(false);

  const scale = externalScale !== undefined ? externalScale : internalScale;

  useEffect(() => {
    const checkOverflow = () => {
      if (containerRef.current) {
        const table = containerRef.current.querySelector('table');
        if (table) {
          setHasOverflow(table.scrollWidth > containerRef.current.clientWidth);
        }
      }
    };

    checkOverflow();
    window.addEventListener('resize', checkOverflow);
    return () => window.removeEventListener('resize', checkOverflow);
  }, [children]);

  // Persist scale to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(ZOOM_STORAGE_KEY, scale.toString());
    } catch {
      // Ignore storage errors
    }
    onScaleChange?.(scale);
  }, [scale, onScaleChange]);

  const handleZoomIn = () => {
    const newScale = Math.min(scale + step, maxScale);
    if (externalScale !== undefined) {
      onScaleChange?.(newScale);
    } else {
      setInternalScale(newScale);
    }
  };

  const handleZoomOut = () => {
    const newScale = Math.max(scale - step, minScale);
    if (externalScale !== undefined) {
      onScaleChange?.(newScale);
    } else {
      setInternalScale(newScale);
    }
  };

  const handleReset = () => {
    if (externalScale !== undefined) {
      onScaleChange?.(1);
    } else {
      setInternalScale(1);
    }
  };

  return (
    <div className="relative" id="zoomable-table-container">
      {/* Controles de zoom - solo visibles cuando hay overflow horizontal */}
      {hasOverflow && (
        <div className="absolute -top-10 right-2 z-10 flex gap-1 bg-white dark:bg-gray-700 rounded-lg shadow-md p-1">
          <button
            onClick={handleZoomOut}
            disabled={scale <= minScale}
            className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600 disabled:opacity-30 transition"
            title={t('common.zoomOut')}
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="px-2 py-1 text-xs font-medium min-w-[40px] text-center">
            {Math.round(scale * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            disabled={scale >= maxScale}
            className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600 disabled:opacity-30 transition"
            title={t('common.zoomIn')}
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleReset}
            className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition"
            title={t('common.reset')}
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Contenedor con transform para el zoom */}
      <div
        ref={containerRef}
        className="overflow-auto"
        style={{
          maxWidth: '100%',
          overflow: hasOverflow ? 'auto' : 'visible',
        }}
      >
        <div
          style={{
            transform: `scale(${scale})`,
            transformOrigin: 'top left',
            width: hasOverflow ? `${100 / scale}%` : 'auto',
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
};
