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

  function drawBarometer(data) {
    var host = el("ms-barometer");
    if (!host) return;
    var b = data.barometer;
    if (!b) { host.innerHTML = ""; host.hidden = true; return; }
    host.hidden = false;
    var horizon = state.horizon || "1d";
    var grid = b[horizon] || {};
    var styles = ["Value", "Blend", "Growth"], sizes = ["Large", "Mid", "Small"];

    function cell(c) {
      if (!c || c.avg == null) return "<div class='ms-baro-cell ms-baro-empty'>—</div>";
      var v = c.avg;
      var cls = v > 0 ? "pos" : v < 0 ? "neg" : "flat";
      var mag = Math.min(Math.abs(v) / (horizon === "1y" ? 40 : horizon === "1w" ? 5 : 2.5), 1);
      return "<div class='ms-baro-cell " + cls + "' style='--mag:" + mag.toFixed(2) + "' title='" +
        c.n + " scrips, simple average'>" + (v > 0 ? "+" : "") + v.toFixed(2) + "</div>";
    }

    var html = "<div class='ms-baro-head'><span class='ms-baro-title'>Sector barometer</span>" +
      "<span class='ms-baro-toggles'>" +
      ["1d", "1w", "1y"].map(function (h) {
        return "<button type='button' class='ms-baro-btn" + (h === horizon ? " active" : "") +
          "' data-h='" + h + "'>" + h.toUpperCase() + "</button>";
      }).join("") + "</span></div><div class='ms-baro-grid'>";
    sizes.forEach(function (sz) {
      styles.forEach(function (st) {
        html += cell((grid[sz] || {})[st]);
      });
      html += "<div class='ms-baro-label'>" + sz + "</div>";
    });
    styles.forEach(function (st) { html += "<div class='ms-baro-label'>" + st + "</div>"; });
    html += "<div></div></div>";
    host.innerHTML = html;
    host.querySelectorAll(".ms-baro-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        state.horizon = btn.getAttribute("data-h");
        drawBarometer(state.data);
      });
    });
  }

  function drawScatter(data) {
    var host = el("ms-scatter");
    if (!host) return;
    var pts = (data.results || []).filter(function (r) {
      return r.growth != null && r.value != null;
    });
    if (!pts.length) { host.innerHTML = ""; return; }

    var W = 920, H = 460, m = { l: 52, r: 24, t: 16, b: 40 };
    var iw = W - m.l - m.r, ih = H - m.t - m.b;
    function X(v) { return m.l + (v / 100) * iw; }
    function Y(v) { return m.t + (1 - v / 100) * ih; }

    var svg = "<svg viewBox='0 0 " + W + " " + H + "' class='ms-scatter-svg' role='img' " +
      "aria-label='Growth versus Value scatter'>";

    // quadrant tints (midpoint 50/50) + grid
    svg += "<rect x='" + X(50) + "' y='" + m.t + "' width='" + (iw / 2) + "' height='" + (ih / 2) +
      "' class='ms-sc-quad best'/>";
    [0, 20, 40, 60, 80, 100].forEach(function (v) {
      svg += "<line x1='" + X(v) + "' y1='" + m.t + "' x2='" + X(v) + "' y2='" + (m.t + ih) + "' class='ms-sc-grid'/>";
      svg += "<line x1='" + m.l + "' y1='" + Y(v) + "' x2='" + (m.l + iw) + "' y2='" + Y(v) + "' class='ms-sc-grid'/>";
      svg += "<text x='" + X(v) + "' y='" + (m.t + ih + 16) + "' class='ms-sc-tick' text-anchor='middle'>" + v + "</text>";
      svg += "<text x='" + (m.l - 8) + "' y='" + (Y(v) + 4) + "' class='ms-sc-tick' text-anchor='end'>" + v + "</text>";
    });
    svg += "<line x1='" + X(50) + "' y1='" + m.t + "' x2='" + X(50) + "' y2='" + (m.t + ih) + "' class='ms-sc-mid'/>";
    svg += "<line x1='" + m.l + "' y1='" + Y(50) + "' x2='" + (m.l + iw) + "' y2='" + Y(50) + "' class='ms-sc-mid'/>";
    svg += "<text x='" + (m.l + iw / 2) + "' y='" + (H - 6) + "' class='ms-sc-axis' text-anchor='middle'>Growth score</text>";
    svg += "<text x='14' y='" + (m.t + ih / 2) + "' class='ms-sc-axis' text-anchor='middle' " +
      "transform='rotate(-90 14 " + (m.t + ih / 2) + ")'>Value score</text>";

    // label anti-collision: greedy vertical nudge per side of each point
    var placed = [];
    function labelY(x, y) {
      var ly = y - 9;
      var tries = 0;
      while (tries < 30 && placed.some(function (p) {
        return Math.abs(p.x - x) < 60 && Math.abs(p.y - ly) < 12;
      })) { ly -= 12; tries++; if (ly < m.t + 8) { ly = y + 16; } }
      placed.push({ x: x, y: ly });
      return ly;
    }

    pts.forEach(function (r) {
      var x = X(r.growth), y = Y(r.value);
      var cls = (r.stars >= 4) ? "star" : (r.gates && r.gates.length) ? "gated" : "";
      svg += "<circle cx='" + x + "' cy='" + y + "' r='4.5' class='ms-sc-dot " + cls + "'>" +
        "<title>" + esc(r.ticker) + " — Growth " + r.growth + ", Value " + r.value +
        (r.stars != null ? ", " + r.stars + "★" : "") + "</title></circle>";
      svg += "<text x='" + x + "' y='" + labelY(x, y) + "' class='ms-sc-label' text-anchor='middle'>" +
        esc(r.ticker) + "</text>";
    });
    svg += "</svg>";
    host.innerHTML = svg;
  }

  function draw(data) {
    state.data = data;
    drawBarometer(data);
    drawScatter(data);
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
