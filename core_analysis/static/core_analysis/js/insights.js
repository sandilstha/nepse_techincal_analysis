/* ============================================================================
   Market Insights dashboard front-end.
   - Renders all widgets from a single payload (single source of truth).
   - Auto-refreshes by polling the JSON API at a user-configurable interval.
   - Degrades gracefully: failed fetches keep the last good data and flag "stale".
   - Dark / light theme toggle persisted in localStorage.
   ========================================================================== */
(function () {
  "use strict";

  var CONFIG = window.MI_CONFIG || { apiUrl: "/insights/api/", refreshSeconds: 30 };
  var LS_THEME = "mi-theme";
  var LS_INTERVAL = "mi-refresh-interval";
  var LS_HEATMAP_SECTOR = "mi-heatmap-sector";

  var HEATMAP_ALL_LIMIT = 60;     // tiles shown for "All sectors"
  var HEATMAP_SECTOR_LIMIT = 80;  // tiles shown when a single sector is picked

  var state = {
    data: null,
    timer: null,
    intervalSec: CONFIG.refreshSeconds,
    inFlight: false,
    charts: {},
    heatmapSector: "ALL"
  };

  // ── Formatting helpers ─────────────────────────────────────────────────
  function isNum(v) { return typeof v === "number" && isFinite(v); }

  function fmtNum(v, dp) {
    if (!isNum(v)) return "—";
    return v.toLocaleString("en-US", { minimumFractionDigits: dp || 0, maximumFractionDigits: dp || 0 });
  }

  function fmtCompact(v) {
    if (!isNum(v)) return "—";
    var abs = Math.abs(v);
    if (abs >= 1e9) return (v / 1e9).toFixed(2) + " Ar";   // Arba (billion)
    if (abs >= 1e7) return (v / 1e7).toFixed(2) + " Cr";   // Crore (10 million)
    if (abs >= 1e5) return (v / 1e5).toFixed(2) + " L";    // Lakh (hundred thousand)
    return fmtNum(v, 0);
  }

  function fmtMoney(v) {
    if (!isNum(v)) return "—";
    return "Rs " + fmtCompact(v);
  }

  function fmtPct(v) {
    if (!isNum(v)) return "—";
    return (v > 0 ? "+" : "") + v.toFixed(2) + "%";
  }

  function fmtSigned(v) {
    if (!isNum(v)) return "—";
    return (v > 0 ? "+" : "") + v.toFixed(2);
  }

  function dirClass(v) {
    if (!isNum(v) || v === 0) return "flat";
    return v > 0 ? "up" : "down";
  }

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function el(id) { return document.getElementById(id); }

  // ── Theme ──────────────────────────────────────────────────────────────
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var btn = el("mi-theme-btn");
    if (btn) btn.textContent = theme === "light" ? "☀" : "🌙";
    try { localStorage.setItem(LS_THEME, theme); } catch (e) {}
  }

  function initTheme() {
    var saved;
    try { saved = localStorage.getItem(LS_THEME); } catch (e) {}
    if (!saved) {
      saved = window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
    }
    applyTheme(saved);
    el("mi-theme-btn").addEventListener("click", function () {
      var next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
      applyTheme(next);
      // Rebuild charts so their baked-in colours match the new palette.
      destroyCharts();
      if (state.data) renderCharts(state.data);
      // Recolour the OHLC chart and the TradingView terminal (if active) too.
      if (window.MIOHLC && window.MIOHLC.setTheme) window.MIOHLC.setTheme(next);
      if (typeof window.MI_setTVTheme === "function") window.MI_setTVTheme(next);
    });
  }

  // ── Status indicator ───────────────────────────────────────────────────
  function setStatus(kind, text) {
    var box = el("mi-status");
    box.classList.remove("is-live", "is-stale");
    if (kind === "live") box.classList.add("is-live");
    if (kind === "stale") box.classList.add("is-stale");
    el("mi-status-text").textContent = text;
  }

  function stamp() {
    var d = new Date();
    el("mi-last-updated").textContent = "Updated " + d.toLocaleTimeString("en-US");
  }

  // ── Renderers ──────────────────────────────────────────────────────────
  function renderOverview(d) {
    var ov = d.overview || {};
    el("ov-index").textContent = fmtNum(ov.nepse_index, 2);

    var deltaEl = el("ov-index-delta");
    deltaEl.textContent = fmtSigned(ov.nepse_change) + "  (" + fmtPct(ov.nepse_pct) + ")";
    deltaEl.className = "mi-stat-delta " + dirClass(ov.nepse_pct);

    var chgEl = el("ov-change");
    chgEl.textContent = fmtPct(ov.nepse_pct);
    chgEl.className = "mi-stat-value " + dirClass(ov.nepse_pct);
    el("ov-change-abs").textContent = "Abs " + fmtSigned(ov.nepse_change);

    el("ov-turnover").textContent = fmtMoney(ov.turnover);
    el("ov-volume").textContent = fmtCompact(ov.volume) + " shares";

    el("ov-trades").textContent = fmtNum(ov.trades, 0);
    el("ov-scrips").textContent = fmtNum(ov.scrips_traded, 0) + " scrips traded";

    el("mi-asof-date").textContent = d.as_of || "—";

    // Live vs end-of-day indicator.
    var badge = el("mi-live-badge");
    var label = el("mi-asof-label");
    if (badge) badge.hidden = !d.live;
    if (label) label.textContent = d.live ? "Live" : "As of";

    renderBreadthMini(d.breadth || {});
  }

  function renderBreadthMini(b) {
    var adv = b.advancing || 0, dec = b.declining || 0, unch = b.unchanged || 0;
    el("ov-adv").textContent = fmtNum(adv, 0);
    el("ov-unch").textContent = fmtNum(unch, 0);
    el("ov-dec").textContent = fmtNum(dec, 0);
    var total = adv + dec + unch;
    var bar = el("ov-breadth-bar");
    if (!total) { bar.innerHTML = ""; return; }
    var pa = (adv / total * 100).toFixed(1);
    var pf = (unch / total * 100).toFixed(1);
    var pd = (dec / total * 100).toFixed(1);
    bar.innerHTML =
      '<i class="up" style="width:' + pa + '%"></i>' +
      '<i class="flat" style="width:' + pf + '%"></i>' +
      '<i class="down" style="width:' + pd + '%"></i>';
  }

  function symCell(row) {
    var name = row.name ? "<small>" + escapeHtml(row.name) + "</small>" : "";
    return '<span class="mi-sym">' + escapeHtml(row.symbol) + name + "</span>";
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function renderRankedTable(tbodyId, rows, kind) {
    var tbody = el(tbodyId);
    if (!rows || !rows.length) {
      tbody.innerHTML = '<tr><td colspan="3" class="mi-empty">No data available</td></tr>';
      return;
    }
    var html = rows.map(function (r) {
      if (kind === "active") {
        return "<tr><td>" + symCell(r) + "</td><td class='num'>" + fmtCompact(r.volume) +
          "</td><td class='num'>" + fmtMoney(r.turnover) + "</td></tr>";
      }
      var cls = dirClass(r.pct);
      return "<tr><td>" + symCell(r) + "</td><td class='num'>" + fmtNum(r.ltp, 2) +
        "</td><td class='num'><span class='mi-chg-badge " + cls + "'>" + fmtPct(r.pct) + "</span></td></tr>";
    }).join("");
    tbody.innerHTML = html;
  }

  function renderSectors(sectors) {
    var box = el("sector-list");
    if (!box) return;
    if (!sectors || !sectors.length) {
      box.innerHTML = '<div class="mi-empty">No sector data available</div>';
      return;
    }
    var maxAbs = sectors.reduce(function (m, s) {
      return Math.max(m, Math.abs(isNum(s.pct) ? s.pct : 0));
    }, 0.01);
    box.innerHTML = sectors.map(function (s) {
      var pct = isNum(s.pct) ? s.pct : 0;
      var cls = dirClass(pct);
      var width = Math.min(100, Math.abs(pct) / maxAbs * 100);
      // Diverging bars: positive grows from centre to the right, negative to the left.
      var fill = pct >= 0
        ? '<span class="mi-sector-fill up" style="left:50%;width:' + (width / 2) + '%"></span>'
        : '<span class="mi-sector-fill down" style="right:50%;width:' + (width / 2) + '%"></span>';
      return '<div class="mi-sector-row">' +
        '<span class="mi-sector-name" title="' + escapeHtml(s.sector) + '">' + escapeHtml(s.sector) + "</span>" +
        '<span class="mi-sector-track">' + fill + "</span>" +
        '<span class="mi-sector-pct ' + cls + '">' + fmtPct(s.pct) + "</span>" +
        "</div>";
    }).join("");
  }

  // ── Charts (ApexCharts) ────────────────────────────────────────────────
  function baseChartOpts() {
    var grid = cssVar("--line-soft");
    var ink = cssVar("--ink-2");
    return {
      foreColor: ink,
      gridColor: grid,
      up: cssVar("--up"),
      down: cssVar("--down"),
      flat: cssVar("--flat"),
      accent: cssVar("--accent")
    };
  }

  function destroyCharts() {
    Object.keys(state.charts).forEach(function (k) {
      try { state.charts[k].destroy(); } catch (e) {}
    });
    state.charts = {};
  }

  function renderCharts(d) {
    // The NEPSE Index card is now the Lightweight Charts OHLC chart (ohlc-chart.js).
    renderBreadthChart(d.breadth || {}, d.live);
    renderSectorChart(d.sectors || []);
    populateHeatmapSectors(d.heatmap || []);
    renderHeatmap();
  }

  // Build the sector <select> from the tiles present, preserving the current
  // choice when it still exists after a refresh.
  function populateHeatmapSectors(tiles) {
    var sel = el("heatmap-sector");
    if (!sel) return;
    var counts = {};
    tiles.forEach(function (t) {
      var s = t.sector || "Other";
      counts[s] = (counts[s] || 0) + 1;
    });
    var current = state.heatmapSector || "ALL";
    if (current !== "ALL" && counts[current] === undefined) current = "ALL";

    var opts = ['<option value="ALL">All sectors (' + tiles.length + ")</option>"];
    Object.keys(counts).sort().forEach(function (s) {
      opts.push('<option value="' + escapeHtml(s) + '">' + escapeHtml(s) + " (" + counts[s] + ")</option>");
    });
    sel.innerHTML = opts.join("");
    sel.value = current;
    state.heatmapSector = current;
  }

  function filteredHeatmap() {
    var all = (state.data && state.data.heatmap) || [];
    var sel = state.heatmapSector || "ALL";
    if (sel === "ALL") return all.slice(0, HEATMAP_ALL_LIMIT);
    return all.filter(function (t) { return (t.sector || "Other") === sel; }).slice(0, HEATMAP_SECTOR_LIMIT);
  }

  function renderBreadthChart(b, live) {
    // Donut for the Market Breadth card; detail rows beside it carry the exact
    // counts and stale-feed note.
    var node = el("chart-breadth");
    if (node) {
      var t = baseChartOpts();
      var opts = {
        chart: { type: "donut", height: 230, fontFamily: "Manrope, sans-serif" },
        series: [b.advancing || 0, b.declining || 0, b.unchanged || 0],
        labels: ["Advancing", "Declining", "Unchanged"],
        colors: [t.up, t.down, t.flat],
        stroke: { width: 0 },
        legend: { show: false },
        dataLabels: { enabled: true, formatter: function (val, o) { return o.w.config.series[o.seriesIndex]; }, style: { fontSize: "11px" } },
        plotOptions: { pie: { donut: { size: "62%", labels: { show: true, total: { show: true, label: "Scrips", color: t.foreColor, formatter: function (w) { return w.globals.seriesTotals.reduce(function (a, c) { return a + c; }, 0); } } } } } },
        tooltip: { theme: themeName() }
      };
      mountChart("chart-breadth", "breadth", opts);
      var legend = el("breadth-legend");
      if (legend) {
        legend.innerHTML =
          '<span><i style="background:' + t.up + '"></i>Advancing</span>' +
          '<span><i style="background:' + t.down + '"></i>Declining</span>' +
          '<span><i style="background:' + t.flat + '"></i>Unchanged</span>';
      }
    }
    renderBreadthDetail(b, live);
  }

  function renderBreadthDetail(b, live) {
    var box = el("breadth-detail");
    if (!box) return;
    var adv = b.advancing || 0, dec = b.declining || 0, unch = b.unchanged || 0;
    var total = adv + dec + unch;
    var chip = el("breadth-sentiment");

    // Breadth is counted per-scrip from the live feed; when that feed is stale
    // (not live), these advancing/declining counts are a prior session's and
    // won't match the official headline totals — so grey the card and badge it
    // "Delayed" instead of presenting old counts as current.
    var card = box.closest(".mi-card-breadth");
    var stale = live === false && total > 0;
    if (card) card.classList.toggle("is-stale", stale);

    if (!total) { box.innerHTML = ""; if (chip) { chip.textContent = "—"; chip.className = "mi-pill"; } return; }

    function pct(n) { return (n / total * 100).toFixed(1) + "%"; }
    var ratio = dec > 0 ? adv / dec : (adv > 0 ? Infinity : 0);
    var ratioTxt = dec > 0 ? ratio.toFixed(2) : (adv > 0 ? "∞" : "0.00");

    var label, cls;
    if (Math.abs(adv - dec) <= total * 0.03) { label = "Neutral"; cls = "flat"; }
    else if (ratio >= 1.5) { label = "Strong Bullish"; cls = "up"; }
    else if (ratio > 1) { label = "Bullish"; cls = "up"; }
    else if (ratio > 0.67) { label = "Bearish"; cls = "down"; }
    else { label = "Strong Bearish"; cls = "down"; }

    if (chip) {
      // When stale, the sentiment is computed off a prior session — badge it
      // "Delayed" rather than implying a current bullish/bearish read.
      chip.textContent = stale ? "Delayed" : label;
      chip.className = "mi-pill " + (stale ? "mi-pill-stale" : cls === "up" ? "mi-pill-up" : cls === "down" ? "mi-pill-down" : "");
    }

    function row(k, v, c) {
      return '<div class="mi-bd-row"><span class="mi-bd-k">' + k +
        '</span><span class="mi-bd-v ' + (c || "") + '">' + v + "</span></div>";
    }

    box.innerHTML =
      (stale ? '<div class="mi-bd-stale-note">Last session — live feed delayed</div>' : "") +
      '<div class="mi-bd-bar">' +
        '<i class="up" style="width:' + (adv / total * 100) + '%"></i>' +
        '<i class="flat" style="width:' + (unch / total * 100) + '%"></i>' +
        '<i class="down" style="width:' + (dec / total * 100) + '%"></i>' +
      "</div>" +
      row("A/D Ratio", ratioTxt, ratio >= 1 ? "up" : "down") +
      row("Advancing", fmtNum(adv, 0) + " · " + pct(adv), "up") +
      row("Declining", fmtNum(dec, 0) + " · " + pct(dec), "down") +
      row("Unchanged", fmtNum(unch, 0) + " · " + pct(unch), "flat") +
      row("Total scrips", fmtNum(total, 0), "");
  }

  var SECTOR_COLORS = [
    "#12d39a", "#5cb3ff", "#ffc166", "#ff6e72", "#a78bfa", "#34d399", "#f472b6",
    "#60a5fa", "#fbbf24", "#fb7185", "#2dd4bf", "#c084fc", "#4ade80", "#f59e0b"
  ];

  // Sector turnover share — where the money flowed today (complements the
  // Sector Performance list, which shows daily % change).
  function renderSectorChart(sectors) {
    var t = baseChartOpts();
    var rows = (sectors || []).filter(function (s) { return isNum(s.turnover) && s.turnover > 0; });
    rows.sort(function (a, b) { return b.turnover - a.turnover; });
    var labels = rows.map(function (s) { return s.sector; });
    var data = rows.map(function (s) { return Math.round(s.turnover); });
    var total = data.reduce(function (sum, v) { return sum + v; }, 0);

    var opts = {
      chart: { type: "bar", height: "100%", toolbar: { show: false }, fontFamily: "Manrope, sans-serif" },
      series: [{ name: "Turnover", data: data }],
      colors: SECTOR_COLORS.slice(0, Math.max(data.length, 1)),
      legend: { show: false },
      plotOptions: {
        bar: {
          horizontal: true,
          distributed: true,
          borderRadius: 4,
          barHeight: "62%",
          dataLabels: { position: "right" }
        }
      },
      dataLabels: {
        enabled: true,
        formatter: function (v) {
          return total ? (v / total * 100).toFixed(1) + "%" : "";
        },
        offsetX: 8,
        style: { fontSize: "11px", fontWeight: 700, colors: [t.foreColor] },
        background: { enabled: false },
        dropShadow: { enabled: false }
      },
      xaxis: {
        categories: labels,
        labels: {
          formatter: function (v) { return fmtCompact(Number(v)); },
          style: { colors: t.foreColor, fontSize: "11px" }
        },
        axisBorder: { color: t.grid },
        axisTicks: { color: t.grid }
      },
      yaxis: {
        labels: {
          maxWidth: 150,
          style: { colors: t.foreColor, fontSize: "11px", fontWeight: 600 }
        }
      },
      grid: { borderColor: t.grid, strokeDashArray: 3, xaxis: { lines: { show: true } }, yaxis: { lines: { show: false } } },
      tooltip: { theme: themeName(), y: { formatter: function (v) { return fmtMoney(v); } } },
      noData: { text: "No sector turnover available", style: { color: t.foreColor } }
    };
    mountChart("chart-sectors", "sectors", opts);
  }

  function pctColor(pct) {
    var t = baseChartOpts();
    if (!isNum(pct) || pct === 0) return t.flat;
    if (pct <= -3) return "#c0392b";
    if (pct <= -1) return t.down;
    if (pct < 0) return "#e98a8c";
    if (pct < 1) return "#7fd8b4";
    if (pct < 3) return t.up;
    return "#0f9e6e";
  }

  function renderHeatmap() {
    // Tile SIZE = turnover (liquidity), tile COLOUR = daily change % via a
    // per-point fillColor. Grouped by sector so related scrips sit together.
    // Honours the sector filter dropdown (state.heatmapSector).
    var tiles = filteredHeatmap();
    var bySector = {};
    tiles.forEach(function (tile) {
      var key = tile.sector || "Other";
      (bySector[key] = bySector[key] || []).push({
        x: tile.symbol,
        y: Math.round(tile.turnover || 0),
        fillColor: pctColor(tile.pct),
        pct: tile.pct,
        ltp: tile.ltp
      });
    });
    var series = Object.keys(bySector).map(function (k) { return { name: k, data: bySector[k] }; });

    var opts = {
      chart: { type: "treemap", height: 440, toolbar: { show: false }, fontFamily: "Manrope, sans-serif" },
      series: series.length ? series : [{ name: "Market", data: [] }],
      legend: { show: false },
      dataLabels: {
        enabled: true,
        style: { fontSize: "11px", fontFamily: "JetBrains Mono, monospace", colors: ["#ffffff"] },
        formatter: function (text, op) {
          var pt = (op.w.config.series[op.seriesIndex].data[op.dataPointIndex] || {}).pct;
          return [text, isNum(pt) ? fmtPct(pt) : ""];
        },
        offsetY: -4
      },
      plotOptions: {
        treemap: { distributed: true, enableShades: false, useFillColorAsStroke: false }
      },
      tooltip: {
        theme: themeName(),
        custom: function (op) {
          var pt = op.ctx.w.config.series[op.seriesIndex].data[op.dataPointIndex] || {};
          return '<div style="padding:6px 10px;font-family:Manrope">' +
            "<strong>" + escapeHtml(pt.x) + "</strong><br/>" +
            "LTP: " + fmtNum(pt.ltp, 2) + "<br/>" +
            "Change: " + fmtPct(pt.pct) + "<br/>" +
            "Turnover: " + fmtMoney(pt.y) + "</div>";
        }
      }
    };
    mountChart("chart-heatmap", "heatmap", opts);
  }

  function themeName() {
    return document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
  }

  function mountChart(elemId, key, opts) {
    if (state.charts[key]) {
      state.charts[key].updateOptions(opts, true, true);
      return;
    }
    var node = el(elemId);
    if (!node || typeof ApexCharts === "undefined") return;
    state.charts[key] = new ApexCharts(node, opts);
    state.charts[key].render();
  }

  function renderContributors(d) {
    var c = d.contributors || {};
    renderContribList("contrib-positive", c.positive, "up");
    renderContribList("contrib-negative", c.negative, "down");
  }

  function renderContribList(id, rows, cls) {
    var box = el(id);
    if (!box) return;
    if (!rows || !rows.length) {
      box.innerHTML = '<div class="mi-empty">No data available</div>';
      return;
    }
    var maxAbs = rows.reduce(function (m, r) {
      return Math.max(m, Math.abs(isNum(r.points) ? r.points : 0));
    }, 0.01);
    box.innerHTML = rows.map(function (r) {
      var pts = isNum(r.points) ? r.points : 0;
      var width = Math.min(100, Math.abs(pts) / maxAbs * 100);
      return '<div class="mi-contrib-row">' +
        '<span class="mi-contrib-sym">' + escapeHtml(r.symbol) + "</span>" +
        '<span class="mi-contrib-track"><i class="' + cls + '" style="width:' + width + '%"></i></span>' +
        '<span class="mi-contrib-pts ' + cls + '">' + (pts > 0 ? "+" : "") + pts.toFixed(2) + "</span>" +
        '<span class="mi-contrib-pct ' + cls + '">' + fmtPct(r.pct) + "</span>" +
        "</div>";
    }).join("");
  }

  // ── Render everything ──────────────────────────────────────────────────
  function renderAll(d) {
    state.data = d;
    // Stock-level widgets sourced from the per-scrip live feed (heatmap, breadth)
    // are a prior session's data when the feed lags. Flag the page so those are
    // visibly marked delayed rather than read as current.
    document.body.classList.toggle("mi-feed-delayed", d.live === false && !!d.has_data);
    renderOverview(d);
    renderRankedTable("tbl-gainers", d.gainers, "ranked");
    renderRankedTable("tbl-losers", d.losers, "ranked");
    renderRankedTable("tbl-active", d.most_active, "active");
    renderContributors(d);
    renderCharts(d);
  }

  // ── Polling ────────────────────────────────────────────────────────────
  function refresh(manual) {
    if (state.inFlight) return;
    state.inFlight = true;
    var btn = el("mi-refresh-btn");
    if (manual && btn) btn.classList.add("is-spinning");

    // A manual refresh forces a fresh server build (bypasses the short payload cache).
    var url = CONFIG.apiUrl + (manual ? (CONFIG.apiUrl.indexOf("?") >= 0 ? "&" : "?") + "force=1" : "");
    // Abort a hung request so it can't pin inFlight=true and stall auto-refresh.
    var ctrl = (typeof AbortController !== "undefined") ? new AbortController() : null;
    var timeoutId = ctrl ? setTimeout(function () { ctrl.abort(); }, 12000) : null;
    fetch(url, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
      credentials: "same-origin",
      signal: ctrl ? ctrl.signal : undefined
    })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (d) {
        if (d.ok === false) throw new Error(d.error || "Service error");
        var banner = el("mi-load-banner");
        if (banner && d.has_data) banner.style.display = "none";
        renderAll(d);
        setStatus("live", "Live");
        stamp();
      })
      .catch(function (err) {
        setStatus("stale", "Stale — retrying");
        // Keep last good data on screen; just flag the staleness.
        if (window.console) console.warn("Market Insights refresh failed:", err.message);
      })
      .finally(function () {
        if (timeoutId) clearTimeout(timeoutId);
        state.inFlight = false;
        if (btn) btn.classList.remove("is-spinning");
      });
  }

  function scheduleNext() {
    if (state.timer) { clearTimeout(state.timer); state.timer = null; }
    if (state.intervalSec > 0) {
      state.timer = setTimeout(function () {
        if (!document.hidden) refresh(false);
        scheduleNext();
      }, state.intervalSec * 1000);
    }
  }

  function initControls() {
    var sel = el("mi-refresh-select");
    var saved;
    try { saved = localStorage.getItem(LS_INTERVAL); } catch (e) {}
    if (saved !== null && saved !== undefined) state.intervalSec = parseInt(saved, 10);
    sel.value = String(state.intervalSec);
    sel.addEventListener("change", function () {
      state.intervalSec = parseInt(sel.value, 10) || 0;
      try { localStorage.setItem(LS_INTERVAL, String(state.intervalSec)); } catch (e) {}
      scheduleNext();
    });

    el("mi-refresh-btn").addEventListener("click", function () { refresh(true); });

    // Heatmap sector filter (restore last choice, re-render on change).
    var hsel = el("heatmap-sector");
    if (hsel) {
      var savedSector;
      try { savedSector = localStorage.getItem(LS_HEATMAP_SECTOR); } catch (e) {}
      if (savedSector) state.heatmapSector = savedSector;
      hsel.addEventListener("change", function () {
        state.heatmapSector = hsel.value || "ALL";
        try { localStorage.setItem(LS_HEATMAP_SECTOR, state.heatmapSector); } catch (e) {}
        renderHeatmap();
      });
    }

    // Resume promptly when the tab regains focus.
    document.addEventListener("visibilitychange", function () {
      if (!document.hidden && state.intervalSec > 0) refresh(false);
    });
  }

  // ── Boot ───────────────────────────────────────────────────────────────
  function init() {
    initTheme();
    initControls();

    var bootstrap = el("mi-bootstrap");
    var initial = null;
    if (bootstrap) {
      try { initial = JSON.parse(bootstrap.textContent); } catch (e) {}
    }
    if (initial) {
      renderAll(initial);
      setStatus(initial.has_data ? "live" : "stale", initial.has_data ? "Live" : "No data");
      stamp();
    } else {
      setStatus("stale", "Loading…");
      refresh(false);
    }
    scheduleNext();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
