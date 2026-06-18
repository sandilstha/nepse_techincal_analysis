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

  // ── table builders ────────────────────────────────────────────────────
  function buildFavTable(table, rows) {
    if (!rows || !rows.length) { empty(table, 6); return; }
    var head = "<thead><tr><th>No.</th><th class='l'>Ticker</th><th>Quantity</th>" +
      "<th>Amount (Rs)</th><th>Average Price (Rs)</th><th>% Of Total Transactions</th></tr></thead>";
    var body = rows.map(function (r, i) {
      return "<tr><td>" + (i + 1) + "</td><td class='l tkr'>" + r.key + "</td><td>" +
        fmtQty(r.quantity) + "</td><td>" + fmtRs(r.amount) + "</td><td>" +
        fmtPrice(r.avg_price) + "</td><td>" + fmtPct(r.pct) + "</td></tr>";
    }).join("");
    table.innerHTML = head + "<tbody>" + body + "</tbody>";
  }

  function buildBrokerTable(table, rows) {
    if (!rows || !rows.length) { empty(table, 5); return; }
    var head = "<thead><tr><th class='l'>Broker</th><th>Quantity</th><th>Amount (Rs)</th>" +
      "<th>Average Price (Rs)</th><th>% Of Total</th></tr></thead>";
    var body = rows.map(function (r) {
      return "<tr><td class='l tkr'>" + r.key + "</td><td>" + fmtQty(r.quantity) + "</td><td>" +
        fmtRs(r.amount) + "</td><td>" + fmtPrice(r.avg_price) + "</td><td>" + fmtPct(r.pct) + "</td></tr>";
    }).join("");
    table.innerHTML = head + "<tbody>" + body + "</tbody>";
  }

  function buildHoldTable(table, rows) {
    if (!rows || !rows.length) { empty(table, 4); return; }
    var head = "<thead><tr><th class='l'>Broker</th><th>Net Qty</th>" +
      "<th>Avg Buy (Rs)</th><th>Avg Sell (Rs)</th></tr></thead>";
    var body = rows.map(function (r) {
      var cls = r.quantity >= 0 ? "num-pos" : "num-neg";
      return "<tr><td class='l tkr'>" + r.key + "</td><td class='" + cls + "'>" + fmtQty(r.quantity) +
        "</td><td>" + fmtPrice(r.avg_buy) + "</td><td>" + fmtPrice(r.avg_sell) + "</td></tr>";
    }).join("");
    table.innerHTML = head + "<tbody>" + body + "</tbody>";
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
  var favState = { brokers: [], view: "shares", range: "today", trendSide: "buy", trendSym: null };
  var TABS = {};

  TABS.favorites = {
    init: function () {
      // Multi-select brokers: default to the first broker selected.
      var first = (META.brokers || [])[0];
      favState.brokers = first != null ? [String(first)] : [];
      buildBrokerMulti(function () { TABS.favorites.load(); });
      segGroup("fav-view", function (v) { favState.view = v; TABS.favorites.load(); });
      segGroup("fav-range", function (v) { favState.range = v; TABS.favorites.load(); });
      segGroup("fav-trend-side", function (v) { favState.trendSide = v; TABS.favorites.loadTrend(); });
    },
    load: function () {
      if (!favState.brokers.length) { empty(el("fav-buy"), 6, "Select a broker"); empty(el("fav-sell"), 6, "Select a broker"); return; }
      loading(el("fav-buy"), 6); loading(el("fav-sell"), 6);
      getJSON("favorites/", { brokers: favState.brokers.join(","), range: favState.range, view: favState.view }, "favorites")
        .then(function (d) {
          buildFavTable(el("fav-buy"), d.buy);
          buildFavTable(el("fav-sell"), d.sell);
          // row click selects ticker for the trend; default to top buy ticker
          wireRowSelect(el("fav-buy"), d.buy);
          wireRowSelect(el("fav-sell"), d.sell);
          if (!favState.trendSym && d.buy && d.buy.length) favState.trendSym = d.buy[0].key;
          TABS.favorites.loadTrend();
        })
        .catch(function (err) { if (isAbort(err)) return; empty(el("fav-buy"), 6, "Error"); empty(el("fav-sell"), 6, "Error"); });
    },
    loadTrend: function () {
      if (!favState.trendSym) return;
      el("fav-trend-sym").textContent = favState.trendSym;
      getJSON("trend/", { symbol: favState.trendSym, side: favState.trendSide }, "fav-trend")
        .then(function (d) { renderTrend("fav-trend-chart", d); })
        .catch(function () {});
    }
  };
  function wireRowSelect(table, rows) {
    var trs = table.querySelectorAll("tbody tr");
    trs.forEach(function (tr, i) {
      if (!rows[i]) return;
      tr.style.cursor = "pointer";
      tr.addEventListener("click", function () {
        favState.trendSym = rows[i].key;
        TABS.favorites.loadTrend();
      });
    });
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
  var swState = { symbol: null, view: "shares", range: "today", trendSide: "buy" };
  TABS.stockwise = {
    init: function () {
      fillSymbols(el("sw-symbol"));
      swState.symbol = el("sw-symbol").value || ((META.symbols || [])[0] || {}).symbol;
      el("sw-symbol").addEventListener("change", function () { swState.symbol = this.value; TABS.stockwise.load(); });
      segGroup("sw-view", function (v) { swState.view = v; TABS.stockwise.load(); });
      segGroup("sw-range", function (v) { swState.range = v; TABS.stockwise.load(); });
      segGroup("sw-trend-side", function (v) { swState.trendSide = v; TABS.stockwise.loadTrend(); });
    },
    load: function () {
      if (!swState.symbol) { empty(el("sw-buy"), 5, "No symbols"); return; }
      loading(el("sw-buy"), 5); loading(el("sw-sell"), 5); loading(el("sw-hold"), 4);
      getJSON("stockwise/", { symbol: swState.symbol, range: swState.range, view: swState.view }, "stockwise")
        .then(function (d) {
          buildBrokerTable(el("sw-buy"), d.buy);
          buildBrokerTable(el("sw-sell"), d.sell);
          buildHoldTable(el("sw-hold"), d.holdings);
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
  var hotState = { view: "shares", range: "today", sector: "All" };
  TABS.hotstocks = {
    init: function () {
      fillSectors(el("hot-sector"));
      el("hot-sector").addEventListener("change", function () { hotState.sector = this.value; TABS.hotstocks.load(); });
      segGroup("hot-view", function (v) { hotState.view = v; TABS.hotstocks.load(); });
      segGroup("hot-range", function (v) { hotState.range = v; TABS.hotstocks.load(); });
    },
    load: function () {
      var t = el("hot-table");
      loading(t, 10);
      getJSON("hotstocks/", { range: hotState.range, view: hotState.view, sector: hotState.sector }, "hotstocks")
        .then(function (d) {
          var rows = d.rows || [];
          if (!rows.length) { empty(t, 10); return; }
          var head = "<thead><tr><th>No.</th><th class='l'>Ticker</th><th class='l'>Sector</th>" +
            "<th>Quantity</th><th>Amount (Rs)</th><th>Avg Price</th><th>Buyers</th><th>Sellers</th>" +
            "<th>Top Buy</th><th>Top Sell</th></tr></thead>";
          var body = rows.map(function (r, i) {
            var tb = r.top_buy ? r.top_buy.broker + " (" + fmtPct(r.top_buy.pct) + ")" : "—";
            var ts = r.top_sell ? r.top_sell.broker + " (" + fmtPct(r.top_sell.pct) + ")" : "—";
            return "<tr><td>" + (i + 1) + "</td><td class='l tkr'>" + r.symbol + "</td><td class='l'>" +
              (r.sector || "") + "</td><td>" + fmtQty(r.quantity) + "</td><td>" + fmtRs(r.amount) +
              "</td><td>" + fmtPrice(r.avg_price) + "</td><td>" + r.buyers + "</td><td>" + r.sellers +
              "</td><td class='num-pos'>" + tb + "</td><td class='num-neg'>" + ts + "</td></tr>";
          }).join("");
          t.innerHTML = head + "<tbody>" + body + "</tbody>";
        })
        .catch(function (err) { if (isAbort(err)) return; empty(t, 10, "Error"); });
    }
  };

  // ─────────────────────────────────────────────────────────────────────
  // TAB: Net Holding (treemap)
  // ─────────────────────────────────────────────────────────────────────
  var nhState = { broker: null, range: "today", excludeMf: false, sector: "All" };
  TABS.netholding = {
    init: function () {
      fillBrokers(el("nh-broker"));
      fillSectors(el("nh-sector"));
      nhState.broker = el("nh-broker").value || (META.brokers || [])[0];
      el("nh-broker").addEventListener("change", function () { nhState.broker = this.value; TABS.netholding.load(); });
      el("nh-sector").addEventListener("change", function () { nhState.sector = this.value; TABS.netholding.load(); });
      el("nh-exclude-mf").addEventListener("change", function () { nhState.excludeMf = this.checked; TABS.netholding.load(); });
      segGroup("nh-range", function (v) { nhState.range = v; TABS.netholding.load(); });
    },
    load: function () {
      var box = el("nh-treemap");
      box.innerHTML = '<div class="dsx-loading">Loading…</div>';
      if (!nhState.broker) { box.innerHTML = '<div class="dsx-empty">No brokers</div>'; return; }
      getJSON("netholding/", {
        broker: nhState.broker, range: nhState.range,
        exclude_mf: nhState.excludeMf ? 1 : 0, sector: nhState.sector
      }, "netholding").then(function (d) {
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
  }

  function drawCell(box, it, x, y, w, h) {
    var d = document.createElement("div");
    d.className = "dsx-tm-cell " + (it.side === "buy" ? "buy" : "sell");
    d.style.left = x + "px"; d.style.top = y + "px";
    d.style.width = Math.max(0, w - 1) + "px"; d.style.height = Math.max(0, h - 1) + "px";
    d.title = it.symbol + " : net " + (it.net > 0 ? "+" : "") + nf(it.net);
    if (w > 34 && h > 18) {
      var fs = Math.max(9, Math.min(15, Math.sqrt(w * h) / 6));
      d.innerHTML = '<span class="dsx-tm-label" style="font-size:' + fs + 'px">' + it.symbol + "</span>";
    }
    box.appendChild(d);
  }

  // ─────────────────────────────────────────────────────────────────────
  // TAB: Broker Concentration
  // ─────────────────────────────────────────────────────────────────────
  var concState = { range: "today", sector: "All" };
  TABS.concentration = {
    init: function () {
      fillSectors(el("conc-sector"));
      el("conc-sector").addEventListener("change", function () { concState.sector = this.value; TABS.concentration.load(); });
      segGroup("conc-range", function (v) { concState.range = v; TABS.concentration.load(); });
    },
    load: function () {
      var t = el("conc-table");
      loading(t, 10);
      getJSON("concentration/", { range: concState.range, sector: concState.sector }, "concentration")
        .then(function (d) {
          var rows = d.rows || [];
          if (!rows.length) { empty(t, 10); return; }
          var head = "<thead>" +
            "<tr><th rowspan='2' class='l'>Ticker</th><th rowspan='2'>Total Traded</th>" +
            "<th colspan='4' class='grp'>Top Broker On Buy Side</th>" +
            "<th colspan='4' class='grp'>Top Broker On Sell Side</th></tr>" +
            "<tr><th class='grp'>1st</th><th>2nd</th><th>3rd</th><th>Sum Top 3</th>" +
            "<th class='grp'>1st</th><th>2nd</th><th>3rd</th><th>Sum Top 3</th></tr></thead>";
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
          t.innerHTML = head + "<tbody>" + body + "</tbody>";
        })
        .catch(function (err) { if (isAbort(err)) return; empty(t, 10, "Error"); });
    }
  };

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
