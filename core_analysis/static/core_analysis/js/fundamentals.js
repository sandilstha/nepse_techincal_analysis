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
    status: document.getElementById("fa-status"),
    content: document.getElementById("fa-content"),
    ticker: document.getElementById("fa-ticker"),
    secname: document.getElementById("fa-secname"),
    sector: document.getElementById("fa-sector"),
    periodLabel: document.getElementById("fa-periodlabel"),
    cards: document.getElementById("fa-cards"),
    trendSection: document.getElementById("fa-trend-section"),
    trend: document.getElementById("fa-trend"),
    subtabs: document.getElementById("fa-subtabs"),
    panelStatement: document.getElementById("fa-panel-statement"),
    panelMorningstar: document.getElementById("fa-panel-morningstar"),
    morningstar: document.getElementById("fa-morningstar"),
    model: document.getElementById("fa-model"),
    // Company Financials matrix controls.
    fmStatement: document.getElementById("fm-statement"),
    fmVersion: document.getElementById("fm-version"),
    fmPeriods: document.getElementById("fm-periods"),
    fmLoad: document.getElementById("fm-load"),
    fmTable: document.getElementById("fm-table"),
  };

  var state = { data: null, activeSubtab: "statement", matrix: null };

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
    return fmtRs(v * 1000);
  }

  function fmtRs(v) {
    if (v == null || isNaN(v)) return "—";
    var rupees = v;
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

  function render(data) {
    state.data = data;

    els.ticker.textContent = data.symbol;
    els.secname.textContent = data.profile.security_name || "";
    if (data.profile.sector_name) {
      els.sector.textContent = data.profile.sector_name;
      els.sector.classList.remove("fa-hidden");
    } else {
      els.sector.classList.add("fa-hidden");
    }
    els.periodLabel.textContent = "Ratios as of " + periodLabel(data.selected);

    renderCards(data.headline);
    renderTrend(data.trend);
    loadMatrix();  // multi-period Company Financials matrix (own request)
    state.modelLoaded = false;
    if (state.activeSubtab === "morningstar") loadModel();

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

  // --- Company Financials matrix (multi-period statement table) -------------

  // Numbers in the matrix mirror the source scale (e.g. Rs '000 shown as-is,
  // grouped) rather than the compact card formatting.
  function fmtCell(v, fmt) {
    if (v == null || isNaN(v)) return "—";
    if (fmt === "pct") return (v * 100).toFixed(2) + "%";
    if (fmt === "rs000") return Math.round(v).toLocaleString();
    return v.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }

  function fmtGrowth(curr, prev) {
    if (curr == null || prev == null || prev === 0) return { text: "", cls: "" };
    var g = curr / prev - 1;
    return { text: (g * 100).toFixed(2) + "%", cls: g >= 0 ? "fm-up" : "fm-down" };
  }

  // "2025/26" → "2024/25" (the same quarter one fiscal year earlier).
  function prevFy(fy) {
    var m = (fy || "").split("/");
    if (m.length !== 2) return null;
    var a = parseInt(m[0], 10), b = parseInt(m[1], 10);
    if (isNaN(a) || isNaN(b)) return null;
    var pb = String((b - 1 + 100) % 100);
    if (pb.length < 2) pb = "0" + pb;
    return (a - 1) + "/" + pb;
  }

  function loadMatrix() {
    if (!state.data) return;
    var url = cfg.matrixUrl + "?symbol=" + encodeURIComponent(state.data.symbol) +
      "&statement=" + encodeURIComponent(els.fmStatement.value) +
      "&periods=" + encodeURIComponent(els.fmPeriods.value);
    if (els.fmVersion.value) url += "&data_version=" + encodeURIComponent(els.fmVersion.value);
    els.fmTable.innerHTML = '<tbody><tr><td class="fm-empty">Loading…</td></tr></tbody>';
    fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (r) { return r.json(); })
      .then(function (m) {
        if (!m.ok) {
          els.fmTable.innerHTML = '<tbody><tr><td class="fm-empty">' +
            (m.error || "No data.") + "</td></tr></tbody>";
          return;
        }
        state.matrix = m;
        syncVersionOptions(m);
        renderMatrix(m);
      })
      .catch(function () {
        els.fmTable.innerHTML = '<tbody><tr><td class="fm-empty">Network error.</td></tr></tbody>';
      });
  }

  function syncVersionOptions(m) {
    if (els.fmVersion.options.length === m.data_versions.length && els.fmVersion.value) return;
    els.fmVersion.innerHTML = "";
    m.data_versions.forEach(function (v) {
      var label = v.charAt(0) + v.slice(1).toLowerCase(); // PUBLISHED → Published
      var opt = el("option", null, label);
      opt.value = v;
      if (v === m.data_version) opt.selected = true;
      els.fmVersion.appendChild(opt);
    });
  }

  function renderMatrix(m) {
    els.fmTable.innerHTML = "";
    if (!m.columns.length || !m.rows.length) {
      els.fmTable.innerHTML = '<tbody><tr><td class="fm-empty">No line items.</td></tr></tbody>';
      return;
    }

    // Alternate a subtle band per fiscal-year group of columns.
    var bandByKey = {}, fyOrder = [];
    m.columns.forEach(function (c) {
      if (fyOrder.indexOf(c.fy) === -1) fyOrder.push(c.fy);
      bandByKey[c.key] = fyOrder.indexOf(c.fy) % 2 === 1;
    });

    // Header.
    var thead = el("thead");
    var htr = el("tr");
    htr.appendChild(thEl("Financial Year", "fm-firstcol"));
    m.columns.forEach(function (c) {
      var th = thEl("", bandByKey[c.key] ? "fm-band" : null);
      th.appendChild(el("span", "fm-yr", c.fy));
      th.appendChild(el("span", "fm-q", "Q" + c.quarter));
      htr.appendChild(th);
    });
    thead.appendChild(htr);
    els.fmTable.appendChild(thead);

    var tbody = el("tbody");
    m.rows.forEach(function (row) {
      var isTotal = /\bTOTAL\b/.test(row.name || "");
      var cls = isTotal ? "fm-row-total" : (row.header ? "fm-row-section" : null);
      var tr = el("tr", cls);
      tr.appendChild(tdEl(row.name || row.code, "fm-firstcol"));
      m.columns.forEach(function (c) {
        var td = tdEl(fmtCell(row.values[c.key], row.fmt), bandByKey[c.key] ? "fm-band" : null);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);

      // Growth sub-rows under section/total rows: QoQ and YoY.
      if (row.header) {
        tbody.appendChild(growthRow(row, m.columns, bandByKey, "↳ Over Prior Period", "qoq"));
        tbody.appendChild(growthRow(row, m.columns, bandByKey, "↳ Period on Period", "yoy"));
      }
    });
    els.fmTable.appendChild(tbody);
  }

  function growthRow(row, columns, bandByKey, label, mode) {
    var tr = el("tr", "fm-growth");
    tr.appendChild(tdEl(label, "fm-firstcol"));
    columns.forEach(function (c, i) {
      var curr = row.values[c.key], prev;
      if (mode === "qoq") {
        var nxt = columns[i + 1];                 // next column = previous period
        prev = nxt ? row.values[nxt.key] : null;
      } else {                                     // yoy: same quarter, prior fy
        prev = row.values[prevFy(c.fy) + "|" + c.quarter];
      }
      var g = fmtGrowth(curr, prev);
      var td = tdEl(g.text, (bandByKey[c.key] ? "fm-band " : "") + g.cls);
      tr.appendChild(td);
    });
    return tr;
  }

  function thEl(text, cls) {
    var th = document.createElement("th");
    if (cls) th.className = cls;
    if (text) th.textContent = text;
    return th;
  }
  function tdEl(text, cls) {
    var td = document.createElement("td");
    if (cls) td.className = cls;
    if (text != null) td.textContent = text;
    return td;
  }

  if (els.fmStatement) {
    els.fmStatement.addEventListener("change", loadMatrix);
    els.fmVersion.addEventListener("change", loadMatrix);
    els.fmPeriods.addEventListener("change", loadMatrix);
    els.fmLoad.addEventListener("click", loadMatrix);
  }

  // --- Growth & Value model (Morningstar-style sector scoring) -------------

  function loadModel(sector) {
    state.modelLoading = true;
    els.model.innerHTML = '<div class="fa-section-title">Sector Growth &amp; Value model</div>' +
      '<div class="fm-empty">Scoring sector peers…</div>';
    // Independent of the Financial Statement tab: pick a sector directly, else
    // default to the searched company's sector, else the first sector.
    var qs = "";
    if (sector) qs = "sector=" + encodeURIComponent(sector);
    else if (state.data) qs = "symbol=" + encodeURIComponent(state.data.symbol);
    fetch(cfg.modelUrl + (qs ? "?" + qs : ""),
      { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (r) { return r.json(); })
      .then(function (m) {
        state.modelLoading = false;
        if (!m.ok || !m.results.length) {
          state.modelLoaded = false;
          els.model.innerHTML = '<div class="fa-section-title">Sector Growth &amp; Value model</div>' +
            '<div class="fm-empty">' + (m.error || "Not enough peers to score.") + "</div>";
          return;
        }
        state.modelLoaded = true;
        state.model = m;
        state.gvFilter = { segment: "", score: "", q: "" };
        state.gvSort = { col: "score", dir: "desc" };
        state.gvPage = 1;
        renderModel(m);
      })
      .catch(function () {
        state.modelLoading = false;
        state.modelLoaded = false;
        els.model.innerHTML = '<div class="fm-empty">Network error.</div>';
      });
  }

  function renderModel(m) {
    els.model.innerHTML = "";

    // Header with a sector picker.
    var head = el("div", "gv-head");
    head.appendChild(el("h3", null, "Growth & Value model"));
    var secSel = el("select", "fa-select");
    secSel.id = "gv-sector";
    (m.sectors || [m.sector]).forEach(function (s) {
      var opt = el("option", null, s);
      opt.value = s;
      if (s === m.sector) opt.selected = true;
      secSel.appendChild(opt);
    });
    secSel.addEventListener("change", function (e) { loadModel(e.target.value); });
    head.appendChild(secSel);
    head.appendChild(el("span", "gv-sub",
      m.results.length + " companies · FY " + m.selected.fy + " Q" + m.selected.quarter));
    els.model.appendChild(head);

    // Summary cards.
    var cards = el("div", "gv-cards");
    [["total", "Companies", ""], ["strong", "Strong (3)", "s3"],
     ["watch", "Watchlist (2)", "s2"], ["weak", "Weak (1)", "s1"]].forEach(function (c) {
      var card = el("div", "gv-card" + (c[2] ? " " + c[2] : ""));
      card.appendChild(el("b", null, String(m.summary[c[0]])));
      card.appendChild(el("span", null, c[1]));
      cards.appendChild(card);
    });
    els.model.appendChild(cards);

    // Growth-vs-Value scatter with a market-cap filter. The cap buttons drive
    // both this chart and the ranking table below.
    var sw = el("div", "gv-scatter-wrap");
    var capRow = el("div", "gv-cap-row");
    capRow.appendChild(el("span", "gv-cap-label", "Market cap:"));
    var segCounts = m.segment_summary || {};
    var capOptions = [
      ["", "All", m.results.length],
      ["Large", "Large", segCounts.Large || 0],
      ["Mid", "Mid", segCounts.Mid || 0],
      ["Small", "Small", segCounts.Small || 0],
    ];
    if (segCounts.Unclassified) capOptions.push(["Unclassified", "Unclassified", segCounts.Unclassified]);
    capOptions.forEach(function (o) {
      var label = o[1] + " (" + o[2] + ")";
      var b = el("button", "gv-cap-btn" + (state.gvFilter.segment === o[0] ? " active" : ""), label);
      b.dataset.seg = o[0];
      b.addEventListener("click", function () {
        state.gvFilter.segment = o[0];
        state.gvPage = 1;
        Array.prototype.forEach.call(capRow.querySelectorAll(".gv-cap-btn"), function (x) {
          x.classList.toggle("active", x.dataset.seg === o[0]);
        });
        renderGvChart();
        renderGvRows();
      });
      capRow.appendChild(b);
    });
    sw.appendChild(capRow);
    var chartHost = el("div", null);
    chartHost.id = "gv-chart";
    sw.appendChild(chartHost);
    els.model.appendChild(sw);

    // Filters (Score + ticker search; segment is the cap buttons above).
    var filters = el("div", "gv-filters");
    filters.appendChild(selectCtrl("Score", "gv-f-score",
      [["", "All"], ["3", "Strong (3)"], ["2", "Watchlist (2)"], ["1", "Weak (1)"]]));
    var sLabel = el("label", "fm-ctrl");
    sLabel.appendChild(el("span", null, "Search"));
    var sInput = el("input", "fa-input");
    sInput.id = "gv-f-q";
    sInput.placeholder = "Ticker…";
    sInput.style.textTransform = "uppercase";
    sLabel.appendChild(sInput);
    filters.appendChild(sLabel);

    // Pager lives in the filters toolbar (next to Score), not below the table.
    var pager = el("div", "gv-pager");
    pager.id = "gv-pager";
    pager.style.marginTop = "0";
    pager.style.marginLeft = "auto";
    filters.appendChild(pager);

    els.model.appendChild(filters);

    // Table — sortable headers + pagination.
    var wrap = el("div", "gv-table-wrap");
    var table = el("table", "gv-table");
    var thead = el("thead");
    var htr = el("tr");
    GV_COLS.forEach(function (col) {
      var th = el("th", (col.num ? "" : "gv-l ") + "gv-sortable");
      th.dataset.col = col.key;
      th.appendChild(el("span", null, col.label));
      th.appendChild(el("span", "gv-arrow", ""));
      htr.appendChild(th);
    });
    thead.appendChild(htr);
    table.appendChild(thead);
    table.appendChild(el("tbody", null));
    table.querySelector("tbody").id = "gv-tbody";
    wrap.appendChild(table);
    els.model.appendChild(wrap);

    htr.addEventListener("click", function (e) {
      var th = e.target.closest(".gv-sortable");
      if (!th) return;
      var col = th.dataset.col;
      if (state.gvSort.col === col) state.gvSort.dir = state.gvSort.dir === "asc" ? "desc" : "asc";
      else { state.gvSort.col = col; state.gvSort.dir = col === "ticker" || col === "name" ? "asc" : "desc"; }
      state.gvPage = 1;
      renderGvRows();
    });
    document.getElementById("gv-f-score").addEventListener("change", function (e) {
      state.gvFilter.score = e.target.value; state.gvPage = 1; renderGvRows();
    });
    sInput.addEventListener("input", function (e) {
      state.gvFilter.q = e.target.value.trim().toUpperCase(); state.gvPage = 1; renderGvRows();
    });
    renderGvChart();
    renderGvRows();
  }

  // Render the scatter into #gv-chart for the currently selected cap segment.
  function renderGvChart() {
    var host = document.getElementById("gv-chart");
    if (!host || !state.model) return;
    host.innerHTML = "";
    var seg = state.gvFilter.segment;
    var subset = state.model.results.filter(function (r) {
      return (!seg || r.segment === seg) && r.growth != null && r.value != null;
    });

    var bar = el("div", "gv-chart-bar");
    var chartLabel = seg ? (seg === "Unclassified" ? seg : seg + " cap") : "All cap";
    bar.appendChild(el("span", "fa-section-title", chartLabel + " · " + subset.length + " companies"));
    var bOut, bIn, bReset;
    if (subset.length) {
      var zoom = el("div", "gv-zoom");
      zoom.appendChild(el("span", "gv-zoom-hint", "scroll to zoom · drag to pan"));
      bOut = el("button", "fa-btn ghost", "−");
      bIn = el("button", "fa-btn ghost", "+");
      bReset = el("button", "fa-btn ghost", "Reset");
      zoom.appendChild(bOut); zoom.appendChild(bIn); zoom.appendChild(bReset);
      bar.appendChild(zoom);
    }
    host.appendChild(bar);

    if (!subset.length) { host.appendChild(el("div", "fm-empty", "No companies.")); return; }
    var svg = buildScatter(subset, state.data ? state.data.symbol : null);
    host.appendChild(svg);
    var api = attachZoom(svg);
    bIn.addEventListener("click", api.zoomIn);
    bOut.addEventListener("click", api.zoomOut);
    bReset.addEventListener("click", api.reset);
  }

  // Interactive zoom/pan over an SVG via its viewBox. Wheel zooms toward the
  // cursor, drag pans; can't zoom out past the fitted window. Listeners live on
  // the svg, so they're discarded when the chart is re-rendered (no leak).
  function attachZoom(svg) {
    var vb = svg.getAttribute("viewBox").split(/\s+/).map(Number);
    var base = { x: vb[0], y: vb[1], w: vb[2], h: vb[3] };
    var cur = { x: base.x, y: base.y, w: base.w, h: base.h };

    function apply() { svg.setAttribute("viewBox", cur.x + " " + cur.y + " " + cur.w + " " + cur.h); }
    function clampPan() {
      if (cur.x < base.x) cur.x = base.x;
      if (cur.y < base.y) cur.y = base.y;
      if (cur.x + cur.w > base.x + base.w) cur.x = base.x + base.w - cur.w;
      if (cur.y + cur.h > base.y + base.h) cur.y = base.y + base.h - cur.h;
    }
    function zoomAt(factor, ax, ay) {
      var minW = base.w / 24;
      var newW = Math.min(base.w, Math.max(minW, cur.w / factor));
      var newH = newW * (base.h / base.w);
      cur.x = ax - (ax - cur.x) * (newW / cur.w);
      cur.y = ay - (ay - cur.y) * (newH / cur.h);
      cur.w = newW; cur.h = newH;
      clampPan(); apply();
    }
    function toSvg(cx, cy) {
      var m = svg.getScreenCTM();
      if (!m) return null;
      var pt = svg.createSVGPoint();
      pt.x = cx; pt.y = cy;
      return pt.matrixTransform(m.inverse());
    }

    svg.addEventListener("wheel", function (e) {
      e.preventDefault();
      var loc = toSvg(e.clientX, e.clientY);
      if (loc) zoomAt(e.deltaY < 0 ? 1.2 : 1 / 1.2, loc.x, loc.y);
    }, { passive: false });

    var drag = null;
    svg.addEventListener("mousedown", function (e) {
      var loc = toSvg(e.clientX, e.clientY);
      if (loc) { drag = loc; svg.classList.add("grabbing"); }
    });
    function onMove(e) {
      if (!drag) return;
      var loc = toSvg(e.clientX, e.clientY);
      if (!loc) return;
      cur.x -= (loc.x - drag.x);
      cur.y -= (loc.y - drag.y);
      clampPan(); apply();
      drag = toSvg(e.clientX, e.clientY);  // re-anchor in the updated coord system
    }
    function endDrag() { drag = null; svg.classList.remove("grabbing"); }
    svg.addEventListener("mousemove", onMove);
    svg.addEventListener("mouseup", endDrag);
    svg.addEventListener("mouseleave", endDrag);

    return {
      zoomIn: function () { zoomAt(1.4, cur.x + cur.w / 2, cur.y + cur.h / 2); },
      zoomOut: function () { zoomAt(1 / 1.4, cur.x + cur.w / 2, cur.y + cur.h / 2); },
      reset: function () { cur = { x: base.x, y: base.y, w: base.w, h: base.h }; apply(); },
    };
  }

  var GV_COLS = [
    { key: "ticker", label: "Ticker" },
    { key: "name", label: "Company" },
    { key: "segment", label: "Segment" },
    { key: "market_cap", label: "Market Cap", num: true, fmt: "money" },
    { key: "growth", label: "Growth", num: true },
    { key: "value", label: "Value", num: true },
    { key: "score", label: "Score", num: true },
    { key: "decision", label: "Decision" },
  ];
  var GV_PAGE_SIZE_OPTIONS = [5, 10, 20, 50, 100, 200];
  var GV_PAGE_SIZE = GV_PAGE_SIZE_OPTIONS[0];

  function renderGvRows() {
    var m = state.model, f = state.gvFilter;
    var body = document.getElementById("gv-tbody");
    if (!m || !body) return;
    body.innerHTML = "";
    var sel = state.data ? state.data.symbol : null;

    // Filter.
    var rows = m.results.filter(function (r) {
      if (f.segment && r.segment !== f.segment) return false;
      if (f.score && String(r.score) !== f.score) return false;
      if (f.q && r.ticker.indexOf(f.q) === -1) return false;
      return true;
    });

    // Sort.
    var sc = state.gvSort, dir = sc.dir === "asc" ? 1 : -1;
    var numeric = GV_COLS.some(function (c) { return c.key === sc.col && c.num; });
    rows.sort(function (a, b) {
      var x = a[sc.col], y = b[sc.col];
      if (x == null && y == null) return 0;
      if (x == null) return 1;          // nulls always last
      if (y == null) return -1;
      if (numeric) return (x - y) * dir;
      return String(x).localeCompare(String(y)) * dir;
    });

    // Paginate.
    var total = rows.length;
    var pages = Math.max(1, Math.ceil(total / GV_PAGE_SIZE));
    if (state.gvPage > pages) state.gvPage = pages;
    var start = (state.gvPage - 1) * GV_PAGE_SIZE;
    rows.slice(start, start + GV_PAGE_SIZE).forEach(function (r) {
      var tr = el("tr", r.ticker === sel ? "gv-sel" : null);
      tr.appendChild(el("td", "gv-l", r.ticker));
      tr.appendChild(el("td", "gv-l", r.name || ""));
      tr.appendChild(el("td", "gv-l", r.segment || "—"));
      tr.appendChild(el("td", null, fmtRs(r.market_cap)));
      tr.appendChild(el("td", null, r.growth != null ? r.growth.toFixed(2) : "—"));
      tr.appendChild(el("td", null, r.value != null ? r.value.toFixed(2) : "—"));
      var scoreTd = el("td", "gv-l");
      if (r.score) scoreTd.appendChild(el("span", "gv-pill s" + r.score, String(r.score)));
      else scoreTd.textContent = "—";
      tr.appendChild(scoreTd);
      tr.appendChild(el("td", "gv-l", r.decision));
      body.appendChild(tr);
    });
    if (!total) {
      var tr0 = el("tr");
      var td0 = el("td", "fm-empty", "No companies match the filters.");
      td0.colSpan = GV_COLS.length;
      tr0.appendChild(td0);
      body.appendChild(tr0);
    }

    // Sort arrows.
    Array.prototype.forEach.call(els.model.querySelectorAll(".gv-sortable"), function (th) {
      var a = th.querySelector(".gv-arrow");
      a.textContent = th.dataset.col === sc.col ? (sc.dir === "asc" ? " ▲" : " ▼") : "";
    });

    renderGvPager(total, pages, start);
  }

  function renderGvPager(total, pages, start) {
    var pager = document.getElementById("gv-pager");
    if (!pager) return;
    pager.innerHTML = "";
    if (!total) return;
    var info = el("span", "gv-page-info",
      (start + 1) + "–" + Math.min(start + GV_PAGE_SIZE, total) + " of " + total);
    var prev = el("button", "fa-btn ghost", "‹ Prev");
    var next = el("button", "fa-btn ghost", "Next ›");
    var sizeLabel = el("label", "gv-page-size");
    sizeLabel.appendChild(el("span", null, "Rows"));
    var sizeSelect = el("select", "fa-select");
    GV_PAGE_SIZE_OPTIONS.forEach(function (n) {
      var opt = el("option", null, String(n));
      opt.value = String(n);
      if (n === GV_PAGE_SIZE) opt.selected = true;
      sizeSelect.appendChild(opt);
    });
    sizeSelect.addEventListener("change", function (e) {
      GV_PAGE_SIZE = parseInt(e.target.value, 10) || GV_PAGE_SIZE_OPTIONS[0];
      state.gvPage = 1;
      renderGvRows();
    });
    sizeLabel.appendChild(sizeSelect);
    prev.disabled = state.gvPage <= 1;
    next.disabled = state.gvPage >= pages;
    prev.addEventListener("click", function () { state.gvPage--; renderGvRows(); });
    next.addEventListener("click", function () { state.gvPage++; renderGvRows(); });
    pager.appendChild(sizeLabel);
    pager.appendChild(prev);
    pager.appendChild(el("span", "gv-page-info", "Page " + state.gvPage + " / " + pages));
    pager.appendChild(next);
    pager.appendChild(info);
  }

  function selectCtrl(label, id, options) {
    var lab = el("label", "fm-ctrl");
    lab.appendChild(el("span", null, label));
    var sel = el("select", "fa-select");
    sel.id = id;
    options.forEach(function (o) {
      var opt = el("option", null, o[1]);
      opt.value = o[0];
      sel.appendChild(opt);
    });
    lab.appendChild(sel);
    return lab;
  }

  function buildScatter(results, selSymbol) {
    var NS = "http://www.w3.org/2000/svg";
    var W = 720, H = 380, pad = 52;
    var x0 = pad, x1 = W - 18, y0 = H - pad, y1 = 18;

    // Flexible ("auto-zoom") axes: fit the domain to the data so clusters spread
    // out, instead of fixing 0–100. A small pad keeps edge dots off the border.
    var gs = results.map(function (r) { return r.growth; });
    var vs = results.map(function (r) { return r.value; });
    function domain(arr) {
      var lo = Math.min.apply(null, arr), hi = Math.max.apply(null, arr);
      var span = hi - lo;
      if (span < 1e-6) { lo -= 5; hi += 5; span = hi - lo; }
      var p = span * 0.08;
      return [lo - p, hi + p];
    }
    var gd = domain(gs), vd = domain(vs);
    function sx(g) { return x0 + (g - gd[0]) / (gd[1] - gd[0]) * (x1 - x0); }
    function sy(v) { return y0 - (v - vd[0]) / (vd[1] - vd[0]) * (y0 - y1); }

    var svg = document.createElementNS(NS, "svg");
    svg.setAttribute("class", "gv-scatter");
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);

    function line(a, b, cc, dd, cls) {
      var l = document.createElementNS(NS, "line");
      l.setAttribute("x1", a); l.setAttribute("y1", b);
      l.setAttribute("x2", cc); l.setAttribute("y2", dd);
      l.setAttribute("class", cls);
      svg.appendChild(l);
    }
    function txt(x, y, s, cls, anchor) {
      var t = document.createElementNS(NS, "text");
      t.setAttribute("x", x); t.setAttribute("y", y);
      if (anchor) t.setAttribute("text-anchor", anchor);
      if (cls) t.setAttribute("class", cls);
      t.setAttribute("font-size", "10");
      t.textContent = s;
      svg.appendChild(t);
    }

    // Gridlines + numeric tick labels for the fitted domain (4 ticks/axis).
    var TICKS = 4;
    for (var i = 0; i <= TICKS; i++) {
      var gx = gd[0] + (gd[1] - gd[0]) * i / TICKS;
      var px = sx(gx);
      line(px, y0, px, y1, "gv-grid");
      txt(px, y0 + 14, gx.toFixed(0), "gv-tick", "middle");
      var vy = vd[0] + (vd[1] - vd[0]) * i / TICKS;
      var py = sy(vy);
      line(x0, py, x1, py, "gv-grid");
      txt(x0 - 6, py + 3, vy.toFixed(0), "gv-tick", "end");
    }
    line(x0, y0, x1, y0, "gv-axis");
    line(x0, y0, x0, y1, "gv-axis");
    // The 50/50 strong-quadrant guides, drawn only if inside the fitted window.
    if (50 >= gd[0] && 50 <= gd[1]) line(sx(50), y0, sx(50), y1, "gv-mid");
    if (50 >= vd[0] && 50 <= vd[1]) line(x0, sy(50), x1, sy(50), "gv-mid");

    txt((x0 + x1) / 2, H - 6, "Growth →", "gv-axis-label", "middle");
    var yl = document.createElementNS(NS, "text");
    yl.setAttribute("x", 14); yl.setAttribute("y", (y0 + y1) / 2);
    yl.setAttribute("class", "gv-axis-label");
    yl.setAttribute("font-size", "10"); yl.setAttribute("text-anchor", "middle");
    yl.setAttribute("transform", "rotate(-90 14 " + ((y0 + y1) / 2) + ")");
    yl.textContent = "Value →"; svg.appendChild(yl);

    results.forEach(function (r) {
      var isSel = r.ticker === selSymbol;
      var cx = sx(r.growth), cy = sy(r.value);
      var dot = document.createElementNS(NS, "circle");
      dot.setAttribute("cx", cx); dot.setAttribute("cy", cy);
      dot.setAttribute("r", isSel ? 7 : 4.5);
      dot.setAttribute("class", "gv-dot-" + (r.score || 1) + (isSel ? " gv-dot-sel" : ""));
      var title = document.createElementNS(NS, "title");
      title.textContent = r.ticker + " — " + (r.segment || "Unclassified") +
        ", Market cap " + fmtRs(r.market_cap) +
        ", Growth " + r.growth + ", Value " + r.value + " (score " + r.score + ")";
      dot.appendChild(title);
      svg.appendChild(dot);
      txt(cx + 6, cy - 5, r.ticker, "gv-dotlabel", "start");
    });
    return svg;
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
    // Morningstar is independent of the company search — load it on first open.
    if (name === "morningstar" && !state.modelLoaded && !state.modelLoading) loadModel();
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

  // --- boot -----------------------------------------------------------------

  if (cfg.symbol) {
    els.symbol.value = cfg.symbol;
    load(cfg.symbol);
  }
})();
