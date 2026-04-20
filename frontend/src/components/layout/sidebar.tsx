import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar: React.FC = () => {
    const location = useLocation();

    const navigation = [
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
    ];

    return (
        <div className="flex h-full w-64 flex-col bg-gray-900 px-3 py-4 overflow-y-auto flex-shrink-0">
            {/* Header */}
            <div className="mb-6 px-2">
                <h1 className="text-xl font-bold text-white">Flintrex</h1>
                <p className="text-xs text-gray-400 mt-1">Data Integration Tool</p>
            </div>

            {/* Main nav */}
            <nav className="flex flex-col gap-0.5">
                {navigation.map((item) => {
                    const isActive = location.pathname === item.href;
                    return (
                        <Link
                            key={item.name}
                            to={item.href}
                            className={`flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm transition-colors ${
                                isActive
                                    ? "bg-gray-800 text-white font-medium"
                                    : "text-gray-400 hover:bg-gray-800 hover:text-gray-100"
                            }`}
                        >
                            {item.icon}
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer info */}
            <div className="mt-auto pt-6 border-t border-gray-800">
                <p className="text-xs text-gray-500 px-2">
                    v1.0.0
                </p>
            </div>
        </div>
    );
};

export default Sidebar;
