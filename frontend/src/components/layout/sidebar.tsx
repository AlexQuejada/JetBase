import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar: React.FC<{ collapsed?: boolean; onCollapsedChange?: (collapsed: boolean) => void }> = ({ collapsed: externalCollapsed, onCollapsedChange }) => {
    const [internalCollapsed, setInternalCollapsed] = useState(false);
    const collapsed = externalCollapsed ?? internalCollapsed;
    const location = useLocation();

    const navigation = [
        {
            name: "Transformar",
            href: "/transform",
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
                </svg>
            ),
        },
        {
            name: "Dashboard",
            href: "/dashboard",
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                    <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                    <polyline points="9 22 9 12 15 12 15 22" />
                </svg>
            ),
        },
        {
            name: "Intelligence Report",
            href: "/report",
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                    <polyline points="10 9 9 9 8 9" />
                </svg>
            ),
        },
    ];

    const toggleCollapse = () => {
        const newCollapsed = !collapsed;
        setInternalCollapsed(newCollapsed);
        onCollapsedChange?.(newCollapsed);
    };

    return (
        <div className={`relative flex-shrink-0 transition-all duration-500 ease-in-out ${collapsed ? 'w-16' : 'w-64'}`}>
            {/* Background que se desvanece suavemente */}
            <div className={`absolute inset-0 bg-gray-900 dark:bg-gray-950 transition-opacity duration-500 ease-in-out pointer-events-none ${collapsed ? 'opacity-0' : 'opacity-100'}`} />
            {/* Contenido */}
            <div className="relative z-10 flex h-full flex-col px-3 py-4 overflow-hidden">

            {/* Botón colapsar */}
            <button
                onClick={toggleCollapse}
                className={`flex items-center justify-center w-8 h-8 mb-4 mx-auto rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 dark:hover:bg-gray-700 transition-all duration-300 ${collapsed ? '' : 'hover:scale-110'}`}
                title={collapsed ? 'Expandir' : 'Colapsar'}
            >
                <svg className={`w-5 h-5 transition-transform duration-500 ease-in-out ${collapsed ? 'rotate-[540deg]' : ''}`} fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                </svg>
            </button>

            {/* Main nav */}
            <nav className="flex flex-col gap-0.5">
                {navigation.map((item) => {
                    const isActive = location.pathname === item.href;
                    return (
                        <Link
                            key={item.name}
                            to={item.href}
                            className={`flex items-center rounded-lg px-2.5 py-2 text-sm transition-all duration-500 ease-in-out ${isActive
                                ? "bg-gray-800 dark:bg-gray-700 text-white font-medium shadow-sm"
                                : "text-gray-400 hover:bg-gray-800 dark:hover:bg-gray-700 hover:text-gray-100"
                                } gap-2.5`}>
                            <span className={`transition-transform duration-500 ease-in-out ${collapsed ? 'rotate-[360deg]' : ''}`}>
                                {item.icon}
                            </span>
                            <span className={`whitespace-nowrap overflow-hidden transition-all duration-500 ease-in-out ${collapsed ? 'w-0 opacity-0' : 'w-auto opacity-100'}`}>
                                {item.name}
                            </span>
                        </Link>
                    );
                })}
            </nav>

            </div>
        </div>
    );
};

export default Sidebar;
