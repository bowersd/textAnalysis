// assets/js/align-triplet.js
console.log("align-triplet.js loaded");

function findOuterWrapper() {
  // Find the wrapper table that contains other tables
  const tables = document.querySelectorAll("table");
  for (const t of tables) {
    if (t.querySelector("table")) return t;
  }
  return null;
}

(function () {
  let originalWrapper;      // the original <table>…<table><table><table>… structure
  let tripletWrap;          // <div class="triplet-wrap"> holding the 3 tables
  let unifiedWrap;          // <div class="unified-wrap"> holding the single unified table
  let toolbar;              // the toggle toolbar

  function rebuildTriplet() {
    const outer = findOuterWrapper();
    if (!outer) return;

    originalWrapper = outer; // keep reference so we can swap views
    const innerTables = outer.querySelectorAll(':scope > tbody > tr > td > table');
    if (innerTables.length !== 3) return;

    // Build triplet flex wrapper and move the three tables into it
    tripletWrap = document.createElement('div');
    tripletWrap.className = 'triplet-wrap';

    innerTables.forEach(t => {
      t.classList.add('col');
      tripletWrap.appendChild(t);
    });

    // Toolbar (toggle)
    toolbar = document.createElement('div');
    toolbar.className = 'triplet-toolbar';
    toolbar.innerHTML = `
      <label><input type="checkbox" id="rowSelectToggle"> Row-select mode</label>
    `;

    // Insert toolbar + triplet view in place of original table
    outer.replaceWith(toolbar, tripletWrap);

    // Toggle behavior
    toolbar.querySelector('#rowSelectToggle').addEventListener('change', (e) => {
      if (e.target.checked) {
        showUnified(innerTables);
      } else {
        showTriplet();
      }
    });
  }

  function showTriplet() {
    // If unified was shown, remove it and restore triplet
    if (unifiedWrap && unifiedWrap.isConnected) {
      unifiedWrap.remove();
    }
    if (!tripletWrap.isConnected) {
      toolbar.insertAdjacentElement('afterend', tripletWrap);
    }
    syncHeights(); // keep rows aligned in triplet view
  }

  function showUnified(innerTables) {
    // Build a single 3-column table from the three separate tables
    const [tNums, tOj, tEn] = innerTables;

    const rowsNums = [...tNums.querySelectorAll('tr')];
    const rowsOj   = [...tOj.querySelectorAll('tr')];
    const rowsEn   = [...tEn.querySelectorAll('tr')];

    const maxRows = Math.max(rowsNums.length, rowsOj.length, rowsEn.length);

    // Create unified wrapper + table
    unifiedWrap = document.createElement('div');
    unifiedWrap.className = 'unified-wrap';

    const table = document.createElement('table');
    table.className = 'unified';
    table.innerHTML = `
      <thead>
        <tr>
          <th>No.</th>
          <th>Nishnaabemwin Sentence</th>
          <th>English Translation</th>
        </tr>
      </thead>
      <tbody></tbody>
    `;

    const tbody = table.querySelector('tbody');

    // Helper to get text content safely (skipping header rows)
    const cellText = (rowList, i) => {
      const r = rowList[i];
      if (!r) return "";
      // If it's a header row use its cell text; otherwise td text
      const cell = r.querySelector('td, th');
      return cell ? cell.textContent : "";
    };

    // Start from row index 1 to skip the <th> header rows present in each inner table
    for (let i = 1; i < maxRows; i++) {
      const tr = document.createElement('tr');
      const td1 = document.createElement('td');
      const td2 = document.createElement('td');
      const td3 = document.createElement('td');
      td1.textContent = cellText(rowsNums, i);
      td2.textContent = cellText(rowsOj, i);
      td3.textContent = cellText(rowsEn, i);
      tr.append(td1, td2, td3);
      tbody.appendChild(tr);
    }

    unifiedWrap.appendChild(table);

    // Swap views: remove triplet, insert unified
    if (tripletWrap && tripletWrap.isConnected) {
      tripletWrap.remove();
    }
    toolbar.insertAdjacentElement('afterend', unifiedWrap);
  }

  function syncHeights() {
    document.querySelectorAll('.triplet-wrap').forEach(wrapper => {
      const tables = wrapper.querySelectorAll('.col');
      const groups = [];
      tables.forEach(t => {
        [...t.rows].forEach((row, i) => {
          (groups[i] ??= []).push(row);
          row.style.height = '';
        });
      });
      groups.forEach(rows => {
        const max = Math.max(...rows.map(r => r.getBoundingClientRect().height));
        rows.forEach(r => (r.style.height = `${max}px`));
      });
    });
  }

  function init() {
    rebuildTriplet();
    syncHeights();
    window.addEventListener('resize', () => {
      clearTimeout(init._timer);
      init._timer = setTimeout(syncHeights, 120);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();