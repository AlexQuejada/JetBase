import React from 'react';
import FileUpload from '../components/FileUpload';
import FileMerge from '../components/FileMerge';

const TransformPage: React.FC = () => {
    return (
        <div className="space-y-6">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Transformar Datos</h1>
                <p className="text-gray-600 dark:text-gray-400">
                    Sube, combina y limpia tus archivos CSV/Excel para prepararlos para el dashboard.
                </p>
            </div>

            <FileUpload />

            <hr className="my-6" />

            <FileMerge />
        </div>
    );
};

export default TransformPage;
