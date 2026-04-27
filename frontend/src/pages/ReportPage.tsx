import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useData, ProcessedData } from '../context/DataContext';
import ChartRenderer from '../components/dashboard/ChartRenderer';
import { ChartConfig } from '../components/dashboard/MetricSelector';
import { ZoomableTable } from '../components/common/ZoomableTable';
import { generateReportPdf } from '../utils/pdfExporter';

interface DashboardWidget {
  id: string;
  config: ChartConfig;
}

const STORAGE_KEY_WIDGETS = 'flintrex_dashboard_widgets';
const STORAGE_KEY_DATA = 'flintrex_processed_data';
const ZOOM_STORAGE_KEY = 'flintrex_table_zoom';

const ReportPage: React.FC = () => {
  const { t } = useTranslation();
  const { processedData: contextData } = useData();
  const [reportSubtitle, setReportSubtitle] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const [processedData, setProcessedData] = useState<ProcessedData | null>(null);
  const [widgets, setWidgets] = useState<DashboardWidget[]>([]);
  const [tableZoom, setTableZoom] = useState(() => {
    try {
      const stored = localStorage.getItem(ZOOM_STORAGE_KEY);
      return stored ? parseFloat(stored) : 1;
    } catch {
      return 1;
    }
  });
  const reportRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    try {
      const storedData = localStorage.getItem(STORAGE_KEY_DATA);
      if (storedData) {
        setProcessedData(JSON.parse(storedData));
      }
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
      const filename = reportSubtitle
        ? `Intelligence_Report_${reportSubtitle.replace(/\s+/g, '_')}.pdf`
        : 'Intelligence_Report.pdf';

      await generateReportPdf(reportRef.current, filename);
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

  const getTableData = () => {
    if (!processedData?.preview) return [];
    return processedData.preview.slice(0, 100);
  };

  const getDisplayColumns = () => {
    if (!processedData?.columns) return [];
    return processedData.columns.filter(col => col !== '_row_name');
  };

  const hasData = processedData && processedData.preview && processedData.preview.length > 0;

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{t('pages.report.title')}</h1>
        <p className="text-gray-600 dark:text-gray-400">
          {t('pages.report.description')}
        </p>
      </div>

      {!hasData && (
        <div className="bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4">
          <p className="text-yellow-800 dark:text-yellow-200">
            {t('pages.report.noData')}
          </p>
        </div>
      )}

      {hasData && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
              {t('pages.report.reportTitle')}
            </label>
            <input
              type="text"
              value={reportSubtitle}
              onChange={(e) => setReportSubtitle(e.target.value)}
              placeholder={t('pages.report.titlePlaceholder')}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white dark:bg-gray-700 dark:text-white"
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
                {t('pages.report.generatingPdf')}
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {t('pages.report.exportPdf')}
              </>
            )}
          </button>
        </div>
      )}

      {hasData && (
        <div ref={reportRef} className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
          <div className="text-center mb-8 border-b pb-6">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">INTELLIGENCE REPORT</h2>
            {reportSubtitle && (
              <p className="text-xl text-blue-600 font-medium">{reportSubtitle}</p>
            )}
            <p className="text-gray-500 dark:text-gray-400 mt-2">{t('pages.report.generated')}: {formatDate()}</p>
          </div>

          <div className="mb-8 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{t('pages.report.dataSummary')}</h3>
            <div className="grid grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-400">{t('pages.report.file')}:</span>
                <p className="font-medium">{processedData.filename}</p>
              </div>
              <div>
                <span className="text-gray-400">{t('pages.report.rows')}:</span>
                <p className="font-medium">{processedData.transformed_rows.toLocaleString()}</p>
              </div>
              <div>
                <span className="text-gray-400">{t('pages.report.columns')}:</span>
                <p className="font-medium">{getDisplayColumns().length}</p>
              </div>
              <div>
                <span className="text-gray-400">{t('pages.report.source')}:</span>
                <p className="font-medium capitalize">{processedData.source || 'single'}</p>
              </div>
            </div>
          </div>

          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">{t('pages.report.data')}</h3>
            <div className="border rounded-lg overflow-hidden">
              <ZoomableTable
                externalScale={tableZoom}
                onScaleChange={setTableZoom}
              >
                <table className="w-full text-sm">
                  <thead className="bg-gray-100 dark:bg-gray-700">
                    <tr>
                      {getDisplayColumns().map((col) => (
                        <th key={col} className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-200 border-b">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {getTableData().map((row, idx) => (
                      <tr key={idx} className={idx % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-700/50'}>
                        {getDisplayColumns().map((col) => (
                          <td key={col} className="px-4 py-2 border-b text-gray-600 dark:text-gray-300">
                            {row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </ZoomableTable>
              {processedData.preview.length > 100 && (
                <p className="text-sm text-gray-500 dark:text-gray-400 p-2 bg-gray-50 dark:bg-gray-700">
                  {t('pages.report.showingRows', { n: processedData.preview.length.toLocaleString() })}
                </p>
              )}
            </div>
          </div>

          {widgets.length > 0 && processedData && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">{t('pages.report.dashboardSection')}</h3>
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