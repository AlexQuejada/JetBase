import React, { useState, useRef, useEffect } from 'react';
import { useData, ProcessedData } from '../context/DataContext';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import ChartRenderer from '../components/dashboard/ChartRenderer';
import { ChartConfig } from '../components/dashboard/MetricSelector';

interface DashboardWidget {
  id: string;
  config: ChartConfig;
}

const STORAGE_KEY_WIDGETS = 'flintrex_dashboard_widgets';
const STORAGE_KEY_DATA = 'flintrex_processed_data';

const ReportPage: React.FC = () => {
  const { processedData: contextData } = useData();
  const [reportSubtitle, setReportSubtitle] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const [processedData, setProcessedData] = useState<ProcessedData | null>(null);
  const [widgets, setWidgets] = useState<DashboardWidget[]>([]);
  const reportRef = useRef<HTMLDivElement>(null);

  // Load data and widgets from localStorage on mount
  useEffect(() => {
    try {
      // Load processed data
      const storedData = localStorage.getItem(STORAGE_KEY_DATA);
      if (storedData) {
        setProcessedData(JSON.parse(storedData));
      }
      // Load widgets
      const storedWidgets = localStorage.getItem(STORAGE_KEY_WIDGETS);
      if (storedWidgets) {
        setWidgets(JSON.parse(storedWidgets));
      }
    } catch (err) {
      console.error('Error loading data for report:', err);
    }
  }, []);

  const handleExportPDF = async () => {
    if (!reportRef.current) return;

    setIsExporting(true);
    try {
      const element = reportRef.current;
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff'
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const imgWidth = 210; // A4 width in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;

      pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);

      const filename = reportSubtitle
        ? `Intelligence_Report_${reportSubtitle.replace(/\s+/g, '_')}.pdf`
        : 'Intelligence_Report.pdf';

      pdf.save(filename);
    } catch (error) {
      console.error('Error exporting PDF:', error);
      alert('Error exporting PDF. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const formatDate = () => {
    return new Date().toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get table data (max 100 rows) - filter out _row_name
  const getTableData = () => {
    if (!processedData?.preview) return [];
    return processedData.preview.slice(0, 100);
  };

  // Get columns for display (filter out _row_name)
  const getDisplayColumns = () => {
    if (!processedData?.columns) return [];
    return processedData.columns.filter(col => col !== '_row_name');
  };

  const hasData = processedData && processedData.preview && processedData.preview.length > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Intelligence Report</h1>
        <p className="text-gray-600">
          Genera un reporte profesional con tus datos y dashboard.
        </p>
      </div>

      {/* No Data Warning */}
      {!hasData && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">
            No hay datos disponibles. Por favor, sube y procesa archivos en la sección "Transformar" primero.
          </p>
        </div>
      )}

      {/* Report Configuration */}
      {hasData && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Título del Reporte
            </label>
            <input
              type="text"
              value={reportSubtitle}
              onChange={(e) => setReportSubtitle(e.target.value)}
              placeholder="Ej: Reporte de Clientes Q1 2024"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>

          <button
            onClick={handleExportPDF}
            disabled={isExporting}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium text-white transition-colors ${
              isExporting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isExporting ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Generando PDF...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Exportar a PDF
              </>
            )}
          </button>
        </div>
      )}

      {/* Report Preview (captured for PDF) */}
      {hasData && (
        <div ref={reportRef} className="bg-white rounded-lg shadow p-8">
          {/* Report Header */}
          <div className="text-center mb-8 border-b pb-6">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">INTELLIGENCE REPORT</h2>
            {reportSubtitle && (
              <p className="text-xl text-blue-600 font-medium">{reportSubtitle}</p>
            )}
            <p className="text-gray-500 mt-2">Generado: {formatDate()}</p>
          </div>

          {/* Data Summary */}
          <div className="mb-8 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Resumen de Datos</h3>
            <div className="grid grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Archivo:</span>
                <p className="font-medium">{processedData.filename}</p>
              </div>
              <div>
                <span className="text-gray-500">Filas:</span>
                <p className="font-medium">{processedData.transformed_rows.toLocaleString()}</p>
              </div>
              <div>
                <span className="text-gray-500">Columnas:</span>
                <p className="font-medium">{getDisplayColumns().length}</p>
              </div>
              <div>
                <span className="text-gray-500">Origen:</span>
                <p className="font-medium capitalize">{processedData.source || 'single'}</p>
              </div>
            </div>
          </div>

          {/* Data Table */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Datos</h3>
            <div className="overflow-x-auto border rounded-lg">
              <table className="w-full text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    {getDisplayColumns().map((col) => (
                      <th key={col} className="px-4 py-3 text-left font-semibold text-gray-700 border-b">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {getTableData().map((row, idx) => (
                    <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      {getDisplayColumns().map((col) => (
                        <td key={col} className="px-4 py-2 border-b text-gray-600">
                          {row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              {processedData.preview.length > 100 && (
                <p className="text-sm text-gray-500 p-2 bg-gray-50">
                  Mostrando 100 de {processedData.preview.length.toLocaleString()} filas
                </p>
              )}
            </div>
          </div>

          {/* Dashboard Widgets */}
          {widgets.length > 0 && processedData && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Dashboard</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {widgets.map((widget) => (
                  <ChartRenderer
                    key={widget.id}
                    data={processedData}
                    config={widget.config}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ReportPage;