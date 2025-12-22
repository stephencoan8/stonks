/**
 * Sortable Tables
 * Makes table columns sortable by clicking on headers
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all sortable tables
    const tables = document.querySelectorAll('.sortable-table');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.style.userSelect = 'none';
            
            // Add sort indicator
            const indicator = document.createElement('span');
            indicator.className = 'sort-indicator';
            indicator.innerHTML = ' ↕';
            header.appendChild(indicator);
            
            header.addEventListener('click', () => {
                sortTable(table, index, header);
            });
        });
    });
});

function sortTable(table, columnIndex, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const sortType = header.getAttribute('data-sort');
    const currentOrder = header.getAttribute('data-order') || 'asc';
    const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
    
    // Remove sort indicators from all headers
    table.querySelectorAll('th[data-sort]').forEach(h => {
        h.removeAttribute('data-order');
        const indicator = h.querySelector('.sort-indicator');
        if (indicator) {
            indicator.innerHTML = ' ↕';
        }
    });
    
    // Set new sort order
    header.setAttribute('data-order', newOrder);
    const indicator = header.querySelector('.sort-indicator');
    if (indicator) {
        indicator.innerHTML = newOrder === 'asc' ? ' ▲' : ' ▼';
    }
    
    // Sort rows
    rows.sort((a, b) => {
        const aCell = a.cells[columnIndex];
        const bCell = b.cells[columnIndex];
        
        let aValue = aCell.textContent.trim();
        let bValue = bCell.textContent.trim();
        
        // Get data-value if available (for formatted values)
        if (aCell.hasAttribute('data-value')) {
            aValue = aCell.getAttribute('data-value');
        }
        if (bCell.hasAttribute('data-value')) {
            bValue = bCell.getAttribute('data-value');
        }
        
        let comparison = 0;
        
        switch(sortType) {
            case 'number':
                // Remove currency symbols and commas
                const aNum = parseFloat(aValue.replace(/[$,]/g, ''));
                const bNum = parseFloat(bValue.replace(/[$,]/g, ''));
                comparison = aNum - bNum;
                break;
                
            case 'date':
                const aDate = new Date(aValue);
                const bDate = new Date(bValue);
                comparison = aDate - bDate;
                break;
                
            case 'text':
            default:
                comparison = aValue.localeCompare(bValue);
                break;
        }
        
        return newOrder === 'asc' ? comparison : -comparison;
    });
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}
