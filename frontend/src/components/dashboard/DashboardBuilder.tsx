import React, { useState, useCallback, useEffect, useRef } from 'react';
import html2canvas from 'html2canvas';
import { useData } from '../../context/DataContext';
import MetricSelector, { ChartConfig } from './MetricSelector';
import ChartRenderer from './ChartRenderer';
import { BarChart3, CheckCircle2, LayoutDashboard, Image } from 'lucide-react';

interface DashboardWidget {
  id: string;
  config: ChartConfig;
}

const STORAGE_KEY_WIDGETS = 'flintrex_dashboard_widgets';

const DashboardBuilder: React.FC = () => {
  const { processedData, clearProcessedData } = useData();
  const widgetRefs = useRef<Record<string, HTMLDivElement | null>>({});

  // Load widgets directly from localStorage as initial state (always runs on mount)
  const [widgets, setWidgets] = useState<DashboardWidget[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY_WIDGETS);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (err) {
      console.error('Error loading widgets:', err);
    }
    return [];
  });

  const [currentConfig, setCurrentConfig] = useState<ChartConfig | null>(null);
  const [configError, setConfigError] = useState('');

  // Save widgets to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_WIDGETS, JSON.stringify(widgets));
    } catch (err) {
      console.error('Error saving widgets:', err);
    }
  }, [widgets]);

  const handleConfigChange = useCallback((config: ChartConfig | null, error: string) => {
    setCurrentConfig(config);
    setConfigError(error);
  }, []);

  const handleAddWidget = () => {
    if (currentConfig && !configError) {
      const newWidget: DashboardWidget = {
        id: Date.now().toString(),
        config: { ...currentConfig }
      };
      setWidgets(prev => [...prev, newWidget]);
      setCurrentConfig(null);
    }
  };

  const handleRemoveWidget = (id: string) => {
    setWidgets(prev => prev.filter(w => w.id !== id));
  };

  const handleClearDashboard = () => {
    if (window.confirm('¿Estás seguro de que quieres eliminar todos los gráficos del dashboard?')) {
      setWidgets([]);
      localStorage.removeItem(STORAGE_KEY_WIDGETS);
    }
  };

  const handleExportDashboard = () => {
    if (!processedData) return;

    const dashboardData = {
      filename: processedData.filename,
      createdAt: new Date().toISOString(),
      widgets: widgets.map(w => ({
        title: w.config.title,
        column: w.config.column,
        metric: w.config.metric,
        chartType: w.config.chartType,
        groupBy: w.config.groupBy
      }))
    };

    const blob = new Blob([JSON.stringify(dashboardData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `dashboard-config-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  const handleExportWidgetImage = async (widgetId: string, title?: string) => {
    const element = widgetRefs.current[widgetId];
    if (!element) return;

    try {
      const canvas = await html2canvas(element, {
        backgroundColor: '#ffffff',
        scale: 2
      });
      const url = canvas.toDataURL('image/png');
      const link = document.createElement('a');
      link.href = url;
      link.download = `grafico-${title || widgetId}-${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Error exportando imagen:', err);
    }
  };

  const handleExportAllImages = async () => {
    for (const widget of widgets) {
      await handleExportWidgetImage(widget.id, widget.config.title);
    }
  };

  // Verificar si hay datos procesados disponibles
  const hasData = processedData && processedData.preview && processedData.preview.length > 0;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Dashboard Builder</h2>
        <div className="flex gap-2">
          {hasData && (
            <button
              onClick={clearProcessedData}
              className="text-sm text-red-600 hover:text-red-800 btn-ghost px-2 py-1 rounded-md"
            >
              Limpiar datos
            </button>
          )}
          {widgets.length > 0 && (
            <>
              <button
                onClick={handleExportDashboard}
                className="text-sm bg-gray-600 text-white px-3 py-1 rounded hover:bg-gray-700 transition btn-relief"
              >
                Exportar Config
              </button>
              {hasData && (
                <button
                  onClick={handleExportAllImages}
                  className="text-sm bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 transition btn-relief flex items-center gap-1"
                >
                  <Image className="w-4 h-4" />
                  Exportar PNG
                </button>
              )}
              <button
                onClick={handleClearDashboard}
                className="text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 transition btn-relief"
              >
                Limpiar Todo
              </button>
            </>
          )}
        </div>
      </div>

      {/* Info de datos procesados */}
      {hasData && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-700 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-800 dark:text-green-200">
                <CheckCircle2 className="w-4 h-4 inline mr-1" /> Datos listos para visualizar
              </p>
              <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                {processedData.transformed_rows.toLocaleString()} filas · {processedData.columns.length} columnas
              </p>
            </div>
            <div className="text-right text-xs text-green-600 dark:text-green-400">
              <p>Original: {processedData.original_rows.toLocaleString()} filas</p>
            </div>
          </div>
        </div>
      )}

      {/* Mensaje cuando no hay datos pero hay widgets guardados */}
      {!hasData && widgets.length > 0 && (
        <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700 rounded-lg">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            <BarChart3 className="w-4 h-4 inline mr-1" /> Tienes {widgets.length} gráficos guardados
          </p>
          <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
            Sube datos compatibles para ver los gráficos realescharts.
          </p>
        </div>
      )}

      {/* Configuración de Gráfico */}
      {hasData && (
        <>
          <div className="mb-6">
            <MetricSelector
              data={processedData}
              onConfigChange={handleConfigChange}
            />

            {/* Botón Agregar al Dashboard */}
            {currentConfig && !configError && (
              <div className="mt-4 text-center">
                <button
                  onClick={handleAddWidget}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition font-medium btn-relief"
                >
                  + Agregar al Dashboard
                </button>
              </div>
            )}
          </div>

          {/* Vista Previa del Gráfico Actual */}
          {currentConfig && (
            <div className="mb-8">
              <h3 className="text-lg font-medium mb-3 text-gray-900 dark:text-white">Vista Previa</h3>
              <ChartRenderer
                data={processedData}
                config={currentConfig}
              />
            </div>
          )}
        </>
      )}

      {/* Estado sin datos y sin widgets */}
      {!hasData && widgets.length === 0 && (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <LayoutDashboard className="w-10 h-10 mx-auto mb-4 text-gray-400" />
          <p className="text-lg mb-2">No hay datos procesados</p>
          <p className="text-sm">
            Primero procesa tus archivos en la sección <strong>"Transformar"</strong>.
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
            El dashboard usará automáticamente los datos limpios y unificados.
          </p>
        </div>
      )}

      {/* Dashboard con Widgets Guardados */}
      {widgets.length > 0 && (
        <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
          <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Mi Dashboard ({widgets.length} gráficos)</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {widgets.map((widget) => (
              <div key={widget.id} className="relative group" ref={(el) => { widgetRefs.current[widget.id] = el; }}>
                {hasData ? (
                  <ChartRenderer
                    data={processedData}
                    config={widget.config}
                  />
                ) : (
                  <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-6 border h-64 flex flex-col items-center justify-center">
                    <BarChart3 className="w-10 h-10 mb-2 text-gray-400" />
                    <p className="font-medium text-gray-600 dark:text-gray-300">{widget.config.title || 'Widget'}</p>
                    <p className="text-sm text-gray-400 mt-1">
                      {widget.config.chartType} - {widget.config.metric} ({widget.config.column})
                    </p>
                    <p className="text-xs text-gray-400 mt-2">
                      Carga datos para ver el gráfico
                    </p>
                  </div>
                )}

                <button
                  onClick={() => handleExportWidgetImage(widget.id, widget.config.title)}
                  className="absolute top-2 left-2 bg-green-500 text-white p-1 rounded opacity-0 group-hover:opacity-100 transition"
                  title="Exportar como PNG"
                >
                  <Image className="w-4 h-4" />
                </button>

                <button
                  onClick={() => handleRemoveWidget(widget.id)}
                  className="absolute top-2 right-2 bg-red-500 text-white p-1 rounded opacity-0 group-hover:opacity-100 transition"
                  title="Eliminar gráfico"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Estado vacío con datos disponibles */}
      {hasData && widgets.length === 0 && (
        <div className="text-center py-8 text-gray-400 dark:text-gray-500 border-t border-gray-200 dark:border-gray-700">
          <p>Configura tu primer gráfico arriba para empezar</p>
        </div>
      )}
    </div>
  );
};

export default DashboardBuilder;
