import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

interface PdfExporterOptions {
  pageWidth: number;
  pageHeight: number;
  margin: number;
  contentWidth: number;
}

const DEFAULT_OPTIONS: PdfExporterOptions = {
  pageWidth: 210,
  pageHeight: 297,
  margin: 10,
  contentWidth: 190, // pageWidth - margin * 2
};

const addNewPage = (pdf: jsPDF): (() => void) => {
  return () => {
    pdf.addPage();
  };
};

export const captureElementAsCanvas = async (
  element: HTMLElement,
  options: Partial<PdfExporterOptions> = {}
): Promise<HTMLCanvasElement> => {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  return html2canvas(element, {
    scale: 2,
    useCORS: true,
    logging: false,
    backgroundColor: '#ffffff',
    width: element.scrollWidth,
    height: element.scrollHeight,
  });
};

export const addImageToPdf = (
  pdf: jsPDF,
  canvas: HTMLCanvasElement,
  x: number,
  y: number,
  contentWidth: number
): number => {
  const imgData = canvas.toDataURL('image/png');
  const imgHeight = (canvas.height * contentWidth) / canvas.width;
  pdf.addImage(imgData, 'PNG', x, y, contentWidth, imgHeight);
  return imgHeight;
};

export const exportHeaderToPdf = async (
  pdf: jsPDF,
  headerEl: HTMLElement,
  yPos: { value: number },
  margin: number,
  contentWidth: number,
  pageHeight: number
): Promise<number> => {
  if (!headerEl) return yPos.value;

  const canvas = await html2canvas(headerEl, {
    scale: 2,
    useCORS: true,
    logging: false,
    backgroundColor: '#ffffff',
  });

  const h = (canvas.height * contentWidth) / canvas.width;
  if (yPos.value + h > pageHeight - margin) {
    pdf.addPage();
    yPos.value = margin;
  }

  pdf.addImage(canvas.toDataURL('image/png'), 'PNG', margin, yPos.value, contentWidth, h);
  yPos.value += h + 8;
  return yPos.value;
};

export const exportSummaryToPdf = async (
  pdf: jsPDF,
  summaryEl: HTMLElement,
  yPos: { value: number },
  margin: number,
  contentWidth: number,
  pageHeight: number
): Promise<number> => {
  if (!summaryEl) return yPos.value;

  const canvas = await html2canvas(summaryEl, {
    scale: 2,
    useCORS: true,
    logging: false,
    backgroundColor: '#ffffff',
  });

  const h = (canvas.height * contentWidth) / canvas.width;
  if (yPos.value + h > pageHeight - margin) {
    pdf.addPage();
    yPos.value = margin;
  }

  pdf.addImage(canvas.toDataURL('image/png'), 'PNG', margin, yPos.value, contentWidth, h);
  yPos.value += h + 8;
  return yPos.value;
};

export const exportTableToPdf = async (
  pdf: jsPDF,
  tableWrapper: HTMLElement,
  yPos: { value: number },
  margin: number,
  contentWidth: number,
  pageHeight: number,
  addNewPageFn: () => void
): Promise<number> => {
  const originalTable = tableWrapper?.querySelector('table') as HTMLTableElement;
  if (!originalTable) return yPos.value;

  // Clone the table to manipulate rows
  const tableClone = originalTable.cloneNode(true) as HTMLTableElement;
  tableClone.style.position = 'absolute';
  tableClone.style.visibility = 'hidden';
  tableClone.style.left = '-9999px';
  tableClone.style.top = '-9999px';
  document.body.appendChild(tableClone);

  const thead = tableClone.querySelector('thead');
  const tbody = tableClone.querySelector('tbody');
  const originalRows = tbody ? Array.from(tbody.querySelectorAll('tr')) : [];

  tableClone.style.display = 'block';
  const tempDiv = document.createElement('div');
  tempDiv.style.visibility = 'hidden';
  tempDiv.style.position = 'absolute';
  tempDiv.style.width = `${tableWrapper.clientWidth || 800}px`;
  tempDiv.appendChild(tableClone.cloneNode(true) as Node);
  document.body.appendChild(tempDiv);

  const theadHeight = thead ? (thead as HTMLElement).offsetHeight : 0;
  const fullAvailableHeight = pageHeight - margin * 2 - theadHeight;

  document.body.removeChild(tempDiv);

  let rowsAdded = 0;

  while (rowsAdded < originalRows.length) {
    // If no more room, start new page
    if (yPos.value >= pageHeight - margin - theadHeight) {
      addNewPageFn();
    }

    const pageAvailable = fullAvailableHeight;
    if (pageAvailable <= theadHeight) {
      addNewPageFn();
      continue;
    }

    // Build page table with header + rows that fit
    const pageTable = document.createElement('table');
    pageTable.className = originalTable.className;
    pageTable.style.width = '100%';
    pageTable.style.fontSize = '12px';

    if (thead) {
      pageTable.appendChild(thead.cloneNode(true));
    }

    const newTbody = document.createElement('tbody');
    let accumulatedHeight = 0;
    const rowsForThisPage: HTMLElement[] = [];

    while (rowsAdded + rowsForThisPage.length < originalRows.length) {
      const nextRow = originalRows[rowsAdded + rowsForThisPage.length] as HTMLElement;
      const nextRowHeight = nextRow.offsetHeight;

      if (accumulatedHeight + nextRowHeight > pageAvailable) {
        break;
      }
      rowsForThisPage.push(nextRow);
      accumulatedHeight += nextRowHeight;
    }

    if (rowsForThisPage.length === 0 && rowsAdded < originalRows.length) {
      rowsForThisPage.push(originalRows[rowsAdded] as HTMLElement);
    }

    rowsForThisPage.forEach(row => {
      newTbody.appendChild(row.cloneNode(true));
    });
    pageTable.appendChild(newTbody);

    // Capture page slice
    const captureDiv = document.createElement('div');
    captureDiv.style.backgroundColor = '#ffffff';
    captureDiv.style.padding = '0';
    captureDiv.style.position = 'absolute';
    captureDiv.style.left = '-9999px';
    captureDiv.style.top = '-9999px';
    captureDiv.appendChild(pageTable);
    document.body.appendChild(captureDiv);

    try {
      const pageCanvas = await html2canvas(captureDiv, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
      });

      const pageImgH = (pageCanvas.height * contentWidth) / pageCanvas.width;
      pdf.addImage(pageCanvas.toDataURL('image/png'), 'PNG', margin, yPos.value, contentWidth, pageImgH);
      yPos.value += pageImgH + 8;
    } catch (e) {
      console.error('Error capturing table page:', e);
    }

    document.body.removeChild(captureDiv);
    rowsAdded += rowsForThisPage.length;
  }

  document.body.removeChild(tableClone);
  return yPos.value;
};

export const exportDashboardToPdf = async (
  pdf: jsPDF,
  dashboardGrid: HTMLElement,
  yPos: { value: number },
  margin: number,
  contentWidth: number,
  pageHeight: number,
  addNewPageFn: () => void
): Promise<number> => {
  if (!dashboardGrid || dashboardGrid.children.length === 0) return yPos.value;

  addNewPageFn();
  yPos.value = margin;

  const widgets = Array.from(dashboardGrid.children) as HTMLElement[];

  for (const widget of widgets) {
    const canvas = await html2canvas(widget, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff',
    });

    const widgetH = (canvas.height * contentWidth) / canvas.width;

    if (yPos.value + widgetH > pageHeight - margin) {
      addNewPageFn();
      yPos.value = margin;
    }

    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', margin, yPos.value, contentWidth, widgetH);
    yPos.value += widgetH + 6;
  }

  return yPos.value;
};

export const generateReportPdf = async (
  reportRef: HTMLDivElement,
  filename: string,
  options: Partial<PdfExporterOptions> = {}
): Promise<void> => {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const { pageWidth, pageHeight, margin, contentWidth } = opts;

  const pdf = new jsPDF('p', 'mm', 'a4');
  let yPos = margin;

  const addNewPageFn = () => {
    pdf.addPage();
    yPos = margin;
  };

  // Add header
  const headerEl = reportRef.querySelector('.text-center.mb-8') as HTMLElement;
  if (headerEl) {
    const canvas = await html2canvas(headerEl, { scale: 2, useCORS: true, logging: false, backgroundColor: '#ffffff' });
    const h = (canvas.height * contentWidth) / canvas.width;
    if (yPos + h > pageHeight - margin) { addNewPageFn(); }
    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', margin, yPos, contentWidth, h);
    yPos += h + 8;
  }

  // Add summary
  const summaryEl = reportRef.querySelector('.bg-gray-50.dark\\:bg-gray-700') as HTMLElement;
  if (summaryEl) {
    const canvas = await html2canvas(summaryEl, { scale: 2, useCORS: true, logging: false, backgroundColor: '#ffffff' });
    const h = (canvas.height * contentWidth) / canvas.width;
    if (yPos + h > pageHeight - margin) { addNewPageFn(); }
    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', margin, yPos, contentWidth, h);
    yPos += h + 8;
  }

  // Add table
  const tableWrapper = reportRef.querySelector('#zoomable-table-container');
  if (tableWrapper) {
    const originalTable = tableWrapper.querySelector('table') as HTMLTableElement;
    if (originalTable) {
      const tableClone = originalTable.cloneNode(true) as HTMLTableElement;
      tableClone.style.position = 'absolute';
      tableClone.style.visibility = 'hidden';
      tableClone.style.left = '-9999px';
      tableClone.style.top = '-9999px';
      document.body.appendChild(tableClone);

      const thead = tableClone.querySelector('thead');
      const tbody = tableClone.querySelector('tbody');
      const originalRows = tbody ? Array.from(tbody.querySelectorAll('tr')) : [];

      tableClone.style.display = 'block';
      const tempDiv = document.createElement('div');
      tempDiv.style.visibility = 'hidden';
      tempDiv.style.position = 'absolute';
      tempDiv.style.width = `${tableWrapper.clientWidth || 800}px`;
      tempDiv.appendChild(tableClone.cloneNode(true) as Node);
      document.body.appendChild(tempDiv);

      const theadHeight = thead ? (thead as HTMLElement).offsetHeight : 0;
      const fullAvailableHeight = pageHeight - margin * 2 - theadHeight;

      document.body.removeChild(tempDiv);

      let rowsAdded = 0;

      while (rowsAdded < originalRows.length) {
        if (yPos >= pageHeight - margin - theadHeight) {
          addNewPageFn();
        }

        const pageAvailable = fullAvailableHeight;
        if (pageAvailable <= theadHeight) {
          addNewPageFn();
          continue;
        }

        const pageTable = document.createElement('table');
        pageTable.className = originalTable.className;
        pageTable.style.width = '100%';
        pageTable.style.fontSize = '12px';

        if (thead) {
          pageTable.appendChild(thead.cloneNode(true));
        }

        const newTbody = document.createElement('tbody');
        let accumulatedHeight = 0;
        const rowsForThisPage: HTMLElement[] = [];

        while (rowsAdded + rowsForThisPage.length < originalRows.length) {
          const nextRow = originalRows[rowsAdded + rowsForThisPage.length] as HTMLElement;
          const nextRowHeight = nextRow.offsetHeight;

          if (accumulatedHeight + nextRowHeight > pageAvailable) {
            break;
          }
          rowsForThisPage.push(nextRow);
          accumulatedHeight += nextRowHeight;
        }

        if (rowsForThisPage.length === 0 && rowsAdded < originalRows.length) {
          rowsForThisPage.push(originalRows[rowsAdded] as HTMLElement);
        }

        rowsForThisPage.forEach(row => {
          newTbody.appendChild(row.cloneNode(true));
        });
        pageTable.appendChild(newTbody);

        const captureDiv = document.createElement('div');
        captureDiv.style.backgroundColor = '#ffffff';
        captureDiv.style.padding = '0';
        captureDiv.style.position = 'absolute';
        captureDiv.style.left = '-9999px';
        captureDiv.style.top = '-9999px';
        captureDiv.appendChild(pageTable);
        document.body.appendChild(captureDiv);

        try {
          const pageCanvas = await html2canvas(captureDiv, {
            scale: 2,
            useCORS: true,
            logging: false,
            backgroundColor: '#ffffff',
          });

          const pageImgH = (pageCanvas.height * contentWidth) / pageCanvas.width;
          pdf.addImage(pageCanvas.toDataURL('image/png'), 'PNG', margin, yPos, contentWidth, pageImgH);
          yPos += pageImgH + 8;
        } catch (e) {
          console.error('Error capturing table page:', e);
        }

        document.body.removeChild(captureDiv);
        rowsAdded += rowsForThisPage.length;
      }

      document.body.removeChild(tableClone);
    }
  }

  // Add dashboard
  const dashboardGrid = reportRef.querySelector('.grid.grid-cols-1.lg\\:grid-cols-2') as HTMLElement;
  if (dashboardGrid && dashboardGrid.children.length > 0) {
    addNewPageFn();
    yPos = margin;

    const widgets = Array.from(dashboardGrid.children) as HTMLElement[];

    for (const widget of widgets) {
      const canvas = await html2canvas(widget, { scale: 2, useCORS: true, logging: false, backgroundColor: '#ffffff' });
      const widgetH = (canvas.height * contentWidth) / canvas.width;

      if (yPos + widgetH > pageHeight - margin) {
        addNewPageFn();
        yPos = margin;
      }

      pdf.addImage(canvas.toDataURL('image/png'), 'PNG', margin, yPos, contentWidth, widgetH);
      yPos += widgetH + 6;
    }
  }

  pdf.save(filename);
};