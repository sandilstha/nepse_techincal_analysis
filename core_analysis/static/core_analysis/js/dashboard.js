  (function initWorkspaceNavigation() {
    const onReady = (callback) => {
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback, { once: true });
      } else {
        callback();
      }
    };

    onReady(function() {
      const workspaceTabs = document.getElementById('workspaceTabs');
      if (!workspaceTabs || !window.bootstrap) return;

      const sectionDefaults = {
        inventory: '#inventory-pane',
        strategy: '#backtest-pane',
        advanced: '#msv-backtest-pane',
        rrg: '#rrg-backtest-pane',
      };

      const getActiveSectionTarget = (section) => {
        const activeChild = document.querySelector(`[data-section="${section}"].active[data-bs-target]`);
        return activeChild?.getAttribute('data-bs-target') || sectionDefaults[section];
      };

      const setPrimarySection = (section) => {
        workspaceTabs.classList.remove('nav-section-inventory', 'nav-section-strategy', 'nav-section-advanced', 'nav-section-rrg');
        workspaceTabs.classList.add(`nav-section-${section}`);

        document.querySelectorAll('[data-primary-section]').forEach((button) => {
          const isActive = button.dataset.primarySection === section;
          button.classList.toggle('active', isActive);
          if (!button.hasAttribute('data-bs-toggle')) {
            button.setAttribute('aria-selected', isActive ? 'true' : 'false');
          }
          button.setAttribute('aria-expanded', isActive ? 'true' : 'false');
        });
      };

      const showWorkspaceTab = (target) => {
        const button = document.querySelector(`[data-bs-target="${target}"]`);
        if (!button) return;

        // Explicitly deactivate the current active pane & its button before
        // Bootstrap shows the new one. Bootstrap tracks "active" per-tablist
        // but when switching primary sections the outgoing pane may be in a
        // different CSS-hidden group, so Bootstrap won't deactivate it.
        const activePane = document.querySelector('#workspaceTabsContent .tab-pane.active');
        if (activePane && '#' + activePane.id !== target) {
          activePane.classList.remove('show', 'active');
          const oldBtn = document.querySelector('[data-bs-target="#' + activePane.id + '"]');
          if (oldBtn) {
            oldBtn.classList.remove('active');
            oldBtn.setAttribute('aria-selected', 'false');
          }
        }

        bootstrap.Tab.getOrCreateInstance(button).show();
      };

      document.querySelectorAll('[data-primary-section]').forEach((button) => {
        button.addEventListener('click', () => {
          const section = button.dataset.primarySection;
          setPrimarySection(section);
          showWorkspaceTab(getActiveSectionTarget(section));
        });
      });

      document.querySelectorAll('[data-section]').forEach((button) => {
        button.addEventListener('click', () => {
          setPrimarySection(button.dataset.section);
        });
      });

      // Register the server-rendered active tab with Bootstrap so it correctly
      // tracks state for future tab switches (without re-triggering show/hide).
      const serverActiveBtn = document.querySelector(
        '#workspaceTabsContent .tab-pane.show.active'
      );
      if (serverActiveBtn) {
        const id = serverActiveBtn.id;
        const triggerBtn = document.querySelector('[data-bs-target="#' + id + '"]');
        if (triggerBtn) {
          bootstrap.Tab.getOrCreateInstance(triggerBtn);
        }
      }
    });
  })();

  /**
   * AUTOCOMPLETE SEARCH SYSTEM
   * Each strategy tab has its own autocomplete search input
   */
  class AutocompleteSearch {
    constructor(inputId, dropdownId, hiddenInputId, apiUrl, options = {}) {
      this.input = document.getElementById(inputId);
      this.dropdown = document.getElementById(dropdownId);
      this.hiddenInput = document.getElementById(hiddenInputId);
      this.apiUrl = apiUrl;
      this.debounceMs = options.debounceMs || 180;
      this.extraParams = options.extraParams || {};
      this.minChars = options.minChars === undefined ? 2 : options.minChars;
      this.emptySearch = options.emptySearch || false;
      this.showAllOnFocus = options.showAllOnFocus || false;
      this.hintText = options.hintText || 'Start typing to search for stocks and indices...';
      this.searchTimeout = null;
      this.abortController = null;
      this.resultCache = new Map();
      this.lastQuery = '';
      this.activeIndex = -1;
      this.results = [];
      this.metaEl = null;
      
      this.init();
    }
    
    init() {
      this.metaEl = document.createElement('div');
      this.metaEl.className = 'autocomplete-selected-meta';
      this.dropdown.parentNode.appendChild(this.metaEl);

      // Input events
      this.input.addEventListener('input', () => this.handleInput());
      this.input.addEventListener('focus', () => {
        if (this.showAllOnFocus && this.emptySearch) {
          clearTimeout(this.searchTimeout);
          this.searchTimeout = setTimeout(() => {
            this.performSearch('');
          }, this.debounceMs);
        } else {
          this.handleInput();
        }
      });
      this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
      
      // Click outside to close
      document.addEventListener('click', (e) => {
        if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
          this.hideDropdown();
        }
      });
    }
    
    handleInput() {
      const query = this.input.value.trim();
      
      // Clear existing timeout
      clearTimeout(this.searchTimeout);
      
      // Keep results focused: require at least 2 characters.
      if (query.length === 0) {
        this.hiddenInput.value = '';
        if (this.emptySearch) {
          this.searchTimeout = setTimeout(() => {
            this.performSearch('');
          }, this.debounceMs);
        } else {
          this.showHint();
        }
        return;
      }
      this.hiddenInput.value = query.toUpperCase();
      this.metaEl.textContent = '';
      if (query.length < this.minChars) {
        this.showHint(`Type at least ${this.minChars} characters to search`);
        return;
      }
      
      // Debounce search
      this.searchTimeout = setTimeout(() => {
        this.performSearch(query);
      }, this.debounceMs);
    }
    
    async performSearch(query) {
      const normalizedQuery = query.trim();
      if (!normalizedQuery && !this.emptySearch) return;
      this.lastQuery = normalizedQuery;

      if (this.resultCache.has(normalizedQuery.toUpperCase())) {
        this.results = this.resultCache.get(normalizedQuery.toUpperCase());
        this.showResults();
        return;
      }

      try {
        this.showLoading();

        if (this.abortController) {
          this.abortController.abort();
        }
        this.abortController = new AbortController();
        
        const searchUrl = new URL(this.apiUrl, window.location.origin);
        searchUrl.searchParams.set('q', normalizedQuery);
        Object.entries(this.extraParams).forEach(([key, value]) => {
          searchUrl.searchParams.set(key, value);
        });

        const response = await fetch(searchUrl.toString(), {
          signal: this.abortController.signal,
        });
        const data = await response.json();
        if (this.lastQuery !== normalizedQuery) return;
        
        this.results = data.results || [];
        this.resultCache.set(normalizedQuery.toUpperCase(), this.results);
        this.showResults();
      } catch (error) {
        if (error.name === 'AbortError') return;
        console.error('Search error:', error);
        this.hideDropdown();
      }
    }
    
    showHint(message = this.hintText) {
      this.dropdown.innerHTML = `<div class="autocomplete-hint">${message}</div>`;
      this.dropdown.classList.add('show');
    }
    
    showLoading() {
      this.dropdown.innerHTML = '<div class="autocomplete-loading">Searching...</div>';
      this.dropdown.classList.add('show');
    }
    
    showResults() {
      if (this.results.length === 0) {
        this.dropdown.innerHTML = '<div class="autocomplete-hint">No matches found</div>';
        this.dropdown.classList.add('show');
        return;
      }

      const escapeHtml = (text) => String(text || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
      const formatDisplayDate = (value) => {
        if (!value) return '';
        const text = String(value).slice(0, 10);
        return /^\d{4}-\d{2}-\d{2}$/.test(text) ? text : String(value);
      };

      this.dropdown.innerHTML = this.results.map((result, index) => {
        const isObject = result && typeof result === 'object';
        const value = isObject ? (result.value || '') : String(result || '');
        const label = isObject ? (result.label || value) : value;
        const type = isObject ? (result.type || '') : '';
        const latestClose = isObject ? result.latest_close : null;
        const latestDate = isObject ? result.latest_date : null;
        const mainText = escapeHtml(label);
        const subParts = [];
        if (type) {
          subParts.push(type);
        }
        if (latestClose !== null && latestClose !== undefined) {
          const priceText = Number(latestClose).toFixed(2);
          const dateText = latestDate ? ` (${formatDisplayDate(latestDate)})` : '';
          subParts.push(`Latest: NPR ${priceText}${dateText}`);
        }
        const subText = subParts.length ? `<div class="autocomplete-item-sub">${escapeHtml(subParts.join(' | '))}</div>` : '';

        return `<div class="autocomplete-item" data-index="${index}">
                  <div class="autocomplete-item-main">${mainText}</div>
                  ${subText}
                </div>`;
      }).join('');
      
      // Add click handlers
      this.dropdown.querySelectorAll('.autocomplete-item').forEach(item => {
        item.addEventListener('click', () => {
          this.selectItem(parseInt(item.dataset.index, 10));
        });
      });
      
      this.dropdown.classList.add('show');
      this.activeIndex = -1;
    }
    
    hideDropdown() {
      this.dropdown.classList.remove('show');
      this.activeIndex = -1;
    }
    
    selectItem(indexOrValue) {
      const selected = Number.isInteger(indexOrValue) ? this.results[indexOrValue] : null;
      const isObject = selected && typeof selected === 'object';
      const value = isObject ? (selected.value || '') : String(indexOrValue || '');
      const latestClose = isObject ? selected.latest_close : null;
      const latestDate = isObject ? selected.latest_date : null;
      const formatDisplayDate = (value) => {
        if (!value) return '';
        const text = String(value).slice(0, 10);
        return /^\d{4}-\d{2}-\d{2}$/.test(text) ? text : String(value);
      };

      this.input.value = value;
      this.hiddenInput.value = value;
      if (latestClose !== null && latestClose !== undefined) {
        const datePart = latestDate ? ` on ${formatDisplayDate(latestDate)}` : '';
        this.metaEl.textContent = `Latest close: NPR ${Number(latestClose).toFixed(2)}${datePart}`;
      } else {
        this.metaEl.textContent = '';
      }
      this.hideDropdown();
    }
    
    handleKeydown(e) {
      const items = this.dropdown.querySelectorAll('.autocomplete-item');
      
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        this.activeIndex = Math.min(this.activeIndex + 1, items.length - 1);
        this.updateActiveItem(items);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        this.activeIndex = Math.max(this.activeIndex - 1, -1);
        this.updateActiveItem(items);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (this.activeIndex >= 0 && items[this.activeIndex]) {
          this.selectItem(this.activeIndex);
        } else if (this.input.value.trim()) {
          // Use current input value
          this.hiddenInput.value = this.input.value.trim().toUpperCase();
          this.input.value = this.input.value.trim().toUpperCase();
          this.metaEl.textContent = '';
          this.hideDropdown();
        }
      } else if (e.key === 'Escape') {
        this.hideDropdown();
      }
    }
    
    updateActiveItem(items) {
      items.forEach((item, index) => {
        if (index === this.activeIndex) {
          item.classList.add('active');
          item.scrollIntoView({ block: 'nearest' });
        } else {
          item.classList.remove('active');
        }
      });
    }
  }
  
  // Initialize autocomplete for each tab
  document.addEventListener('DOMContentLoaded', function() {
    // T3MA tab
    new AutocompleteSearch(
      't3SearchInput',
      't3Dropdown',
      't3SymbolHidden',
      window.NEPSE_URLS.symbolAutocomplete
    );
    
    // EMA tab
    new AutocompleteSearch(
      'emaSearchInput',
      'emaDropdown',
      'emaSymbolHidden',
      window.NEPSE_URLS.symbolAutocomplete
    );
    
    // CCI tab
    new AutocompleteSearch(
      'cciSearchInput',
      'cciDropdown',
      'cciSymbolHidden',
      window.NEPSE_URLS.symbolAutocomplete
    );
    
    // RSI tab
    new AutocompleteSearch(
      'rsiSearchInput',
      'rsiDropdown',
      'rsiSymbolHidden',
      window.NEPSE_URLS.symbolAutocomplete
    );

    // MSV tab
    new AutocompleteSearch(
      'msvSearchInput',
      'msvDropdown',
      'msvSymbolHidden',
      window.NEPSE_URLS.symbolAutocomplete
    );

    // IMM tab
    new AutocompleteSearch(
      'immSearchInput',
      'immDropdown',
      'immSymbolHidden',
      window.NEPSE_URLS.symbolAutocomplete
    );

    // Stage Analysis tab
    new AutocompleteSearch(
      'stageSearchInput',
      'stageDropdown',
      'stageSymbolHidden',
      window.NEPSE_URLS.symbolAutocomplete
    );

    // Support & Resistance tab
    new AutocompleteSearch(
      'supportResistanceSearchInput',
      'supportResistanceDropdown',
      'supportResistanceSymbolHidden',
      window.NEPSE_URLS.symbolAutocomplete
    );

    // RRG tab
    new AutocompleteSearch(
      'rrgSearchInput',
      'rrgDropdown',
      'rrgSymbolHidden',
      window.NEPSE_URLS.symbolAutocomplete,
      { debounceMs: 120, extraParams: { fast: '1' } }
    );

    new AutocompleteSearch(
      'rrgIndicesBenchmarkSearchInput',
      'rrgIndicesBenchmarkDropdown',
      'rrgIndicesBenchmarkHidden',
      window.NEPSE_URLS.symbolAutocomplete,
      {
        debounceMs: 80,
        minChars: 0,
        emptySearch: true,
        showAllOnFocus: true,
        extraParams: { indices_only: '1', all: '1' },
        hintText: 'Search NEPSE indices only...'
      }
    );

    const rrgForm = document.getElementById('rrgForm');
    if (rrgForm) {
      rrgForm.addEventListener('submit', () => {
        const rrgSearchInput = document.getElementById('rrgSearchInput');
        const rrgSymbolHidden = document.getElementById('rrgSymbolHidden');
        if (rrgSearchInput && rrgSymbolHidden) {
          const typedSymbol = rrgSearchInput.value.trim().toUpperCase();
          if (typedSymbol) {
            rrgSearchInput.value = typedSymbol;
            rrgSymbolHidden.value = typedSymbol;
          }
        }
      });
    }

    const setupRrgIndicesMultiSelect = () => {
      const grid = document.getElementById('rrgIndicesChoiceGrid');
      const countEl = document.getElementById('rrgIndicesSelectedCount');
      const selectAllBtn = document.getElementById('rrgIndicesSelectAllBtn');
      const clearBtn = document.getElementById('rrgIndicesClearBtn');
      if (!grid || !countEl || !selectAllBtn || !clearBtn) return;

      const checkboxes = Array.from(grid.querySelectorAll('.rrg-index-checkbox'));
      const refresh = () => {
        const selectedCount = checkboxes.filter((checkbox) => checkbox.checked).length;
        countEl.textContent = `${selectedCount} selected`;
        checkboxes.forEach((checkbox) => {
          const label = checkbox.closest('.rrg-index-choice');
          if (label) label.classList.toggle('is-selected', checkbox.checked);
        });
      };

      selectAllBtn.addEventListener('click', () => {
        checkboxes.forEach((checkbox) => { checkbox.checked = true; });
        refresh();
      });
      clearBtn.addEventListener('click', () => {
        checkboxes.forEach((checkbox) => { checkbox.checked = false; });
        refresh();
      });
      checkboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', refresh);
      });
      refresh();
    };

    setupRrgIndicesMultiSelect();

    const rrgIndicesForm = document.getElementById('rrgIndicesForm');
    if (rrgIndicesForm) {
      rrgIndicesForm.addEventListener('submit', (e) => {
        const searchInput = document.getElementById('rrgIndicesBenchmarkSearchInput');
        const hiddenInput = document.getElementById('rrgIndicesBenchmarkHidden');
        if (searchInput && hiddenInput) {
          const typedIndex = searchInput.value.trim().toUpperCase();
          if (typedIndex) {
            searchInput.value = typedIndex;
            hiddenInput.value = typedIndex;
          }
        }
        const selectedIndices = rrgIndicesForm.querySelectorAll('.rrg-index-checkbox:checked');
        if (!selectedIndices.length) {
          e.preventDefault();
          alert('Select at least one NEPSE index to plot.');
        }
      });
    }

    const formatDate = (d) => {
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    };
    const isTradingDay = (d) => d.getDay() !== 0 && d.getDay() !== 6;
    const normalizeToTradingDay = (d, reverse = false) => {
      const cursor = new Date(d);
      while (!isTradingDay(cursor)) {
        cursor.setDate(cursor.getDate() + (reverse ? -1 : 1));
      }
      return cursor;
    };

    const setupFlatpickrRange = (fromId, toId, opts = {}) => {
      if (!window.flatpickr) return;
      const fromInput = document.getElementById(fromId);
      const toInput = document.getElementById(toId);
      if (!fromInput || !toInput) return;

      const today = normalizeToTradingDay(new Date(), true);
      const todayStr = formatDate(today);
      if (!toInput.value) toInput.value = todayStr;
      if (!fromInput.value) {
        if (opts.defaultMonthRange) {
          // Sync bars: default to the last month (From = one month before the
          // latest trading day) so a routine sync covers recent gaps without
          // pulling a whole year.
          const oneMonthAgo = new Date(today);
          oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
          fromInput.value = formatDate(normalizeToTradingDay(oneMonthAgo));
        } else {
          const oneYearAgo = new Date(today);
          oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
          fromInput.value = formatDate(normalizeToTradingDay(oneYearAgo));
        }
      }

      let fromPicker;
      let toPicker;
      const syncBounds = () => {
        if (toPicker) {
          toPicker.set('maxDate', todayStr);
          toPicker.set('minDate', fromInput.value || null);
        }
        if (fromPicker) {
          fromPicker.set('maxDate', toInput.value || todayStr);
        }
        if (fromInput.value && toInput.value && fromInput.value > toInput.value) {
          fromInput.value = toInput.value;
          if (fromPicker) fromPicker.setDate(fromInput.value, false);
        }
      };

      toPicker = flatpickr(toInput, {
        dateFormat: 'Y-m-d',
        defaultDate: toInput.value || todayStr,
        maxDate: todayStr,
        enable: [isTradingDay],
        allowInput: false,
        onChange: function(selectedDates) {
          if (!selectedDates.length) return;
          const selectedTo = formatDate(selectedDates[0]);
          if (fromPicker) {
            fromPicker.set('maxDate', selectedTo);
            if (fromInput.value && fromInput.value > selectedTo) {
              fromInput.value = selectedTo;
              fromPicker.setDate(selectedTo, false);
            }
          }
          syncBounds();
        }
      });

      fromPicker = flatpickr(fromInput, {
        dateFormat: 'Y-m-d',
        defaultDate: fromInput.value || undefined,
        maxDate: toInput.value || todayStr,
        enable: [isTradingDay],
        allowInput: false,
        onChange: function(selectedDates) {
          if (!selectedDates.length) return;
          const selectedFrom = formatDate(selectedDates[0]);
          if (toPicker) {
            toPicker.set('minDate', selectedFrom);
            if (toInput.value && toInput.value < selectedFrom) {
              toInput.value = selectedFrom;
              toPicker.setDate(selectedFrom, false);
            }
          }
          syncBounds();
        }
      });

      syncBounds();
    };

    const setupFlatpickrSingle = (inputId) => {
      if (!window.flatpickr) return;
      const input = document.getElementById(inputId);
      if (!input) return;
      const today = normalizeToTradingDay(new Date(), true);
      const todayStr = formatDate(today);
      if (!input.value) input.value = todayStr;
      flatpickr(input, {
        dateFormat: 'Y-m-d',
        defaultDate: input.value || todayStr,
        maxDate: todayStr,
        enable: [isTradingDay],
        allowInput: false,
      });
    };

    const setDateInputValue = (input, value) => {
      input.value = value;
      if (input._flatpickr) {
        input._flatpickr.setDate(value, false);
      }
      input.dispatchEvent(new Event('change', { bubbles: true }));
    };

    const setupGenericQuickRanges = () => {
      const today = normalizeToTradingDay(new Date(), true);
      const todayStr = formatDate(today);

      document.querySelectorAll('[data-date-range][data-from-id][data-to-id]').forEach((button) => {
        button.addEventListener('click', () => {
          const fromInput = document.getElementById(button.dataset.fromId);
          const toInput = document.getElementById(button.dataset.toId);
          if (!fromInput || !toInput) return;

          const start = new Date(today);
          const rangeKey = button.dataset.dateRange;
          if (rangeKey === '6m') {
            start.setMonth(start.getMonth() - 6);
          } else if (rangeKey === '1y') {
            start.setFullYear(start.getFullYear() - 1);
          } else if (rangeKey === '2y') {
            start.setFullYear(start.getFullYear() - 2);
          } else if (rangeKey === '3y') {
            start.setFullYear(start.getFullYear() - 3);
          } else if (rangeKey === 'ytd') {
            start.setFullYear(today.getFullYear(), 0, 1);
          }

          setDateInputValue(fromInput, formatDate(normalizeToTradingDay(start)));
          setDateInputValue(toInput, todayStr);
        });
      });
    };

    const getTableDataRows = (table) => {
      const tbody = table.querySelector('tbody');
      if (!tbody) return [];
      return Array.from(tbody.querySelectorAll('tr')).filter((row) => {
        const cells = Array.from(row.querySelectorAll('td'));
        return cells.length && !cells.some((cell) => cell.colSpan > 1);
      });
    };

    const setRowVisibility = (row) => {
      const hiddenByFilter = row.dataset.tableFilterHidden === '1';
      const hiddenByPage = row.dataset.tablePageHidden === '1';
      row.style.display = hiddenByFilter || hiddenByPage ? 'none' : '';
    };

    const applyTablePagination = (table) => {
      const state = table._paginationState;
      if (!state) return;

      const visibleRows = state.rows.filter((row) => row.dataset.tableFilterHidden !== '1');
      const totalPages = Math.max(1, Math.ceil(visibleRows.length / state.pageSize));
      state.currentPage = Math.min(Math.max(1, state.currentPage), totalPages);

      const start = (state.currentPage - 1) * state.pageSize;
      const end = start + state.pageSize;
      state.rows.forEach((row) => {
        const visibleIndex = visibleRows.indexOf(row);
        row.dataset.tablePageHidden = visibleIndex >= start && visibleIndex < end ? '0' : '1';
        setRowVisibility(row);
      });

      if (state.status) {
        const from = visibleRows.length ? start + 1 : 0;
        const to = Math.min(end, visibleRows.length);
        state.status.textContent = `${from}-${to} of ${visibleRows.length}`;
      }
      if (state.prevBtn) state.prevBtn.disabled = state.currentPage <= 1;
      if (state.nextBtn) state.nextBtn.disabled = state.currentPage >= totalPages;
    };
    window.applyTablePagination = applyTablePagination;

    const setupTablePagination = () => {
      document.querySelectorAll('table.minimal-table').forEach((table, index) => {
        if (table.dataset.paginationReady === '1') return;

        const rows = getTableDataRows(table);
        const defaultPageSize = parseInt(table.dataset.defaultPageSize || '10', 10) || 10;
        if (rows.length <= defaultPageSize) return;

        const toolbar = document.createElement('div');
        toolbar.className = 'table-page-toolbar';
        toolbar.innerHTML = `
          <label>Items Per Page
            <select class="table-page-size" aria-label="Items per page">
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="200">200</option>
              <option value="300">300</option>
              <option value="500">500</option>
            </select>
          </label>
          <button type="button" class="table-page-filter">Filter</button>
          <button type="button" class="table-page-reset">Reset</button>
          <button type="button" class="table-page-nav" data-page-action="prev">Prev</button>
          <span class="table-page-status" aria-live="polite"></span>
          <button type="button" class="table-page-nav" data-page-action="next">Next</button>
        `;

        const tableWrap = table.closest('.imm-scroll-wrap') || table;
        tableWrap.parentNode.insertBefore(toolbar, tableWrap);

        const pageSizeSelect = toolbar.querySelector('.table-page-size');
        const filterBtn = toolbar.querySelector('.table-page-filter');
        const resetBtn = toolbar.querySelector('.table-page-reset');
        const prevBtn = toolbar.querySelector('[data-page-action="prev"]');
        const nextBtn = toolbar.querySelector('[data-page-action="next"]');
        const status = toolbar.querySelector('.table-page-status');

        table.dataset.paginationReady = '1';
        table.dataset.paginationIndex = String(index);
        table._paginationState = {
          rows,
          pageSize: defaultPageSize,
          currentPage: 1,
          pageSizeSelect,
          prevBtn,
          nextBtn,
          status,
        };
        pageSizeSelect.value = String(defaultPageSize);

        filterBtn.addEventListener('click', () => {
          table._paginationState.pageSize = parseInt(pageSizeSelect.value, 10) || defaultPageSize;
          table._paginationState.currentPage = 1;
          applyTablePagination(table);
        });
        resetBtn.addEventListener('click', () => {
          pageSizeSelect.value = String(defaultPageSize);
          table._paginationState.pageSize = defaultPageSize;
          table._paginationState.currentPage = 1;
          rows.forEach((row) => {
            row.dataset.tableFilterHidden = row.dataset.tableFilterHidden || '0';
          });
          applyTablePagination(table);
        });
        prevBtn.addEventListener('click', () => {
          table._paginationState.currentPage -= 1;
          applyTablePagination(table);
        });
        nextBtn.addEventListener('click', () => {
          table._paginationState.currentPage += 1;
          applyTablePagination(table);
        });

        applyTablePagination(table);
      });
    };

    const setupBottomTableFilters = (config) => {
      const table = document.getElementById(config.tableId);
      if (!table) return;
      const tbody = table.querySelector('tbody');
      if (!tbody) return;
      const rows = Array.from(tbody.querySelectorAll('tr')).filter((row) => row.querySelector('td'));
      if (!rows.length) return;

      const els = {
        dateFrom: document.getElementById(config.dateFromId),
        dateTo: document.getElementById(config.dateToId),
        closeMin: document.getElementById(config.closeMinId),
        closeMax: document.getElementById(config.closeMaxId),
        scoreMin: document.getElementById(config.scoreMinId),
        scoreMax: document.getElementById(config.scoreMaxId),
      };
      if (Object.values(els).some((el) => !el)) return;

      const parseNum = (v) => {
        const n = parseFloat(v);
        return Number.isFinite(n) ? n : null;
      };
      const normDate = (v) => (v || '').trim();

      const apply = () => {
        const dateFrom = normDate(els.dateFrom.value);
        const dateTo = normDate(els.dateTo.value);
        const closeMin = parseNum(els.closeMin.value);
        const closeMax = parseNum(els.closeMax.value);
        const scoreMin = parseNum(els.scoreMin.value);
        const scoreMax = parseNum(els.scoreMax.value);

        rows.forEach((row) => {
          const rowDate = row.dataset.date || '';
          const rowClose = parseFloat(row.dataset.close || 'NaN');
          const rowScore = parseFloat(row.dataset.score || 'NaN');

          let visible = true;
          if (dateFrom && rowDate < dateFrom) visible = false;
          if (dateTo && rowDate > dateTo) visible = false;
          if (closeMin !== null && !(rowClose >= closeMin)) visible = false;
          if (closeMax !== null && !(rowClose <= closeMax)) visible = false;
          if (scoreMin !== null && !(rowScore >= scoreMin)) visible = false;
          if (scoreMax !== null && !(rowScore <= scoreMax)) visible = false;

          row.dataset.tableFilterHidden = visible ? '0' : '1';
          row.dataset.tablePageHidden = row.dataset.tablePageHidden || '0';
          setRowVisibility(row);
        });
        if (table._paginationState) {
          table._paginationState.currentPage = 1;
          applyTablePagination(table);
        }
      };

      const bindEvent = (el) => {
        el.addEventListener('input', apply);
        el.addEventListener('change', apply);
      };
      Object.values(els).forEach(bindEvent);
      apply();
    };

    setupFlatpickrSingle('inventoryBusinessDate');
    setupFlatpickrRange('headerSyncFromDate', 'headerSyncToDate', { defaultMonthRange: true });
    setupFlatpickrRange('headerCalcFromDate', 'headerCalcToDate', { defaultMonthRange: true });
    setupFlatpickrRange('t3FromDate', 't3ToDate');
    setupFlatpickrRange('emaFromDate', 'emaToDate');
    setupFlatpickrRange('cciFromDate', 'cciToDate');
    setupFlatpickrRange('rsiFromDate', 'rsiToDate');
    setupFlatpickrRange('msvFromDate', 'msvToDate');
    setupFlatpickrRange('supportResistanceFromDate', 'supportResistanceToDate');
    setupFlatpickrRange('rrgFromDate', 'rrgToDate');
    setupFlatpickrRange('rrgIndicesFromDate', 'rrgIndicesToDate');
    setupGenericQuickRanges();
    setupTablePagination();
    setupBottomTableFilters({
      tableId: 'immScoringTable',
      dateFromId: 'immFilterDateFrom',
      dateToId: 'immFilterDateTo',
      closeMinId: 'immFilterCloseMin',
      closeMaxId: 'immFilterCloseMax',
      scoreMinId: 'immFilterScoreMin',
      scoreMaxId: 'immFilterScoreMax',
    });
    setupBottomTableFilters({
      tableId: 'stageOutputTable',
      dateFromId: 'stageFilterDateFrom',
      dateToId: 'stageFilterDateTo',
      closeMinId: 'stageFilterCloseMin',
      closeMaxId: 'stageFilterCloseMax',
      scoreMinId: 'stageFilterScoreMin',
      scoreMaxId: 'stageFilterScoreMax',
    });

    const msvForm = document.getElementById('msvForm');
    if (msvForm) {
      msvForm.addEventListener('submit', function(e) {
        const symbolInput = document.getElementById('msvSearchInput');
        const symbolHidden = document.getElementById('msvSymbolHidden');
        const symbol = ((symbolHidden && symbolHidden.value) || (symbolInput && symbolInput.value) || '').trim().toUpperCase();
        if (symbolInput) symbolInput.value = symbol;
        if (symbolHidden) symbolHidden.value = symbol;
        const getNum = (name) => parseFloat(msvForm.querySelector(`[name="${name}"]`).value || '0');
        const fast = getNum('msv_macd_fast');
        const slow = getNum('msv_macd_slow');
        const signal = getNum('msv_macd_signal');
        const atrLen = getNum('msv_atr_length');
        const atrMult = getNum('msv_atr_multiplier');
        const rvolPeriod = getNum('msv_rvol_period');
        const rvolTh = getNum('msv_rvol_threshold');
        const stLen = getNum('msv_supertrend_length');
        const stMult = getNum('msv_supertrend_multiplier');
        const fromDate = msvForm.querySelector('[name="msv_from_date"]').value;
        const toDate = msvForm.querySelector('[name="msv_to_date"]').value;

        const issues = [];
        if (!symbol) issues.push('Target asset is required.');
        if (!fromDate || !toDate) issues.push('From/To date is required.');
        if (fast >= slow) issues.push('MACD Fast must be smaller than MACD Slow.');
        if (signal < 1 || atrLen < 2 || rvolPeriod < 2 || stLen < 2) issues.push('Lookback periods are too small.');
        if (atrMult <= 0 || rvolTh <= 0 || stMult <= 0) issues.push('Multipliers and thresholds must be greater than zero.');

        if (issues.length) {
          e.preventDefault();
          alert('Validation warnings:\\n- ' + issues.join('\\n- '));
        }
      });
    }

    const immForm = document.getElementById('immForm');
    if (immForm) {
      const fromInput = document.getElementById('immFromDate');
      const toInput = document.getElementById('immToDate');

      const formatDate = (d) => {
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      };
      const isTradingDay = (d) => d.getDay() !== 0 && d.getDay() !== 6;
      const normalizeToTradingDay = (d, reverse = false) => {
        const cursor = new Date(d);
        while (!isTradingDay(cursor)) {
          cursor.setDate(cursor.getDate() + (reverse ? -1 : 1));
        }
        return cursor;
      };

      const today = new Date();
      const todayTrading = normalizeToTradingDay(today, true);
      const todayStr = formatDate(todayTrading);

      if (!toInput.value) {
        toInput.value = todayStr;
      }
      if (!fromInput.value) {
        const oneYearAgo = new Date(todayTrading);
        oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
        fromInput.value = formatDate(normalizeToTradingDay(oneYearAgo));
      }

      let immFromPicker;
      let immToPicker;

      const syncDateBounds = () => {
        if (immToPicker) {
          immToPicker.set('maxDate', todayStr);
          immToPicker.set('minDate', fromInput.value || null);
        }
        if (immFromPicker) {
          immFromPicker.set('maxDate', toInput.value || todayStr);
        }
        if (toInput.value && fromInput.value) {
          if (fromInput.value > toInput.value) {
            fromInput.value = toInput.value;
            if (immFromPicker) immFromPicker.setDate(fromInput.value, false);
          }
        }
      };
      
      if (window.flatpickr) {
        // Descending flow: user picks latest "To Date" first, then "From Date" constrained to <= To Date.
        immToPicker = flatpickr(toInput, {
          dateFormat: 'Y-m-d',
          defaultDate: toInput.value || todayStr,
          maxDate: todayStr,
          enable: [isTradingDay],
          allowInput: false,
          onChange: function(selectedDates) {
            if (!selectedDates.length) return;
            const selectedTo = formatDate(selectedDates[0]);
            if (immFromPicker) {
              immFromPicker.set('maxDate', selectedTo);
              if (fromInput.value && fromInput.value > selectedTo) {
                fromInput.value = selectedTo;
                immFromPicker.setDate(selectedTo, false);
              }
            }
            syncDateBounds();
          }
        });

        immFromPicker = flatpickr(fromInput, {
          dateFormat: 'Y-m-d',
          defaultDate: fromInput.value || undefined,
          maxDate: toInput.value || todayStr,
          enable: [isTradingDay],
          allowInput: false,
          onChange: function(selectedDates) {
            if (!selectedDates.length) return;
            const selectedFrom = formatDate(selectedDates[0]);
            if (immToPicker) {
              immToPicker.set('minDate', selectedFrom);
              if (toInput.value && toInput.value < selectedFrom) {
                toInput.value = selectedFrom;
                immToPicker.setDate(selectedFrom, false);
              }
            }
            syncDateBounds();
          }
        });
      } else {
        // Fallback when flatpickr is unavailable.
        toInput.max = todayStr;
        fromInput.max = toInput.value || todayStr;
        toInput.min = fromInput.value || '';
        fromInput.addEventListener('change', syncDateBounds);
        toInput.addEventListener('change', syncDateBounds);
      }

      const setImmRange = (rangeKey) => {
        const end = new Date(todayTrading);
        let start = new Date(todayTrading);

        if (rangeKey === 'latest') {
          start = new Date(todayTrading);
        } else if (rangeKey === '1m') {
          start.setMonth(start.getMonth() - 1);
        } else if (rangeKey === '3m') {
          start.setMonth(start.getMonth() - 3);
        } else if (rangeKey === '6m') {
          start.setMonth(start.getMonth() - 6);
        } else if (rangeKey === '1y') {
          start.setFullYear(start.getFullYear() - 1);
        } else if (rangeKey === 'ytd') {
          start = new Date(today.getFullYear(), 0, 1);
        }

        const normalizedStart = normalizeToTradingDay(start);
        const normalizedEnd = normalizeToTradingDay(end, true);
        fromInput.value = formatDate(normalizedStart);
        toInput.value = formatDate(normalizedEnd);
        if (immFromPicker) immFromPicker.setDate(fromInput.value, false);
        if (immToPicker) immToPicker.setDate(toInput.value, false);
        syncDateBounds();
      };

      immForm.querySelectorAll('[data-imm-range]').forEach((btn) => {
        btn.addEventListener('click', () => setImmRange(btn.dataset.immRange));
      });

      immForm.addEventListener('submit', function(e) {
        const getNum = (name) => parseFloat(immForm.querySelector(`[name="${name}"]`).value || '0');
        const fast = getNum('imm_macd_fast');
        const slow = getNum('imm_macd_slow');
        const rsLookback = getNum('imm_rs_lookback');
        const atrLen = getNum('imm_atr_length');
        const rsiLen = getNum('imm_rsi_length');
        const stLen = getNum('imm_supertrend_length');
        const stMult = getNum('imm_supertrend_multiplier');
        const fromDate = immForm.querySelector('[name="imm_from_date"]').value;
        const toDate = immForm.querySelector('[name="imm_to_date"]').value;

        const issues = [];
        if (!fromDate || !toDate) issues.push('From/To date is required.');
        if (fast >= slow) issues.push('MACD Fast must be smaller than MACD Slow.');
        if (rsLookback < 2 || atrLen < 2 || rsiLen < 2 || stLen < 2) issues.push('Lookback periods are too small.');
        if (stMult <= 0) issues.push('Supertrend multiplier must be greater than zero.');

        if (issues.length) {
          e.preventDefault();
          alert('Validation warnings:\\n- ' + issues.join('\\n- '));
        }
      });
    }
    
    // Stage Analysis date pickers — IMM-quality: trading-day filter + quick ranges
    const stageFromInput = document.getElementById('stageFromDate');
    const stageToInput   = document.getElementById('stageToDate');
    const stageForm      = document.getElementById('stageForm');
    if (stageFromInput && stageToInput && stageForm) {
      const fmtDate = (d) => {
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
      };
      const isTradingDay = (d) => d.getDay() !== 0 && d.getDay() !== 6;
      const toTradingDay = (d, rev = false) => {
        const c = new Date(d);
        while (!isTradingDay(c)) c.setDate(c.getDate() + (rev ? -1 : 1));
        return c;
      };

      const stageToday = toTradingDay(new Date(), true);
      const stageTodayStr = fmtDate(stageToday);

      if (!stageToInput.value)   stageToInput.value = stageTodayStr;
      if (!stageFromInput.value) {
        const y1 = new Date(stageToday);
        y1.setFullYear(y1.getFullYear() - 1);
        stageFromInput.value = fmtDate(toTradingDay(y1));
      }

      let stageToPicker, stageFromPicker;

      const syncStageBounds = () => {
        if (stageToPicker)   stageToPicker.set('minDate', stageFromInput.value || null);
        if (stageFromPicker) stageFromPicker.set('maxDate', stageToInput.value || stageTodayStr);
        if (stageFromInput.value && stageToInput.value && stageFromInput.value > stageToInput.value) {
          stageFromInput.value = stageToInput.value;
          if (stageFromPicker) stageFromPicker.setDate(stageFromInput.value, false);
        }
      };

      if (window.flatpickr) {
        stageToPicker = flatpickr(stageToInput, {
          dateFormat: 'Y-m-d',
          defaultDate: stageToInput.value || stageTodayStr,
          maxDate: stageTodayStr,
          enable: [isTradingDay],
          allowInput: false,
          onChange(selectedDates) {
            if (!selectedDates.length) return;
            const sel = fmtDate(selectedDates[0]);
            if (stageFromPicker) {
              stageFromPicker.set('maxDate', sel);
              if (stageFromInput.value && stageFromInput.value > sel) {
                stageFromInput.value = sel;
                stageFromPicker.setDate(sel, false);
              }
            }
            syncStageBounds();
          }
        });

        stageFromPicker = flatpickr(stageFromInput, {
          dateFormat: 'Y-m-d',
          defaultDate: stageFromInput.value || undefined,
          maxDate: stageToInput.value || stageTodayStr,
          enable: [isTradingDay],
          allowInput: false,
          onChange(selectedDates) {
            if (!selectedDates.length) return;
            const sel = fmtDate(selectedDates[0]);
            if (stageToPicker) {
              stageToPicker.set('minDate', sel);
              if (stageToInput.value && stageToInput.value < sel) {
                stageToInput.value = sel;
                stageToPicker.setDate(sel, false);
              }
            }
            syncStageBounds();
          }
        });
      }

      // Quick-range shortcut buttons (Stage needs ≥150 rows — minimum 8 months recommended)
      const setStageRange = (rangeKey) => {
        const end = new Date(stageToday);
        let start = new Date(stageToday);
        if      (rangeKey === '6m')  start.setMonth(start.getMonth() - 6);
        else if (rangeKey === '1y')  start.setFullYear(start.getFullYear() - 1);
        else if (rangeKey === '2y')  start.setFullYear(start.getFullYear() - 2);
        else if (rangeKey === '3y')  start.setFullYear(start.getFullYear() - 3);
        else if (rangeKey === 'ytd') start = new Date(stageToday.getFullYear(), 0, 1);
        const ns = fmtDate(toTradingDay(start));
        const ne = fmtDate(toTradingDay(end, true));
        stageFromInput.value = ns;
        stageToInput.value   = ne;
        if (stageFromPicker) stageFromPicker.setDate(ns, false);
        if (stageToPicker)   stageToPicker.setDate(ne, false);
        syncStageBounds();
      };

      stageForm.querySelectorAll('[data-stage-range]').forEach((btn) => {
        btn.addEventListener('click', () => setStageRange(btn.dataset.stageRange));
      });

      stageForm.addEventListener('submit', function(e) {
        const getNum = (name) => parseFloat(stageForm.querySelector(`[name="${name}"]`)?.value || '0');
        const volMult = getNum('stage_volume_multiplier');
        const resLookback = getNum('stage_resistance_lookback');
        const volLookback = getNum('stage_volume_lookback');
        const momentumPeriod = getNum('stage_momentum_period');
        const rsiLen = getNum('stage_rsi_length');
        const rsiMin = getNum('stage_rsi_threshold');
        const adxLen = getNum('stage_adx_length');
        const adxMin = getNum('stage_adx_threshold');

        const issues = [];
        if (!stageFromInput.value || !stageToInput.value) issues.push('From/To date is required.');
        if (volMult <= 0) issues.push('Volume ratio minimum must be greater than zero.');
        if (resLookback < 2 || volLookback < 2 || momentumPeriod < 2 || rsiLen < 2 || adxLen < 2) {
          issues.push('Lookback/length values must be at least 2.');
        }
        if (rsiMin < 0 || rsiMin > 100) issues.push('RSI minimum should be between 0 and 100.');
        if (adxMin < 0 || adxMin > 100) issues.push('ADX minimum should be between 0 and 100.');

        if (issues.length) {
          e.preventDefault();
          alert('Validation warnings:\\n- ' + issues.join('\\n- '));
        }
      });
    }

    // --- Single-symbol RRG toolbar state (mirrors the indices toolbar) ---
    let rrgScaleMode = 'center';   // 'center' | 'fit'
    let rrgLockedDomain = null;
    let rrgLastDomain = null;
    let rrgAnimationTimer = null;

    const readRrgPoints = () => {
      const dataEl = document.getElementById('rrg-chart-data');
      if (!dataEl) return [];
      try {
        return JSON.parse(dataEl.textContent || '[]')
          .filter((row) => Number.isFinite(Number(row.RS_Ratio)) && Number.isFinite(Number(row.RS_Momentum)));
      } catch (e) {
        return [];
      }
    };

    const getRrgMaxTail = () => Math.max(1, readRrgPoints().length);

    const syncRrgTailControls = (value) => {
      const maxTail = getRrgMaxTail();
      const normalized = Math.max(1, Math.min(Number(value) || maxTail, maxTail));
      const slider = document.getElementById('rrgTailSlider');
      const number = document.getElementById('rrgTailNumber');
      if (slider) {
        slider.max = String(maxTail);
        slider.value = String(normalized);
      }
      if (number) {
        number.max = String(maxTail);
        number.value = String(normalized);
      }
      return normalized;
    };

    const drawRrgChart = () => {
      const container = document.getElementById('rrgChart');
      const dataEl = document.getElementById('rrg-chart-data');
      if (!container || !dataEl) return;

      const allPoints = readRrgPoints();
      if (!allPoints.length) return;
      // Tail Length: show only the last N points of the trail (1 = latest only).
      const maxTail = getRrgMaxTail();
      const tailLength = syncRrgTailControls(document.getElementById('rrgTailNumber')?.value || maxTail);
      const arrowMode = document.getElementById('rrgArrowMode')?.checked || false;
      const points = allPoints.slice(-tailLength);

      const width = 900;
      const height = 390;
      const pad = 46;
      // Domain (axis range): Lock pins it, Fit hugs the visible points, Center
      // keeps 100 in the middle with a symmetric spread.
      let min;
      let max;
      if (rrgLockedDomain) {
        min = rrgLockedDomain.min;
        max = rrgLockedDomain.max;
      } else if (rrgScaleMode === 'fit') {
        const values = points.flatMap((row) => [Number(row.RS_Ratio), Number(row.RS_Momentum)]).concat([100]);
        min = Math.floor(Math.min(...values)) - 1;
        max = Math.ceil(Math.max(...values)) + 1;
      } else {
        const spread = Math.max(
          2,
          Math.ceil(Math.max(...points.flatMap((row) => [
            Math.abs(Number(row.RS_Ratio) - 100),
            Math.abs(Number(row.RS_Momentum) - 100),
          ])))
        );
        min = 100 - spread;
        max = 100 + spread;
      }
      if (!Number.isFinite(min) || !Number.isFinite(max) || min === max) {
        min = 98;
        max = 102;
      }
      rrgLastDomain = { min, max };
      const scaleX = (value) => pad + ((value - min) / (max - min)) * (width - pad * 2);
      const scaleY = (value) => height - pad - ((value - min) / (max - min)) * (height - pad * 2);
      const colorFor = (quadrant) => ({
        Leading: '#16a34a',
        Weakening: '#f59e0b',
        Lagging: '#dc2626',
        Improving: '#2563eb',
      }[quadrant] || '#6b7280');
      const formatDisplayDate = (value) => {
        if (!value) return '';
        const text = String(value).slice(0, 10);
        return /^\d{4}-\d{2}-\d{2}$/.test(text) ? text : String(value);
      };

      // Quadrant cross is anchored at value 100, clamped into the plot box so
      // it stays visible even when Fit/Lock push 100 toward an edge.
      const centerX = scaleX(100);
      const centerY = scaleY(100);
      const cx = Math.max(pad, Math.min(width - pad, centerX));
      const cy = Math.max(pad, Math.min(height - pad, centerY));

      const latest = points[points.length - 1];
      const latestX = scaleX(Number(latest.RS_Ratio));
      const latestY = scaleY(Number(latest.RS_Momentum));
      const latestColor = colorFor(latest.Quadrant);

      // Trail along the visible tail (needs >= 2 points). Arrow Mode adds a
      // direction arrowhead at the leading (latest) end.
      const arrowAttr = arrowMode ? ' marker-end="url(#rrgArrowHead)"' : '';
      const path = points.length > 1
        ? `<path d="${points
            .map((row, index) => `${index === 0 ? 'M' : 'L'} ${scaleX(Number(row.RS_Ratio)).toFixed(2)} ${scaleY(Number(row.RS_Momentum)).toFixed(2)}`)
            .join(' ')}" fill="none" stroke="#0f172a" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"${arrowAttr}></path>`
        : '';

      // Historical dots (all but the latest), fading toward the start of the tail.
      const trailDots = points.slice(0, -1).map((row, index) => {
        const opacity = 0.25 + (index / Math.max(1, points.length - 1)) * 0.45;
        return `<circle cx="${scaleX(Number(row.RS_Ratio)).toFixed(2)}" cy="${scaleY(Number(row.RS_Momentum)).toFixed(2)}" r="3.5" fill="${colorFor(row.Quadrant)}" opacity="${opacity.toFixed(2)}"><title>${formatDisplayDate(row.business_date)}: ${Number(row.RS_Ratio).toFixed(2)}, ${Number(row.RS_Momentum).toFixed(2)} (${row.Quadrant})</title></circle>`;
      }).join('');

      const latestDot = `<circle cx="${latestX.toFixed(2)}" cy="${latestY.toFixed(2)}" r="6" fill="${latestColor}"><title>${formatDisplayDate(latest.business_date)}: ${Number(latest.RS_Ratio).toFixed(2)}, ${Number(latest.RS_Momentum).toFixed(2)} (${latest.Quadrant})</title></circle>`;

      // Pulsing halo around the latest point so it visibly blinks (CSS
      // animation in dashboard.css — reliable on innerHTML-injected SVG).
      const blink = `<circle class="rrg-blink" cx="${latestX.toFixed(2)}" cy="${latestY.toFixed(2)}" r="6" fill="none" stroke="${latestColor}" stroke-width="2.5"></circle>`;

      container.innerHTML = `
        <svg class="rrg-chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Relative Rotation Graph">
          ${arrowMode ? '<defs><marker id="rrgArrowHead" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#0f172a"></path></marker></defs>' : ''}
          <rect x="${pad}" y="${pad}" width="${(cx - pad).toFixed(2)}" height="${(cy - pad).toFixed(2)}" fill="rgba(37, 99, 235, 0.08)"></rect>
          <rect x="${cx.toFixed(2)}" y="${pad}" width="${(width - pad - cx).toFixed(2)}" height="${(cy - pad).toFixed(2)}" fill="rgba(22, 163, 74, 0.08)"></rect>
          <rect x="${pad}" y="${cy.toFixed(2)}" width="${(cx - pad).toFixed(2)}" height="${(height - pad - cy).toFixed(2)}" fill="rgba(220, 38, 38, 0.08)"></rect>
          <rect x="${cx.toFixed(2)}" y="${cy.toFixed(2)}" width="${(width - pad - cx).toFixed(2)}" height="${(height - pad - cy).toFixed(2)}" fill="rgba(245, 158, 11, 0.08)"></rect>
          <line x1="${pad}" y1="${cy.toFixed(2)}" x2="${width - pad}" y2="${cy.toFixed(2)}" stroke="#94a3b8" stroke-width="1.5"></line>
          <line x1="${cx.toFixed(2)}" y1="${pad}" x2="${cx.toFixed(2)}" y2="${height - pad}" stroke="#94a3b8" stroke-width="1.5"></line>
          <rect x="${pad}" y="${pad}" width="${width - pad * 2}" height="${height - pad * 2}" fill="none" stroke="#cbd5e1"></rect>
          <text x="${width - pad - 70}" y="${pad + 22}" fill="#16a34a" font-size="13" font-weight="700">Leading</text>
          <text x="${width - pad - 88}" y="${height - pad - 12}" fill="#f59e0b" font-size="13" font-weight="700">Weakening</text>
          <text x="${pad + 14}" y="${height - pad - 12}" fill="#dc2626" font-size="13" font-weight="700">Lagging</text>
          <text x="${pad + 14}" y="${pad + 22}" fill="#2563eb" font-size="13" font-weight="700">Improving</text>
          <text x="${width / 2}" y="${height - 12}" fill="#475569" font-size="12" text-anchor="middle">RS-Ratio</text>
          <text x="15" y="${height / 2}" fill="#475569" font-size="12" text-anchor="middle" transform="rotate(-90 15 ${height / 2})">RS-Momentum</text>
          <text x="${(cx + 6).toFixed(2)}" y="${(cy - 7).toFixed(2)}" fill="#64748b" font-size="11">100</text>
          ${path}
          ${trailDots}
          ${latestDot}
          ${blink}
          <text x="${(latestX + 10).toFixed(2)}" y="${(latestY - 12).toFixed(2)}" fill="#0f172a" font-size="12" font-weight="700">Latest</text>
        </svg>`;
    };

    const setupRrgToolbar = () => {
      const chartCard = document.querySelector('.rrg-chart-card');
      const animateBtn = document.getElementById('rrgAnimateBtn');
      const fitBtn = document.getElementById('rrgFitBtn');
      const maxBtn = document.getElementById('rrgMaxBtn');
      const centerBtn = document.getElementById('rrgCenterBtn');
      const lockBtn = document.getElementById('rrgLockBtn');
      const slider = document.getElementById('rrgTailSlider');
      const number = document.getElementById('rrgTailNumber');
      const arrowMode = document.getElementById('rrgArrowMode');
      if (!chartCard || !animateBtn || !fitBtn || !maxBtn || !centerBtn || !lockBtn || !slider || !number || !arrowMode) return;

      syncRrgTailControls(getRrgMaxTail());   // default: show the full trail
      centerBtn.classList.add('active');

      const refreshScaleButtons = () => {
        fitBtn.classList.toggle('active', rrgScaleMode === 'fit');
        centerBtn.classList.toggle('active', rrgScaleMode === 'center');
      };
      const refreshLockButton = () => {
        lockBtn.classList.toggle('active', Boolean(rrgLockedDomain));
        lockBtn.innerHTML = rrgLockedDomain ? '&#128274;' : '&#128275;';
      };
      const stopAnimation = () => {
        if (rrgAnimationTimer) {
          clearInterval(rrgAnimationTimer);
          rrgAnimationTimer = null;
        }
        animateBtn.innerHTML = '&#9658; Animate';
        animateBtn.classList.remove('active');
      };

      slider.addEventListener('input', () => {
        stopAnimation();
        syncRrgTailControls(slider.value);
        drawRrgChart();
      });
      number.addEventListener('input', () => {
        stopAnimation();
        syncRrgTailControls(number.value);
        drawRrgChart();
      });
      arrowMode.addEventListener('change', drawRrgChart);

      fitBtn.addEventListener('click', () => {
        rrgScaleMode = 'fit';
        rrgLockedDomain = null;
        refreshScaleButtons();
        refreshLockButton();
        drawRrgChart();
      });
      centerBtn.addEventListener('click', () => {
        rrgScaleMode = 'center';
        rrgLockedDomain = null;
        refreshScaleButtons();
        refreshLockButton();
        drawRrgChart();
      });
      maxBtn.addEventListener('click', () => {
        chartCard.classList.toggle('rrg-max-view');
        maxBtn.classList.toggle('active', chartCard.classList.contains('rrg-max-view'));
        drawRrgChart();
      });
      lockBtn.addEventListener('click', () => {
        rrgLockedDomain = rrgLockedDomain ? null : (rrgLastDomain ? { ...rrgLastDomain } : null);
        refreshLockButton();
        drawRrgChart();
      });
      animateBtn.addEventListener('click', () => {
        if (rrgAnimationTimer) {
          stopAnimation();
          return;
        }
        const total = getRrgMaxTail();
        let nextTail = 1;
        animateBtn.textContent = 'Animating';
        animateBtn.classList.add('active');
        syncRrgTailControls(nextTail);
        drawRrgChart();
        rrgAnimationTimer = setInterval(() => {
          nextTail += 1;
          syncRrgTailControls(nextTail);
          drawRrgChart();
          if (nextTail >= total) stopAnimation();
        }, 180);
      });
    };

    const readRrgIndicesJson = (id) => {
      const el = document.getElementById(id);
      if (!el) return [];
      try {
        return JSON.parse(el.textContent || '[]');
      } catch (e) {
        return [];
      }
    };

    let rrgIndicesScaleMode = 'center';
    let rrgIndicesLockedDomain = null;
    let rrgIndicesLastDomain = null;
    let rrgIndicesAnimationTimer = null;

    const getRrgIndicesMaxTail = () => {
      const trails = readRrgIndicesJson('rrg-indices-trails-data');
      const counts = trails.reduce((acc, row) => {
        const key = row.symbol || '';
        acc.set(key, (acc.get(key) || 0) + 1);
        return acc;
      }, new Map());
      return Math.max(1, ...Array.from(counts.values()), 1);
    };

    const syncRrgIndicesTailControls = (value) => {
      const maxTail = getRrgIndicesMaxTail();
      const normalized = Math.max(1, Math.min(Number(value) || maxTail, maxTail));
      const slider = document.getElementById('rrgIndicesTailSlider');
      const number = document.getElementById('rrgIndicesTailNumber');
      const hidden = document.getElementById('rrgIndicesTailLengthInput');
      if (slider) {
        slider.max = String(maxTail);
        slider.value = String(normalized);
      }
      if (number) {
        number.max = String(maxTail);
        number.value = String(normalized);
      }
      if (hidden) hidden.value = String(normalized);
      return normalized;
    };

    const setupRrgIndicesToolbar = () => {
      const chartCard = document.querySelector('.rrg-indices-chart-card');
      const animateBtn = document.getElementById('rrgIndicesAnimateBtn');
      const fitBtn = document.getElementById('rrgIndicesFitBtn');
      const maxBtn = document.getElementById('rrgIndicesMaxBtn');
      const centerBtn = document.getElementById('rrgIndicesCenterBtn');
      const lockBtn = document.getElementById('rrgIndicesLockBtn');
      const slider = document.getElementById('rrgIndicesTailSlider');
      const number = document.getElementById('rrgIndicesTailNumber');
      const arrowMode = document.getElementById('rrgIndicesArrowMode');
      if (!chartCard || !animateBtn || !fitBtn || !maxBtn || !centerBtn || !lockBtn || !slider || !number || !arrowMode) return;

      syncRrgIndicesTailControls(number.value || slider.value || 30);
      centerBtn.classList.add('active');

      const refreshScaleButtons = () => {
        fitBtn.classList.toggle('active', rrgIndicesScaleMode === 'fit');
        centerBtn.classList.toggle('active', rrgIndicesScaleMode === 'center');
      };
      const refreshLockButton = () => {
        lockBtn.classList.toggle('active', Boolean(rrgIndicesLockedDomain));
        lockBtn.innerHTML = rrgIndicesLockedDomain ? '&#128274;' : '&#128275;';
      };
      const stopAnimation = () => {
        if (rrgIndicesAnimationTimer) {
          clearInterval(rrgIndicesAnimationTimer);
          rrgIndicesAnimationTimer = null;
        }
        animateBtn.innerHTML = '&#9658; Animate';
        animateBtn.classList.remove('active');
      };

      slider.addEventListener('input', () => {
        stopAnimation();
        syncRrgIndicesTailControls(slider.value);
        drawRrgIndicesChart();
      });
      number.addEventListener('input', () => {
        stopAnimation();
        syncRrgIndicesTailControls(number.value);
        drawRrgIndicesChart();
      });
      arrowMode.addEventListener('change', drawRrgIndicesChart);

      fitBtn.addEventListener('click', () => {
        rrgIndicesScaleMode = 'fit';
        rrgIndicesLockedDomain = null;
        refreshScaleButtons();
        refreshLockButton();
        drawRrgIndicesChart();
      });
      centerBtn.addEventListener('click', () => {
        rrgIndicesScaleMode = 'center';
        rrgIndicesLockedDomain = null;
        refreshScaleButtons();
        refreshLockButton();
        drawRrgIndicesChart();
      });
      maxBtn.addEventListener('click', () => {
        chartCard.classList.toggle('rrg-indices-max-view');
        maxBtn.classList.toggle('active', chartCard.classList.contains('rrg-indices-max-view'));
        drawRrgIndicesChart();
      });
      lockBtn.addEventListener('click', () => {
        rrgIndicesLockedDomain = rrgIndicesLockedDomain ? null : (rrgIndicesLastDomain ? { ...rrgIndicesLastDomain } : null);
        refreshLockButton();
        drawRrgIndicesChart();
      });
      animateBtn.addEventListener('click', () => {
        if (rrgIndicesAnimationTimer) {
          stopAnimation();
          return;
        }
        const maxTail = getRrgIndicesMaxTail();
        let nextTail = 1;
        animateBtn.textContent = 'Animating';
        animateBtn.classList.add('active');
        syncRrgIndicesTailControls(nextTail);
        drawRrgIndicesChart();
        rrgIndicesAnimationTimer = setInterval(() => {
          nextTail += 1;
          syncRrgIndicesTailControls(nextTail);
          drawRrgIndicesChart();
          if (nextTail >= maxTail) stopAnimation();
        }, 180);
      });
    };

    const drawRrgIndicesChart = () => {
      const container = document.getElementById('rrgIndicesChart');
      if (!container) return;

      const readJson = readRrgIndicesJson;
      const escapeSvg = (value) => {
        const entityMap = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
        return String(value == null ? '' : value).replace(/[&<>"']/g, (ch) => entityMap[ch]);
      };
      const colorFor = (quadrant) => ({
        Leading: '#057a1f',
        Weakening: '#f0b400',
        Lagging: '#e11919',
        Improving: '#2749df',
      }[quadrant] || '#475569');

      const points = readJson('rrg-indices-points-data')
        .filter((row) => Number.isFinite(Number(row.RS_Ratio)) && Number.isFinite(Number(row.RS_Momentum)));
      if (!points.length) return;

      const allTrails = readJson('rrg-indices-trails-data')
        .filter((row) => Number.isFinite(Number(row.RS_Ratio)) && Number.isFinite(Number(row.RS_Momentum)));
      const maxTail = getRrgIndicesMaxTail();
      const tailLength = syncRrgIndicesTailControls(document.getElementById('rrgIndicesTailNumber')?.value || maxTail);
      const arrowMode = document.getElementById('rrgIndicesArrowMode')?.checked || false;
      const allTrailsBySymbol = allTrails.reduce((acc, row) => {
        if (!acc.has(row.symbol)) acc.set(row.symbol, []);
        acc.get(row.symbol).push(row);
        return acc;
      }, new Map());
      const trails = Array.from(allTrailsBySymbol.values()).flatMap((rows) => {
        rows.sort((a, b) => Number(a.step) - Number(b.step));
        return rows.slice(-tailLength).map((row, index) => ({ ...row, step: index + 1 }));
      });
      const benchmark = readJson('rrg-indices-benchmark-data')
        .filter((row) => Number.isFinite(Number(row.close)));

      const width = 1080;
      const height = 620;
      const plotLeft = 74;
      const plotRight = width - 38;
      const plotTop = 148;
      const plotBottom = height - 58;
      const plotWidth = plotRight - plotLeft;
      const plotHeight = plotBottom - plotTop;
      const coords = points.concat(trails);
      let min;
      let max;
      if (rrgIndicesLockedDomain) {
        min = rrgIndicesLockedDomain.min;
        max = rrgIndicesLockedDomain.max;
      } else if (rrgIndicesScaleMode === 'fit') {
        const values = coords.flatMap((row) => [Number(row.RS_Ratio), Number(row.RS_Momentum)]).concat([100]);
        min = Math.floor(Math.min(...values)) - 1;
        max = Math.ceil(Math.max(...values)) + 1;
      } else {
        const spread = Math.max(
          2,
          Math.ceil(Math.max(...coords.flatMap((row) => [
            Math.abs(Number(row.RS_Ratio) - 100),
            Math.abs(Number(row.RS_Momentum) - 100),
          ]))) + 1
        );
        min = 100 - spread;
        max = 100 + spread;
      }
      if (!Number.isFinite(min) || !Number.isFinite(max) || min === max) {
        min = 98;
        max = 102;
      }
      rrgIndicesLastDomain = { min, max };
      const scaleX = (value) => plotLeft + ((value - min) / (max - min)) * plotWidth;
      const scaleY = (value) => plotBottom - ((value - min) / (max - min)) * plotHeight;
      const centerX = scaleX(100);
      const centerY = scaleY(100);

      const tickStep = Math.max(1, Math.ceil((max - min) / 8));
      const ticks = [];
      for (let value = Math.floor(min / tickStep) * tickStep; value <= max + 0.001; value += tickStep) {
        if (value >= min - 0.001) ticks.push(value);
      }
      if (!ticks.some((value) => Math.abs(value - 100) < 0.001)) ticks.push(100);
      ticks.sort((a, b) => a - b);

      const gridNodes = ticks.map((value) => {
        const x = scaleX(value);
        const y = scaleY(value);
        const strong = Math.abs(value - 100) < 0.001;
        return `
          <line x1="${x.toFixed(2)}" y1="${plotTop}" x2="${x.toFixed(2)}" y2="${plotBottom}" stroke="${strong ? '#111827' : '#9ca3af'}" stroke-width="${strong ? 2 : 1}" opacity="${strong ? 0.9 : 0.55}"></line>
          <line x1="${plotLeft}" y1="${y.toFixed(2)}" x2="${plotRight}" y2="${y.toFixed(2)}" stroke="${strong ? '#111827' : '#9ca3af'}" stroke-width="${strong ? 2 : 1}" opacity="${strong ? 0.9 : 0.55}"></line>
          <text x="${x.toFixed(2)}" y="${plotBottom + 25}" fill="#111827" font-size="14" text-anchor="middle">${value}</text>
          <text x="${plotLeft - 12}" y="${(y + 5).toFixed(2)}" fill="#111827" font-size="14" text-anchor="end">${value}</text>
        `;
      }).join('');

      let sparkNodes = '';
      if (benchmark.length > 1) {
        const sparkLeft = plotLeft;
        const sparkRight = plotRight;
        const sparkTop = 24;
        const sparkBottom = 116;
        const closes = benchmark.map((row) => Number(row.close));
        const minClose = Math.min(...closes);
        const maxClose = Math.max(...closes);
        const closeRange = Math.max(1, maxClose - minClose);
        const sparkX = (index) => sparkLeft + (index / (benchmark.length - 1)) * (sparkRight - sparkLeft);
        const sparkY = (close) => sparkBottom - ((close - minClose) / closeRange) * (sparkBottom - sparkTop - 12) - 6;
        const linePath = benchmark
          .map((row, index) => `${index === 0 ? 'M' : 'L'} ${sparkX(index).toFixed(2)} ${sparkY(Number(row.close)).toFixed(2)}`)
          .join(' ');
        const firstY = sparkY(Number(benchmark[0].close));
        const lastX = sparkX(benchmark.length - 1);
        const lastY = sparkY(closes[closes.length - 1]);
        const areaPath = `${linePath} L ${lastX.toFixed(2)} ${sparkBottom} L ${sparkLeft} ${sparkBottom} Z`;
        const latest = benchmark[benchmark.length - 1];
        sparkNodes = `
          <text x="${plotLeft}" y="19" fill="#111827" font-size="19" font-weight="700">${escapeSvg('NEPSE RRG Indices')}</text>
          <text x="${plotLeft + 198}" y="19" fill="#334155" font-size="13">${escapeSvg(latest.business_date || '')}</text>
          <rect x="${sparkLeft}" y="${sparkTop}" width="${sparkRight - sparkLeft}" height="${sparkBottom - sparkTop}" fill="#f3f4f6"></rect>
          <path d="${areaPath}" fill="#e5e7eb"></path>
          <path d="${linePath}" fill="none" stroke="#c7c7c7" stroke-width="3" stroke-linejoin="round"></path>
          <line x1="${sparkLeft}" y1="${lastY.toFixed(2)}" x2="${sparkRight}" y2="${lastY.toFixed(2)}" stroke="#303030" stroke-width="2"></line>
          <line x1="${lastX.toFixed(2)}" y1="${sparkTop}" x2="${lastX.toFixed(2)}" y2="${sparkBottom}" stroke="#303030" stroke-width="2"></line>
          <text x="${sparkLeft - 10}" y="${(lastY + 5).toFixed(2)}" fill="#111827" font-size="15" font-weight="700" text-anchor="end">${Number(latest.close).toFixed(2)}</text>
          <circle cx="${sparkLeft}" cy="${firstY.toFixed(2)}" r="0.1" fill="transparent"></circle>
        `;
      }

      const trailsBySymbol = trails.reduce((acc, row) => {
        if (!acc.has(row.symbol)) acc.set(row.symbol, []);
        acc.get(row.symbol).push(row);
        return acc;
      }, new Map());
      const trailNodes = Array.from(trailsBySymbol.entries()).map(([symbol, rows]) => {
        rows.sort((a, b) => Number(a.step) - Number(b.step));
        if (rows.length < 2) return '';
        const point = points.find((row) => row.symbol === symbol) || rows[rows.length - 1];
        const path = rows
          .map((row, index) => `${index === 0 ? 'M' : 'L'} ${scaleX(Number(row.RS_Ratio)).toFixed(2)} ${scaleY(Number(row.RS_Momentum)).toFixed(2)}`)
          .join(' ');
        const trailDots = rows.slice(0, -1).map((row, index) => {
          const opacity = 0.18 + (index / Math.max(1, rows.length - 1)) * 0.35;
          return `<circle cx="${scaleX(Number(row.RS_Ratio)).toFixed(2)}" cy="${scaleY(Number(row.RS_Momentum)).toFixed(2)}" r="3" fill="${colorFor(row.Quadrant)}" opacity="${opacity.toFixed(2)}"></circle>`;
        }).join('');
        const arrowAttr = arrowMode ? ' marker-end="url(#rrgIndicesArrowHead)"' : '';
        return `<path d="${path}" fill="none" stroke="${colorFor(point.Quadrant)}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.42"${arrowAttr}></path>${trailDots}`;
      }).join('');

      const pointNodes = points.map((point) => {
        const x = scaleX(Number(point.RS_Ratio));
        const y = scaleY(Number(point.RS_Momentum));
        const rightSide = Number(point.RS_Ratio) >= 100;
        const dx = rightSide ? 10 : -10;
        const anchor = rightSide ? 'start' : 'end';
        const dy = ((Number(point.order) % 3) - 1) * 5 - 5;
        const color = colorFor(point.Quadrant);
        return `
          <circle cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="7" fill="${color}" stroke="#ffffff" stroke-width="2">
            <title>${escapeSvg(point.symbol)}: ${Number(point.RS_Ratio).toFixed(2)}, ${Number(point.RS_Momentum).toFixed(2)} (${escapeSvg(point.Quadrant)})</title>
          </circle>
          <text x="${(x + dx).toFixed(2)}" y="${(y + dy).toFixed(2)}" fill="#111827" font-size="13" font-weight="700" text-anchor="${anchor}">${escapeSvg(point.label)}</text>
        `;
      }).join('');

      container.innerHTML = `
        <svg class="rrg-indices-chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="NEPSE indices relative rotation graph">
          ${arrowMode ? '<defs><marker id="rrgIndicesArrowHead" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#1f2937"></path></marker></defs>' : ''}
          <rect x="0" y="0" width="${width}" height="${height}" fill="#ffffff"></rect>
          ${sparkNodes}
          <rect x="${plotLeft}" y="${plotTop}" width="${centerX - plotLeft}" height="${centerY - plotTop}" fill="#c9d0ff" opacity="0.78"></rect>
          <rect x="${centerX}" y="${plotTop}" width="${plotRight - centerX}" height="${centerY - plotTop}" fill="#bfe3bf" opacity="0.9"></rect>
          <rect x="${plotLeft}" y="${centerY}" width="${centerX - plotLeft}" height="${plotBottom - centerY}" fill="#ffb7b7" opacity="0.9"></rect>
          <rect x="${centerX}" y="${centerY}" width="${plotRight - centerX}" height="${plotBottom - centerY}" fill="#fff0b8" opacity="0.92"></rect>
          ${gridNodes}
          <rect x="${plotLeft}" y="${plotTop}" width="${plotWidth}" height="${plotHeight}" fill="none" stroke="#b7b7b7" stroke-width="1"></rect>
          <text x="${plotLeft + 18}" y="${plotTop + 30}" fill="#2749df" font-size="21" font-weight="800">Improving</text>
          <text x="${plotRight - 22}" y="${plotTop + 30}" fill="#057a1f" font-size="21" font-weight="800" text-anchor="end">Leading</text>
          <text x="${plotLeft + 18}" y="${plotBottom - 22}" fill="#e11919" font-size="21" font-weight="800">Lagging</text>
          <text x="${plotRight - 22}" y="${plotBottom - 22}" fill="#f0b400" font-size="21" font-weight="800" text-anchor="end">Weakening</text>
          <text x="${(plotLeft + plotRight) / 2}" y="${height - 16}" fill="#111827" font-size="16" font-weight="700" text-anchor="middle">JdK RS-Ratio</text>
          <text x="24" y="${(plotTop + plotBottom) / 2}" fill="#111827" font-size="16" font-weight="700" text-anchor="middle" transform="rotate(-90 24 ${(plotTop + plotBottom) / 2})">JdK RS-Momentum</text>
          <text x="${(plotLeft + plotRight) / 2}" y="${plotBottom - 16}" fill="#64748b" font-size="22" font-weight="800" opacity="0.7" text-anchor="middle">NEPSE / RRG</text>
          ${trailNodes}
          ${pointNodes}
        </svg>`;
    };

    const drawAdvancedMarketStructureChart = () => {
      const chartContainer = document.getElementById('advancedMarketStructureChart');
      const dataEl = document.getElementById('advanced-market-structure-data');
      if (!chartContainer || !dataEl) return;

      // Ensure LightweightCharts library is loaded
      if (typeof LightweightCharts === 'undefined') {
        chartContainer.innerHTML = '<div class="alert alert-warning m-4"><strong>Lightweight Charts library not loaded.</strong> Please check the script tag.</div>';
        return;
      }

      let chartPayload;
      try {
        // The json_script should contain the 'chart' object from the backend metrics
        chartPayload = JSON.parse(dataEl.textContent || '{}');
      } catch (e) {
        chartContainer.innerHTML = "<p class='text-muted p-4'>Failed to parse chart data.</p>";
        return;
      }

      if (!chartPayload || !chartPayload.candles || chartPayload.candles.length === 0) {
        chartContainer.innerHTML = "<p class='text-muted p-4'>Not enough chart data available.</p>";
        return;
      }

      chartContainer.innerHTML = '';
      chartContainer.style.height = '600px';
      chartContainer.style.backgroundColor = '#ffffff';

      const chart = LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: 600,
        layout: { background: { color: '#ffffff' }, textColor: '#333' },
        grid: { vertLines: { color: '#f0f3fa' }, horzLines: { color: '#f0f3fa' } },
        crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
        rightPriceScale: { borderColor: '#cccccc' },
        timeScale: { borderColor: '#cccccc', timeVisible: false, secondsVisible: false },
      });

      const candleSeries = chart.addCandlestickSeries({
        upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
        wickUpColor: '#26a69a', wickDownColor: '#ef5350',
      });

      const candleData = chartPayload.candles.map(c => ({
        time: c.date, open: c.open, high: c.high, low: c.low, close: c.close
      }));
      candleSeries.setData(candleData);

      if (chartPayload.candles.some(c => c.volume !== undefined && c.volume !== null)) {
        const volumeSeries = chart.addHistogramSeries({
          priceFormat: { type: 'volume' },
          priceScaleId: '',
          scaleMargins: { top: 0.8, bottom: 0 },
        });
        const volumeData = chartPayload.candles.map(c => ({
          time: c.date, value: c.volume,
          color: c.close >= c.open ? 'rgba(38, 166, 154, 0.4)' : 'rgba(239, 83, 80, 0.4)'
        }));
        volumeSeries.setData(volumeData);
      }

      if (chartPayload.baselines && chartPayload.baselines.vwap) {
        const vwapSeries = chart.addLineSeries({ color: '#2962FF', lineWidth: 2, title: 'VWAP' });
        const vwapData = chartPayload.baselines.vwap.map(p => ({ time: p.date, value: p.value })).filter(p => p.value !== null);
        if (vwapData.length > 0) vwapSeries.setData(vwapData);
      }

      // Markers carry NO text — with many pivots/sweeps the labels overlap into
      // an unreadable pile. The arrow direction + colour encodes the meaning and
      // the legend (added below) explains the shapes.
      let markers = [];
      if (chartPayload.pivots) {
        chartPayload.pivots.forEach(p => {
          markers.push({
            time: p.date,
            position: p.pivot_type === 'swing_high' ? 'aboveBar' : 'belowBar',
            color: p.pivot_type === 'swing_high' ? '#ef5350' : '#26a69a',
            shape: p.pivot_type === 'swing_high' ? 'arrowDown' : 'arrowUp',
          });
        });
      }
      if (chartPayload.sweeps) {
        chartPayload.sweeps.forEach(s => {
          markers.push({
            time: s.date,
            position: s.type.includes('Buy-side') ? 'aboveBar' : 'belowBar',
            color: '#ff9800',
            shape: 'circle',
          });
        });
      }
      if (markers.length > 0) {
        markers.sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime());
        candleSeries.setMarkers(markers);
      }

      if (chartPayload.zones) {
        chartPayload.zones.forEach(zone => {
          candleSeries.createPriceLine({
            price: zone.center,
            color: zone.type.includes('Supply') || zone.type.includes('Resistance') ? 'rgba(239, 83, 80, 0.7)' : 'rgba(38, 166, 154, 0.7)',
            lineWidth: 2,
            lineStyle: LightweightCharts.LineStyle.Solid,
            axisLabelVisible: true,
            title: zone.type,
          });
        });
      }

      if (chartPayload.trendlines) {
        chartPayload.trendlines.forEach(line => {
          const tlSeries = chart.addLineSeries({
            color: line.direction === 'Ascending' ? '#26a69a' : '#ef5350',
            lineWidth: 2,
            lineStyle: LightweightCharts.LineStyle.Dotted,
            title: line.label,
          });
          const lineData = [{ time: line.start_date, value: line.start_price }, { time: line.end_date, value: line.end_price }].filter(p => p.value !== null);
          if (lineData.length === 2) tlSeries.setData(lineData);
        });
      }

      // Spread the bars across the full width (fixes the large empty gap on the
      // left where bars were packed against the right edge at default spacing).
      chart.timeScale().fitContent();

      // Compact legend so the markers can stay text-free.
      chartContainer.style.position = 'relative';
      const legend = document.createElement('div');
      legend.className = 'ams-chart-legend';
      legend.innerHTML =
        '<span><i style="color:#ef5350">&#9660;</i> Swing High</span>' +
        '<span><i style="color:#26a69a">&#9650;</i> Swing Low</span>' +
        '<span><i style="color:#ff9800">&#9679;</i> Liquidity sweep</span>' +
        '<span><i style="color:#2962FF">&#9472;</i> VWAP</span>';
      chartContainer.appendChild(legend);

      const fitAndResize = () => {
        if (chartContainer.clientWidth > 0) {
          chart.resize(chartContainer.clientWidth, 600);
          chart.timeScale().fitContent();
        }
      };
      window.addEventListener('resize', fitAndResize);

      // Re-fit whenever the tab becomes visible (it may render at 0 width while hidden).
      const tabButton = document.querySelector('[data-bs-target="#support-resistance-pane"]');
      if (tabButton) {
        tabButton.addEventListener('shown.bs.tab', () => {
          setTimeout(fitAndResize, 50);
        });
      }
    };

    setupRrgToolbar();
    drawRrgChart();
    drawAdvancedMarketStructureChart();
    setupRrgIndicesToolbar();
    drawRrgIndicesChart();
  });
