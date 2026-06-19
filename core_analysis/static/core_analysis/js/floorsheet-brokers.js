/* ============================================================================
   Dalal Street X broker analytics — frontend controller.
   Reads bootstrap meta (brokers/symbols/sectors), drives 5 tabs, each backed by
   a JSON endpoint under /floorsheet/api/*. Tables + squarified treemap are
   rendered by hand; the 90-day trend uses Chart.js (bar qty + line close).
   ========================================================================== */
(function () {
  "use strict";

  var META = window.DSX_BOOTSTRAP || { brokers: [], symbols: [], sectors: [] };
  var API = "/floorsheet/api/";

  // ── formatting ───────────────────────────────────────────────────────
  function nf(n) { return (n == null ? 0 : n).toLocaleString("en-IN"); }
  function fmtQty(n) { return nf(Math.round(n || 0)); }
  function fmtRs(n) { return "Rs. " + nf(Math.round(n || 0)); }
  function fmtPrice(n) {
    return "Rs. " + (n || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function fmtPct(n) { return (n || 0).toFixed(2) + "%"; }
  // Compact Rs in NEPSE numbering (crore / lakh) for KPI tiles.
  function fmtRsCompact(n) {
    var v = Math.round(n || 0), s = v < 0 ? "-" : "", a = Math.abs(v);
    if (a >= 1e7) return s + "Rs " + (a / 1e7).toFixed(2) + " Cr";
    if (a >= 1e5) return s + "Rs " + (a / 1e5).toFixed(2) + " L";
    return fmtRs(v);
  }
  function el(id) { return document.getElementById(id); }

  var inflight = {};
  function getJSON(path, params, key) {
    var qs = new URLSearchParams(params || {}).toString();
    var options = { headers: { Accept: "application/json" } };
    var controller = null;
    if (key && window.AbortController) {
      if (inflight[key]) inflight[key].abort();
      controller = new AbortController();
      inflight[key] = controller;
      options.signal = controller.signal;
    }
    return fetch(API + path + (qs ? "?" + qs : ""), options)
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (d) {
        if (controller && inflight[key] === controller) delete inflight[key];
        return d;
      }, function (err) {
        if (controller && inflight[key] === controller) delete inflight[key];
        throw err;
      });
  }
  function isAbort(err) { return err && err.name === "AbortError"; }

  function loading(table, cols) {
    table.innerHTML = '<tbody><tr><td colspan="' + cols + '" class="dsx-loading">Loading…</td></tr></tbody>';
  }
  function empty(table, cols, msg) {
    table.innerHTML = '<tbody><tr><td colspan="' + cols + '" class="dsx-empty">' + (msg || "No data") + "</td></tr></tbody>";
  }

  // ── populate dropdowns ────────────────────────────────────────────────
  function fillBrokers(sel) {
    sel.innerHTML = "";
    (META.brokers || []).forEach(function (b) {
      var o = document.createElement("option");
      o.value = b; o.textContent = b;
      sel.appendChild(o);
    });
  }
  function fillSymbols(sel) {
    sel.innerHTML = "";
    (META.symbols || []).forEach(function (s) {
      var o = document.createElement("option");
      o.value = s.symbol;
      o.textContent = s.name && s.name !== s.symbol ? s.name + " ( " + s.symbol + " )" : s.symbol;
      sel.appendChild(o);
    });
  }
  function fillSectors(sel) {
    sel.innerHTML = '<option value="All">All</option>';
    (META.sectors || []).forEach(function (s) {
      var o = document.createElement("option");
      o.value = s; o.textContent = s;
      sel.appendChild(o);
    });
  }

  // ── segmented control helper ──────────────────────────────────────────
  // group => current value, with onChange callback.
  function segGroup(name, onChange) {
    var wrap = document.querySelector('[data-group="' + name + '"]');
    var state = { value: null };
    if (!wrap) return state;
    var pills = wrap.querySelectorAll(".dsx-pill");
    pills.forEach(function (p) {
      if (p.classList.contains("active")) state.value = p.dataset.val;
      p.addEventListener("click", function () {
        pills.forEach(function (q) { q.classList.remove("active"); });
        p.classList.add("active");
        state.value = p.dataset.val;
        onChange(state.value);
      });
    });
    return state;
  }

  function assign(dst, src) {
    for (var k in src) { if (Object.prototype.hasOwnProperty.call(src, k)) dst[k] = src[k]; }
    return dst;
  }

  // ── shared date-range control ─────────────────────────────────────────
  // Preset dropdown (Current Day / Last Week / Month / 3M / Custom Range) with
  // Start/End inputs and an Analyze button, namespaced by `prefix`. Presets fill
  // read-only Start/End and apply immediately; "Custom Range" enables the inputs
  // and applies on Analyze. params() yields the query params for the request.
  var _dateRanges = [];
  function dateRange(prefix, onApply) {
    var preset = el(prefix + "-preset"),
        startI = el(prefix + "-start"),
        endI = el(prefix + "-end"),
        analyze = el(prefix + "-analyze");
    var state = { range: "today", start: null, end: null };
    var SPANS = { today: 1, "1w": 7, "1m": 30, "3m": 90 };

    function addDays(iso, n) {
      var p = (iso || "").split("-");
      if (p.length !== 3) return iso || "";
      var d = new Date(+p[0], +p[1] - 1, +p[2]);
      d.setDate(d.getDate() + n);
      return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2);
    }
    function presetWindow(val) {
      var L = META.latest_date;
      if (!L) return { start: "", end: "" };
      return { start: addDays(L, -((SPANS[val] || 1) - 1)), end: L };
    }
    function setMax() {
      if (!META.latest_date) return;
      if (startI) startI.max = META.latest_date;
      if (endI) endI.max = META.latest_date;
    }
    function setDisabled(on) {
      if (startI) startI.disabled = on;
      if (endI) endI.disabled = on;
    }
    function apply(val, fire) {
      if (val === "custom") {
        setDisabled(false);
        if (startI && !startI.value) {
          var seed = presetWindow("today");
          startI.value = seed.start; if (endI) endI.value = seed.end;
        }
        state.range = "custom";
        state.start = startI ? startI.value : null;
        state.end = endI ? endI.value : null;
        return;                 // wait for Analyze
      }
      setDisabled(true);
      var w = presetWindow(val);
      if (startI) startI.value = w.start;
      if (endI) endI.value = w.end;
      state.range = val; state.start = w.start; state.end = w.end;
      if (fire) onApply();
    }

    if (preset) preset.addEventListener("change", function () { apply(this.value, true); });
    if (analyze) analyze.addEventListener("click", function () {
      if (state.range === "custom") {
        state.start = startI ? startI.value : null;
        state.end = endI ? endI.value : null;
      }
      onApply();
    });

    setMax();
    apply("today", false);      // seed defaults; caller fires the first load

    var ctrl = {
      refresh: function () { setMax(); if (state.range !== "custom") apply(state.range, false); },
      params: function () {
        return state.range === "custom"
          ? { range: "custom", start_date: state.start || "", end_date: state.end || "" }
          : { range: state.range };
      }
    };
    _dateRanges.push(ctrl);
    return ctrl;
  }
  function refreshDateRanges() { _dateRanges.forEach(function (d) { d.refresh(); }); }

  // ── tab switching ─────────────────────────────────────────────────────
  var loaded = {};
  function activateTab(name) {
    document.querySelectorAll(".dsx-tab").forEach(function (t) {
      t.classList.toggle("active", t.dataset.tab === name);
    });
    document.querySelectorAll(".dsx-panel").forEach(function (p) {
      p.classList.toggle("active", p.id === "panel-" + name);
    });
    if (TABS[name] && !loaded[name]) { loaded[name] = true; TABS[name].init(); }
    if (TABS[name]) TABS[name].load();
  }

  // ── sortable tables ───────────────────────────────────────────────────
  // Click a column header to sort by that column (numeric desc / text asc on
  // first click, toggles thereafter). Sort state is kept per table id and
  // survives data reloads. Each builder renders its header via sortableHead and
  // is mounted through showTable, which re-sorts + re-draws on header clicks.
  var _tables = {};

  function sortRows(rows, key, dir, type) {
    var out = rows.slice();
    var sign = dir === "asc" ? 1 : -1;
    out.sort(function (a, b) {
      var av = a[key], bv = b[key];
      if (type === "num") return sign * ((+av || 0) - (+bv || 0));
      av = (av == null ? "" : String(av)).toUpperCase();
      bv = (bv == null ? "" : String(bv)).toUpperCase();
      return av < bv ? -sign : av > bv ? sign : 0;
    });
    return out;
  }

  // cols: [{label, key?, type?, cls?}]. Omit key for a non-sortable column.
  function sortableHead(tableId, cols) {
    var st = _tables[tableId] && _tables[tableId].sort;
    var cells = cols.map(function (c) {
      var cls = c.cls || "";
      if (!c.key) return "<th" + (cls ? " class='" + cls + "'" : "") + ">" + c.label + "</th>";
      var arrow = "";
      if (st && st.key === c.key) { cls += " sorted"; arrow = st.dir === "asc" ? " ▲" : " ▼"; }
      cls = ("sortable " + cls).trim();
      return "<th class='" + cls + "' data-sort='" + c.key + "' data-type='" + (c.type || "str") +
        "'>" + c.label + "<span class='dsx-arrow'>" + arrow + "</span></th>";
    }).join("");
    return "<thead><tr>" + cells + "</tr></thead>";
  }

  // Class suffix + arrow markup for a custom-built sortable header cell.
  function _sortMark(tableId, key) {
    var st = _tables[tableId] && _tables[tableId].sort;
    var on = st && st.key === key;
    return { cls: on ? " sorted" : "", arrow: "<span class='dsx-arrow'>" + (on ? (st.dir === "asc" ? " ▲" : " ▼") : "") + "</span>" };
  }

  function _drawTable(reg) {
    var rows = reg.rows || [];
    if (reg.sort && reg.sort.key) rows = sortRows(rows, reg.sort.key, reg.sort.dir, reg.sort.type);
    reg.build(reg.table, rows);
  }

  // Mount/refresh a sortable table. `build(table, sortedRows)` renders it.
  function showTable(table, rows, build) {
    var reg = _tables[table.id];
    if (!reg) {
      reg = _tables[table.id] = { table: table, sort: null };
      table.addEventListener("click", function (e) {
        var th = e.target.closest ? e.target.closest("th[data-sort]") : null;
        if (!th || !table.contains(th)) return;
        var key = th.getAttribute("data-sort"), type = th.getAttribute("data-type") || "str";
        if (reg.sort && reg.sort.key === key) {
          reg.sort = { key: key, dir: reg.sort.dir === "asc" ? "desc" : "asc", type: type };
        } else {
          reg.sort = { key: key, dir: type === "num" ? "desc" : "asc", type: type };
        }
        _drawTable(reg);
      });
    }
    reg.rows = rows;
    reg.build = build;
    _drawTable(reg);
  }

  // ── table builders ────────────────────────────────────────────────────
  var FAV_COLS = [
    { label: "No." },
    { label: "Ticker", key: "key", type: "str", cls: "l" },
    { label: "Quantity", key: "quantity", type: "num" },
    { label: "Amount (Rs)", key: "amount", type: "num" },
    { label: "Average Price (Rs)", key: "avg_price", type: "num" },
    { label: "% Of Total Transactions", key: "pct", type: "num" }
  ];
  function buildFavTable(table, rows) {
    if (!rows || !rows.length) { empty(table, 6); return; }
    var maxPct = rows.reduce(function (m, r) { return Math.max(m, r.pct || 0); }, 0) || 1;
    var body = rows.map(function (r, i) {
      var ratio = Math.max(0, Math.min(1, (r.pct || 0) / maxPct));
      var bar = "<span class='dsx-pctbar' style='width:calc((100% - 24px) * " + ratio.toFixed(3) + ")'></span>";
      return "<tr data-key='" + r.key + "'><td>" + (i + 1) + "</td><td class='l tkr'>" + r.key + "</td><td>" +
        fmtQty(r.quantity) + "</td><td>" + fmtRs(r.amount) + "</td><td>" +
        fmtPrice(r.avg_price) + "</td><td class='dsx-pctcell'>" + bar +
        "<span class='dsx-pctnum'>" + fmtPct(r.pct) + "</span></td></tr>";
    }).join("");
    table.innerHTML = sortableHead(table.id, FAV_COLS) + "<tbody>" + body + "</tbody>";
  }

  var BROKER_COLS = [
    { label: "Broker", key: "key", type: "str", cls: "l" },
    { label: "Quantity", key: "quantity", type: "num" },
    { label: "Amount (Rs)", key: "amount", type: "num" },
    { label: "Average Price (Rs)", key: "avg_price", type: "num" },
    { label: "% Of Total", key: "pct", type: "num" }
  ];
  function buildBrokerTable(table, rows) {
    if (!rows || !rows.length) { empty(table, 5); return; }
    var body = rows.map(function (r) {
      return "<tr><td class='l tkr'>" + r.key + "</td><td>" + fmtQty(r.quantity) + "</td><td>" +
        fmtRs(r.amount) + "</td><td>" + fmtPrice(r.avg_price) + "</td><td>" + fmtPct(r.pct) + "</td></tr>";
    }).join("");
    table.innerHTML = sortableHead(table.id, BROKER_COLS) + "<tbody>" + body + "</tbody>";
  }

  var HOLD_COLS = [
    { label: "Broker", key: "key", type: "str", cls: "l" },
    { label: "Net Qty", key: "quantity", type: "num" },
    { label: "Avg Buy (Rs)", key: "avg_buy", type: "num" },
    { label: "Avg Sell (Rs)", key: "avg_sell", type: "num" }
  ];
  function buildHoldTable(table, rows) {
    if (!rows || !rows.length) { empty(table, 4); return; }
    var body = rows.map(function (r) {
      var cls = r.quantity >= 0 ? "num-pos" : "num-neg";
      return "<tr><td class='l tkr'>" + r.key + "</td><td class='" + cls + "'>" + fmtQty(r.quantity) +
        "</td><td>" + fmtPrice(r.avg_buy) + "</td><td>" + fmtPrice(r.avg_sell) + "</td></tr>";
    }).join("");
    table.innerHTML = sortableHead(table.id, HOLD_COLS) + "<tbody>" + body + "</tbody>";
  }

  // ── trend chart (shared) ──────────────────────────────────────────────
  var charts = {};
  var chartLoader = null;
  function ensureChart() {
    if (window.Chart) return Promise.resolve(true);
    if (chartLoader) return chartLoader;
    chartLoader = new Promise(function (resolve) {
      var s = document.createElement("script");
      s.src = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js";
      s.async = true;
      s.onload = function () { resolve(true); };
      s.onerror = function () { resolve(false); };
      document.head.appendChild(s);
    });
    return chartLoader;
  }
  function renderTrend(canvasId, data) {
    var cv = el(canvasId);
    if (!cv) return;
    var pts = (data && data.points) || [];
    var labels = pts.map(function (p) { return p.date; });
    var qty = pts.map(function (p) { return p.quantity; });
    var close = pts.map(function (p) { return p.close; });
    ensureChart().then(function (ok) {
      if (!ok || !window.Chart) return;
      if (charts[canvasId]) charts[canvasId].destroy();
      charts[canvasId] = new Chart(cv.getContext("2d"), {
        data: {
          labels: labels,
          datasets: [
            { type: "bar", label: "Traded Qty", data: qty, yAxisID: "y",
              backgroundColor: "rgba(94,201,143,.55)", borderColor: "rgba(94,201,143,.9)", borderWidth: 1 },
            { type: "line", label: "Close", data: close, yAxisID: "y1",
              borderColor: "#3f8cff", backgroundColor: "#3f8cff", tension: .25,
              pointRadius: 0, borderWidth: 2, spanGaps: true }
          ]
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          plugins: { legend: { labels: { color: "#9bb0d3", boxWidth: 12 } } },
          scales: {
            x: { ticks: { color: "#6f88ad", maxTicksLimit: 14, autoSkip: true }, grid: { display: false } },
            y: { position: "left", ticks: { color: "#6f88ad" }, grid: { color: "rgba(120,150,200,.08)" } },
            y1: { position: "right", ticks: { color: "#6f88ad" }, grid: { display: false } }
          }
        }
      });
    });
  }

  // ─────────────────────────────────────────────────────────────────────
  // TAB: Broker Favorites
  // ─────────────────────────────────────────────────────────────────────
  var favState = { brokers: [], trendSide: "buy", trendSym: null, dr: null };
  var TABS = {};

  TABS.favorites = {
    init: function () {
      // Multi-select brokers: default to the first broker selected.
      var first = (META.brokers || [])[0];
      favState.brokers = first != null ? [String(first)] : [];
      buildBrokerMulti(function () { TABS.favorites.load(); });
      favState.dr = dateRange("fav", function () { TABS.favorites.load(); });
      segGroup("fav-trend-side", function (v) { favState.trendSide = v; TABS.favorites.loadTrend(); });
      // Row click selects that ticker for the trend (delegated so it survives
      // table re-renders from sorting).
      wireFavSelect(el("fav-buy"));
      wireFavSelect(el("fav-sell"));
      // A/D rows pick the trend ticker too (delegated; survives re-renders).
      var ad = el("fav-ad");
      if (ad) ad.addEventListener("click", function (e) {
        var row = e.target.closest ? e.target.closest(".dsx-ad-row[data-key]") : null;
        if (!row || !ad.contains(row)) return;
        favState.trendSym = row.getAttribute("data-key");
        TABS.favorites.loadTrend();
      });
    },
    load: function () {
      if (!favState.brokers.length) {
        empty(el("fav-buy"), 6, "Select a broker"); empty(el("fav-sell"), 6, "Select a broker");
        renderFavKpis(null);
        if (el("fav-ad")) el("fav-ad").innerHTML = '<div class="dsx-empty">Select a broker</div>';
        if (el("fav-ad-sub")) el("fav-ad-sub").textContent = "";
        return;
      }
      loading(el("fav-buy"), 6); loading(el("fav-sell"), 6);
      var params = assign({ brokers: favState.brokers.join(",") }, favState.dr.params());
      getJSON("favorites/", params, "favorites")
        .then(function (d) {
          renderFavKpis(d);
          showTable(el("fav-buy"), d.buy, buildFavTable);
          showTable(el("fav-sell"), d.sell, buildFavTable);
          if (!favState.trendSym && d.buy && d.buy.length) favState.trendSym = d.buy[0].key;
          TABS.favorites.loadTrend();
        })
        .catch(function (err) { if (isAbort(err)) return; empty(el("fav-buy"), 6, "Error"); empty(el("fav-sell"), 6, "Error"); });
      TABS.favorites.loadPersistence();
    },
    loadPersistence: function () {
      var box = el("fav-ad");
      if (!box) return;
      box.innerHTML = '<div class="dsx-loading">Loading…</div>';
      getJSON("persistence/", { brokers: favState.brokers.join(","), lookback: "1m" }, "fav-persist")
        .then(renderPersistence)
        .catch(function (err) { if (isAbort(err)) return; box.innerHTML = '<div class="dsx-empty">Error</div>'; });
    },
    loadTrend: function () {
      if (!favState.trendSym) return;
      el("fav-trend-sym").textContent = favState.trendSym;
      getJSON("trend/", { symbol: favState.trendSym, side: favState.trendSide }, "fav-trend")
        .then(function (d) { renderTrend("fav-trend-chart", d); })
        .catch(function () {});
    }
  };
  function wireFavSelect(table) {
    if (!table) return;
    table.style.cursor = "pointer";
    table.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest("th")) return;   // header clicks sort
      var tr = e.target.closest ? e.target.closest("tr[data-key]") : null;
      if (!tr || !table.contains(tr)) return;
      favState.trendSym = tr.getAttribute("data-key");
      TABS.favorites.loadTrend();
    });
  }

  // KPI strip: the selected desk's stance, all derived from the favorites/
  // response (no extra request). Buy/sell turnover, net flow, breadth, and the
  // single most-concentrated position.
  function renderFavKpis(d) {
    var box = el("fav-kpis");
    if (!box) return;
    if (!d || (!((d.buy || []).length) && !((d.sell || []).length))) { box.innerHTML = ""; return; }
    var buy = d.buy || [], sell = d.sell || [];
    var sum = function (rows, k) { return rows.reduce(function (s, r) { return s + (r[k] || 0); }, 0); };
    var buyAmt = sum(buy, "amount"), sellAmt = sum(sell, "amount");
    var net = buyAmt - sellAmt;
    var stocks = {};
    buy.forEach(function (r) { stocks[r.key] = 1; });
    sell.forEach(function (r) { stocks[r.key] = 1; });
    var top = { pct: 0, key: "—", side: "" };
    buy.forEach(function (r) { if ((r.pct || 0) > top.pct) top = { pct: r.pct, key: r.key, side: "buy" }; });
    sell.forEach(function (r) { if ((r.pct || 0) > top.pct) top = { pct: r.pct, key: r.key, side: "sell" }; });

    function tile(label, val, sub, cls) {
      return "<div class='dsx-kpi'><span class='dsx-kpi-label'>" + label + "</span>" +
        "<span class='dsx-kpi-val " + (cls || "") + "'>" + val + "</span>" +
        "<span class='dsx-kpi-sub'>" + (sub || "") + "</span></div>";
    }
    box.innerHTML =
      tile("Buy Turnover", fmtRsCompact(buyAmt), buy.length + " stocks", "num-pos") +
      tile("Sell Turnover", fmtRsCompact(sellAmt), sell.length + " stocks", "num-neg") +
      tile("Net Flow", (net >= 0 ? "+" : "") + fmtRsCompact(net),
           net >= 0 ? "Net accumulating" : "Net distributing", net >= 0 ? "num-pos" : "num-neg") +
      tile("Stocks Touched", nf(Object.keys(stocks).length), "buy ∪ sell side") +
      tile("Top Concentration", fmtPct(top.pct),
           top.key + " · " + (top.side === "sell" ? "sell" : "buy"), top.side === "sell" ? "num-neg" : "num-pos");
  }

  // Persistent Accumulation / Distribution: multi-session net per stock for the
  // selected desk, with a conviction streak (consecutive same-side sessions) and
  // an all-broker concentration read (HHI). Diverging bar = cumulative net qty.
  function renderPersistence(d) {
    var box = el("fav-ad"), sub = el("fav-ad-sub");
    if (!box) return;
    var rows = (d && d.rows) || [];
    if (sub) sub.textContent = d && d.days ? ("Last " + d.days + " sessions · click a row to chart it") : "";
    if (!rows.length) { box.innerHTML = "<div class='dsx-empty'>No multi-day positions</div>"; return; }
    var maxAbs = rows.reduce(function (m, r) { return Math.max(m, Math.abs(r.cum_net || 0)); }, 0) || 1;
    box.innerHTML = rows.map(function (r) {
      var pos = r.cum_net >= 0;
      var w = (50 * Math.abs(r.cum_net || 0) / maxAbs).toFixed(2);   // half-track %
      var fill = "<span class='dsx-ad-fill " + (pos ? "buy" : "sell") + "' style='width:" + w + "%'></span>";
      var arrow = r.side === "buy" ? "▲" : r.side === "sell" ? "▼" : "–";
      var streakCls = r.side === "buy" ? "buy" : r.side === "sell" ? "sell" : "flat";
      var streak = "<span class='dsx-streak " + streakCls + "' title='" + r.buy_days + " buy / " +
        r.sell_days + " sell sessions of " + r.active_days + " active'>" + arrow + " " + r.streak + "d</span>";
      var dom = r.dominant ? ("Broker " + r.dominant.broker + " " + fmtPct(r.dominant.pct)) : "—";
      var hhi = "<span class='dsx-hhi risk-" + (r.risk || "low") + "' title='Concentration (HHI) " +
        nf(r.hhi) + " · dominant " + dom + "'>" + nf(r.hhi) + "</span>";
      return "<div class='dsx-ad-row' data-key='" + r.symbol + "'>" +
        "<span class='dsx-ad-sym'>" + r.symbol + "</span>" + streak +
        "<span class='dsx-ad-track'>" + fill + "</span>" +
        "<span class='dsx-ad-net " + (pos ? "num-pos" : "num-neg") + "'>" +
          (pos ? "+" : "") + fmtQty(r.cum_net) + "</span>" + hhi + "</div>";
    }).join("");
  }

  // Multi-select broker checklist (button + searchable checkbox menu).
  function buildBrokerMulti(onChange) {
    var btn = el("fav-broker-btn"), menu = el("fav-broker-menu"),
        list = el("fav-broker-list"), search = el("fav-broker-search");
    if (!btn || !menu || !list) return;

    function syncLabel() {
      var n = favState.brokers.length;
      btn.textContent = (n === 0 ? "Select brokers"
        : n === 1 ? "Broker " + favState.brokers[0]
        : n + " brokers selected") + " ▾";
    }
    function render(filter) {
      list.innerHTML = "";
      (META.brokers || []).forEach(function (b) {
        var bs = String(b);
        if (filter && bs.indexOf(filter) === -1) return;
        var lbl = document.createElement("label");
        lbl.className = "dsx-multi-opt";
        var cb = document.createElement("input");
        cb.type = "checkbox"; cb.value = bs;
        cb.checked = favState.brokers.indexOf(bs) !== -1;
        cb.addEventListener("change", function () {
          if (cb.checked) { if (favState.brokers.indexOf(bs) === -1) favState.brokers.push(bs); }
          else { favState.brokers = favState.brokers.filter(function (x) { return x !== bs; }); }
          syncLabel(); onChange();
        });
        lbl.appendChild(cb);
        lbl.appendChild(document.createTextNode(" " + bs));
        list.appendChild(lbl);
      });
    }

    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      menu.hidden = !menu.hidden;
      if (!menu.hidden) { render(search.value.trim()); search.focus(); }
    });
    menu.addEventListener("click", function (e) { e.stopPropagation(); });
    document.addEventListener("click", function () { menu.hidden = true; });
    search.addEventListener("input", function () { render(search.value.trim()); });
    menu.querySelectorAll(".dsx-multi-actions button").forEach(function (b) {
      b.addEventListener("click", function () {
        if (b.dataset.act === "all") {
          favState.brokers = (META.brokers || []).map(String);
        } else {
          favState.brokers = [];
        }
        render(search.value.trim()); syncLabel(); onChange();
      });
    });

    syncLabel();
  }

  // ─────────────────────────────────────────────────────────────────────
  // TAB: Stock Wise Details
  // ─────────────────────────────────────────────────────────────────────
  var swState = { symbol: null, trendSide: "buy", dr: null };
  TABS.stockwise = {
    init: function () {
      fillSymbols(el("sw-symbol"));
      swState.symbol = el("sw-symbol").value || ((META.symbols || [])[0] || {}).symbol;
      el("sw-symbol").addEventListener("change", function () { swState.symbol = this.value; TABS.stockwise.load(); });
      swState.dr = dateRange("sw", function () { TABS.stockwise.load(); });
      segGroup("sw-trend-side", function (v) { swState.trendSide = v; TABS.stockwise.loadTrend(); });
    },
    load: function () {
      if (!swState.symbol) { empty(el("sw-buy"), 5, "No symbols"); return; }
      loading(el("sw-buy"), 5); loading(el("sw-sell"), 5); loading(el("sw-hold"), 4);
      getJSON("stockwise/", assign({ symbol: swState.symbol }, swState.dr.params()), "stockwise")
        .then(function (d) {
          showTable(el("sw-buy"), d.buy, buildBrokerTable);
          showTable(el("sw-sell"), d.sell, buildBrokerTable);
          showTable(el("sw-hold"), d.holdings, buildHoldTable);
          TABS.stockwise.loadTrend();
        })
        .catch(function (err) { if (isAbort(err)) return; empty(el("sw-buy"), 5, "Error"); empty(el("sw-sell"), 5, "Error"); empty(el("sw-hold"), 4, "Error"); });
    },
    loadTrend: function () {
      if (!swState.symbol) return;
      el("sw-trend-sym").textContent = swState.symbol;
      getJSON("trend/", { symbol: swState.symbol, side: swState.trendSide }, "sw-trend")
        .then(function (d) { renderTrend("sw-trend-chart", d); })
        .catch(function () {});
    }
  };

  // ─────────────────────────────────────────────────────────────────────
  // TAB: Hotstocks
  // ─────────────────────────────────────────────────────────────────────
  var hotState = { sector: "All", dr: null };
  TABS.hotstocks = {
    init: function () {
      fillSectors(el("hot-sector"));
      el("hot-sector").addEventListener("change", function () { hotState.sector = this.value; TABS.hotstocks.load(); });
      hotState.dr = dateRange("hot", function () { TABS.hotstocks.load(); });
    },
    load: function () {
      var t = el("hot-table");
      loading(t, 10);
      getJSON("hotstocks/", assign({ sector: hotState.sector }, hotState.dr.params()), "hotstocks")
        .then(function (d) {
          showTable(t, d.rows || [], buildHotTable);
        })
        .catch(function (err) { if (isAbort(err)) return; empty(t, 10, "Error"); });
    }
  };

  var HOT_COLS = [
    { label: "No." },
    { label: "Ticker", key: "symbol", type: "str", cls: "l" },
    { label: "Sector", key: "sector", type: "str", cls: "l" },
    { label: "Quantity", key: "quantity", type: "num" },
    { label: "Amount (Rs)", key: "amount", type: "num" },
    { label: "Avg Price", key: "avg_price", type: "num" },
    { label: "Buyers", key: "buyers", type: "num" },
    { label: "Sellers", key: "sellers", type: "num" },
    { label: "Top Buy" },
    { label: "Top Sell" }
  ];
  function buildHotTable(table, rows) {
    if (!rows || !rows.length) { empty(table, 10); return; }
    var body = rows.map(function (r, i) {
      var tb = r.top_buy ? r.top_buy.broker + " (" + fmtPct(r.top_buy.pct) + ")" : "—";
      var ts = r.top_sell ? r.top_sell.broker + " (" + fmtPct(r.top_sell.pct) + ")" : "—";
      return "<tr><td>" + (i + 1) + "</td><td class='l tkr'>" + r.symbol + "</td><td class='l'>" +
        (r.sector || "") + "</td><td>" + fmtQty(r.quantity) + "</td><td>" + fmtRs(r.amount) +
        "</td><td>" + fmtPrice(r.avg_price) + "</td><td>" + r.buyers + "</td><td>" + r.sellers +
        "</td><td class='num-pos'>" + tb + "</td><td class='num-neg'>" + ts + "</td></tr>";
    }).join("");
    table.innerHTML = sortableHead(table.id, HOT_COLS) + "<tbody>" + body + "</tbody>";
  }

  // ─────────────────────────────────────────────────────────────────────
  // TAB: Net Holding (treemap)
  // ─────────────────────────────────────────────────────────────────────
  var nhState = { broker: null, excludeMf: false, sector: "All", dr: null };
  TABS.netholding = {
    init: function () {
      fillBrokers(el("nh-broker"));
      fillSectors(el("nh-sector"));
      nhState.broker = el("nh-broker").value || (META.brokers || [])[0];
      el("nh-broker").addEventListener("change", function () { nhState.broker = this.value; TABS.netholding.load(); });
      el("nh-sector").addEventListener("change", function () { nhState.sector = this.value; TABS.netholding.load(); });
      el("nh-exclude-mf").addEventListener("change", function () { nhState.excludeMf = this.checked; TABS.netholding.load(); });
      nhState.dr = dateRange("nh", function () { TABS.netholding.load(); });
    },
    load: function () {
      var box = el("nh-treemap");
      box.innerHTML = '<div class="dsx-loading">Loading…</div>';
      if (!nhState.broker) { box.innerHTML = '<div class="dsx-empty">No brokers</div>'; return; }
      getJSON("netholding/", assign({
        broker: nhState.broker,
        exclude_mf: nhState.excludeMf ? 1 : 0, sector: nhState.sector
      }, nhState.dr.params()), "netholding").then(function (d) {
        renderTreemap(box, (d.items || []));
      }).catch(function (err) { if (isAbort(err)) return; box.innerHTML = '<div class="dsx-empty">Error</div>'; });
    }
  };

  // Squarified treemap (Bruls, Huizing, van Wijk).
  function renderTreemap(box, items) {
    box.innerHTML = "";
    if (!items.length) { box.innerHTML = '<div class="dsx-empty">No net positions</div>'; return; }
    var W = box.clientWidth || 1000, H = box.clientHeight || 640;
    var total = items.reduce(function (s, it) { return s + it.size; }, 0) || 1;
    var scale = (W * H) / total;
    var data = items.map(function (it) { return { it: it, area: it.size * scale }; });

    var x = 0, y = 0, w = W, h = H, i = 0;
    function worst(row, len) {
      var sum = 0, mn = Infinity, mx = 0;
      for (var k = 0; k < row.length; k++) { sum += row[k].area; mn = Math.min(mn, row[k].area); mx = Math.max(mx, row[k].area); }
      var s2 = sum * sum, l2 = len * len;
      return Math.max((l2 * mx) / s2, s2 / (l2 * mn));
    }
    function layoutRow(row, len, horiz) {
      var sum = row.reduce(function (s, r) { return s + r.area; }, 0);
      var thick = sum / len;
      var off = 0;
      row.forEach(function (r) {
        var side = r.area / thick;
        var cx, cy, cw, ch;
        if (horiz) { cx = x; cy = y + off; cw = thick; ch = side; }
        else { cx = x + off; cy = y; cw = side; ch = thick; }
        drawCell(box, r.it, cx, cy, cw, ch);
        off += side;
      });
      if (horiz) { x += thick; w -= thick; } else { y += thick; h -= thick; }
    }

    var row = [];
    while (i < data.length) {
      var horiz = w >= h;     // lay along the shorter side
      var len = horiz ? h : w;
      var withNew = row.concat([data[i]]);
      if (row.length === 0 || worst(row, len) >= worst(withNew, len)) {
        row = withNew; i++;
      } else {
        layoutRow(row, len, horiz); row = [];
      }
    }
    if (row.length) layoutRow(row, (w >= h ? h : w), w >= h);
    mountTreemapTip(box);
  }

  function drawCell(box, it, x, y, w, h) {
    var d = document.createElement("div");
    d.className = "dsx-tm-cell " + (it.side === "buy" ? "buy" : "sell");
    d.style.left = x + "px"; d.style.top = y + "px";
    d.style.width = Math.max(0, w - 1) + "px"; d.style.height = Math.max(0, h - 1) + "px";
    // Data for the hover/tap tooltip (buy / sell / net shares).
    d.setAttribute("data-sym", it.symbol);
    d.setAttribute("data-buy", it.buy != null ? it.buy : 0);
    d.setAttribute("data-sell", it.sell != null ? it.sell : 0);
    d.setAttribute("data-net", it.net);
    // Native title as an accessible fallback.
    d.title = it.symbol + " — Buy " + nf(it.buy || 0) + " / Sell " + nf(it.sell || 0) +
      " / Net " + (it.net > 0 ? "+" : "") + nf(it.net);
    if (w > 34 && h > 18) {
      var fs = Math.max(9, Math.min(15, Math.sqrt(w * h) / 6));
      d.innerHTML = '<span class="dsx-tm-label" style="font-size:' + fs + 'px">' + it.symbol + "</span>";
    }
    box.appendChild(d);
  }

  // Hover/tap tooltip for the treemap: shows Buy / Sell / Net for a cell. Box
  // listeners are wired once; the tip node is re-appended after each re-render
  // (renderTreemap clears box.innerHTML).
  function mountTreemapTip(box) {
    var tip = box._dsxTip;
    if (!tip) {
      tip = box._dsxTip = document.createElement("div");
      tip.className = "dsx-tm-tip";
      tip.hidden = true;

      var show = function (cell, clientX, clientY) {
        var net = +cell.getAttribute("data-net") || 0;
        tip.innerHTML =
          '<div class="dsx-tm-tip-sym">' + cell.getAttribute("data-sym") + '</div>' +
          '<div class="dsx-tm-tip-row"><span>Buy</span><b class="num-pos">' + fmtQty(+cell.getAttribute("data-buy") || 0) + '</b></div>' +
          '<div class="dsx-tm-tip-row"><span>Sell</span><b class="num-neg">' + fmtQty(+cell.getAttribute("data-sell") || 0) + '</b></div>' +
          '<div class="dsx-tm-tip-row net"><span>Net</span><b class="' + (net >= 0 ? "num-pos" : "num-neg") + '">' +
            (net > 0 ? "+" : "") + fmtQty(net) + '</b></div>';
        tip.hidden = false;
        var r = box.getBoundingClientRect();
        var px = clientX - r.left + 14, py = clientY - r.top + 14;
        px = Math.max(6, Math.min(px, r.width - tip.offsetWidth - 6));
        py = Math.max(6, Math.min(py, r.height - tip.offsetHeight - 6));
        tip.style.left = px + "px"; tip.style.top = py + "px";
      };
      var hide = function () { tip.hidden = true; };
      var cellAt = function (e) {
        var c = e.target.closest ? e.target.closest(".dsx-tm-cell") : null;
        return c && box.contains(c) ? c : null;
      };

      box.addEventListener("mousemove", function (e) {
        var c = cellAt(e); if (c) show(c, e.clientX, e.clientY); else hide();
      });
      box.addEventListener("mouseleave", hide);
      // Touch / tap: show for the tapped cell, hide when tapping empty space.
      box.addEventListener("click", function (e) {
        var c = cellAt(e); if (c) show(c, e.clientX, e.clientY); else hide();
      });
    }
    tip.hidden = true;
    box.appendChild(tip);     // re-attach after innerHTML reset
  }

  // ─────────────────────────────────────────────────────────────────────
  // TAB: Broker Concentration
  // ─────────────────────────────────────────────────────────────────────
  var concState = { sector: "All", dr: null };
  TABS.concentration = {
    init: function () {
      fillSectors(el("conc-sector"));
      el("conc-sector").addEventListener("change", function () { concState.sector = this.value; TABS.concentration.load(); });
      concState.dr = dateRange("conc", function () { TABS.concentration.load(); });
    },
    load: function () {
      var t = el("conc-table");
      loading(t, 10);
      getJSON("concentration/", assign({ sector: concState.sector }, concState.dr.params()), "concentration")
        .then(function (d) {
          showTable(t, d.rows || [], buildConcTable);
        })
        .catch(function (err) { if (isAbort(err)) return; empty(t, 10, "Error"); });
    }
  };

  // Grouped two-row header; Ticker / Total Traded / both Sum-Top-3 columns sort.
  function buildConcTable(table, rows) {
    if (!rows || !rows.length) { empty(table, 10); return; }
    var id = table.id;
    var tk = _sortMark(id, "symbol"), tt = _sortMark(id, "total"),
        bs = _sortMark(id, "buy_sum"), ss = _sortMark(id, "sell_sum");
    var head = "<thead>" +
      "<tr><th rowspan='2' class='l sortable" + tk.cls + "' data-sort='symbol' data-type='str'>Ticker" + tk.arrow + "</th>" +
      "<th rowspan='2' class='sortable" + tt.cls + "' data-sort='total' data-type='num'>Total Traded" + tt.arrow + "</th>" +
      "<th colspan='4' class='grp'>Top Broker On Buy Side</th>" +
      "<th colspan='4' class='grp'>Top Broker On Sell Side</th></tr>" +
      "<tr><th class='grp'>1st</th><th>2nd</th><th>3rd</th>" +
      "<th class='sortable" + bs.cls + "' data-sort='buy_sum' data-type='num'>Sum Top 3" + bs.arrow + "</th>" +
      "<th class='grp'>1st</th><th>2nd</th><th>3rd</th>" +
      "<th class='sortable" + ss.cls + "' data-sort='sell_sum' data-type='num'>Sum Top 3" + ss.arrow + "</th></tr></thead>";
    function cell(arr, idx) {
      var b = arr[idx];
      return b ? b.broker + " (" + fmtPct(b.pct) + ")" : "—";
    }
    var body = rows.map(function (r) {
      return "<tr><td class='l tkr'>" + r.symbol + "</td><td>" + fmtQty(r.total) + "</td>" +
        "<td class='grp num-pos'>" + cell(r.buy, 0) + "</td><td class='num-pos'>" + cell(r.buy, 1) +
        "</td><td class='num-pos'>" + cell(r.buy, 2) + "</td><td class='buysum'>" + fmtPct(r.buy_sum) + "</td>" +
        "<td class='grp num-neg'>" + cell(r.sell, 0) + "</td><td class='num-neg'>" + cell(r.sell, 1) +
        "</td><td class='num-neg'>" + cell(r.sell, 2) + "</td><td class='sellsum'>" + fmtPct(r.sell_sum) + "</td></tr>";
    }).join("");
    table.innerHTML = head + "<tbody>" + body + "</tbody>";
  }

  // ── boot ──────────────────────────────────────────────────────────────
  document.querySelectorAll(".dsx-tab").forEach(function (t) {
    t.addEventListener("click", function () { activateTab(t.dataset.tab); });
  });

  function start() {
    var upd = el("fs-updated");
    if (upd && META.latest_date) upd.textContent = "Last Updated On " + META.latest_date;
    var banner = el("dsx-banner");
    if (banner && META.ok) banner.hidden = true;
    activateTab("favorites");
  }

  // If the page was served before today's aggregate was built (cache cold), the
  // bootstrap meta is empty — fetch it now (this triggers the first build) and
  // populate the dropdowns once it lands.
  function hasUsableMeta() {
    return META && ((META.brokers || []).length || (META.symbols || []).length);
  }

  function refreshMeta() {
    getJSON("meta/", {}, "meta")
      .then(function (m) {
        META = m || META;
        var upd = el("fs-updated");
        if (upd && META.latest_date) upd.textContent = "Last Updated On " + META.latest_date;
        var banner = el("dsx-banner");
        if (banner && META.ok) banner.hidden = true;
        refreshDateRanges();
      })
      .catch(function () {});
  }

  if (hasUsableMeta()) {
    start();
    refreshMeta();
  } else {
    var upd = el("fs-updated");
    if (upd) upd.textContent = "Loading floorsheet…";
    getJSON("meta/", {}, "meta")
      .then(function (m) { META = m || META; start(); })
      .catch(function () { start(); });
  }
})();
