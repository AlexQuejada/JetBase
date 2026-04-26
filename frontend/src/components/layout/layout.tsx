import React, { useState, useEffect } from 'react';
import Navbar from './navbar';
import Sidebar from './sidebar';
import Footer from './footer';

const Layout = ({ children }: { children: React.ReactNode }) => {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
        return window.innerWidth < 650;
    });

    useEffect(() => {
        const mediaQuery = window.matchMedia('(max-width: 649px)');
        const handleChange = (e: MediaQueryListEvent) => {
            setSidebarCollapsed(e.matches);
        };
        mediaQuery.addEventListener('change', handleChange);
        return () => mediaQuery.removeEventListener('change', handleChange);
    }, []);

    return (
        <div className="h-screen flex flex-col overflow-hidden">
            <Navbar collapsed={sidebarCollapsed} />
            <div className="flex flex-1 overflow-hidden">
                <Sidebar collapsed={sidebarCollapsed} onCollapsedChange={setSidebarCollapsed} />
                <main className="flex-1 p-6 bg-gray-50 dark:bg-gray-900 overflow-auto">
                    {children}
                </main>
            </div>
            <Footer />
        </div>
    );
};

export default Layout;