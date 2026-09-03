/* canslim.js — CAN SLIM screener table.
 *
 * Renders the ranked cross-section plus the market gate. Every number shown is
 * computed server-side; this file only formats. The factor scores are printed
 * NEXT TO the raw evidence that produced them (growth %, distance from high,
 * volume ratio, excess return) so a row can be audited without opening a drawer.
 */
(function () {
  "use strict";

  var CFG = window.CS_CONFIG || { scanUrl: "/canslim/api/scan/" };
  var state = { data: null, conf: "all" };

  function el(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function num(v, d) {
    if (v === null || v === undefined || isNaN(v)) return "—";
    return Number(v).toFixed(d === undefined ? 1 : d);
  }
  function pct(v, d) { return v == null || isNaN(v) ? "—" : (v > 0 ? "+" : "") + num(v, d) + "%"; }

  /* Factor cell: score out of 10, tinted by strength. */
  function fcell(score) {
    if (score === null || score === undefined) {
      return "<td class='cs-f cs-na' title='not measurable for this stock'>—</td>";
    }
    var cls = score >= 8 ? "cs-hi" : score >= 5 ? "cs-mid" : "cs-lo";
    return "<td class='cs-f " + cls + "'>" + num(score, score % 1 ? 1 : 0) + "</td>";
  }

  function drawGate(g) {
    var box = el("cs-gate");
    if (!box || !g || !g.stage) return;
    box.hidden = false;
    box.className = "cs-gate cs-gate-" + esc(g.stage);
    box.innerHTML =
      "<div class='cs-gate-head'><b>M · Market Direction: " + esc(g.stage.toUpperCase()) +
      "</b><span class='cs-gate-asof'>as of " + esc(g.as_of || "") + "</span></div>" +
      "<div class='cs-gate-note'>" + esc(g.note || "") + "</div>" +
      "<div class='cs-gate-nums'>NEPSE " + num(g.index, 2) +
      " · 50-session avg " + num(g.ma50, 2) +
      " · 150-session avg " + num(g.ma150, 2) + "</div>" +
      "<div class='cs-gate-why'>M is a gate on the whole screen, not a column: it is " +
      "the same for every stock, so it is shown once here instead of shifting all " +
      "scores by the same amount.</div>";
  }

  function drawKpis(d, rows) {
    var k = el("cs-kpis");
    if (!k) return;
    var full = rows.filter(function (r) { return r.confidence === "full"; }).length;
    var strong = rows.filter(function (r) { return r.score >= 60; }).length;
    function tile(label, value, hint) {
      return "<div class='dsx-kpi' title='" + esc(hint) + "'><span class='dsx-kpi-label'>" +
        esc(label) + "</span><span class='dsx-kpi-value'>" + esc(value) +
        "</span></div>";
    }
    k.innerHTML =
      tile("Scored", d.universe, "ordinary equities with at least 3 measurable factors") +
      tile("Showing", rows.length, "after the sector and data filters") +
      tile("Score 60+", strong, "stocks scoring 60 or better out of 100") +
      tile("Full data", full, "all 5 stock factors measurable");
  }

  function drawLimits(d) {
    var box = el("cs-limits");
    if (!box) return;
    var u = d.unavailable || {};
    box.innerHTML =
      "<div class='dsx-ev-flag'><span class='dsx-ev-pill warn'>Screen · not a forecast</span></div>" +
      "<div class='dsx-ev-plain'><b>Two of the seven factors are not fully measurable in NEPSE.</b> " +
      "<b>I</b> (Institutional Sponsorship) is unavailable — " + esc(u.I || "") +
      " <b>N</b> is partial — " + esc(u.N_partial || "") + "</div>" +
      "<div class='dsx-ev-plain'>" + esc(d.caveat || "") + "</div>";
  }

  var COLS = [
    ["#", "rank"], ["Ticker", "symbol"], ["Sector", "sector"], ["Score", "score"],
    ["C", "C"], ["A", "A"], ["N", "N"], ["S", "S"], ["L", "L"],
    ["Quarter YoY", "c_growth_pct"], ["Annual avg", "a_avg_pct"],
    ["Off high", "pct_below_high"], ["Volume", "volume_ratio"], ["vs Market", "excess_pct"]
  ];

  function drawTable(rows) {
    var t = el("cs-table");
    if (!t) return;
    if (!rows.length) {
      t.innerHTML = "<tbody><tr><td class='dsx-empty'>No stocks match this filter.</td></tr></tbody>";
      return;
    }
    var head = "<thead><tr>" + COLS.map(function (c) {
      return "<th>" + esc(c[0]) + "</th>";
    }).join("") + "</tr></thead>";

    var body = rows.map(function (r) {
      /* C is shown as its label when a percentage would be misleading — a
         loss-to-profit swing is a Recovery, not a growth rate. */
      var cTxt = r.c_growth_pct != null ? pct(r.c_growth_pct, 0)
        : r.c_status === "recovery" ? "<span class='cs-recovery'>Recovery</span>"
        : "<span class='cs-na'>N/A</span>";
      var aTxt = (r.A != null && r.a_avg_pct != null)
        ? pct(r.a_avg_pct, 0) + " <span class='cs-consist' title='years of positive growth'>(" +
          r.a_positive + "/" + r.a_measured + ")</span>"
        : r.a_measured != null && r.a_measured < 3
          ? "<span class='cs-na' title='fewer than 3 measured years — not scored'>thin history</span>"
          : "<span class='cs-na'>—</span>";
      var vol = r.volume_ratio != null
        ? "&times;" + num(r.volume_ratio, 2) +
          (r.rising_on_volume ? "" : " <span class='cs-flat' title='volume without a rising price'>flat</span>")
        : "—";
      var conf = r.confidence && r.confidence !== "full"
        ? " <span class='cs-conf' title='" + esc(r.measured) +
          " of 5 factors measurable'>" + esc(r.confidence) + "</span>" : "";
      var ca = r.corp_action
        ? " <span class='cs-ca' title='A bonus/rights ex-date sits inside the price " +
          "window. The return was spliced across the gap, so the price factors " +
          "(N, S, L) are approximate for this stock.'>±</span>"
        : "";
      return "<tr data-sym='" + esc(r.symbol) + "'>" +
        "<td class='cs-rank'>" + r.rank + "</td>" +
        "<td class='l tkr'>" + esc(r.symbol) + ca + conf + "</td>" +
        "<td class='l dsx-ad-sec'>" + esc(r.sector || "—") + "</td>" +
        "<td class='cs-score'>" + num(r.score, 1) + "</td>" +
        fcell(r.C) + fcell(r.A) + fcell(r.N) + fcell(r.S) + fcell(r.L) +
        "<td>" + cTxt + "</td><td>" + aTxt + "</td>" +
        "<td>" + (r.pct_below_high == null ? "—" : num(r.pct_below_high, 1) + "%") + "</td>" +
        "<td>" + vol + "</td>" +
        "<td>" + pct(r.excess_pct, 0) + "</td></tr>";
    }).join("");
    t.innerHTML = head + "<tbody>" + body + "</tbody>";
  }

  function apply() {
    var d = state.data;
    if (!d || !d.ok) return;
    var rows = d.rows || [];
    if (state.conf === "full") {
      rows = rows.filter(function (r) { return r.confidence === "full"; });
    }
    drawKpis(d, rows);
    drawTable(rows);
    var sub = el("cs-sub");
    if (sub) sub.textContent = rows.length + " of " + d.universe + " scored · as of " + (d.as_of || "");
    var uni = el("cs-universe");
    if (uni) uni.textContent = d.universe_note || "";
  }

  function fillSectors(rows) {
    var sel = el("cs-sector");
    if (!sel || sel.options.length) return;
    var counts = {};
    rows.forEach(function (r) {
      var s = r.sector || "—";
      counts[s] = (counts[s] || 0) + 1;
    });
    var opts = ["<option value='All'>All sectors (" + rows.length + ")</option>"];
    Object.keys(counts).sort().forEach(function (s) {
      opts.push("<option value='" + esc(s) + "'>" + esc(s) + " (" + counts[s] + ")</option>");
    });
    sel.innerHTML = opts.join("");
  }

  function load() {
    var t = el("cs-table");
    if (t) t.innerHTML = "<tbody><tr><td class='dsx-empty'>Scoring the market…</td></tr></tbody>";
    var sel = el("cs-sector");
    var q = sel && sel.value && sel.value !== "All"
      ? "?sector=" + encodeURIComponent(sel.value) : "";
    fetch(CFG.scanUrl + q, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d.ok) {
          if (t) t.innerHTML = "<tbody><tr><td class='dsx-empty'>" +
            esc(d.error || "No data") + "</td></tr></tbody>";
          return;
        }
        state.data = d;
        drawGate(d.market_gate);
        drawLimits(d);
        fillSectors(d.rows || []);
        apply();
      })
      .catch(function () {
        if (t) t.innerHTML = "<tbody><tr><td class='dsx-empty'>Could not load the screen.</td></tr></tbody>";
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var s = el("cs-sector"), c = el("cs-conf"), b = el("cs-refresh");
    if (s) s.addEventListener("change", load);
    if (c) c.addEventListener("change", function () { state.conf = c.value; apply(); });
    if (b) b.addEventListener("click", load);
    load();
  });
})();
