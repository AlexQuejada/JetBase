import React from 'react';

interface NavbarProps {
    collapsed?: boolean;
}

const Navbar: React.FC<NavbarProps> = ({ collapsed }) => {
    return (
        <nav className="bg-gray-900 text-white px-6 py-4 shadow-md flex-shrink-0">
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-1">
                    <img src="/IconFLintres.png" alt="Flintrex" className="h-10 w-13 transition-all duration-500 ease-in-out" />
                    <span className={`text-xl font-bold whitespace-nowrap overflow-hidden transition-all duration-500 ease-in-out ${collapsed ? 'opacity-0 w-0' : 'opacity-100 w-auto'}`}>Flintrex</span>
                </div>
                <span className="text-sm text-gray-400">Transformación de datos</span>
            </div>
        </nav>
    );
};

export default Navbar;