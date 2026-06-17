/* ============================================================================
   Technical Analysis terminal — Lightweight Charts edition.

   Reproduces the MetaStock charting window: OHLC bars (or candles/line) with a
   volume pane, and a dropdown to add technical indicators. Price/volume come
   from our UDF history feed (udf_views.py); indicator series are computed
   server-side with pandas_ta (indicator_views.py). "Overlay" indicators (MAs,
   Bollinger, PSAR…) draw on the price chart; "separate" indicators (RSI, MACD,
   ADX…) each open their own synced sub-pane below — like MetaStock's inner
   indicator windows.

   No third-party license required (the TradingView Advanced Charts terminal is
   a separate, optional upgrade).
   ========================================================================== */
(function () {
  "use strict";

  var cfg = window.TA_CONFIG || {};
  var udfHistory = (cfg.udfBase || "/insights/udf") + "/history";
  var udfSearch = (cfg.udfBase || "/insights/udf") + "/search";
  var HISTORY_COUNTBACK = 5000;

  function $(id) { return document.getElementById(id); }
  function cssVar(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function tsToDate(ts) { var d = new Date(ts * 1000); return d.getUTCFullYear() + "-" + pad(d.getUTCMonth() + 1) + "-" + pad(d.getUTCDate()); }

  function palette() {
    return {
      up: cssVar("--up") || "#14b88a",
      down: cssVar("--down") || "#e0414b",
      text: cssVar("--ink-2") || "#888",
      grid: cssVar("--line-soft") || "rgba(120,120,120,0.1)",
      border: cssVar("--line") || "rgba(120,120,120,0.2)"
    };
  }

  function baseOptions(withTimeAxis) {
    var p = palette();
    return {
      autoSize: true,
      layout: { background: { type: "solid", color: "transparent" }, textColor: p.text, fontFamily: "Manrope, sans-serif" },
      grid: { vertLines: { color: p.grid }, horzLines: { color: p.grid } },
      // Fixed gutter width so every pane's plot area is the SAME width — without
      // this each chart sizes its right axis to its own labels (price "3500.00"
      // vs CCI "-250.00"), which shifts the time axes out of vertical alignment.
      rightPriceScale: { borderColor: p.border, minimumWidth: 72 },
      timeScale: { borderColor: p.border, visible: !!withTimeAxis, timeVisible: false, secondsVisible: false, rightOffset: 4 },
      crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
      handleScale: true,
      handleScroll: true
    };
  }

  var state = {
    symbol: cfg.symbol || "NEPSE",
    chartType: "bars",
    main: null,        // main chart
    price: null,       // price series (bar/candle/line)
    volume: null,      // volume histogram
    bars: null,        // raw {t,o,h,l,c,v}
    overlays: {},      // name -> [series,...] on main chart
    panes: {},         // name -> {wrap, chart, series:[...]}
    historyQuery: null,
    syncing: false
  };

  // ── time-scale sync across the main chart and every oscillator pane ────────
  function allCharts() {
    var list = [state.main];
    Object.keys(state.panes).forEach(function (k) { list.push(state.panes[k].chart); });
    return list.filter(Boolean);
  }
  function wireSync(chart) {
    chart.timeScale().subscribeVisibleLogicalRangeChange(function (range) {
      if (state.syncing || !range) return;
      state.syncing = true;
      allCharts().forEach(function (c) {
        if (c !== chart) { try { c.timeScale().setVisibleLogicalRange(range); } catch (e) {} }
      });
      state.syncing = false;
    });
  }

  // ── price chart ────────────────────────────────────────────────────────────
  function makePriceSeries() {
    var p = palette();
    if (state.chartType === "candles") {
      return state.main.addCandlestickSeries({
        upColor: p.up, downColor: p.down, borderUpColor: p.up, borderDownColor: p.down,
        wickUpColor: p.up, wickDownColor: p.down, priceFormat: { type: "price", precision: 2, minMove: 0.01 }
      });
    }
    if (state.chartType === "line") {
      return state.main.addLineSeries({ color: p.up, lineWidth: 2, priceFormat: { type: "price", precision: 2, minMove: 0.01 } });
    }
    // bars (MetaStock default)
    return state.main.addBarSeries({
      upColor: p.up, downColor: p.down, thinBars: false,
      priceFormat: { type: "price", precision: 2, minMove: 0.01 }
    });
  }

  function renderPrice() {
    var b = state.bars, p = palette();
    if (!b) return;
    var price = [], vols = [];
    for (var i = 0; i < b.t.length; i++) {
      var t = tsToDate(b.t[i]);
      if (state.chartType === "line") price.push({ time: t, value: b.c[i] });
      else price.push({ time: t, open: b.o[i], high: b.h[i], low: b.l[i], close: b.c[i] });
      vols.push({ time: t, value: b.v[i], color: (b.c[i] >= b.o[i] ? p.up : p.down) + "80" });
    }
    state.price.setData(price);
    state.volume.setData(vols);
    updateQuote(b.t.length - 1);
  }

  function updateQuote(i) {
    var b = state.bars; if (!b || i < 0) return;
    var el = $("ta-quote"); if (!el) return;
    var chg = b.c[i] - b.o[i];
    el.textContent = state.symbol + "  O " + b.o[i] + "  H " + b.h[i] + "  L " + b.l[i] +
      "  C " + b.c[i] + "  (" + (chg >= 0 ? "+" : "") + chg.toFixed(2) + ")";
  }

  function buildMain() {
    var host = $("ta-price");
    if (state.main) { state.main.remove(); }
    state.main = LightweightCharts.createChart(host, baseOptions(true));
    state.price = makePriceSeries();
    state.volume = state.main.addHistogramSeries({ priceFormat: { type: "volume" }, priceScaleId: "" });
    state.volume.priceScale().applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });
    wireSync(state.main);
    renderPrice();
    // crosshair → live OHLC readout
    state.main.subscribeCrosshairMove(function (param) {
      if (!state.bars) return;
      if (!param || !param.time) {
        updateQuote(state.bars.t.length - 1);
        return;
      }
      // find index by date string
      var t = param.time;
      for (var i = 0; i < state.bars.t.length; i++) {
        if (tsToDate(state.bars.t[i]) === t) {
          updateQuote(i);
          return;
        }
      }
      updateQuote(state.bars.t.length - 1);
    });
  }

  // ── indicators ───────────────────────────────────────────────────────────
  function lineFrom(chart, s) {
    if (s.type === "histogram") {
      var h = chart.addHistogramSeries({ color: s.color, priceFormat: { type: "price", precision: 2, minMove: 0.01 } });
      h.setData(s.data.map(function (d) { return { time: d.time, value: d.value, color: (d.value >= 0 ? "#14b88a" : "#e0414b") + "99" }; }));
      return h;
    }
    var ls = chart.addLineSeries({ color: s.color, lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
    ls.setData(s.data);
    return ls;
  }

  function addIndicator(name) {
    if (!name || state.overlays[name] || state.panes[name]) return;
    var params = new URLSearchParams();
    params.set("symbol", state.symbol);
    params.set("name", name);
    if (state.historyQuery) {
      params.set("to", state.historyQuery.to);
      params.set("countback", state.historyQuery.countback);
    }
    var url = cfg.indicatorUrl + "?" + params.toString();
    fetch(url).then(function (r) { return r.json(); }).then(function (j) {
      if (!j || j.s !== "ok") return;
      var series = alignIndicatorSeries(j.series || []);
      if (!series.length) return;
      if (j.pane === "overlay") {
        state.overlays[name] = series.map(function (s) { return lineFrom(state.main, s); });
      } else {
        addOscPane(name, j.label, series);
      }
      addChip(name, j.label || name);
    }).catch(function () {});
  }

  // A full-length whitespace series so the pane's time domain exactly matches
  // the price chart's. Without it, panes are synced by logical bar index, but
  // each indicator series starts at a different bar (NaN warm-up is dropped),
  // which shifts the pane in time relative to the candles above it.
  function timeAnchor() {
    if (!state.bars) return [];
    return state.bars.t.map(function (ts) { return { time: tsToDate(ts) }; });
  }

  function barTimeLookup() {
    var lookup = Object.create(null);
    if (!state.bars) return lookup;
    state.bars.t.forEach(function (ts) { lookup[tsToDate(ts)] = true; });
    return lookup;
  }

  function alignIndicatorSeries(series) {
    var validTimes = barTimeLookup();
    return series.map(function (s) {
      var copy = Object.assign({}, s);
      copy.data = (s.data || []).filter(function (d) { return d && validTimes[d.time]; });
      return copy;
    }).filter(function (s) { return s.data.length; });
  }

  function addOscPane(name, label, series) {
    var stack = $("ta-osc-stack");
    var wrap = document.createElement("div");
    wrap.className = "ta-osc-pane";
    wrap.innerHTML = '<span class="ta-osc-label">' + (label || name) + '</span>' +
                     '<button class="ta-osc-close" title="Remove">✕</button>';
    stack.appendChild(wrap);
    var chart = LightweightCharts.createChart(wrap, baseOptions(false));
    // Anchor the time domain to the full bar set (see timeAnchor()).
    var anchor = chart.addLineSeries({ lastValueVisible: false, priceLineVisible: false, crosshairMarkerVisible: false });
    anchor.setData(timeAnchor());
    var seriesObjs = series.map(function (s) { return lineFrom(chart, s); });
    state.panes[name] = { wrap: wrap, chart: chart, series: seriesObjs };
    wireSync(chart);
    // align with the main chart's current view
    try { chart.timeScale().setVisibleLogicalRange(state.main.timeScale().getVisibleLogicalRange()); } catch (e) {}
    wrap.querySelector(".ta-osc-close").addEventListener("click", function () { removeIndicator(name); });
  }

  function removeIndicator(name) {
    if (state.overlays[name]) {
      state.overlays[name].forEach(function (s) { try { state.main.removeSeries(s); } catch (e) {} });
      delete state.overlays[name];
    } else if (state.panes[name]) {
      try { state.panes[name].chart.remove(); } catch (e) {}
      state.panes[name].wrap.remove();
      delete state.panes[name];
    }
    var chip = document.querySelector('.ta-chip[data-ind="' + name + '"]');
    if (chip) chip.remove();
  }

  function addChip(name, label) {
    var chips = $("ta-chips");
    if (chips.querySelector('.ta-chip[data-ind="' + name + '"]')) return;
    var chip = document.createElement("span");
    chip.className = "ta-chip";
    chip.setAttribute("data-ind", name);
    chip.innerHTML = "<span>" + label + "</span><button title='Remove'>✕</button>";
    chip.querySelector("button").addEventListener("click", function () { removeIndicator(name); });
    chips.appendChild(chip);
  }

  // ── data load ──────────────────────────────────────────────────────────────
  function loadBars(sym) {
    var to = Math.floor(Date.now() / 1000) + 86400;
    state.historyQuery = { to: to, countback: HISTORY_COUNTBACK };
    var url = udfHistory + "?symbol=" + encodeURIComponent(sym) + "&resolution=1D&from=0&to=" + to + "&countback=" + HISTORY_COUNTBACK;
    return fetch(url).then(function (r) { return r.json(); }).then(function (j) {
      if (!j || j.s !== "ok" || !j.t || !j.t.length) throw new Error("no data");
      state.bars = j;
    });
  }

  function reloadActiveIndicators() {
    var names = Object.keys(state.overlays).concat(Object.keys(state.panes));
    // tear down, then re-add against the new symbol
    names.forEach(removeIndicator);
    names.forEach(addIndicator);
  }

  function loadSymbol(sym) {
    sym = (sym || "").trim().toUpperCase();
    if (!sym) return;
    var loading = $("ta-loading");
    if (loading) { loading.style.display = "flex"; loading.textContent = "Loading " + sym + "…"; }
    loadBars(sym).then(function () {
      state.symbol = sym;
      $("ta-symbol").value = sym;
      syncIndexSelect();
      if (loading) loading.style.display = "none";
      buildMain();
      reloadActiveIndicators();
    }).catch(function () {
      if (loading) loading.textContent = "No data for " + sym;
    });
  }

  // ── controls ───────────────────────────────────────────────────────────────
  function populateCatalog() {
    fetch(cfg.catalogUrl).then(function (r) { return r.json(); }).then(function (list) {
      var sel = $("ta-ind");
      var over = document.createElement("optgroup"); over.label = "Overlays";
      var osc = document.createElement("optgroup"); osc.label = "Oscillators";
      list.forEach(function (ind) {
        var o = document.createElement("option");
        o.value = ind.name; o.textContent = ind.label;
        (ind.pane === "overlay" ? over : osc).appendChild(o);
      });
      sel.appendChild(over); sel.appendChild(osc);
    }).catch(function () {});
  }

  function syncIndexSelect() {
    var sel = $("ta-index");
    if (!sel) return;
    var hasCurrent = Array.prototype.some.call(sel.options, function (option) {
      return option.value === state.symbol;
    });
    sel.value = hasCurrent ? state.symbol : "";
  }

  function populateIndices() {
    var sel = $("ta-index");
    if (!sel) return;
    fetch(udfSearch + "?type=index&limit=50").then(function (r) { return r.json(); }).then(function (rows) {
      sel.textContent = "";
      var placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = "Indices";
      sel.appendChild(placeholder);
      (rows || []).forEach(function (row) {
        var option = document.createElement("option");
        option.value = row.symbol;
        option.textContent = row.symbol + " - " + (row.description || row.symbol);
        sel.appendChild(option);
      });
      syncIndexSelect();
    }).catch(function () {});
  }

  function wireControls() {
    $("ta-add").addEventListener("click", function () { addIndicator($("ta-ind").value); });
    $("ta-go").addEventListener("click", function () { loadSymbol($("ta-symbol").value); });
    $("ta-symbol").addEventListener("change", function () { loadSymbol(this.value); });
    $("ta-symbol").addEventListener("keydown", function (e) { if (e.key === "Enter") loadSymbol(this.value); });
    $("ta-index").addEventListener("change", function () { if (this.value) loadSymbol(this.value); });
    $("ta-symbol").addEventListener("input", function () {
      var q = this.value.trim();
      if (q.length < 1) return;
      fetch(udfSearch + "?query=" + encodeURIComponent(q) + "&limit=20")
        .then(function (r) { return r.json(); })
        .then(function (rows) {
          var dl = $("ta-symlist"); dl.innerHTML = "";
          (rows || []).forEach(function (row) {
            var o = document.createElement("option");
            o.value = row.symbol; o.label = row.description || "";
            dl.appendChild(o);
          });
        }).catch(function () {});
    });
    $("ta-type").addEventListener("change", function () {
      state.chartType = this.value;
      buildMain();          // rebuild price series; overlays live on main, so re-add them
      var overlayNames = Object.keys(state.overlays);
      overlayNames.forEach(function (n) {
        state.overlays[n].forEach(function (s) { try { state.main.removeSeries(s); } catch (e) {} });
        delete state.overlays[n];
      });
      overlayNames.forEach(addIndicator);
    });
  }

  function boot() {
    if (typeof LightweightCharts === "undefined") return;
    populateCatalog();
    populateIndices();
    wireControls();
    loadSymbol(state.symbol);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
