import React from 'react';

const Navbar: React.FC = () => {
    return (
        <nav className="bg-gray-900 text-white px-6 py-4 shadow-md flex-shrink-0">
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-1">
                    <img src="/LogoFlintrex.png" alt="Flintrex" className="h-8 w-8" />
                    <span className="text-xl font-bold">Flintrex</span>
                </div>
                <span className="text-sm text-gray-400">Transformación de datos</span>
            </div>
        </nav>
    );
};

export default Navbar;