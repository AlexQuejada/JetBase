import React from 'react';
import { DashboardBuilder } from '../components/dashboard';

const DashboardPage: React.FC = () => {
    return (
        <div className="space-y-6">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Dashboard</h1>
                <p className="text-gray-600 dark:text-gray-400">
                    Visualiza métricas y gráficos de tus datos procesados.
                </p>
            </div>

            <DashboardBuilder />
        </div>
    );
};

export default DashboardPage;
