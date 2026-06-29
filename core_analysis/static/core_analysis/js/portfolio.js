/* ============================================================================
   Risk & Portfolio Desk — frontend controller.
   Fetches the per-user valuation/risk payload from /portfolio/api/data/ and
   renders the KPI strip, sector-exposure bars, concentration card and holdings
   table. Read-only; the import itself is a plain multipart form POST.
   ========================================================================== */
(function () {
  "use strict";
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
    renderCompliance(d.compliance);
    renderRisk(d.risk);
    renderFactors(d.factors);
    renderLiquidity(d.liquidity);
    renderSectors(d.sectors || []);
    renderConc(d);
    renderTable(d.rows || []);
    if (el("pf-asof")) el("pf-asof").textContent = d.as_of ? "Priced at " + d.as_of + " close" : "";
    renderNote(d);
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
    var beta = d.portfolio_beta;
    box.innerHTML =
      tile("Portfolio Value", rsCompact(d.total_value), d.holdings_count + " holdings") +
      tile("Largest Position", c.top_symbol ? c.top_symbol + " · " + pct(c.top_weight) : "—",
           "single-name weight") +
      tile("Diversification", (c.effective_holdings || 0).toFixed(1),
           "effective holdings (of " + d.holdings_count + ")") +
      tile("Concentration", nf(c.hhi || 0),
           "HHI · " + (c.risk || "low") + " concentration", "risk-" + (c.risk || "low")) +
      tile("Portfolio Beta", beta == null ? "—" : beta.toFixed(2),
           beta == null ? "insufficient history" :
           (beta > 1 ? "more volatile than NEPSE" : "less volatile than NEPSE"));
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

  function renderTable(rows) {
    var t = el("pf-table");
    if (!t) return;
    if (!rows.length) { t.innerHTML = "<tbody><tr><td class='pf-muted'>No holdings</td></tr></tbody>"; return; }
    var head = "<thead><tr><th>#</th><th class='l'>Scrip</th><th class='l'>Company</th>" +
      "<th class='l'>Sector</th><th>Qty</th><th>Price (Rs)</th><th>Value (Rs)</th>" +
      "<th>Weight</th><th title='Annualised volatility'>Volatility</th>" +
      "<th title='Beta vs NEPSE index'>Beta</th>" +
      "<th title='Days to liquidate at 20% of average daily volume'>Liquidity</th></tr></thead>";
    var body = rows.map(function (r, i) {
      var snap = r.price_source === "snapshot"
        ? " <span class='pf-snap' title='Not in EOD feed; priced from your CSV snapshot'>snapshot</span>" : "";
      var betaCls = r.beta == null ? "" : (r.beta > 1 ? "num-neg" : "num-pos");
      return "<tr><td>" + (i + 1) + "</td>" +
        "<td class='l pf-tkr'>" + esc(r.symbol) + "</td>" +
        "<td class='l pf-name'>" + esc(r.name) + "</td>" +
        "<td class='l'>" + esc(r.sector) + "</td>" +
        "<td>" + nf(r.quantity) + "</td>" +
        "<td>" + nf(r.price) + snap + "</td>" +
        "<td>" + rs(r.value) + "</td>" +
        "<td class='pf-wcell'><span class='pf-wbar' style='width:" + Math.min(100, r.weight) + "%'></span>" +
          "<span class='pf-wnum'>" + pct(r.weight) + "</span></td>" +
        "<td>" + (r.vol == null ? "—" : r.vol.toFixed(1) + "%") + "</td>" +
        "<td class='" + betaCls + "'>" + (r.beta == null ? "—" : r.beta.toFixed(2)) + "</td>" +
        "<td><span class='pf-liq-tier tier-" + esc(r.liq_tier) + "'>" + dtlText(r.dtl) + "</span></td></tr>";
    }).join("");
    t.innerHTML = head + "<tbody>" + body + "</tbody>";
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

  function renderRisk(risk) {
    var v = el("pf-var"), st = el("pf-stress");
    if (!risk || !risk.ok) {
      var msg = (risk && risk.reason) || "Risk metrics unavailable.";
      if (v) v.innerHTML = "<div class='pf-muted'>" + esc(msg) + "</div>";
      if (st) st.innerHTML = "<div class='pf-muted'>" + esc(msg) + "</div>";
      return;
    }
    var V = risk.var;
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
        return "<div class='pf-stress-row'>" +
          "<span class='pf-stress-label'>" + esc(s.label) + "</span>" +
          "<span class='pf-stress-bar'><i class='" + (neg ? "down" : "up") + "' style='width:" + w + "%'></i></span>" +
          "<span class='pf-stress-rs " + (neg ? "num-neg" : "num-pos") + "'>" + signedRs(s.impact_rs) + "</span>" +
          "<span class='pf-stress-pct " + (neg ? "num-neg" : "num-pos") + "'>" +
            (s.impact_pct > 0 ? "+" : "") + s.impact_pct.toFixed(1) + "%</span></div>";
      }).join("") + "</div>" +
      "<div class='pf-var-note'>Beta-propagated (β = " + risk.beta_used +
      "): a NEPSE move flows to the book via its beta. Worst observed session: " +
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

  function renderNote(d) {
    var box = el("pf-note");
    if (!box) return;
    var parts = [];
    if (d.snapshot_count) {
      parts.push(d.snapshot_count + " holding(s) aren't in the NEPSE EOD feed (newly listed / delisted / "
        + "renamed) and are priced from your uploaded snapshot.");
    }
    parts.push("Volatility &amp; beta are close-to-close estimates over ~100 sessions vs the NEPSE index; "
      + "thinly-traded scrips show “—”. Portfolio beta is the weight-weighted average of holding betas.");
    box.innerHTML = parts.join(" ");
  }
})();
