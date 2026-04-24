import React from 'react';

const Footer: React.FC = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="bg-gray-900 dark:bg-gray-950 text-white px-6 py-4 shadow-md flex-shrink-0">
            <div className="flex flex-col sm:flex-row justify-between items-center gap-2 text-sm text-gray-500">
                {/* Izquierda - Copyright */}
                <div className="flex items-center gap-2">
                    <span>© {currentYear} Flintrex(BETA)</span>
                    <span className="hidden sm:inline">•</span>
                    <span className="text-xs">Desarrollado por</span>
                    <a
                        href="https://www.linkedin.com/in/alex-quejada-9ba8561b7/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs font-medium text-blue-600 hover:underline"
                    >
                        Alex Gabriel Quejada
                    </a>
                    <span className="hidden sm:inline">•</span>
                    <a
                        href="https://github.com/AlexQuejada"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-gray-500 hover:text-gray-400"
                    >
                        <i className="fab fa-github"></i>
                        GitHub
                    </a>
                </div>

                {/* Centro - Versión (opcional) */}
                <div className="flex items-center gap-8">
                    <span className="text-xs text-gray-500">v1.0.0</span>
                    <img src="/LogoFlintrex.png" alt="Flintrex" className="h-9 w-12" />
                </div>

            </div>
        </footer>
    );
};

export default Footer;