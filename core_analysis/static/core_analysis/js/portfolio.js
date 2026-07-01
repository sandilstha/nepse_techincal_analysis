/* ============================================================================
   Risk & Portfolio Desk — frontend controller.
   Fetches the per-user valuation/risk payload from /portfolio/api/data/ and
   renders the KPI strip, sector-exposure bars, concentration card and holdings
   table. Read-only; the import itself is a plain multipart form POST.
   ========================================================================== */
(function () {
  "use strict";
  bindFileInputs();
  if (!window.PF_HAS_HOLDINGS) return;

  function el(id) { return document.getElementById(id); }
  function nf(n) { return (n == null ? 0 : n).toLocaleString("en-IN"); }
  function rs(n) { return "Rs " + nf(Math.round(n || 0)); }
  function pct(n) { return (n == null ? 0 : n).toFixed(2) + "%"; }
  function rsCompact(n) {
    var v = Math.round(n || 0), s = v < 0 ? "-" : "", a = Math.abs(v);
    if (a >= 1e7) return s + "Rs " + (a / 1e7).toFixed(2) + " Cr";
    if (a >= 1e5) return s + "Rs " + (a / 1e5).toFixed(2) + " L";
    return rs(v);
  }
  function signedRs(n) {
    var v = Math.round(n || 0);
    return (v >= 0 ? "+" : "-") + "Rs " + nf(Math.abs(v));
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function bindFileInputs() {
    Array.prototype.forEach.call(document.querySelectorAll(".pf-file-input"), function (input) {
      var wrap = input.closest(".pf-upload");
      var name = wrap ? wrap.querySelector(".pf-file-name") : null;
      if (!name) return;
      function syncName() {
        var label = input.files && input.files.length
          ? input.files[0].name
          : (name.getAttribute("data-empty-label") || "No file selected");
        name.textContent = label;
        name.title = label;
      }
      input.addEventListener("change", syncName);
      syncName();
    });
  }

  fetch("/portfolio/api/data/", { headers: { Accept: "application/json" } })
    .then(function (r) { return r.json(); })
    .then(render)
    .catch(function () {
      var k = el("pf-kpis");
      if (k) k.innerHTML = "<div class='pf-error'>Could not load portfolio data.</div>";
    });

  function render(d) {
    if (!d || !d.ok) {
      var k = el("pf-kpis");
      if (k) k.innerHTML = "<div class='pf-error'>" + esc((d && d.error) || "No data") + "</div>";
      return;
    }
    renderKpis(d);
    renderSummaryDesk(d);
    renderCompliance(d.compliance);
    renderRisk(d.risk, d.nepse_index);
    renderFactors(d.factors);
    renderLiquidity(d.liquidity);
    renderSectors(d.sectors || []);
    renderConc(d);
    if (el("pf-asof")) el("pf-asof").textContent = d.as_of ? "Priced at " + d.as_of + " close" : "";
  }

  function tile(label, val, sub, cls) {
    return "<div class='pf-kpi'><span class='pf-kpi-label'>" + esc(label) + "</span>" +
      "<span class='pf-kpi-val " + (cls || "") + "'>" + val + "</span>" +
      "<span class='pf-kpi-sub'>" + esc(sub || "") + "</span></div>";
  }

  function renderKpis(d) {
    var box = el("pf-kpis");
    if (!box) return;
    var c = d.concentration || {};
    var cost = d.cost || {};
    var risk = d.risk || {};
    var var95 = risk.ok && risk.var ? risk.var : null;
    var beta = d.portfolio_beta;
    var na = "\u2014";
    var html = tile("Portfolio Value", rsCompact(d.total_value), d.holdings_count + " holdings");
    if (cost.has_cost) {
      html += tile("Paper P/L", signedRs(cost.paper_pl),
        (cost.paper_pl_pct == null ? na : (cost.paper_pl_pct >= 0 ? "+" : "") + cost.paper_pl_pct.toFixed(2) + "%") + " vs cost",
        cost.paper_pl >= 0 ? "num-pos" : "num-neg");
    } else {
      html += tile("Diversification", (c.effective_holdings || 0).toFixed(1),
        "effective holdings (of " + d.holdings_count + ")");
    }
    html += tile("1-Day VaR", var95 ? "-" + rsCompact(Math.abs(var95.hist_95_1d_rs)) : na,
      var95 ? Math.abs(var95.hist_95_1d_pct).toFixed(2) + "% historical 95%" : "insufficient history",
      var95 ? "num-neg" : "");
    html += tile("Largest Position", c.top_symbol ? c.top_symbol + " / " + pct(c.top_weight) : na,
      "single-name weight");
    html += tile("Concentration", nf(c.hhi || 0),
      (c.effective_holdings || 0).toFixed(1) + " effective / " + (c.risk || "low") + " risk",
      "risk-" + (c.risk || "low"));
    html += tile("Portfolio Beta", beta == null ? na : beta.toFixed(2),
      beta == null ? "insufficient history" :
      (beta > 1 ? "more volatile than NEPSE" : "less volatile than NEPSE"));
    box.innerHTML = html;
  }

  // ── Portfolio Summary — Beta Forecast & VaR ───────────────────────────
  // A sector-grouped desk driven by a "what if NEPSE moves to X" scenario.
  // The whole recompute is client-side (beta × index move) so Recalculate is
  // instant and never refetches. VaR/loss come pre-computed from the payload.
  var SUMMARY_DEFAULTS = { query: "", sector: "", liquidity: "", sort: "value", dir: "desc" };
  var state = {
    data: null,
    summary: {
      query: SUMMARY_DEFAULTS.query,
      sector: SUMMARY_DEFAULTS.sector,
      liquidity: SUMMARY_DEFAULTS.liquidity,
      sort: SUMMARY_DEFAULTS.sort,
      dir: SUMMARY_DEFAULTS.dir
    }
  };

  function snf(n) {                    // signed, thousands-grouped integer
    var v = Math.round(n || 0);
    return (v >= 0 ? "+" : "") + nf(v);
  }

  // Beta-forecast one holding for a given NEPSE % move.
  function computeExp(r, changePct) {
    if (r.beta == null || r.price == null) {
      return { expPrice: r.price, expValue: r.value, gain: 0 };
    }
    var expPrice = r.price * (1 + r.beta * changePct / 100);
    var expValue = (r.quantity || 0) * expPrice;
    return { expPrice: expPrice, expValue: expValue, gain: expValue - (r.value || 0) };
  }

  function resetSummaryFilters() {
    state.summary = {
      query: SUMMARY_DEFAULTS.query,
      sector: SUMMARY_DEFAULTS.sector,
      liquidity: SUMMARY_DEFAULTS.liquidity,
      sort: SUMMARY_DEFAULTS.sort,
      dir: SUMMARY_DEFAULTS.dir
    };
  }

  function bindSummaryFilters(rows) {
    syncSummarySectorOptions(rows || []);
    bindSummaryControl("pf-sum-query", "input", function (node) {
      state.summary.query = node.value || "";
      recalcSummary();
    });
    bindSummaryControl("pf-sum-sector-filter", "change", function (node) {
      state.summary.sector = node.value || "";
      recalcSummary();
    });
    bindSummaryControl("pf-sum-liq-filter", "change", function (node) {
      state.summary.liquidity = node.value || "";
      recalcSummary();
    });
    bindSummaryControl("pf-sum-sort", "change", function (node) {
      var next = node.value || SUMMARY_DEFAULTS.sort;
      if (state.summary.sort !== next) {
        state.summary.sort = next;
        state.summary.dir = next === "symbol" ? "asc" : "desc";
        syncSummaryFilterControls();
      }
      recalcSummary();
    });
    bindSummaryControl("pf-sum-dir", "click", function () {
      state.summary.dir = state.summary.dir === "asc" ? "desc" : "asc";
      syncSummaryFilterControls();
      recalcSummary();
    });
    bindSummaryControl("pf-sum-reset", "click", function () {
      resetSummaryFilters();
      syncSummaryFilterControls();
      recalcSummary();
    });
    syncSummaryFilterControls();
  }

  function bindSummaryControl(id, eventName, handler) {
    var node = el(id);
    if (!node || node._pfBound) return;
    node._pfBound = true;
    node.addEventListener(eventName, function () { handler(node); });
  }

  function syncSummarySectorOptions(rows) {
    var select = el("pf-sum-sector-filter");
    if (!select) return;
    var seen = {}, sectors = [];
    rows.forEach(function (r) {
      var sec = r.sector || "Other";
      if (!seen[sec]) { seen[sec] = true; sectors.push(sec); }
    });
    sectors.sort(function (a, b) { return a.localeCompare(b); });
    if (state.summary.sector && !seen[state.summary.sector]) state.summary.sector = "";
    select.innerHTML = "<option value=''>All sectors</option>" + sectors.map(function (sec) {
      return "<option value=\"" + esc(sec) + "\">" + esc(sec) + "</option>";
    }).join("");
  }

  function syncSummaryFilterControls() {
    var q = el("pf-sum-query");
    var sec = el("pf-sum-sector-filter");
    var liq = el("pf-sum-liq-filter");
    var sort = el("pf-sum-sort");
    var dir = el("pf-sum-dir");
    if (q) q.value = state.summary.query;
    if (sec) sec.value = state.summary.sector;
    if (liq) liq.value = state.summary.liquidity;
    if (sort) sort.value = state.summary.sort;
    if (dir) {
      dir.textContent = state.summary.dir === "asc" ? "Asc" : "Desc";
      dir.setAttribute("aria-pressed", state.summary.dir === "asc" ? "true" : "false");
    }
  }

  function summaryMetric(r, key, changePct) {
    var e = (key === "expPrice" || key === "expValue" || key === "gain") ? computeExp(r, changePct) : null;
    if (key === "symbol") return r.symbol || "";
    if (key === "quantity") return r.quantity;
    if (key === "wacc") return r.wacc;
    if (key === "price") return r.price;
    if (key === "value") return r.value;
    if (key === "weight") return r.weight;
    if (key === "vol") return r.vol;
    if (key === "beta") return r.beta;
    if (key === "dtl") return r.dtl;
    if (key === "expPrice") return e.expPrice;
    if (key === "expValue") return e.expValue;
    if (key === "gain") return e.gain;
    if (key === "var1w") return r.var_1w_pct == null ? null : Math.abs(r.var_1w_pct);
    if (key === "loss1w") return r.loss_1w == null ? null : Math.abs(r.loss_1w);
    if (key === "var1m") return r.var_1m_pct == null ? null : Math.abs(r.var_1m_pct);
    if (key === "loss1m") return r.loss_1m == null ? null : Math.abs(r.loss_1m);
    return r.value;
  }

  function filteredSummaryRows(rows, changePct) {
    var f = state.summary;
    var q = (f.query || "").toLowerCase().trim();
    var wrapped = rows.map(function (r, idx) { return { row: r, idx: idx }; }).filter(function (item) {
      var r = item.row;
      var hay = [r.symbol, r.company, r.sector].join(" ").toLowerCase();
      if (q && hay.indexOf(q) === -1) return false;
      if (f.sector && (r.sector || "Other") !== f.sector) return false;
      if (f.liquidity && (r.liq_tier || "untradeable") !== f.liquidity) return false;
      return true;
    });
    wrapped.sort(function (a, b) {
      var av = summaryMetric(a.row, f.sort, changePct);
      var bv = summaryMetric(b.row, f.sort, changePct);
      var an = av == null || av === "";
      var bn = bv == null || bv === "";
      var cmp;
      if (an && bn) return a.idx - b.idx;
      if (an) return 1;
      if (bn) return -1;
      if (typeof av === "string" || typeof bv === "string") cmp = String(av).localeCompare(String(bv));
      else cmp = av - bv;
      if (cmp === 0) cmp = a.idx - b.idx;
      return f.dir === "asc" ? cmp : -cmp;
    });
    return wrapped.map(function (item) { return item.row; });
  }

  function updateSummaryCount(count, total) {
    var c = el("pf-sum-count");
    if (c) c.textContent = count + " of " + total + " holdings";
  }

  function renderSummaryDesk(d) {
    state.data = d;
    bindSummaryFilters(d.rows || []);
    var idx = (d.nepse_index || {}).value;
    var cur = el("pf-idx-current"), exp = el("pf-idx-expected");
    if (cur) cur.value = idx == null ? "—" : nf(idx);
    if (exp && !exp.value) exp.value = idx == null ? "" : idx;
    var rc = el("pf-recalc");
    if (rc && !rc._bound) { rc._bound = true; rc.addEventListener("click", recalcSummary); }
    if (exp && !exp._bound) {
      exp._bound = true;
      exp.addEventListener("input", recalcSummary);
      exp.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); recalcSummary(); }
      });
    }
    recalcSummary();
  }

  function recalcSummary() {
    var d = state.data;
    if (!d) return;
    var rows = d.rows || [];
    var idx = (d.nepse_index || {}).value;
    var expEl = el("pf-idx-expected");
    var expected = expEl ? parseFloat(expEl.value) : idx;
    if (isNaN(expected)) expected = idx;
    var changePct = (idx && idx > 0) ? (expected - idx) / idx * 100 : 0;

    var chEl = el("pf-idx-change");
    if (chEl) {
      chEl.textContent = (changePct >= 0 ? "+" : "") + changePct.toFixed(2) + "%";
      chEl.className = "pf-idx-change " + (changePct >= 0 ? "num-pos" : "num-neg");
    }

    var totVal = 0, totExp = 0, totL1w = 0, totL1m = 0, costedExp = 0;
    rows.forEach(function (r) {
      var e = computeExp(r, changePct);
      totVal += r.value || 0;
      totExp += e.expValue || 0;
      totL1w += r.loss_1w || 0;
      totL1m += r.loss_1m || 0;
      if (r.cost_value != null) costedExp += e.expValue || 0;   // costed subset, for Exp. Paper P/L
    });

    var cost = d.cost || {};
    var nHold = d.holdings_count || rows.length;
    var tiles = el("pf-sum-tiles");
    if (tiles) {
      var html = "";
      if (cost.has_cost) {
        html += tile("Book Value", rsCompact(cost.book_value), cost.covered_count + " of " + nHold + " costed");
      }
      html += tile("Market Value", rsCompact(totVal), nHold + " holdings");
      if (cost.has_cost) {
        html += tile("Paper P/L", signedRs(cost.paper_pl),
          (cost.paper_pl_pct == null ? "—" : (cost.paper_pl_pct >= 0 ? "+" : "") + cost.paper_pl_pct.toFixed(2) + "%") + " vs cost",
          cost.paper_pl >= 0 ? "num-pos" : "num-neg");
      }
      html += tile("Expected Value", rsCompact(totExp),
        (changePct >= 0 ? "+" : "") + changePct.toFixed(2) + "% NEPSE scenario");
      if (cost.has_cost) {
        html += tile("Exp. Paper P/L", signedRs(costedExp - cost.book_value), "at scenario",
          (costedExp - cost.book_value) >= 0 ? "num-pos" : "num-neg");
      }
      html += tile("Scenario P/L", signedRs(totExp - totVal), "vs current value",
        (totExp - totVal) >= 0 ? "num-pos" : "num-neg");
      // Prefer the diversified portfolio VaR (Z·σ_p·√h, correlation-aware) from the
      // Risk block; fall back to the undiversified sum of per-holding VaRs on thin
      // history where the portfolio return series is too short for a portfolio VaR.
      var pvar = (d.risk && d.risk.ok && d.risk.var) ? d.risk.var : null;
      var l1w = pvar ? -pvar.param_95_1w_rs : totL1w;
      var l1m = pvar ? -pvar.param_95_1m_rs : totL1m;
      var vsub = pvar ? "diversified VaR" : "undiversified VaR";
      html += tile("Loss @ 1W · 95%", rsCompact(l1w), vsub, "num-neg");
      html += tile("Loss @ 1M · 95%", rsCompact(l1m), vsub, "num-neg");
      tiles.innerHTML = html;
    }

    var tableRows = filteredSummaryRows(rows, changePct);
    updateSummaryCount(tableRows.length, rows.length);
    renderSummaryTable(tableRows, changePct);

    var note = el("pf-sum-note");
    if (note) {
      var base = "Expected price = LTP × (1 + β × NEPSE change%); Gain/Loss is the scenario move vs current value. " +
        "Per-holding VaR is parametric (95%, √-time) on each holding's annualised volatility — 1W ≈ 5 sessions, 1M ≈ 20. " +
        "The Loss tiles show the DIVERSIFIED portfolio VaR (Z·σₚ·√h on the portfolio's own return series, so correlation lowers it below the sum of the columns); " +
        "on thin history they fall back to the undiversified column sum. " +
        "Weight, volatility, beta and liquidity are pulled from the same holdings payload. " +
        "Thinly-traded scrips with no beta/volatility show “—”.";
      if (d.snapshot_count) {
        base += " " + d.snapshot_count + " holding(s) are priced from your uploaded snapshot because they are not in the NEPSE EOD feed.";
      }
      var costNote = (cost.has_cost)
        ? " WACC · Book Value · Paper P/L are from your imported “My WACC” report (" + cost.covered_count + " scrips matched)."
        : " Import your broker “My WACC” report (button top-right) to add WACC, Book Value & Paper P/L.";
      note.innerHTML = base + costNote;
    }
  }

  function summaryColgroup() {
    return "<colgroup>" +
      "<col class='pf-col-rank'><col class='pf-col-symbol'>" +
      "<col class='pf-col-kitta'><col class='pf-col-wacc'><col class='pf-col-ltp'><col class='pf-col-value'><col class='pf-col-weight'>" +
      "<col class='pf-col-vol'><col class='pf-col-beta'><col class='pf-col-liq'>" +
      "<col class='pf-col-exp-price'><col class='pf-col-exp-value'><col class='pf-col-gain'>" +
      "<col class='pf-col-var'><col class='pf-col-loss'><col class='pf-col-var'><col class='pf-col-loss'>" +
      "</colgroup>";
  }

  function summarySortHeader(label, key, title) {
    var active = state.summary.sort === key;
    var mark = active ? (state.summary.dir === "asc" ? "^" : "v") : "";
    return "<button type='button' class='pf-sort-head" + (active ? " active" : "") + "' " +
      "data-summary-sort='" + esc(key) + "' title='" + esc(title || ("Sort by " + label)) + "'>" +
      "<span>" + esc(label) + "</span><span class='pf-sort-mark'>" + mark + "</span></button>";
  }

  function setSummarySort(key) {
    if (state.summary.sort === key) {
      state.summary.dir = state.summary.dir === "asc" ? "desc" : "asc";
    } else {
      state.summary.sort = key;
      state.summary.dir = key === "symbol" ? "asc" : "desc";
    }
    syncSummaryFilterControls();
    recalcSummary();
  }

  function bindSummaryHeaderSort(table) {
    Array.prototype.forEach.call(table.querySelectorAll("[data-summary-sort]"), function (btn) {
      btn.addEventListener("click", function () {
        setSummarySort(btn.getAttribute("data-summary-sort"));
      });
    });
  }

  function renderSummaryTable(rows, changePct) {
    var t = el("pf-sum-table");
    if (!t) return;
    var colgroup = summaryColgroup();
    var head = "<thead>" +
      "<tr class='pf-sum-grp'><th rowspan='2'>#</th><th rowspan='2' class='l'>" + summarySortHeader("Symbol", "symbol") + "</th>" +
        "<th colspan='5'>Portfolio Status</th>" +
        "<th colspan='3'>Risk &amp; Liquidity</th>" +
        "<th colspan='3'>Sensitivity (Beta Forecast)</th>" +
        "<th colspan='4'>Max Loss Potential (VaR)</th></tr>" +
      "<tr><th>" + summarySortHeader("Kitta", "quantity") + "</th>" +
        "<th>" + summarySortHeader("WACC", "wacc", "Sort by weighted average cost") + "</th>" +
        "<th>" + summarySortHeader("LTP", "price") + "</th>" +
        "<th>" + summarySortHeader("Value", "value") + "</th>" +
        "<th>" + summarySortHeader("Weight", "weight") + "</th>" +
        "<th>" + summarySortHeader("Vol", "vol", "Sort by annualised volatility") + "</th>" +
        "<th>" + summarySortHeader("Beta", "beta", "Sort by beta vs NEPSE index") + "</th>" +
        "<th>" + summarySortHeader("Liq.", "dtl", "Sort by days to liquidate") + "</th>" +
        "<th>" + summarySortHeader("Exp Px", "expPrice", "Sort by expected price") + "</th>" +
        "<th>" + summarySortHeader("Exp Val", "expValue", "Sort by expected value") + "</th>" +
        "<th>" + summarySortHeader("G/L", "gain", "Sort by gain or loss") + "</th>" +
        "<th>" + summarySortHeader("VaR 1W", "var1w") + "</th>" +
        "<th>" + summarySortHeader("Loss 1W", "loss1w") + "</th>" +
        "<th>" + summarySortHeader("VaR 1M", "var1m") + "</th>" +
        "<th>" + summarySortHeader("Loss 1M", "loss1m") + "</th></tr></thead>";

    if (!rows.length) {
      t.innerHTML = colgroup + head + "<tbody><tr><td colspan='17' class='pf-muted'>No matching holdings</td></tr></tbody>";
      bindSummaryHeaderSort(t);
      return;
    }

    // Group by sector, preserving the payload's value-descending order.
    var groups = {}, order = [];
    var totalValue = (state.data && state.data.total_value) || rows.reduce(function (sum, r) { return sum + (r.value || 0); }, 0);
    rows.forEach(function (r) {
      var s = r.sector || "Other";
      if (!groups[s]) { groups[s] = []; order.push(s); }
      groups[s].push(r);
    });

    var body = "", sn = 0;
    order.forEach(function (sec) {
      var grp = groups[sec];
      var gVal = 0, gExp = 0, gWeight = 0, gL1w = 0, gL1m = 0;
      var rowsHtml = grp.map(function (r) {
        sn++;
        var e = computeExp(r, changePct);
        gVal += r.value || 0; gExp += e.expValue || 0;
        gWeight += r.weight != null ? r.weight : (totalValue ? (100 * (r.value || 0) / totalValue) : 0);
        gL1w += r.loss_1w || 0; gL1m += r.loss_1m || 0;
        var snap = r.price_source === "snapshot"
          ? " <span class='pf-snap' title='Priced from your CSV snapshot'>snap</span>" : "";
        var betaCls = r.beta == null ? "" : (r.beta > 1 ? "num-neg" : "num-pos");
        var tier = r.liq_tier || "untradeable";
        return "<tr>" +
          "<td>" + sn + "</td>" +
          "<td class='l pf-tkr'>" + esc(r.symbol) + "</td>" +
          "<td>" + nf(r.quantity) + "</td>" +
          "<td>" + (r.wacc == null ? "—" : nf(r.wacc)) + "</td>" +
          "<td>" + nf(r.price) + snap + "</td>" +
          "<td>" + nf(Math.round(r.value)) + "</td>" +
          "<td class='pf-wcell'><span class='pf-wbar' style='width:" + Math.min(100, r.weight || 0) + "%'></span>" +
            "<span class='pf-wnum'>" + pct(r.weight) + "</span></td>" +
          "<td>" + (r.vol == null ? "—" : r.vol.toFixed(1) + "%") + "</td>" +
          "<td class='" + betaCls + "'>" + (r.beta == null ? "—" : r.beta.toFixed(2)) + "</td>" +
          "<td><span class='pf-liq-tier tier-" + esc(tier) + "'>" + dtlText(r.dtl) + "</span></td>" +
          "<td>" + (e.expPrice == null ? "—" : nf(Math.round(e.expPrice * 100) / 100)) + "</td>" +
          "<td>" + nf(Math.round(e.expValue)) + "</td>" +
          "<td class='" + (e.gain >= 0 ? "num-pos" : "num-neg") + "'>" + snf(e.gain) + "</td>" +
          "<td class='num-neg'>" + (r.var_1w_pct == null ? "—" : r.var_1w_pct.toFixed(2) + "%") + "</td>" +
          "<td class='num-neg'>" + (r.loss_1w == null ? "—" : nf(Math.round(r.loss_1w))) + "</td>" +
          "<td class='num-neg'>" + (r.var_1m_pct == null ? "—" : r.var_1m_pct.toFixed(2) + "%") + "</td>" +
          "<td class='num-neg'>" + (r.loss_1m == null ? "—" : nf(Math.round(r.loss_1m))) + "</td>" +
          "</tr>";
      }).join("");
      var gGain = gExp - gVal;
      body += "<tr class='pf-sum-sector'>" +
        "<td></td><td class='l'>" + esc(sec) + "</td>" +
        "<td></td><td></td><td></td><td>" + nf(Math.round(gVal)) + "</td><td>" + pct(gWeight) + "</td>" +
        "<td></td><td></td><td></td>" +
        "<td></td><td>" + nf(Math.round(gExp)) + "</td>" +
        "<td class='" + (gGain >= 0 ? "num-pos" : "num-neg") + "'>" + snf(gGain) + "</td>" +
        "<td></td><td class='num-neg'>" + nf(Math.round(gL1w)) + "</td>" +
        "<td></td><td class='num-neg'>" + nf(Math.round(gL1m)) + "</td></tr>" +
        rowsHtml;
    });
    t.innerHTML = colgroup + head + "<tbody>" + body + "</tbody>";
    bindSummaryHeaderSort(t);
  }

  function renderSectors(sectors) {
    var box = el("pf-sectors");
    if (!box) return;
    if (!sectors.length) { box.innerHTML = "<div class='pf-muted'>No sector data</div>"; return; }
    var max = sectors.reduce(function (m, s) { return Math.max(m, s.weight || 0); }, 0) || 1;
    box.innerHTML = sectors.map(function (s) {
      var w = (100 * (s.weight || 0) / max).toFixed(1);
      return "<div class='pf-sec-row'>" +
        "<span class='pf-sec-name' title='" + esc(s.sector) + "'>" + esc(s.sector) + "</span>" +
        "<span class='pf-sec-bar'><i style='width:" + w + "%'></i></span>" +
        "<span class='pf-sec-pct'>" + pct(s.weight) + "</span>" +
        "<span class='pf-sec-val'>" + rsCompact(s.value) + "</span></div>";
    }).join("");
  }

  function renderConc(d) {
    var box = el("pf-conc");
    if (!box) return;
    var c = d.concentration || {};
    var rows = (d.rows || []).slice(0, 5);
    var bandText = { low: "Well diversified", moderate: "Moderately concentrated", high: "Highly concentrated" };
    var top = "<div class='pf-conc-top'>" + rows.map(function (r) {
      return "<div class='pf-conc-row'><span class='pf-tkr'>" + esc(r.symbol) + "</span>" +
        "<span class='pf-conc-bar'><i style='width:" + Math.min(100, r.weight) + "%'></i></span>" +
        "<span class='pf-conc-w'>" + pct(r.weight) + "</span></div>";
    }).join("") + "</div>";
    box.innerHTML =
      "<div class='pf-conc-summary'>" +
        "<div><span class='pf-conc-num risk-" + (c.risk || "low") + "'>" + nf(c.hhi || 0) + "</span>" +
        "<span class='pf-conc-cap'>HHI — " + esc(bandText[c.risk] || "—") + "</span></div>" +
        "<div><span class='pf-conc-num'>" + (c.effective_holdings || 0).toFixed(1) + "</span>" +
        "<span class='pf-conc-cap'>effective holdings</span></div>" +
      "</div>" +
      "<div class='pf-conc-label'>Top 5 positions</div>" + top;
  }

  function renderCompliance(c) {
    var box = el("pf-compliance"), sum = el("pf-compliance-summary");
    if (!box) return;
    if (!c || !c.checks || !c.checks.length) {
      box.innerHTML = "<div class='pf-muted'>No limits evaluated.</div>";
      if (sum) sum.innerHTML = "";
      return;
    }
    var s = c.summary || {};
    if (sum) sum.innerHTML =
      (s.breach ? "<span class='pf-cpill breach'>" + s.breach + " breach</span>" : "") +
      (s.warn ? "<span class='pf-cpill warn'>" + s.warn + " watch</span>" : "") +
      "<span class='pf-cpill ok'>" + (s.ok || 0) + " ok</span>";
    var lbl = { ok: "OK", warn: "WATCH", breach: "BREACH" };
    box.innerHTML = c.checks.map(function (ch) {
      return "<div class='pf-chk pf-chk-" + ch.status + "'>" +
        "<span class='pf-chk-status " + ch.status + "'>" + (lbl[ch.status] || ch.status) + "</span>" +
        "<span class='pf-chk-label'>" + esc(ch.label) +
          (ch.detail ? "<span class='pf-chk-detail'>" + esc(ch.detail) + "</span>" : "") + "</span>" +
        "<span class='pf-chk-cur'>" + esc(ch.current) + "</span>" +
        "<span class='pf-chk-lim'>" + esc(ch.limit) + "</span></div>";
    }).join("");
  }

  function stat(label, val, sub) {
    return "<div class='pf-stat'><span class='pf-stat-label'>" + esc(label) + "</span>" +
      "<span class='pf-stat-val'>" + val + "</span>" +
      (sub ? "<span class='pf-stat-sub'>" + esc(sub) + "</span>" : "") + "</div>";
  }

  function renderRisk(risk, indexInfo) {
    var v = el("pf-var"), st = el("pf-stress");
    if (!risk || !risk.ok) {
      var msg = (risk && risk.reason) || "Risk metrics unavailable.";
      if (v) v.innerHTML = "<div class='pf-muted'>" + esc(msg) + "</div>";
      if (st) st.innerHTML = "<div class='pf-muted'>" + esc(msg) + "</div>";
      return;
    }
    var V = risk.var;
    var idxVal = indexInfo && indexInfo.value;
    function indexPointText(shock) {
      if (idxVal == null || shock == null) return "";
      var pts = idxVal * shock / 100;
      return (pts >= 0 ? "+" : "") + nf(Math.round(pts)) + " pts";
    }
    function lossRow(label, rsv, pctv, big) {
      return "<div class='pf-var-row" + (big ? " big" : "") + "'>" +
        "<span class='pf-var-label'>" + esc(label) + "</span>" +
        "<span class='pf-var-val num-neg'>-" + rs(Math.abs(rsv)) + "</span>" +
        "<span class='pf-var-pct num-neg'>-" + Math.abs(pctv).toFixed(2) + "%</span></div>";
    }
    if (v) v.innerHTML =
      lossRow("1-day VaR · 95%", V.hist_95_1d_rs, V.hist_95_1d_pct, true) +
      lossRow("1-day VaR · 99%", V.hist_99_1d_rs, V.hist_99_1d_pct) +
      lossRow("10-day VaR · 95%", V.hist_95_10d_rs, V.hist_95_10d_pct) +
      lossRow("Expected shortfall · CVaR 95%", V.cvar_95_1d_rs, V.cvar_95_1d_pct) +
      "<div class='pf-stat-grid'>" +
        stat("Ann. volatility", risk.ann_vol_pct == null ? "—" : risk.ann_vol_pct.toFixed(1) + "%") +
        stat("Worst session", risk.worst_day ? risk.worst_day.pct.toFixed(2) + "%" : "—",
             risk.worst_day ? risk.worst_day.date : "") +
        stat("Max drawdown", risk.max_drawdown_pct.toFixed(2) + "%") +
        stat("Worst 5-session", risk.worst_5d_pct == null ? "—" : risk.worst_5d_pct.toFixed(2) + "%") +
      "</div>" +
      "<div class='pf-var-note'>Historical simulation over " + risk.sessions +
      " sessions. Parametric 95% (normal) ≈ -" + rs(Math.abs(V.param_95_1d_rs)) +
      " — shown only for comparison; NEPSE returns are fat-tailed &amp; circuit-bounded, " +
      "so the historical figure governs.</div>";

    if (st) {
      var maxAbs = risk.scenarios.reduce(function (m, s) {
        return Math.max(m, Math.abs(s.impact_pct || 0)); }, 0) || 1;
      st.innerHTML = "<div class='pf-stress-list'>" + risk.scenarios.map(function (s) {
        var neg = s.impact_rs < 0;
        var w = (100 * Math.abs(s.impact_pct) / maxAbs).toFixed(1);
        var idxPts = indexPointText(s.shock);
        return "<div class='pf-stress-row'>" +
          "<span class='pf-stress-label'><span>" + esc(s.label) + "</span>" +
            (idxPts ? "<small>" + esc(idxPts) + "</small>" : "") + "</span>" +
          "<span class='pf-stress-bar'><i class='" + (neg ? "down" : "up") + "' style='width:" + w + "%'></i></span>" +
          "<span class='pf-stress-rs " + (neg ? "num-neg" : "num-pos") + "'>" + signedRs(s.impact_rs) + "</span>" +
          "<span class='pf-stress-pct " + (neg ? "num-neg" : "num-pos") + "'>" +
            (s.impact_pct > 0 ? "+" : "") + s.impact_pct.toFixed(1) + "%</span></div>";
      }).join("") + "</div>" +
      "<div class='pf-var-note'>Beta-propagated (β = " + risk.beta_used +
      "): NEPSE shocks show % and index-point move from " +
      (idxVal == null ? "the current index" : nf(Math.round(idxVal)) + " pts") +
      ". Book impact flows via beta. Worst observed session: " +
      (risk.worst_day ? risk.worst_day.pct.toFixed(2) + "% on " + risk.worst_day.date : "—") + ".</div>";
    }
  }

  function renderFactors(f) {
    var box = el("pf-factors");
    if (!box) return;
    if (!f || !f.ok) {
      box.innerHTML = "<div class='pf-muted'>" + esc((f && f.reason) || "Risk decomposition unavailable.") + "</div>";
      return;
    }
    var sys = f.systematic_pct, idio = f.idiosyncratic_pct;
    var split = "<div class='pf-split'><div class='pf-split-bar'>" +
      "<i class='sys' style='width:" + sys + "%'></i><i class='idio' style='width:" + idio + "%'></i></div>" +
      "<div class='pf-split-legend'>" +
        "<span><i class='sys'></i>Market " + sys.toFixed(1) + "%</span>" +
        "<span><i class='idio'></i>Stock-specific " + idio.toFixed(1) + "%</span></div></div>";
    var stats = "<div class='pf-stat-grid pf-stat-3'>" +
      stat("Total volatility", f.total_vol_pct.toFixed(1) + "%", "annualised") +
      stat("Market (systematic)", f.systematic_vol_pct.toFixed(1) + "%", "β = " + f.beta) +
      stat("Stock-specific", f.idiosyncratic_vol_pct.toFixed(1) + "%", "diversifiable") +
      "</div>";
    var secs = f.sectors || [];
    var max = (secs[0] && secs[0].pct) || 1;
    var sectors = "<div class='pf-liq-label'>Risk contribution by sector</div>" +
      secs.map(function (s) {
        var w = (100 * s.pct / max).toFixed(1);
        return "<div class='pf-fac-srow'><span class='pf-sec-name' title='" + esc(s.sector) + "'>" + esc(s.sector) + "</span>" +
          "<span class='pf-sec-bar'><i style='width:" + w + "%'></i></span>" +
          "<span class='pf-sec-pct'>" + s.pct.toFixed(1) + "%</span></div>";
      }).join("");
    var contrib = "<div class='pf-liq-label'>Top risk contributors</div><div class='pf-fac-chips'>" +
      (f.top_contributors || []).map(function (c) {
        return "<span class='pf-fac-chip'><b>" + esc(c.symbol) + "</b> " + c.pct.toFixed(1) + "%</span>";
      }).join("") + "</div>";
    box.innerHTML = split + stats + sectors + contrib +
      "<div class='pf-var-note'>Single-factor (NEPSE) model. <b>Market</b> risk moves with the index and can't be " +
      "diversified away; <b>stock-specific</b> risk can be cut by diversifying. Covers " +
      f.covered_weight_pct.toFixed(0) + "% of book value (names with price history).</div>";
  }

  function dtlText(dtl) {
    if (dtl == null) return "untradeable";
    if (dtl > 30) return ">30d";
    if (dtl < 0.1) return "<0.1d";
    return dtl.toFixed(1) + "d";
  }

  function renderLiquidity(L) {
    var box = el("pf-liq");
    if (!box) return;
    if (!L || !L.ok) { box.innerHTML = "<div class='pf-muted'>Liquidity data unavailable.</div>"; return; }
    var illiq = L.illiquid_count + (L.untradeable_count ? " (" + L.untradeable_count + " untradeable)" : "");
    var kpis = "<div class='pf-stat-grid pf-liq-kpis'>" +
      stat("Sellable in 1 day", (L.liquidatable_1d_pct || 0).toFixed(1) + "%", "of book value") +
      stat("Sellable in 5 days", (L.liquidatable_5d_pct || 0).toFixed(1) + "%", "of book value") +
      stat("Avg days to exit", L.wavg_days == null ? "—" : L.wavg_days.toFixed(1), "value-weighted") +
      stat("Illiquid positions", illiq, "> 5 days to exit") +
      "</div>";
    var list = "<div class='pf-liq-label'>Least liquid holdings</div><div class='pf-liq-list'>" +
      (L.least_liquid || []).map(function (r) {
        return "<div class='pf-liq-row'><span class='pf-tkr'>" + esc(r.symbol) + "</span>" +
          "<span class='pf-liq-tier tier-" + esc(r.tier) + "'>" + esc(r.tier) + "</span>" +
          "<span class='pf-liq-adv'>ADV " + nf(r.adv_qty) + "</span>" +
          "<span class='pf-liq-dtl'>" + dtlText(r.dtl) + "</span></div>";
      }).join("") + "</div>";
    box.innerHTML = kpis + list +
      "<div class='pf-var-note'>Days-to-liquidate = position ÷ (" + L.participation_pct + "% of the " +
      L.lookback_sessions + "-session average daily volume). Assumes you can trade ~" + L.participation_pct +
      "% of ADV per session without moving the price — thin NEPSE names exit slowly.</div>";
  }

})();
