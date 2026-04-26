import React from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const features = [
        {
            title: t('home.features.transform.title'),
            description: t('home.features.transform.description'),
            icon: (
                <svg className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21 3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
                </svg>
            ),
            action: () => navigate('/transform'),
            buttonText: t('home.features.transform.action'),
        },
        {
            title: t('home.features.dashboard.title'),
            description: t('home.features.dashboard.description'),
            icon: (
                <svg className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                    <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
            ),
            action: () => navigate('/dashboard'),
            buttonText: t('home.features.dashboard.action'),
        },
        {
            title: t('home.features.report.title'),
            description: t('home.features.report.description'),
            icon: (
                <svg className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                    <path d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
            ),
            action: () => navigate('/report'),
            buttonText: t('home.features.report.action'),
        },
    ];

    return (
        <div className="min-h-[calc(100vh-8rem)] flex flex-col">
            {/* Hero Section */}
            <div className="flex-1 flex items-center justify-center py-12 px-4">
                <div className="text-center max-w-2xl mx-auto">
                    <div className="mb-6 flex flex-col items-center">
                        <img src="/LogoFlintrex.png" alt="Flintrex" className="h-40 w-45" />
                        <span className="inline-block px-3 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full">
                            BETA
                        </span>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
                        {t('home.hero.title')}
                    </h1>
                    <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
                        {t('home.hero.subtitle')}
                    </p>
                    <button
                        onClick={() => navigate('/transform')}
                        className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                    >
                        {t('home.hero.cta')}
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                            <path d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                    </button>
                </div>
            </div>

            {/* Feature Cards */}
            <div className="py-8 px-4">
                <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4">
                    {features.map((feature, index) => (
                        <div
                            key={index}
                            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
                        >
                            <div className="w-12 h-12 flex items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 mb-4">
                                {feature.icon}
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                                {feature.title}
                            </h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                                {feature.description}
                            </p>
                            <button
                                onClick={feature.action}
                                className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                            >
                                {feature.buttonText} →
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default HomePage;
