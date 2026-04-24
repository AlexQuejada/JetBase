import React from 'react';
import { useTheme } from '../../context/ThemeContext';

interface NavbarProps {
    collapsed?: boolean;
}

const Navbar: React.FC<NavbarProps> = ({ collapsed }) => {
    const { theme, toggleTheme } = useTheme();

    return (
        <nav className="bg-gray-900 dark:bg-gray-950 text-white px-6 py-4 shadow-md flex-shrink-0">
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-1">
                    <img src="/IconFLintres.png" alt="FlintrexBETA" className="h-10 w-13" />
                    <span className={`text-xl font-bold whitespace-nowrap overflow-hidden transition-all duration-500 ease-in-out ${collapsed ? 'opacity-0 w-0' : 'opacity-100 w-auto'}`}>Flintrex(BETA)</span>
                </div>
                <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-400 hidden sm:block">Transformación de datos</span>
                    <button
                        onClick={toggleTheme}
                        className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-700 transition-all duration-200"
                        title={theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
                    >
                        {theme === 'dark' ? (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                                <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                        ) : (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                                <path d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                            </svg>
                        )}
                    </button>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;