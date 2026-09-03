/* morningstar.js — Morning Star tab on the Fundamental Analysis desk.
 *
 * Renders the sector scan from /fundamentals/morningstar/ (services/
 * morningstar.py): star ratings, Growth/Value percentiles, style box, size
 * tier, confidence tag, and quality gates/flags. Clicking a row expands the
 * per-factor breakdown (raw value + within-sector percentile + weight) so
 * every score is auditable against the methodology.
 *
 * Namespaced ms-* / MS_CONFIG — must never collide with fundamentals-desk.js
 * (ia-*) or canslim.js (cs-*) which share this page.
 */
(function () {
  "use strict";

  var CFG = window.MS_CONFIG || { scanUrl: "/fundamentals/morningstar/" };
  var state = { loaded: false, data: null };

  function el(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function stars(n) {
    if (n == null) return "<span class='ms-dim'>—</span>";
    var out = "";
    for (var i = 1; i <= 5; i++) {
      out += "<span class='" + (i <= n ? "ms-star on" : "ms-star") + "'>★</span>";
    }
    return "<span class='ms-stars' title='" + n + " of 5'>" + out + "</span>";
  }

  function pct(v) {
    if (v == null) return "<span class='ms-dim'>—</span>";
    var cls = v >= 60 ? "num-pos" : v < 40 ? "num-neg" : "";
    return "<span class='" + cls + "'>" + v.toFixed(1) + "</span>";
  }

  function styleChip(s) {
    if (!s || s === "—") return "<span class='ms-dim'>—</span>";
    return "<span class='ms-chip ms-style-" + s.toLowerCase() + "'>" + esc(s) + "</span>";
  }

  function fmtRaw(v) {
    if (v == null) return "—";
    if (typeof v !== "number") return esc(v);
    if (Math.abs(v) >= 1e9) return (v / 1e9).toFixed(2) + "B";
    if (Math.abs(v) >= 1e6) return (v / 1e6).toFixed(2) + "M";
    if (Math.abs(v) < 1 && v !== 0) return (v * 100).toFixed(2) + "%";
    return v.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }

  function factorRows(dd) {
    var html = "";
    ["growth", "value"].forEach(function (pillar) {
      var d = dd[pillar];
      if (!d) return;
      html += "<div class='ms-detail-block'><div class='ms-detail-head'>" +
        (pillar === "growth" ? "Growth factors" : "Value factors") +
        " <span class='ms-dim'>(" + d.present + " of " + d.total + " present)</span></div>";
      html += "<table class='ms-detail-table'><thead><tr><th>Factor</th><th>Weight</th><th>Raw</th><th>Sector percentile</th></tr></thead><tbody>";
      (d.factors || []).forEach(function (f) {
        html += "<tr><td>" + esc(f.label) + "</td><td>" + f.weight + "%</td><td>" +
          fmtRaw(f.raw) + "</td><td>" + (f.pct == null ? "<span class='ms-dim'>missing — weight redistributed</span>" : f.pct.toFixed(1)) + "</td></tr>";
      });
      html += "</tbody></table></div>";
    });
    return html;
  }

  function draw(data) {
    state.data = data;
    var sub = el("ms-sub");
    if (sub) {
      sub.textContent = data.period + " · Growth " + (data.mix ? data.mix.growth : 60) +
        "% / Value " + (data.mix ? data.mix.value : 40) + "% · ranked within sector";
    }
    var note = el("ms-note");
    if (note) {
      note.textContent = data.note ||
        "Percentile rank within sector; YTD vs prior-year YTD; missing factors redistribute their weight " +
        "(see confidence). Quality gates cap stars at 2; each soft flag costs 5 combined points.";
    }

    // KPI strip
    var rows = data.results || [];
    var k = el("ms-kpis");
    if (k) {
      var five = rows.filter(function (r) { return r.stars === 5; }).length;
      var four = rows.filter(function (r) { return r.stars === 4; }).length;
      var gated = rows.filter(function (r) { return (r.gates || []).length; }).length;
      var growthN = rows.filter(function (r) { return r.style === "Growth"; }).length;
      var valueN = rows.filter(function (r) { return r.style === "Value"; }).length;
      k.innerHTML =
        "<div class='dsx-kpi'><span>" + rows.length + "</span>Companies scored</div>" +
        "<div class='dsx-kpi'><span>" + five + " / " + four + "</span>5★ / 4★</div>" +
        "<div class='dsx-kpi'><span>" + growthN + " / " + valueN + "</span>Growth / Value style</div>" +
        "<div class='dsx-kpi'><span>" + gated + "</span>Quality-gated (capped 2★)</div>";
    }

    var t = el("ms-table");
    if (!t) return;
    var html = "<thead><tr><th>Company</th><th>Rating</th><th>Combined</th><th>Growth</th>" +
      "<th>Value</th><th>Style</th><th>Size</th><th>Confidence</th><th>Quality</th></tr></thead><tbody>";
    rows.forEach(function (r, i) {
      var quality = "";
      (r.gates || []).forEach(function (g) {
        quality += "<span class='ms-chip ms-gate' title='Hard gate — stars capped at 2'>" + esc(g) + "</span>";
      });
      (r.flags || []).forEach(function (f) {
        quality += "<span class='ms-chip ms-flag' title='Soft flag — −5 combined points'>" + esc(f) + "</span>";
      });
      if (!quality) quality = "<span class='ms-dim'>clean</span>";
      html += "<tr class='ms-row' data-i='" + i + "' title='Click for the factor breakdown'>" +
        "<td><span class='ms-ticker'>" + esc(r.ticker) + "</span>" +
        (r.name ? "<span class='ms-name'>" + esc(r.name) + "</span>" : "") + "</td>" +
        "<td>" + stars(r.stars) + "</td>" +
        "<td>" + pct(r.combined) + "</td>" +
        "<td>" + pct(r.growth) + "</td>" +
        "<td>" + pct(r.value) + "</td>" +
        "<td>" + styleChip(r.style) + "</td>" +
        "<td>" + esc(r.size || "—") + "</td>" +
        "<td class='" + (r.low_confidence ? "ms-lowconf" : "") + "'>" + esc(r.confidence || "") + "</td>" +
        "<td class='ms-quality'>" + quality + "</td></tr>" +
        "<tr class='ms-detail' data-for='" + i + "' hidden><td colspan='9'>" + factorRows(r.detail || {}) + "</td></tr>";
    });
    if (!rows.length) {
      html += "<tr><td colspan='9' class='dsx-empty'>No companies could be scored for this sector.</td></tr>";
    }
    html += "</tbody>";
    t.innerHTML = html;

    t.querySelectorAll(".ms-row").forEach(function (row) {
      row.addEventListener("click", function () {
        var d = t.querySelector(".ms-detail[data-for='" + row.getAttribute("data-i") + "']");
        if (d) d.hidden = !d.hidden;
      });
    });
  }

  function fillSectors(sectors, selected) {
    var sel = el("ms-sector");
    if (!sel || sel.options.length) return;
    (sectors || []).forEach(function (s) {
      var o = document.createElement("option");
      o.value = s; o.textContent = s;
      if (s === selected) o.selected = true;
      sel.appendChild(o);
    });
  }

  function load() {
    var t = el("ms-table");
    if (t) t.innerHTML = "<tbody><tr><td class='dsx-empty'>Scoring sector…</td></tr></tbody>";
    var sel = el("ms-sector");
    var url = CFG.scanUrl + (sel && sel.value ? "?sector=" + encodeURIComponent(sel.value) : "");
    fetch(url, { credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        fillSectors(d.sectors, d.sector);
        if (!d.ok) {
          if (t) t.innerHTML = "<tbody><tr><td class='dsx-empty'>" + esc(d.error || "Scan failed.") + "</td></tr></tbody>";
          return;
        }
        state.loaded = true;
        draw(d);
      })
      .catch(function () {
        if (t) t.innerHTML = "<tbody><tr><td class='dsx-empty'>Could not load the Morning Star scan.</td></tr></tbody>";
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var sel = el("ms-sector"), btn = el("ms-refresh");
    if (sel) sel.addEventListener("change", load);
    if (btn) btn.addEventListener("click", load);
    // Lazy: only fetch when the tab is first opened.
    var tab = document.querySelector(".dsx-tab[data-tab='morningstar']");
    if (tab) tab.addEventListener("click", function () { if (!state.loaded) load(); });
  });
})();
