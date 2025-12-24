import { useState } from 'react';
import { Download } from 'lucide-react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

interface ExportButtonProps {
    targetId: string;
    filename?: string;
    buttonText?: string;
}

export const ExportToPDFButton = ({
    targetId,
    filename = 'dashboard-export.pdf',
    buttonText = 'Export PDF'
}: ExportButtonProps) => {
    const [exporting, setExporting] = useState(false);

    const handleExport = async () => {
        setExporting(true);

        try {
            const element = document.getElementById(targetId);
            if (!element) {
                alert('Export target not found');
                return;
            }

            // Capture element as canvas
            const canvas = await html2canvas(element, {
                scale: 2, // Higher quality
                useCORS: true,
                logging: false
            });

            // Create PDF
            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF({
                orientation: canvas.width > canvas.height ? 'landscape' : 'portrait',
                unit: 'px',
                format: [canvas.width, canvas.height]
            });

            pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
            pdf.save(filename);
        } catch (error) {
            console.error('Export failed:', error);
            alert('Export failed. Please try again.');
        } finally {
            setExporting(false);
        }
    };

    return (
        <button
            onClick={handleExport}
            disabled={exporting}
            className="bg-green-600 hover:bg-green-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
            {exporting ? (
                <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                    Exporting...
                </>
            ) : (
                <>
                    <Download size={18} />
                    {buttonText}
                </>
            )}
        </button>
    );
};

// CSV Export for data tables
export const ExportToCSVButton = ({
    data,
    filename = 'data-export.csv',
    buttonText = 'Export CSV'
}: {
    data: any[];
    filename?: string;
    buttonText?: string;
}) => {
    const handleExport = () => {
        if (!data || data.length === 0) {
            alert('No data to export');
            return;
        }

        // Convert to CSV
        const headers = Object.keys(data[0]).join(',');
        const rows = data.map(row =>
            Object.values(row).map(val =>
                typeof val === 'string' && val.includes(',') ? `"${val}"` : val
            ).join(',')
        );
        const csv = [headers, ...rows].join('\n');

        // Download
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    };

    return (
        <button
            onClick={handleExport}
            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
            <Download size={18} />
            {buttonText}
        </button>
    );
};
