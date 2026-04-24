import React, { useState } from 'react';
import Navbar from './navbar';
import Sidebar from './sidebar';
import Footer from './footer';

const Layout = ({ children }: { children: React.ReactNode }) => {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    return (
        <div className="h-screen flex flex-col">
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