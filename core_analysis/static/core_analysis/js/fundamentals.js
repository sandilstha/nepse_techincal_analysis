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
    subtabs: document.getElementById("fa-subtabs"),
    panelStatement: document.getElementById("fa-panel-statement"),
    panelMorningstar: document.getElementById("fa-panel-morningstar"),
    morningstar: document.getElementById("fa-morningstar"),
  };

  var state = { data: null, activeType: null, activeSubtab: "statement" };

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
    renderMorningstar(data);

    els.status.classList.add("fa-hidden");
    els.content.classList.remove("fa-hidden");
  }

  // --- Morningstar-style research ------------------------------------------
  // Derived entirely from the data already loaded for the Financial Statement
  // tab (KS line items + the annual trend) — no extra request, so switching
  // tabs is instant and never changes the statement tab's behaviour.

  var GRADE_CLASS = { A: "grade-A", B: "grade-B", C: "grade-C", D: "grade-D", F: "grade-F" };
  var GRADE_POINTS = { A: 4, B: 3, C: 2, D: 1, F: 0 };

  // Grade a value against four descending/ascending boundaries.
  function grade(value, bounds, higherBetter) {
    if (value == null || isNaN(value)) return null;
    var letters = ["A", "B", "C", "D"];
    for (var i = 0; i < bounds.length; i++) {
      if (higherBetter ? value >= bounds[i] : value <= bounds[i]) return letters[i];
    }
    return "F";
  }

  function ksLookup(data) {
    var ks = (data.statements || []).find(function (s) { return s.type === "KS"; });
    var map = {};
    if (ks) ks.rows.forEach(function (r) { map[r.code] = r.amount; });
    return map;
  }

  // Compound annual growth rate across a trend series' points (first→last).
  function cagr(points) {
    if (!points || points.length < 2) return null;
    var first = points[0].value, last = points[points.length - 1].value;
    var years = points.length - 1;
    if (first == null || last == null || first <= 0 || last <= 0) return null;
    return Math.pow(last / first, 1 / years) - 1;
  }

  function trendByLabel(data, label) {
    var s = (data.trend || []).find(function (t) { return t.label === label; });
    return s ? s.points : null;
  }

  function msMetric(label, valueStr, gr) {
    var row = el("div", "ms-metric");
    row.appendChild(el("span", "ms-k", label));
    var rhs = el("div", "ms-rhs");
    rhs.appendChild(el("span", "ms-v", valueStr));
    if (gr) rhs.appendChild(el("span", "ms-grade " + GRADE_CLASS[gr], gr));
    row.appendChild(rhs);
    return row;
  }

  function msSection(title, metrics) {
    var frag = document.createDocumentFragment();
    frag.appendChild(el("div", "fa-section-title", title));
    var grid = el("div", "ms-grid");
    var graded = [];
    metrics.forEach(function (m) {
      if (m.value == null || isNaN(m.value)) return;
      var gr = m.bounds ? grade(m.value, m.bounds, m.higherBetter) : null;
      if (gr) graded.push(gr);
      grid.appendChild(msMetric(m.label, fmtValue(m.value, m.fmt), gr));
    });
    frag.appendChild(grid);
    return { frag: frag, grades: graded, count: metrics.length };
  }

  function renderMorningstar(data) {
    var host = els.morningstar;
    host.innerHTML = "";

    var ks = ksLookup(data);
    var price = ks["cb_ks_512_market_value_per_share"];
    var eps = ks["cb_ks_509_eps_annualized"];
    var pe = ks["cb_ks_510_reported_pe_annualized"];
    var bvps = ks["cb_ks_511_book_value_per_share"];
    var dps = ks["cb_ks_513_dividend_per_share_rs"];
    var roe = ks["cb_ks_508_return_on_equity_ttm"];
    var roa = ks["cb_ks_507_return_on_asset_ttm"];
    var grossMargin = ks["cb_ks_504_margin_mrq_percent"];
    var revenue = ks["cb_ks_501_total_revenue_rs_000"];
    var netIncome = ks["cb_ks_505_net_income_rs_000"];

    var pb = (price != null && bvps) ? price / bvps : null;
    var divYield = (dps != null && price) ? dps / price : null;
    var earnYield = (eps != null && price) ? eps / price : null;
    var netMargin = (netIncome != null && revenue) ? netIncome / revenue : null;

    var revCagr = cagr(trendByLabel(data, "Total Revenue"));
    var niCagr = cagr(trendByLabel(data, "Net Income"));
    var epsCagr = cagr(trendByLabel(data, "EPS"));

    var valuation = msSection("Valuation", [
      { label: "Price / Earnings", value: pe, fmt: "num", bounds: [12, 18, 25, 35], higherBetter: false },
      { label: "Price / Book", value: pb, fmt: "num", bounds: [1, 2, 3, 4], higherBetter: false },
      { label: "Dividend Yield", value: divYield, fmt: "pct", bounds: [0.05, 0.03, 0.015, 0.005], higherBetter: true },
      { label: "Earnings Yield", value: earnYield, fmt: "pct", bounds: [0.10, 0.07, 0.05, 0.03], higherBetter: true },
    ]);

    var profitability = msSection("Profitability & Returns", [
      { label: "Return on Equity", value: roe, fmt: "pct", bounds: [0.20, 0.15, 0.10, 0.05], higherBetter: true },
      { label: "Return on Assets", value: roa, fmt: "pct", bounds: [0.02, 0.015, 0.01, 0.005], higherBetter: true },
      { label: "Net Margin", value: netMargin, fmt: "pct", bounds: [0.25, 0.18, 0.10, 0.05], higherBetter: true },
      { label: "Gross Margin (MRQ)", value: grossMargin, fmt: "pct", bounds: [0.50, 0.35, 0.20, 0.10], higherBetter: true },
    ]);

    var growth = msSection("Growth (annual CAGR)", [
      { label: "Revenue CAGR", value: revCagr, fmt: "pct", bounds: [0.20, 0.12, 0.06, 0.0], higherBetter: true },
      { label: "Net Income CAGR", value: niCagr, fmt: "pct", bounds: [0.20, 0.12, 0.06, 0.0], higherBetter: true },
      { label: "EPS CAGR", value: epsCagr, fmt: "pct", bounds: [0.20, 0.12, 0.06, 0.0], higherBetter: true },
    ]);

    // Composite star rating from every graded metric (4=A … 0=F → 1–5 stars).
    var allGrades = valuation.grades.concat(profitability.grades, growth.grades);
    var stars = null, avg = null;
    if (allGrades.length) {
      var sum = allGrades.reduce(function (a, g) { return a + GRADE_POINTS[g]; }, 0);
      avg = sum / allGrades.length;
      stars = Math.max(1, Math.min(5, Math.round((avg / 4) * 5)));
    }
    var VERDICTS = {
      5: ["Undervalued · high quality", "Strong fundamentals at an attractive price"],
      4: ["Attractive", "Solid quality with reasonable valuation"],
      3: ["Fairly valued", "Quality and price broadly balanced"],
      2: ["Caution", "Stretched valuation or softer fundamentals"],
      1: ["Expensive · weak", "Rich price relative to fundamentals"],
    };

    host.appendChild(buildSummary(stars, VERDICTS[stars] || ["—", "Not enough data to score"], price, pe, divYield));

    // Sector-peer research (Morningstar "Fair Value" + "% Rank in Category").
    var ms = data.morningstar;
    if (ms && ms.fair_value) host.appendChild(buildFairValue(ms.fair_value));
    if (ms && ms.ranks && ms.ranks.length) host.appendChild(buildPeerRanks(ms));

    host.appendChild(valuation.frag);
    host.appendChild(profitability.frag);
    host.appendChild(growth.frag);

    var note = el("div", "ms-note");
    note.textContent =
      "Morningstar-style research derived from reported NEPSE fundamentals: A–F grades are heuristic and the fair value is the " +
      "sector-median P/E applied to EPS — both are illustrative, not official Morningstar ratings. Sector context matters.";
    host.appendChild(note);
  }

  function buildFairValue(fv) {
    var frag = document.createDocumentFragment();
    frag.appendChild(el("div", "fa-section-title", "Valuation vs fair value"));
    var box = el("div", "ms-fv");

    function cell(label, value) {
      var c = el("div", "ms-fv-cell");
      c.appendChild(el("b", null, value));
      c.appendChild(el("span", null, label));
      return c;
    }
    box.appendChild(cell("Current Price", fv.price != null ? fmtNum(fv.price) : "—"));
    box.appendChild(cell("Fair Value Est.", fv.estimate != null ? fmtNum(fv.estimate) : "—"));
    box.appendChild(cell("Price / Fair Value", fv.ratio != null ? fv.ratio.toFixed(2) : "—"));
    box.appendChild(cell("Sector Median P/E", fv.sector_pe != null ? fmtNum(fv.sector_pe) : "—"));

    var cls = fv.verdict === "Undervalued" ? "verdict-under"
            : fv.verdict === "Overvalued" ? "verdict-over" : "verdict-fair";
    box.appendChild(el("span", "ms-verdict-pill " + cls, fv.verdict));
    frag.appendChild(box);
    return frag;
  }

  function buildPeerRanks(ms) {
    var frag = document.createDocumentFragment();
    frag.appendChild(el("div", "fa-section-title",
      "Sector percentile rank · " + ms.sector + " (" + ms.peer_count + " peers)"));

    ms.ranks.forEach(function (r) {
      var row = el("div", "ms-rank");
      var head = el("div", "ms-rank-head");
      head.appendChild(el("span", null, r.label));
      var rhs = el("span", null);
      rhs.appendChild(el("span", "ms-rank-val", fmtValue(r.value, r.fmt)));
      if (r.percentile != null) {
        rhs.appendChild(document.createTextNode("  "));
        rhs.appendChild(el("span", "ms-rank-pct", "top " + (100 - r.percentile) + "%"));
      }
      head.appendChild(rhs);
      row.appendChild(head);

      var bar = el("div", "ms-rank-bar");
      var fill = el("i", null);
      fill.style.width = (r.percentile != null ? r.percentile : 0) + "%";
      bar.appendChild(fill);
      row.appendChild(bar);

      if (r.median != null) {
        row.appendChild(el("div", "ms-rank-sub",
          "Sector median " + fmtValue(r.median, r.fmt) +
          (r.percentile != null ? " · better than " + r.percentile + "% of peers" : "")));
      }
      frag.appendChild(row);
    });
    return frag;
  }

  function buildSummary(stars, verdict, price, pe, divYield) {
    var box = el("div", "ms-summary");

    var rating = el("div", "ms-rating");
    var starsEl = el("div", "ms-stars");
    if (stars) {
      for (var i = 1; i <= 5; i++) {
        var s = el("span", i <= stars ? "" : "off", "★");
        starsEl.appendChild(s);
      }
    } else {
      starsEl.textContent = "—";
    }
    rating.appendChild(starsEl);
    rating.appendChild(el("div", "ms-verdict", verdict[0]));
    rating.appendChild(el("div", "ms-verdict-sub", verdict[1]));
    box.appendChild(rating);

    var stats = el("div", "ms-summary-stats");
    [
      ["Price", price != null ? fmtNum(price) : "—"],
      ["P/E", pe != null ? fmtNum(pe) : "—"],
      ["Div Yield", divYield != null ? fmtPct(divYield) : "—"],
    ].forEach(function (pair) {
      var s = el("div", "ms-s");
      s.appendChild(el("b", null, pair[1]));
      s.appendChild(el("span", null, pair[0]));
      stats.appendChild(s);
    });
    box.appendChild(stats);
    return box;
  }

  // --- sub-tab switching ----------------------------------------------------

  function setSubtab(name) {
    state.activeSubtab = name;
    var isStmt = name === "statement";
    els.panelStatement.classList.toggle("fa-hidden", !isStmt);
    els.panelMorningstar.classList.toggle("fa-hidden", isStmt);
    Array.prototype.forEach.call(els.subtabs.querySelectorAll(".fa-subtab"), function (b) {
      var on = b.dataset.subtab === name;
      b.classList.toggle("active", on);
      b.setAttribute("aria-selected", on ? "true" : "false");
    });
  }

  if (els.subtabs) {
    els.subtabs.addEventListener("click", function (e) {
      var btn = e.target.closest(".fa-subtab");
      if (btn) setSubtab(btn.dataset.subtab);
    });
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
