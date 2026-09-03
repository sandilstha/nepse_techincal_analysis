/* fundamentals-desk.js — Fundamental Analysis desk.
 *
 * NAMESPACE: everything here is ia-* / IA_CONFIG, never fa-* / FA_CONFIG.
 * Those belong to Stock 360's fundamentals.js module. Keeping this desk off
 * that namespace means the two can never collide if they ever share a page —
 * they did once, silently: #fa-sector is a sector LABEL there but a sector
 * <select> here, and FA_CONFIG.matrixUrl is the per-company matrix, not this
 * desk's industry endpoint.
 *
 * Owns tab switching and the Industry Analysis matrix. The Smart Stock Score
 * pane is rendered by canslim.js, which is loaded alongside and binds to its own
 * element ids — the two never touch each other's DOM.
 */
(function () {
  "use strict";

  var CFG = window.IA_CONFIG || {
    matrixUrl: "/fundamentals/industry/",
    periodsUrl: "/fundamentals/industry/periods/"
  };
  var state = { stmt: "BS", loaded: false };

  function el(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /* Figures are shown EXACTLY as filed — in thousands of rupees, with comma
     separators. An earlier version abbreviated to B/M, which was easier to scan
     but silently restated the source: a filing of 420,134,125 (thousands) read
     as "420.13B", so the number on screen matched nothing in the report.

     Only money rows get thousands treatment. Ratios, percentages and per-share
     figures (Margin %, ROE, EPS, PE, Book Value) are NOT in Rs 000 and keep
     their decimals — rounding EPS of -17.4 to an integer would destroy it. */
  function fmtVal(v, unit) {
    if (v === null || v === undefined) {
      return "<span class='ia-blank' title='not reported by this company'>—</span>";
    }
    var n = Number(v);
    if (isNaN(n)) return "—";
    var money = unit && /000/.test(unit);
    var txt = money
      ? n.toLocaleString(undefined, { maximumFractionDigits: 0 })
      : n.toLocaleString(undefined, {
          minimumFractionDigits: Math.abs(n) < 100 ? 2 : 0,
          maximumFractionDigits: Math.abs(n) < 100 ? 2 : 1
        });
    var cls = n < 0 ? "num-neg" : "";
    return "<span class='" + cls + "' title='" +
      n.toLocaleString(undefined, { maximumFractionDigits: 4 }) +
      (unit ? " " + esc(unit) : "") + "'>" + txt + "</span>";
  }

  function drawMatrix(d) {
    var t = el("ia-table");
    if (!t) return;

    if (!d.ok) {
      /* A disabled statement is a DATA LIMIT, not a failure — say which. */
      var msg = d.unavailable
        ? "<b>" + esc(d.statement) + " is not available.</b><br>" + esc(d.reason)
        : esc(d.reason || "No data for this selection.");
      t.innerHTML = "<tbody><tr><td class='dsx-empty'>" + msg + "</td></tr></tbody>";
      var n0 = el("ia-note"); if (n0) n0.textContent = "";
      return;
    }

    var head = "<thead><tr><th class='l ia-item'>Line item</th>" +
      d.companies.map(function (c) { return "<th class='ia-co'>" + esc(c) + "</th>"; }).join("") +
      "</tr></thead>";

    var body = d.rows.map(function (r) {
      /* A line only some companies report is not a sector-wide comparison —
         flag it rather than let the blanks read as zeros. */
      var partial = r.reported_by < d.companies.length
        ? " <span class='ia-partial' title='reported by " + r.reported_by + " of " +
          d.companies.length + " companies'>" + r.reported_by + "/" + d.companies.length + "</span>"
        : "";
      return "<tr><td class='l ia-item'>" + esc(r.item) + partial +
        (r.unit ? " <span class='ia-unit'>" + esc(r.unit) + "</span>" : "") + "</td>" +
        r.values.map(function (v) {
          return "<td class='num'>" + fmtVal(v, r.unit) + "</td>";
        }).join("") + "</tr>";
    }).join("");

    t.innerHTML = head + "<tbody>" + body + "</tbody>";

    var title = el("ia-title");
    if (title) title.textContent = (d.statement || "").toUpperCase();
    var sub = el("ia-sub");
    if (sub) {
      var moneyRows = d.rows.filter(function (r) { return /000/.test(r.unit || ""); }).length;
      sub.textContent = d.sector + " · " + d.period_label + " · " +
        d.companies.length + " companies · " + d.line_items + " line items" +
        (moneyRows ? " · amounts in Rs '000 as filed" : "");
    }
    var note = el("ia-note");
    if (note) note.textContent = (d.statement_note || "") + " " + (d.note || "");
  }

  function fillPeriods(periods, keep) {
    var sel = el("ia-period");
    if (!sel) return;
    sel.innerHTML = (periods || []).map(function (p) {
      return "<option value='" + esc(p.fiscal_year) + "|" + p.quarter + "'>" +
        esc(p.label) + " (" + p.companies + ")</option>";
    }).join("");
    if (keep) sel.value = keep;
  }

  function load(usePeriod) {
    var t = el("ia-table");
    if (t) t.innerHTML = "<tbody><tr><td class='dsx-empty'>Loading…</td></tr></tbody>";
    var sector = (el("ia-sector") || {}).value || "";
    var q = "?sector=" + encodeURIComponent(sector) + "&fs_type=" + encodeURIComponent(state.stmt);
    if (usePeriod) {
      var parts = String(usePeriod).split("|");
      q += "&fiscal_year=" + encodeURIComponent(parts[0]) + "&quarter=" + encodeURIComponent(parts[1]);
    }
    fetch(CFG.matrixUrl + q, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.ok && d.periods) {
          fillPeriods(d.periods, d.fiscal_year + "|" + d.quarter);
        }
        drawMatrix(d);
      })
      .catch(function () {
        if (t) t.innerHTML = "<tbody><tr><td class='dsx-empty'>Could not load this statement.</td></tr></tbody>";
      });
  }

  function initTabs() {
    var tabs = document.querySelectorAll(".dsx-tabs .dsx-tab");
    [].forEach.call(tabs, function (btn) {
      btn.addEventListener("click", function () {
        [].forEach.call(tabs, function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        var want = btn.getAttribute("data-tab");
        ["industry", "smart"].forEach(function (name) {
          var pane = el("panel-" + name);
          if (pane) pane.classList.toggle("active", name === want);
        });
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTabs();
    var sec = el("ia-sector"), per = el("ia-period"), btn = el("ia-refresh");
    if (sec) sec.addEventListener("change", function () { load(); });
    if (per) per.addEventListener("change", function () { load(per.value); });
    if (btn) btn.addEventListener("click", function () { load(per && per.value); });

    /* Statement pills. The disabled Cash Flow pill must not become active — it
       still fires click events in some browsers. */
    var seg = document.querySelector("[data-group='ia-stmt']");
    if (seg) seg.addEventListener("click", function (e) {
      var pill = e.target.closest ? e.target.closest(".dsx-pill") : null;
      if (!pill || pill.disabled || pill.classList.contains("is-disabled")) return;
      [].forEach.call(seg.querySelectorAll(".dsx-pill"), function (p) {
        p.classList.remove("active");
      });
      pill.classList.add("active");
      state.stmt = pill.getAttribute("data-val");
      load();   // period list differs per statement, so re-resolve it
    });

    load();
  });
})();
