(function () {
  function refreshExportControls() {
    const output = document.getElementById("output");
    const tables = output ? output.querySelectorAll("table") : [];
    const controls = document.getElementById("export-controls");
    const sel = document.getElementById("tableSelect");

    if (!controls || !sel) return;

    sel.innerHTML = "";
    if (!tables.length) {
      controls.style.display = "none";
      return;
    }

    tables.forEach((t, i) => {
      const opt = document.createElement("option");
      opt.value = String(i);
      opt.textContent = `Table ${i + 1}`;
      sel.appendChild(opt);
    });

    controls.style.display = "block";
  }

  function tableToCSV(table) {
    const rows = Array.from(table.querySelectorAll("tr"));
    const csvLines = rows.map(row => {
      const cells = Array.from(row.querySelectorAll("th,td")).map(cell => {
        const text = (cell.textContent || "").replace(/\s+/g, " ").trim();
        return '"' + text.replace(/"/g, '""') + '"';
      });
      return cells.join(",");
    });
    return csvLines.join("\n");
  }

  function downloadBlob(filename, content, mime) {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function getSelectedTable() {
    const output = document.getElementById("output");
    const sel = document.getElementById("tableSelect");
    if (!output || !sel) return null;

    const idx = parseInt(sel.value, 10);
    const tables = output.querySelectorAll("table");
    if (!tables.length || Number.isNaN(idx) || !tables[idx]) return null;

    return { table: tables[idx], idx };
  }

  function downloadSelectedTableCSV() {
    const picked = getSelectedTable();
    if (!picked) return;

    const csv = tableToCSV(picked.table);
    downloadBlob(`analysis_table_${picked.idx + 1}.csv`, csv, "text/csv;charset=utf-8");
  }

  function downloadAllTablesCSV() {
    const output = document.getElementById("output");
    if (!output) return;

    const tables = Array.from(output.querySelectorAll("table"));
    if (!tables.length) return;

    tables.forEach((t, i) => {
      const csv = tableToCSV(t);
      downloadBlob(`analysis_table_${i + 1}.csv`, csv, "text/csv;charset=utf-8");
    });
  }

  function downloadSelectedTableXLSX() {
    if (!window.XLSX) {
      console.warn("XLSX (SheetJS) not found. Include the library before using XLSX export.");
      return;
    }

    const picked = getSelectedTable();
    if (!picked) return;

    const wb = window.XLSX.utils.table_to_book(picked.table, { sheet: `Table ${picked.idx + 1}` });
    window.XLSX.writeFile(wb, `analysis_table_${picked.idx + 1}.xlsx`);
  }

  function downloadAllTablesXLSX() {
    if (!window.XLSX) {
      console.warn("XLSX (SheetJS) not found. Include the library before using XLSX export.");
      return;
    }

    const output = document.getElementById("output");
    if (!output) return;

    const tables = Array.from(output.querySelectorAll("table"));
    if (!tables.length) return;

    tables.forEach((t, i) => {
      const wb = window.XLSX.utils.table_to_book(t, { sheet: `Table ${i + 1}` });
      window.XLSX.writeFile(wb, `analysis_table_${i + 1}.xlsx`);
    });
  }

  // Expose globally so HTML onclick= and PyScript js.* can find them
  window.refreshExportControls = refreshExportControls;
  window.downloadSelectedTableCSV = downloadSelectedTableCSV;
  window.downloadAllTablesCSV = downloadAllTablesCSV;
  window.downloadSelectedTableXLSX = downloadSelectedTableXLSX;
  window.downloadAllTablesXLSX = downloadAllTablesXLSX;

  // Optional: refresh once on initial load in case tables are server-rendered
  document.addEventListener("DOMContentLoaded", () => {
    try { refreshExportControls(); } catch (e) {}
  });
})();