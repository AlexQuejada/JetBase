import React, { useRef, useState, useEffect } from 'react';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

interface ZoomableTableProps {
  children: React.ReactNode;
  minScale?: number;
  maxScale?: number;
  step?: number;
}

export const ZoomableTable: React.FC<ZoomableTableProps> = ({
  children,
  minScale = 0.5,
  maxScale = 1.5,
  step = 0.1,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  const [hasOverflow, setHasOverflow] = useState(false);

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

  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + step, maxScale));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - step, minScale));
  };

  const handleReset = () => {
    setScale(1);
  };

  return (
    <div className="relative">
      {/* Controles de zoom - solo visibles cuando hay overflow horizontal */}
      {hasOverflow && (
        <div className="absolute -top-20 right-2 z-10 flex gap-1 bg-white dark:bg-gray-700 rounded-lg shadow-md p-1">
          <button
            onClick={handleZoomOut}
            disabled={scale <= minScale}
            className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600 disabled:opacity-30 transition"
            title="Alejar"
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
            title="Acercar"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleReset}
            className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition"
            title="Restablecer"
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
