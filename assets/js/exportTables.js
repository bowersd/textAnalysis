(function () {
  // ----------------------------
  // UI: detect tables + populate dropdown
  // ----------------------------
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

  // ----------------------------
  // Text extraction helpers
  // ----------------------------
  function cellToText(cell) {
    let text = (cell.innerText ?? cell.textContent ?? "");

    // Normalize line endings inside cell to \n (CSV/XLSX will handle display)
    text = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n");

    // Normalize nbsp -> space
    text = text.replace(/\u00A0/g, " ");

    // Clean only trailing whitespace at end of lines
    text = text.replace(/[ \t]+\n/g, "\n");

    // IMPORTANT: do NOT replace \n with \r\n inside the cell.
    // Only the CSV row joiner should use \r\n.
    return text.trimEnd();
  }

  // ----------------------------
  // Link extraction + rich cells (NEW)
  // ----------------------------
  function extractLink(cell) {
    const a = cell.querySelector?.("a[href]");
    if (!a) return null;

    const href = a.getAttribute("href");
    const label = (a.innerText ?? a.textContent ?? "").trim();

    return href ? { href, label: label || href } : null;
  }

  function cellToRich(cell) {
    let text = (cell.innerText ?? cell.textContent ?? "");

    text = text.replace(/\u00A0/g, " ");
    text = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
    text = text.replace(/[ \t]+\n/g, "\n").trimEnd();

    // NEW: allow HTML to display one thing but export another
    if (cell?.dataset?.export) {
      text = cell.dataset.export;
    }

    const link = extractLink(cell);
    return { text, link };
  }

  // ----------------------------
  // Table -> grid (handles rowspan/colspan)
  // NOTE: returns a 2D grid of { text, link } objects (NEW behavior)
  // ----------------------------
function tableToGrid(table) {
  const rows = Array.from(table.querySelectorAll("tr"))
    .filter(r => !r.classList.contains("child")); // NEW: ignore hidden example rows

  const grid = [];
  const spans = [];

  for (let r = 0; r < rows.length; r++) {
    const row = [];
    let col = 0;

    while (spans[col] > 0) {
      row[col] = { text: "", link: null };
      spans[col]--;
      col++;
    }

    const cells = Array.from(rows[r].querySelectorAll("th,td"));
    for (const cell of cells) {
      while (spans[col] > 0) {
        row[col] = { text: "", link: null };
        spans[col]--;
        col++;
      }

      const colspan = parseInt(cell.getAttribute("colspan") || "1", 10);
      const rowspan = parseInt(cell.getAttribute("rowspan") || "1", 10);

      const rich = cellToRich(cell); // this will use data-export (next section)
      row[col] = rich;

      for (let k = 1; k < colspan; k++) row[col + k] = { text: "", link: null };

      if (rowspan > 1) {
        for (let k = 0; k < colspan; k++) {
          spans[col + k] = (spans[col + k] || 0) + (rowspan - 1);
        }
      }

      col += colspan;
    }

    grid.push(row);
  }

  const width = Math.max(...grid.map(r => r.length));
  for (const r of grid) while (r.length < width) r.push({ text: "", link: null });

  return grid;
}

  // ----------------------------
  // CSV export
  // - Preserves newlines inside quoted fields
  // - Preserves links via Excel-friendly HYPERLINK() formula
  // ----------------------------
  function escapeCSV(s) {
    return String(s ?? "").replace(/"/g, '""');
  }

function richToCSVValue(rich) {
  const text = rich?.text ?? "";
  const link = rich?.link;

  // CSV: plain URL if link exists
  if (link?.href) {
    return `"${escapeCSV(link.href)}"`;
  }

  return `"${escapeCSV(text)}"`;
}

  function gridToCSV(grid) {
    return grid
      .map(row => row.map(richToCSVValue).join(","))
      .join("\r\n");
  }

  function tableToCSV(table) {
    return gridToCSV(tableToGrid(table));
  }

  // ----------------------------
  // XLSX export helpers
  // - Preserves links as real hyperlinks in Excel
  // ----------------------------
  function gridToWorksheet(grid) {
    // Build an AOA of cell objects for SheetJS
    const aoa = grid.map(row =>
      row.map(rich => {
        const text = rich?.text ?? "";
        const link = rich?.link;

        if (link?.href) {
          return { v: (link.label || text || link.href), t: "s", l: { Target: link.href } };
        }
        return { v: text, t: "s" };
      })
    );

    return window.XLSX.utils.aoa_to_sheet(aoa);
  }

  // ----------------------------
  // Download helper
  // ----------------------------
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

  // ----------------------------
  // Table selection helpers
  // ----------------------------
  function getSelectedTable() {
    const output = document.getElementById("output");
    const sel = document.getElementById("tableSelect");
    if (!output || !sel) return null;

    const idx = parseInt(sel.value, 10);
    const tables = output.querySelectorAll("table");
    if (!tables.length || Number.isNaN(idx) || !tables[idx]) return null;

    return { table: tables[idx], idx };
  }

  // ----------------------------
  // CSV downloads
  // ----------------------------
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

  // ----------------------------
  // XLSX downloads
  // ----------------------------
  function downloadSelectedTableXLSX() {
    if (!window.XLSX) {
      console.warn("XLSX (SheetJS) not found. Include the library before using XLSX export.");
      return;
    }

    const picked = getSelectedTable();
    if (!picked) return;

    const grid = tableToGrid(picked.table);
    const ws = gridToWorksheet(grid);

    const wb = window.XLSX.utils.book_new();
    window.XLSX.utils.book_append_sheet(wb, ws, `Table ${picked.idx + 1}`);

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

    const wb = window.XLSX.utils.book_new();

    tables.forEach((t, i) => {
      const grid = tableToGrid(t);
      const ws = gridToWorksheet(grid);
      window.XLSX.utils.book_append_sheet(wb, ws, `Table ${i + 1}`);
    });

    window.XLSX.writeFile(wb, `analysis_tables.xlsx`);
  }

  // ----------------------------
  // Expose globally so HTML onclick= and PyScript js.* can find them
  // ----------------------------
  window.refreshExportControls = refreshExportControls;
  window.downloadSelectedTableCSV = downloadSelectedTableCSV;
  window.downloadAllTablesCSV = downloadAllTablesCSV;
  window.downloadSelectedTableXLSX = downloadSelectedTableXLSX;
  window.downloadAllTablesXLSX = downloadAllTablesXLSX;

  // Optional: refresh once on initial load in case tables are server-rendered
  document.addEventListener("DOMContentLoaded", () => {
    try {
      refreshExportControls();
    } catch (e) {}
  });
})();