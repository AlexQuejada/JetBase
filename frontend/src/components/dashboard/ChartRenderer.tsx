import React, { useMemo } from 'react';
import { ProcessedData } from '../../context/DataContext';
import { ChartConfig } from './MetricSelector';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { useTheme } from '../../context/ThemeContext';

interface ChartRendererProps {
  data: ProcessedData;
  config: ChartConfig | null;
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

const ChartRenderer: React.FC<ChartRendererProps> = ({ data, config }) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Colores para el gráfico según el tema
  const textColor = isDark ? '#E5E7EB' : '#374151';
  const gridColor = isDark ? '#374151' : '#E5E7EB';
  const bgColor = isDark ? '#1F2937' : '#FFFFFF';

  // Calcular la métrica directamente sin useEffect
  const chartData = useMemo(() => {
    if (!config) return [];
    if (!data.preview || data.preview.length === 0) return [];

    const { column, metric, groupBy } = config;
    const rows = data.preview;

    try {
      // Agrupar si es necesario
      let result;
      if (groupBy) {
        const grouped: Record<string, any[]> = {};
        rows.forEach(row => {
          const key = String(row[groupBy] || 'N/A');
          if (!grouped[key]) grouped[key] = [];
          grouped[key].push(row);
        });

        result = Object.entries(grouped).map(([key, groupRows]) => {
          const values = groupRows.map(r => r[column]).filter(v => v !== null && v !== undefined && v !== '');
          return {
            name: key,
            value: calculateMetric(values, metric),
            count: values.length
          };
        });
      } else {
        // Sin agrupación - un solo valor
        const values = rows.map(r => r[column]).filter(v => v !== null && v !== undefined && v !== '');
        result = [{
          name: column,
          value: calculateMetric(values, metric),
          count: values.length
        }];
      }
      return result;
    } catch (err) {
      console.error('Error calculando métrica:', err);
      return [];
    }
  }, [data.preview, config]);

  if (!config) {
    return (
      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-8 text-center text-gray-500 dark:text-gray-400">
        Configura un gráfico para ver la visualización
      </div>
    );
  }

  if (chartData.length === 0) {
    return (
      <div className="bg-yellow-50 dark:bg-yellow-900/30 rounded-lg p-8 text-center">
        <svg className="h-8 w-8 text-yellow-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p className="text-yellow-700 dark:text-yellow-200">No hay datos para mostrar</p>
        <p className="text-sm text-yellow-600 dark:text-yellow-400 mt-1">Verifica que la columna tenga valores</p>
      </div>
    );
  }

  const renderChart = () => {
    switch (config.chartType) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis dataKey="name" tick={{ fill: textColor }} />
              <YAxis tick={{ fill: textColor }} />
              <Tooltip formatter={(value) => [String(Number(value || 0).toLocaleString()), config.metric]} contentStyle={{ backgroundColor: bgColor }} />
              <Bar dataKey="value" fill={COLORS[0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis dataKey="name" tick={{ fill: textColor }} />
              <YAxis tick={{ fill: textColor }} />
              <Tooltip formatter={(value) => [String(Number(value || 0).toLocaleString()), config.metric]} contentStyle={{ backgroundColor: bgColor }} />
              <Line type="monotone" dataKey="value" stroke={COLORS[0]} />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }: any) => `${name || ''}: ${((percent || 0) * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                nameKey="name"
              >
                {chartData.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => String(Number(value || 0).toLocaleString())} contentStyle={{ backgroundColor: bgColor }} />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'table':
      default:
        return (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                    {config.groupBy || 'Columna'}
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">{config.metric}</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Conteo</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-600">
                {chartData.map((row: any, idx: number) => (
                  <tr key={idx}>
                    <td className="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">{row.name}</td>
                    <td className="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">{Number(row.value).toLocaleString()}</td>
                    <td className="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">{row.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
      <h4 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">{config.title}</h4>
      {renderChart()}
      <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
        Columna: <strong>{config.column}</strong> |
        Métrica: <strong>{config.metric}</strong>
        {config.groupBy && <> | Agrupado por: <strong>{config.groupBy}</strong></>}
      </div>
    </div>
  );
};

// Funciones de cálculo de métricas
function calculateMetric(values: any[], metric: string): number {
  if (!values || values.length === 0) return 0;

  // Convertir a números si es necesario
  const numericValues = values.map(v => {
    if (typeof v === 'number') return v;
    const parsed = parseFloat(v);
    return isNaN(parsed) ? 0 : parsed;
  }).filter(v => !isNaN(v) && v !== 0); // Filtrar 0 también para evitar promedios falsos

  // Si no hay valores numéricos válidos, retornar 0
  if (numericValues.length === 0 && metric !== 'count' && metric !== 'unique_count') {
    return 0;
  }

  switch (metric) {
    case 'sum':
      return numericValues.reduce((a, b) => a + b, 0);
    case 'avg':
      return numericValues.length > 0 ? numericValues.reduce((a, b) => a + b, 0) / numericValues.length : 0;
    case 'min':
      return numericValues.length > 0 ? Math.min(...numericValues) : 0;
    case 'max':
      return numericValues.length > 0 ? Math.max(...numericValues) : 0;
    case 'count':
      return values.length;
    case 'median': {
      if (numericValues.length === 0) return 0;
      const sorted = [...numericValues].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      return sorted.length % 2 === 0
        ? (sorted[mid - 1] + sorted[mid]) / 2
        : sorted[mid];
    }
    case 'std_dev': {
      if (numericValues.length < 2) return 0;
      const mean = numericValues.reduce((a, b) => a + b, 0) / numericValues.length;
      const variance = numericValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / numericValues.length;
      return Math.sqrt(variance);
    }
    case 'unique_count':
      return new Set(values.map(v => String(v))).size;
    case 'avg_length':
      return values.reduce((sum, v) => sum + String(v).length, 0) / values.length;
    case 'count_true':
      return values.filter(v => v === true || v === 'true' || v === 1 || v === '1' || v === 'True' || v === 'TRUE').length;
    case 'count_false':
      return values.filter(v => v === false || v === 'false' || v === 0 || v === '0' || v === 'False' || v === 'FALSE').length;
    case 'percentage_true':
      return values.length > 0
        ? (values.filter(v => v === true || v === 'true' || v === 1 || v === '1' || v === 'True' || v === 'TRUE').length / values.length) * 100
        : 0;
    default:
      return values.length;
  }
}

export default ChartRenderer;
