/* fundamentals-desk.js — Fundamental Analysis desk.
 *
 * Owns tab switching and the Industry Analysis matrix. The Smart Stock Score
 * pane is rendered by canslim.js, which is loaded alongside and binds to its own
 * element ids — the two never touch each other's DOM.
 */
(function () {
  "use strict";

  var CFG = window.FA_CONFIG || {
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

  /* Statement figures arrive in thousands of rupees. Printing 420134125 makes
     rows impossible to scan, so large values are abbreviated and the full number
     is kept on hover. Ratios (unit-less, small) are left alone. */
  function fmtVal(v, unit) {
    if (v === null || v === undefined) return "<span class='fa-blank' title='not reported by this company'>—</span>";
    var n = Number(v);
    if (isNaN(n)) return "—";
    var abs = Math.abs(n);
    var txt;
    if (unit && /000/.test(unit) && abs >= 1000) {
      // stored in thousands: 1,000 -> Rs 1M, 1,000,000 -> Rs 1B
      txt = abs >= 1e6 ? (n / 1e6).toFixed(2) + "B"
          : abs >= 1e3 ? (n / 1e3).toFixed(2) + "M"
          : n.toFixed(0);
    } else {
      txt = abs >= 1e6 ? (n / 1e6).toFixed(2) + "M"
          : abs >= 1000 ? n.toLocaleString(undefined, { maximumFractionDigits: 0 })
          : n.toFixed(Math.abs(n) < 10 ? 2 : 1);
    }
    var cls = n < 0 ? "num-neg" : "";
    return "<span class='" + cls + "' title='" +
      n.toLocaleString(undefined, { maximumFractionDigits: 4 }) +
      (unit ? " " + esc(unit) : "") + "'>" + txt + "</span>";
  }

  function drawMatrix(d) {
    var t = el("fa-table");
    if (!t) return;

    if (!d.ok) {
      /* A disabled statement is a DATA LIMIT, not a failure — say which. */
      var msg = d.unavailable
        ? "<b>" + esc(d.statement) + " is not available.</b><br>" + esc(d.reason)
        : esc(d.reason || "No data for this selection.");
      t.innerHTML = "<tbody><tr><td class='dsx-empty'>" + msg + "</td></tr></tbody>";
      var n0 = el("fa-note"); if (n0) n0.textContent = "";
      return;
    }

    var head = "<thead><tr><th class='l fa-item'>Line item</th>" +
      d.companies.map(function (c) { return "<th class='fa-co'>" + esc(c) + "</th>"; }).join("") +
      "</tr></thead>";

    var body = d.rows.map(function (r) {
      /* A line only some companies report is not a sector-wide comparison —
         flag it rather than let the blanks read as zeros. */
      var partial = r.reported_by < d.companies.length
        ? " <span class='fa-partial' title='reported by " + r.reported_by + " of " +
          d.companies.length + " companies'>" + r.reported_by + "/" + d.companies.length + "</span>"
        : "";
      return "<tr><td class='l fa-item'>" + esc(r.item) + partial +
        (r.unit ? " <span class='fa-unit'>" + esc(r.unit) + "</span>" : "") + "</td>" +
        r.values.map(function (v) {
          return "<td class='num'>" + fmtVal(v, r.unit) + "</td>";
        }).join("") + "</tr>";
    }).join("");

    t.innerHTML = head + "<tbody>" + body + "</tbody>";

    var title = el("fa-title");
    if (title) title.textContent = (d.statement || "").toUpperCase();
    var sub = el("fa-sub");
    if (sub) sub.textContent = d.sector + " · " + d.period_label + " · " +
      d.companies.length + " companies · " + d.line_items + " line items";
    var note = el("fa-note");
    if (note) note.textContent = (d.statement_note || "") + " " + (d.note || "");
  }

  function fillPeriods(periods, keep) {
    var sel = el("fa-period");
    if (!sel) return;
    sel.innerHTML = (periods || []).map(function (p) {
      return "<option value='" + esc(p.fiscal_year) + "|" + p.quarter + "'>" +
        esc(p.label) + " (" + p.companies + ")</option>";
    }).join("");
    if (keep) sel.value = keep;
  }

  function load(usePeriod) {
    var t = el("fa-table");
    if (t) t.innerHTML = "<tbody><tr><td class='dsx-empty'>Loading…</td></tr></tbody>";
    var sector = (el("fa-sector") || {}).value || "";
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
    var sec = el("fa-sector"), per = el("fa-period"), btn = el("fa-refresh");
    if (sec) sec.addEventListener("change", function () { load(); });
    if (per) per.addEventListener("change", function () { load(per.value); });
    if (btn) btn.addEventListener("click", function () { load(per && per.value); });

    /* Statement pills. The disabled Cash Flow pill must not become active — it
       still fires click events in some browsers. */
    var seg = document.querySelector("[data-group='fa-stmt']");
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
