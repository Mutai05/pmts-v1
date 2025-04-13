function exportCSV() {
    let csvContent = "Department,Completed,Ongoing,Not Started,Stalled,Under Procurement,All Projects\n";
    
    const rows = document.querySelectorAll("table tbody tr");
    rows.forEach(row => {
        const cols = row.querySelectorAll("td");
        const rowData = Array.from(cols).map(col => col.textContent.trim());
        csvContent += rowData.join(",") + "\n";
    });
    
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "projects_per_department.csv";
    link.click();
}
