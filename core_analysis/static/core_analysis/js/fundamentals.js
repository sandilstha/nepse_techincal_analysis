/* fundamentals.js — Fundamental Analysis desk.
 *
 * Fetches one company's fundamentals from FA_CONFIG.apiUrl and renders the
 * headline ratio cards, a multi-year sparkline trend, and the three financial
 * statements (Key Statistics / Income Statement / Balance Sheet) for a chosen
 * fiscal period. Pure DOM, no framework.
 */
(function () {
  "use strict";

  var cfg = window.FA_CONFIG || {};
  var els = {
    symbol: document.getElementById("fa-symbol"),
    go: document.getElementById("fa-go"),
    period: document.getElementById("fa-period"),
    status: document.getElementById("fa-status"),
    content: document.getElementById("fa-content"),
    ticker: document.getElementById("fa-ticker"),
    secname: document.getElementById("fa-secname"),
    sector: document.getElementById("fa-sector"),
    periodLabel: document.getElementById("fa-periodlabel"),
    cards: document.getElementById("fa-cards"),
    trendSection: document.getElementById("fa-trend-section"),
    trend: document.getElementById("fa-trend"),
    tabs: document.getElementById("fa-tabs"),
    stmtBody: document.getElementById("fa-stmt-body"),
  };

  var state = { data: null, activeType: null };

  // --- formatting -----------------------------------------------------------

  function fmtPct(v) {
    if (v == null) return "—";
    return (v * 100).toFixed(2) + "%";
  }

  function fmtNum(v) {
    if (v == null) return "—";
    return v.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }

  // Source amount is in thousands of rupees; show a compact Nepali scale.
  function fmtRs000(v) {
    if (v == null) return "—";
    var rupees = v * 1000;
    var sign = rupees < 0 ? "-" : "";
    var abs = Math.abs(rupees);
    var out;
    if (abs >= 1e9) out = (abs / 1e9).toFixed(2) + " Ar"; // arba (10^9)
    else if (abs >= 1e7) out = (abs / 1e7).toFixed(2) + " Cr"; // crore (10^7)
    else if (abs >= 1e5) out = (abs / 1e5).toFixed(2) + " L"; // lakh (10^5)
    else out = abs.toLocaleString(undefined, { maximumFractionDigits: 0 });
    return "Rs " + sign + out;
  }

  function fmtValue(v, fmt) {
    if (fmt === "pct") return fmtPct(v);
    if (fmt === "rs000") return fmtRs000(v);
    return fmtNum(v);
  }

  function periodLabel(p) {
    return "FY " + p.fy + " · Q" + p.quarter;
  }

  // --- rendering ------------------------------------------------------------

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function renderCards(headline) {
    els.cards.innerHTML = "";
    if (!headline || !headline.length) {
      els.cards.classList.add("fa-hidden");
      return;
    }
    els.cards.classList.remove("fa-hidden");
    headline.forEach(function (m) {
      var card = el("div", "fa-card");
      card.appendChild(el("div", "fa-card-label", m.label));
      card.appendChild(el("div", "fa-card-value", fmtValue(m.value, m.fmt)));
      els.cards.appendChild(card);
    });
  }

  function sparkline(points) {
    var W = 240, H = 56, gap = 3;
    var svgNS = "http://www.w3.org/2000/svg";
    var svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("class", "fa-spark");
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("preserveAspectRatio", "none");
    var vals = points.map(function (p) { return p.value; });
    var max = Math.max.apply(null, vals.concat([0]));
    var min = Math.min.apply(null, vals.concat([0]));
    var range = max - min || 1;
    var n = points.length;
    var bw = (W - gap * (n - 1)) / n;
    var zeroY = H - ((0 - min) / range) * H;
    points.forEach(function (p, i) {
      var x = i * (bw + gap);
      var y = H - ((p.value - min) / range) * H;
      var top = Math.min(y, zeroY);
      var h = Math.max(1, Math.abs(zeroY - y));
      var rect = document.createElementNS(svgNS, "rect");
      rect.setAttribute("class", p.value < 0 ? "bar neg" : "bar");
      rect.setAttribute("x", x.toFixed(1));
      rect.setAttribute("y", top.toFixed(1));
      rect.setAttribute("width", bw.toFixed(1));
      rect.setAttribute("height", h.toFixed(1));
      var title = document.createElementNS(svgNS, "title");
      title.textContent = p.fy + ": " + p.value;
      rect.appendChild(title);
      svg.appendChild(rect);
    });
    return svg;
  }

  function renderTrend(trend) {
    els.trend.innerHTML = "";
    if (!trend || !trend.length) {
      els.trendSection.classList.add("fa-hidden");
      return;
    }
    els.trendSection.classList.remove("fa-hidden");
    trend.forEach(function (series) {
      var card = el("div", "fa-trend-card");
      var head = el("div", "fa-trend-head");
      head.appendChild(el("span", "fa-trend-label", series.label));
      var last = series.points[series.points.length - 1];
      head.appendChild(el("span", "fa-trend-latest", fmtValue(last.value, series.fmt)));
      card.appendChild(head);
      card.appendChild(sparkline(series.points));
      els.trend.appendChild(card);
    });
  }

  function renderTabs(statements) {
    els.tabs.innerHTML = "";
    statements.forEach(function (s) {
      var btn = el("button", "fa-tab" + (s.type === state.activeType ? " active" : ""), s.label);
      btn.dataset.type = s.type;
      btn.addEventListener("click", function () {
        state.activeType = s.type;
        renderTabs(statements);
        renderStatement(s);
      });
      els.tabs.appendChild(btn);
    });
  }

  function renderStatement(stmt) {
    els.stmtBody.innerHTML = "";
    if (!stmt || !stmt.rows.length) {
      var tr = el("tr");
      var td = el("td", null, "No line items for this statement/period.");
      td.colSpan = 2;
      td.style.opacity = ".6";
      td.style.padding = "20px 14px";
      tr.appendChild(td);
      els.stmtBody.appendChild(tr);
      return;
    }
    stmt.rows.forEach(function (r) {
      var tr = el("tr", r.header ? "fa-row-header" : null);
      tr.appendChild(el("td", null, r.name || r.code));
      tr.appendChild(el("td", "fa-amt", fmtValue(r.amount, r.fmt)));
      els.stmtBody.appendChild(tr);
    });
  }

  function renderPeriods(periods, selected) {
    els.period.innerHTML = "";
    periods.forEach(function (p) {
      var opt = el("option", null, periodLabel(p));
      opt.value = p.fy + "|" + p.quarter;
      if (p.fy === selected.fy && p.quarter === selected.quarter) opt.selected = true;
      els.period.appendChild(opt);
    });
  }

  function render(data) {
    state.data = data;
    state.activeType = (data.statements[0] || {}).type || null;

    els.ticker.textContent = data.symbol;
    els.secname.textContent = data.profile.security_name || "";
    if (data.profile.sector_name) {
      els.sector.textContent = data.profile.sector_name;
      els.sector.classList.remove("fa-hidden");
    } else {
      els.sector.classList.add("fa-hidden");
    }
    els.periodLabel.textContent = periodLabel(data.selected);

    renderPeriods(data.periods, data.selected);
    renderCards(data.headline);
    renderTrend(data.trend);
    renderTabs(data.statements);
    var active = data.statements.find(function (s) { return s.type === state.activeType; });
    renderStatement(active || data.statements[0]);

    els.status.classList.add("fa-hidden");
    els.content.classList.remove("fa-hidden");
  }

  // --- loading --------------------------------------------------------------

  function showStatus(msg) {
    els.status.textContent = msg;
    els.status.classList.remove("fa-hidden");
    els.content.classList.add("fa-hidden");
  }

  function load(symbol, fy, quarter) {
    var sym = (symbol || "").trim().toUpperCase();
    if (!sym) {
      showStatus("Search a company to view its fundamentals.");
      return;
    }
    showStatus("Loading " + sym + "…");
    var url = cfg.apiUrl + "?symbol=" + encodeURIComponent(sym);
    if (fy) url += "&fy=" + encodeURIComponent(fy);
    if (quarter != null) url += "&quarter=" + encodeURIComponent(quarter);
    fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, body: j }; }); })
      .then(function (res) {
        if (!res.ok || !res.body.ok) {
          showStatus(res.body.error || "Unable to load fundamentals.");
          return;
        }
        render(res.body);
      })
      .catch(function () { showStatus("Network error while loading fundamentals."); });
  }

  // --- events ---------------------------------------------------------------

  function loadFromInput() {
    load(els.symbol.value);
  }

  els.go.addEventListener("click", loadFromInput);
  els.symbol.addEventListener("keydown", function (e) {
    if (e.key === "Enter") loadFromInput();
  });
  els.symbol.addEventListener("change", loadFromInput);
  els.period.addEventListener("change", function () {
    if (!state.data) return;
    var parts = els.period.value.split("|");
    load(state.data.symbol, parts[0], parts[1]);
  });

  // --- boot -----------------------------------------------------------------

  if (cfg.symbol) {
    els.symbol.value = cfg.symbol;
    load(cfg.symbol);
  }
})();
