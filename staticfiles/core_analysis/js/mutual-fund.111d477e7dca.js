/* Mutual Fund Desk — NAV & discount, assets allocation, sector allocation.
 *
 * Only the NAV tab has data out of the box: it is fed by the ShareSansar NAV
 * scrape. Both allocation tabs read imported monthly portfolios, so until one
 * is imported they render an explicit empty state that says WHY they are empty
 * and how to fill them — an unexplained blank table reads as a broken page.
 */
(function () {
  "use strict";

  var CFG = window.MF_CONFIG || {};
  var el = function (id) { return document.getElementById(id); };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function num(v, dp) {
    if (v == null || isNaN(v)) return "—";
    return Number(v).toLocaleString("en-US",
      { minimumFractionDigits: dp == null ? 2 : dp, maximumFractionDigits: dp == null ? 2 : dp });
  }
  function pct(v, dp) {
    if (v == null || isNaN(v)) return "—";
    return (v > 0 ? "+" : "") + Number(v).toFixed(dp == null ? 2 : dp) + "%";
  }
  function getJSON(url) {
    return fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); });
  }
  function empty(table, message) {
    table.innerHTML = '<tbody><tr><td class="mf-empty">' + message + "</td></tr></tbody>";
  }

  /* ---------- tabs ---------- */
  (function tabs() {
    var btns = [].slice.call(document.querySelectorAll(".dsx-tabs .dsx-tab"));
    var names = btns.map(function (b) { return b.getAttribute("data-tab"); });
    btns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var want = btn.getAttribute("data-tab");
        btns.forEach(function (b) { b.classList.toggle("active", b === btn); });
        names.forEach(function (n) {
          var pane = el("panel-" + n);
          if (pane) pane.classList.toggle("active", n === want);
        });
        try {
          var u = new URL(window.location.href);
          u.searchParams.set("tab", want);
          window.history.replaceState(null, "", u.toString());
        } catch (e) {}
        if (want === "assets") loadAssets();
        if (want === "sector") loadSector();
      });
    });
    var initial = null;
    try { initial = new URL(window.location.href).searchParams.get("tab"); } catch (e) {}
    if (initial && names.indexOf(initial) !== -1) {
      var b = btns[names.indexOf(initial)];
      if (b) b.click();
    }
  })();

  /* ---------- NAV & discount ---------- */
  function navBar(discount) {
    /* A discount bar, drawn from the centre: left of centre is below NAV.
       Scaled to ±20%, which covers the observed range with room to spare. */
    if (discount == null) return "";
    var capped = Math.max(-20, Math.min(20, discount));
    var half = Math.abs(capped) / 20 * 50;
    var colour = discount < 0 ? "var(--down,#ef4444)" : "var(--up,#22c55e)";
    var style = discount < 0
      ? "right:50%;width:" + half + "%;background:" + colour
      : "left:50%;width:" + half + "%;background:" + colour;
    return '<div class="mf-bar"><span style="' + style + '"></span></div>';
  }

  function renderNav(d) {
    var t = el("mf-table");
    if (!d || !d.ok || !d.funds || !d.funds.length) {
      empty(t, "No NAV data yet. Run <b>Sync Fund NAV</b> in the Raw Inventory Manager.");
      return;
    }
    var head = "<thead><tr>" +
      "<th>Symbol</th><th>Fund</th><th class='num'>NAV</th><th class='num'>Price</th>" +
      "<th class='num'>Discount</th><th></th><th>NAV as of</th></tr></thead>";
    var body = d.funds.map(function (f) {
      var cls = f.discount_pct == null ? "" : (f.discount_pct < 0 ? "neg" : "pos");
      return "<tr>" +
        "<td><a href='/stock/" + encodeURIComponent(f.symbol) + "/'>" + esc(f.symbol) + "</a>" +
          (f.is_matured ? " <span class='mf-chip'>matured</span>" : "") + "</td>" +
        "<td>" + esc(f.name || "") + "</td>" +
        "<td class='num'>" + num(f.nav) + "</td>" +
        "<td class='num'>" + num(f.price) + "</td>" +
        "<td class='num mf-disc " + cls + "'>" + pct(f.discount_pct) + "</td>" +
        "<td>" + navBar(f.discount_pct) + "</td>" +
        "<td class='mf-sub'>" + esc(f.nav_when || "") + " · " + esc(f.nav_basis || "") + "</td>" +
        "</tr>";
    }).join("");
    t.innerHTML = head + "<tbody>" + body + "</tbody>";

    el("mf-sub").textContent = d.count + " funds · " + d.priced + " with a market price";

    var cov = CFG.coverage || {};
    el("mf-kpis").innerHTML = [
      kpi("Funds with NAV", d.count),
      kpi("Median discount", pct(d.median_discount_pct)),
      kpi("Active listed covered", (cov.withNav || 0) + " / " + (cov.listed || 0)),
      kpi("Trading below NAV", d.funds.filter(function (f) {
        return f.discount_pct != null && f.discount_pct < 0;
      }).length)
    ].join("");
  }
  function kpi(label, value) {
    /* Classes must be dsx-kpi-label / dsx-kpi-val — floorsheet.css styles those
       two and nothing else. (canslim.js emits dsx-kpi-value, which has no rule
       at all, so its KPI numbers render unstyled.) */
    return '<div class="dsx-kpi"><span class="dsx-kpi-label">' + esc(label) +
           '</span><span class="dsx-kpi-val">' + esc(value) + "</span></div>";
  }

  /* ---------- allocation tabs ---------- */
  var NO_DATA =
    "No monthly portfolio imported yet.<br><br>" +
    "Mutual funds publish their holdings in a <b>monthly portfolio report</b>, and there is no " +
    "public feed for it — ShareSansar carries NAV only. Import one through " +
    "<b>POST /mutual-fund/api/import/</b> (staff) and this table builds itself.";

  var assetsLoaded = false, sectorLoaded = false;

  function fillPeriods(sel, periods, onChange) {
    if (!sel) return;
    sel.innerHTML = periods.length
      ? periods.map(function (p) { return '<option value="' + esc(p) + '">' + esc(p) + "</option>"; }).join("")
      : '<option value="">— none imported —</option>';
    sel.onchange = onChange;
  }

  function loadAssets() {
    if (assetsLoaded) return;
    assetsLoaded = true;
    var sel = el("mf-assets-period");
    getJSON(CFG.periodsUrl).then(function (p) {
      fillPeriods(sel, (p && p.periods) || [], drawAssets);
      drawAssets();
    }).catch(function () { drawAssets(); });
  }
  function drawAssets() {
    var sel = el("mf-assets-period");
    var q = sel && sel.value ? "?month=" + encodeURIComponent(sel.value) : "";
    getJSON(CFG.assetsUrl + q).then(function (d) {
      var t = el("mf-assets-table");
      if (!d || !d.ok || !d.funds || !d.funds.length) { empty(t, NO_DATA); el("mf-assets-sub").textContent = ""; return; }
      var head = "<thead><tr><th>Fund</th><th class='num'>NAV</th>" +
        "<th class='num'>Equity</th><th class='num'>Equity %</th>" +
        "<th class='num'>Fixed income</th><th class='num'>FI %</th>" +
        "<th class='num'>Cash</th><th class='num'>Cash %</th></tr></thead>";
      var rows = d.funds.map(rowAssets).join("");
      if (d.total) rows += rowAssets(d.total, true);
      t.innerHTML = head + "<tbody>" + rows + "</tbody>";
      el("mf-assets-sub").textContent = d.period + " · " + d.funds.length + " funds";
      el("mf-assets-note").innerHTML =
        "Percentages divide by the fund's own reported net assets where it supplied one, " +
        "which is why a row can total slightly over 100% — liabilities net out. Rows without " +
        "that figure divide by the sum of the buckets and total exactly 100%.";
    }).catch(function () { empty(el("mf-assets-table"), NO_DATA); });
  }
  function rowAssets(f, isTotal) {
    return "<tr" + (isTotal ? " style='font-weight:800'" : "") + ">" +
      "<td>" + esc(f.symbol) + (isTotal ? "" : " <span class='mf-sub'>" + esc(f.fund_name || "") + "</span>") + "</td>" +
      "<td class='num'>" + num(f.nav_monthly) + "</td>" +
      "<td class='num'>" + num(f.equity_value, 0) + "</td><td class='num'>" + pct(f.equity_pct) + "</td>" +
      "<td class='num'>" + num(f.fixed_income_value, 0) + "</td><td class='num'>" + pct(f.fixed_income_pct) + "</td>" +
      "<td class='num'>" + num(f.cash_value, 0) + "</td><td class='num'>" + pct(f.cash_pct) + "</td></tr>";
  }

  function loadSector() {
    if (sectorLoaded) return;
    sectorLoaded = true;
    var sel = el("mf-sector-period");
    getJSON(CFG.periodsUrl).then(function (p) {
      fillPeriods(sel, (p && p.periods) || [], drawSector);
      drawSector();
    }).catch(function () { drawSector(); });
  }
  function drawSector() {
    var sel = el("mf-sector-period");
    var q = sel && sel.value ? "?month=" + encodeURIComponent(sel.value) : "";
    getJSON(CFG.sectorUrl + q).then(function (d) {
      var t = el("mf-sector-table");
      if (!d || !d.ok || !d.funds || !d.funds.length) { empty(t, NO_DATA); el("mf-sector-sub").textContent = ""; return; }
      var head = "<thead><tr><th>Fund</th><th class='num'>Equity</th>" +
        d.sectors.map(function (s) { return "<th class='num'>" + esc(s) + "</th>"; }).join("") +
        "</tr></thead>";
      var body = d.funds.map(function (f) {
        return "<tr><td>" + esc(f.symbol) + "</td><td class='num'>" + num(f.equity_value, 0) + "</td>" +
          d.sectors.map(function (s) {
            var c = f.sectors[s] || {};
            return "<td class='num'>" + (c.pct ? pct(c.pct) : "—") + "</td>";
          }).join("") + "</tr>";
      }).join("");
      t.innerHTML = head + "<tbody>" + body + "</tbody>";
      el("mf-sector-sub").textContent = d.period + " · " + d.funds.length + " funds";
      el("mf-sector-note").innerHTML =
        "Percentages are of each fund's <b>equity book</b>, not of total assets — otherwise two " +
        "funds holding identical stocks would look different because one held more cash. Sectors " +
        "are resolved from the platform's own company register, not from the report's spelling.";
    }).catch(function () { empty(el("mf-sector-table"), NO_DATA); });
  }

  document.addEventListener("DOMContentLoaded", function () {
    getJSON(CFG.navUrl).then(renderNav).catch(function () {
      empty(el("mf-table"), "Could not load NAV data.");
    });
  });
})();
