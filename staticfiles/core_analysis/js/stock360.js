/* Stock 360 — client hydration.
 * The server renders the hero, performance and S&R; this file fills the
 * fundamentals and floorsheet panels from the platform's existing JSON
 * endpoints, draws the adjusted-price chart, and wires search / theme / nav.
 * Every value shown comes from a fetch below — nothing is invented. */
(function () {
  "use strict";

  var SYM = (window.S360 && window.S360.symbol) || "";

  var $ = function (id) { return document.getElementById(id); };
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function num(v, dp) {
    if (v == null || isNaN(v)) return "—";
    return Number(v).toLocaleString("en-US", { minimumFractionDigits: dp || 0, maximumFractionDigits: dp || 0 });
  }
  function pct(v, dp) { return v == null || isNaN(v) ? "—" : Number(v).toFixed(dp == null ? 1 : dp) + "%"; }
  // Rs '000 → human units (South Asian: 1 Cr = 1e7, 1 Ar = 1e9).
  function rs000(v) {
    if (v == null || isNaN(v)) return "—";
    var rs = v * 1000;
    if (Math.abs(rs) >= 1e9) return (rs / 1e9).toFixed(2) + " Ar";
    if (Math.abs(rs) >= 1e7) return (rs / 1e7).toFixed(2) + " Cr";
    if (Math.abs(rs) >= 1e5) return (rs / 1e5).toFixed(2) + " L";
    return num(rs, 0);
  }
  function fmtHead(item) {
    var v = item.value;
    if (v == null) return "—";
    if (item.fmt === "pct") return pct(v * 100, 1);
    if (item.fmt === "rs000") return rs000(v);
    return num(v, 2);
  }
  function getJSON(url) {
    return fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); });
  }

  /* ---------- theme ---------- */
  (function themeToggle() {
    var btn = $("themeBtn");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var n = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", n);
      try { localStorage.setItem("mi-theme", n); } catch (e) {}
      drawChart();
      if (typeof drawOvChart === "function") drawOvChart();
    });
  })();

  /* ---------- search + autocomplete ---------- */
  window.s360 = {
    go: function (ev) {
      if (ev) ev.preventDefault();
      var v = ($("symSearch").value || "").trim().toUpperCase();
      if (v) window.location.href = "/stock/" + encodeURIComponent(v) + "/";
      return false;
    }
  };
  (function autocomplete() {
    var input = $("symSearch"), box = $("symAc"), t = null, hi = -1, items = [];
    if (!input || !box) return;
    function close() { box.classList.remove("open"); box.innerHTML = ""; hi = -1; items = []; }
    function pick(v) { window.location.href = "/stock/" + encodeURIComponent(v) + "/"; }
    input.addEventListener("input", function () {
      var q = input.value.trim();
      clearTimeout(t);
      if (q.length < 2) { close(); return; }
      t = setTimeout(function () {
        getJSON("/dashboard/symbols/?q=" + encodeURIComponent(q)).then(function (d) {
          items = (d.results || []).filter(function (r) { return r.type !== "index"; }).slice(0, 12);
          if (!items.length) { close(); return; }
          box.innerHTML = "";
          items.forEach(function (r) {
            var parts = (r.label || r.value).split(" - ");
            var row = el("div", null,
              '<span class="t">' + esc(r.value) + '</span><span class="n">' + esc(parts[1] || "") + "</span>");
            row.addEventListener("mousedown", function (e) { e.preventDefault(); pick(r.value); });
            box.appendChild(row);
          });
          box.classList.add("open");
        }).catch(close);
      }, 160);
    });
    input.addEventListener("keydown", function (e) {
      var rows = box.querySelectorAll("div");
      if (!rows.length) return;
      if (e.key === "ArrowDown") { e.preventDefault(); hi = Math.min(hi + 1, rows.length - 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); hi = Math.max(hi - 1, 0); }
      else if (e.key === "Enter" && hi >= 0) { e.preventDefault(); pick(items[hi].value); return; }
      else return;
      rows.forEach(function (r, i) { r.classList.toggle("hi", i === hi); });
    });
    document.addEventListener("click", function (e) { if (!input.parentNode.contains(e.target)) close(); });
  })();

  /* ---------- section pills (scrollspy + click) ---------- */
  (function pills() {
    var ps = [].slice.call(document.querySelectorAll(".pill"));
    ps.forEach(function (p) {
      p.addEventListener("click", function () {
        var s = $(p.dataset.t);
        if (s) s.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
    var secs = ps.map(function (p) { return $(p.dataset.t); }).filter(Boolean);
    if (!("IntersectionObserver" in window)) return;
    var obs = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          ps.forEach(function (p) { p.classList.toggle("active", p.dataset.t === e.target.id); });
        }
      });
    }, { rootMargin: "-120px 0px -60% 0px", threshold: 0 });
    secs.forEach(function (s) { obs.observe(s); });
  })();

  /* ---------- price chart (canvas area line, adjusted closes) ---------- */
  var SPARK = null;
  try { SPARK = JSON.parse(($("spark-data") || {}).textContent || "null"); } catch (e) {}
  function css(v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }
  function rgba(color, a) {
    var d = document.createElement("div"); d.style.color = color; document.body.appendChild(d);
    var rgb = getComputedStyle(d).color; document.body.removeChild(d);
    var m = rgb.match(/\d+/g);
    return m ? "rgba(" + m[0] + "," + m[1] + "," + m[2] + "," + a + ")" : color;
  }
  function drawChart() {
    var c = $("priceChart");
    if (!c || !SPARK || SPARK.length < 2) return;
    var data = SPARK, dpr = window.devicePixelRatio || 1;
    var W = c.clientWidth || 700, H = 200;
    c.width = W * dpr; c.height = H * dpr;
    var ctx = c.getContext("2d"); ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, W, H);
    var lo = Math.min.apply(null, data), hi = Math.max.apply(null, data), rng = hi - lo || 1;
    var line = data[data.length - 1] >= data[0] ? css("--pos") : css("--neg");
    var pad = 6;
    function X(i) { return pad + (W - 2 * pad) * i / (data.length - 1); }
    function Y(v) { return H - pad - (H - 2 * pad) * (v - lo) / rng; }
    ctx.strokeStyle = css("--line"); ctx.lineWidth = 1;
    for (var g = 1; g < 4; g++) { var y = H * g / 4; ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
    var grad = ctx.createLinearGradient(0, 0, 0, H);
    grad.addColorStop(0, rgba(line, 0.26)); grad.addColorStop(1, rgba(line, 0));
    ctx.beginPath(); ctx.moveTo(X(0), Y(data[0]));
    data.forEach(function (v, i) { ctx.lineTo(X(i), Y(v)); });
    ctx.lineTo(X(data.length - 1), H - pad); ctx.lineTo(X(0), H - pad); ctx.closePath();
    ctx.fillStyle = grad; ctx.fill();
    ctx.beginPath(); ctx.moveTo(X(0), Y(data[0]));
    data.forEach(function (v, i) { ctx.lineTo(X(i), Y(v)); });
    ctx.strokeStyle = line; ctx.lineWidth = 2; ctx.lineJoin = "round"; ctx.stroke();
    ctx.beginPath(); ctx.arc(X(data.length - 1), Y(data[data.length - 1]), 3.5, 0, 7); ctx.fillStyle = line; ctx.fill();
  }
  window.addEventListener("resize", function () { clearTimeout(window.__s360r); window.__s360r = setTimeout(drawChart, 150); });
  drawChart();

  /* ================= OVERVIEW (photo layout) ================= *
   * Market + Key Ratios + Investment Style cards and a timeframe-toggled price
   * chart. Price-derived numbers (60d avg, market cap, beta) come from the
   * server via window.S360; the ratios come from the fundamentals fetch below,
   * so nothing here is invented — a missing value renders as "—". */

  var S = window.S360 || {};

  function kvRow(label, valHtml) {
    return '<div class="kv-row"><dt>' + esc(label) + "</dt><dd class=\"num\">" + valHtml + "</dd></div>";
  }
  // Fundamentals expose fractions for rate metrics (roe, roa, gross_margin) and
  // Rs '000 for money lines; ratios below account for that.
  function safeDiv(a, b) { return (a != null && b) ? a / b : null; }

  function renderMarketCard(ks) {
    var price = (S.close != null ? S.close : (ks && ks.price));
    var bvps = ks && ks.bvps, eps = ks && ks.eps;
    var pe = (ks && ks.pe != null) ? ks.pe : safeDiv(price, eps);
    var pb = safeDiv(price, bvps);
    var rows =
      kvRow("60 Days Average", num(S.avg60, 2)) +
      kvRow("Market Cap (Millions)", num(S.marketCapM, 2)) +
      kvRow("Book Value Per Share", num(bvps, 2)) +
      kvRow("Price/Earnings", num(pe, 2)) +
      kvRow("Price/Book", num(pb, 2)) +
      kvRow("5 Years Beta", num(S.beta5y, 2));
    var box = $("mktCard"); if (box) box.innerHTML = rows;
    return { pb: pb };
  }

  // Compound annual growth over up to 3 fiscal years from a trend metric.
  function cagr3(points) {
    if (!points || points.length < 2) return null;
    var last = points[points.length - 1].value;
    var span = Math.min(3, points.length - 1);
    var base = points[points.length - 1 - span].value;
    if (base == null || base <= 0 || last == null) return null;
    return (Math.pow(last / base, 1 / span) - 1) * 100;
  }
  function trendPts(trend, label) {
    var t = (trend || []).filter(function (x) { return x.label === label; })[0];
    return t ? t.points : null;
  }

  function renderRatioCard(d) {
    var ks = (d && d.ks) || {};
    var revG = cagr3(trendPts(d && d.trend, "Total Revenue"));
    var niG = cagr3(trendPts(d && d.trend, "Net Income"));
    var netMargin = (ks.net_income != null && ks.revenue) ? (ks.net_income / ks.revenue) * 100 : null;
    var rows =
      kvRow("Rev 3-Yr Growth (%)", revG == null ? "—" : num(revG, 2)) +
      kvRow("Net Income 3-Yr Growth (%)", niG == null ? "—" : num(niG, 2)) +
      kvRow("Net Margin %TTM", netMargin == null ? "—" : num(netMargin, 2)) +
      kvRow("ROA % TTM", ks.roa == null ? "—" : num(ks.roa * 100, 2)) +
      kvRow("ROE % TTM", ks.roe == null ? "—" : num(ks.roe * 100, 2)) +
      kvRow("Earning Per Share", num(ks.eps, 2));
    var box = $("ratioCard"); if (box) box.innerHTML = rows;
    return { revG: revG };
  }

  // Investment style box: size from market cap (NEPSE-scaled millions), style
  // from a P/B + revenue-growth heuristic. Both are coarse buckets, deliberately.
  function renderStyle(pb, revG) {
    var grid = $("styleGrid"); if (!grid) return;
    var cap = S.marketCapM;
    var row = cap == null ? null : (cap >= 40000 ? 0 : cap >= 10000 ? 1 : 2); // Large/Mid/Small
    var col = null;
    if (pb != null || revG != null) {
      var growthy = (pb != null && pb > 3) || (revG != null && revG > 15);
      var valuey = (pb != null && pb < 2) && (revG == null || revG < 5);
      col = growthy ? 2 : valuey ? 0 : 1; // Growth / Value / Core
    }
    var cells = grid.querySelectorAll("span");
    [].forEach.call(cells, function (c) { c.classList.remove("on"); });
    if (row != null && col != null) {
      var idx = row * 3 + col;
      if (cells[idx]) cells[idx].classList.add("on");
    }
  }

  function renderOverview(d) {
    var m = renderMarketCard(d && d.ks);
    var r = renderRatioCard(d);
    renderStyle(m.pb, r.revG);
  }

  // Paint the price-derived Market card and the size axis immediately from the
  // server payload, so a slow or failed fundamentals fetch can never leave these
  // stuck on "Loading…". The fundamentals fetch below re-renders with the ratios.
  renderMarketCard(null);
  renderStyle(null, null);

  // Single source of truth for the ratio cards is our local FinancialStatement,
  // served by /fundamentals/api/. The sync button writes the latest quarter into
  // that table; this just re-reads it. (The initial read happens in the
  // FUNDAMENTALS block below, which also fills the desk panel.)
  function reloadFund() {
    return getJSON("/fundamentals/api/?symbol=" + encodeURIComponent(SYM))
      .then(function (d) { if (d && d.ok) renderOverview(d); })
      .catch(function () {});
  }

  /* ---------- sync latest published report (funda.aurasrp.com.np → our DB) ---------- */
  (function fundaSync() {
    var btn = $("syncFundaBtn"), note = $("syncFundaNote");
    if (!btn) return;
    btn.addEventListener("click", function () {
      btn.disabled = true;
      var label = btn.textContent;
      btn.textContent = "⟳ Syncing…";
      if (note) { note.textContent = "Pulling " + SYM + "'s latest report…"; note.className = "s360-syncnote"; }
      getJSON("/stock/api/funda/sync/?symbol=" + encodeURIComponent(SYM)).then(function (r) {
        if (r && r.ok) {
          if (note) {
            var extra = r.fs_written ? " · " + r.fs_written + " items → Financial Statement" : "";
            note.textContent = "✓ Synced " + (r.period || "latest") + extra;
            note.className = "s360-syncnote ok";
          }
          btn.textContent = "⟳ Re-sync";
          reloadFund();  // re-render cards from the freshly updated Financial Statement
        } else {
          if (note) { note.textContent = (r && r.error) || "Sync failed."; note.className = "s360-syncnote err"; }
          btn.textContent = label;
        }
        btn.disabled = false;
      }).catch(function () {
        if (note) { note.textContent = "Could not reach the sync service."; note.className = "s360-syncnote err"; }
        btn.textContent = label; btn.disabled = false;
      });
    });
  })();

  /* ---------- overview price chart with timeframe toggles ---------- */
  var CHART = [];
  try { CHART = JSON.parse(($("chart-data") || {}).textContent || "[]") || []; } catch (e) {}
  var TF_DAYS = { "5Y": 1826, "1Y": 365, "6M": 182, "3M": 91, "1M": 31, "1W": 7 };
  var curTf = "1Y";

  function sliceTf(tf) {
    if (!CHART.length) return [];
    var days = TF_DAYS[tf] || 365;
    var lastMs = Date.parse(CHART[CHART.length - 1][0]);
    if (isNaN(lastMs)) return CHART.map(function (p) { return p[1]; });
    var cutoff = lastMs - days * 864e5;
    var out = [];
    for (var i = 0; i < CHART.length; i++) {
      var t = Date.parse(CHART[i][0]);
      if (!isNaN(t) && t >= cutoff) out.push(CHART[i][1]);
    }
    if (out.length < 2) out = CHART.slice(-2).map(function (p) { return p[1]; });
    return out;
  }

  function drawOvChart() {
    var c = $("ovChart");
    if (!c) return;
    var data = sliceTf(curTf);
    if (data.length < 2) { c.getContext("2d").clearRect(0, 0, c.width, c.height); return; }
    var dpr = window.devicePixelRatio || 1;
    var W = c.clientWidth || 460, H = c.clientHeight || 220;
    c.width = W * dpr; c.height = H * dpr;
    var ctx = c.getContext("2d"); ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, W, H);
    var lo = Math.min.apply(null, data), hi = Math.max.apply(null, data), rng = hi - lo || 1;
    var line = data[data.length - 1] >= data[0] ? css("--pos") : css("--neg");
    var pad = 6;
    function X(i) { return pad + (W - 2 * pad) * i / (data.length - 1); }
    function Y(v) { return H - pad - (H - 2 * pad) * (v - lo) / rng; }
    ctx.strokeStyle = css("--line"); ctx.lineWidth = 1;
    for (var g = 1; g < 4; g++) { var y = H * g / 4; ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
    var grad = ctx.createLinearGradient(0, 0, 0, H);
    grad.addColorStop(0, rgba(line, 0.24)); grad.addColorStop(1, rgba(line, 0));
    ctx.beginPath(); ctx.moveTo(X(0), Y(data[0]));
    data.forEach(function (v, i) { ctx.lineTo(X(i), Y(v)); });
    ctx.lineTo(X(data.length - 1), H - pad); ctx.lineTo(X(0), H - pad); ctx.closePath();
    ctx.fillStyle = grad; ctx.fill();
    ctx.beginPath(); ctx.moveTo(X(0), Y(data[0]));
    data.forEach(function (v, i) { ctx.lineTo(X(i), Y(v)); });
    ctx.strokeStyle = line; ctx.lineWidth = 2; ctx.lineJoin = "round"; ctx.stroke();
  }

  (function tfToggle() {
    var row = $("tfRow"); if (!row) return;
    row.addEventListener("click", function (e) {
      var b = e.target.closest(".tf"); if (!b) return;
      curTf = b.dataset.tf;
      [].forEach.call(row.querySelectorAll(".tf"), function (x) { x.classList.toggle("active", x === b); });
      drawOvChart();
    });
  })();
  window.addEventListener("resize", function () { clearTimeout(window.__s360ov); window.__s360ov = setTimeout(drawOvChart, 150); });
  drawOvChart();

  /* ---------- risk & opportunity roll-up ---------- */
  var risks = [], opps = [];
  function setChips(id, side, arr) {
    var box = $(id); if (!box) return;
    if (!arr.length) { box.innerHTML = '<div class="loading">No notable ' + side + '.</div>'; return; }
    box.innerHTML = "";
    arr.forEach(function (c) {
      box.appendChild(el("div", "chip " + c.cls,
        '<span class="ic">' + c.ic + '</span><div>' + c.text +
        '<div class="src">source: ' + esc(c.src) + "</div></div>"));
    });
  }
  function flushRO() {
    setChips("roRisk", "risks", risks);
    setChips("roOpp", "opportunities", opps);
    // Overview Risk cell mirrors the tally so the strip is fully live.
    var tone = risks.length > opps.length ? "neg" : opps.length > risks.length ? "pos" : "warn";
    var label = risks.length > opps.length ? "Risk-heavy" : opps.length > risks.length ? "Opportunity-led" : "Balanced";
    setVerdict("risk", risks.length + "R · " + opps.length + "O", label, tone);
  }

  function setVerdict(k, score, label, tone) {
    var sc = document.querySelector('#vstrip [data-k="' + k + '"]');
    var vd = document.querySelector('#vstrip [data-k="' + k + 'v"]');
    var stripe = sc ? sc.parentNode.querySelector(".stripe") : null;
    if (sc) { sc.textContent = score; sc.className = "sc num " + tone; }
    if (vd) { vd.textContent = label; vd.className = "verdict " + tone; }
    if (stripe) stripe.style.background = "var(--" + (tone === "pos" ? "pos" : tone === "neg" ? "neg" : tone === "warn" ? "warn" : "neutral") + ")";
  }

  /* ---------- ③ FUNDAMENTALS ---------- */
  getJSON("/fundamentals/api/?symbol=" + encodeURIComponent(SYM)).then(function (d) {
    if (!d || !d.ok) throw 0;
    renderOverview(d);
    var body = $("fundBody"); body.innerHTML = "";
    var grid = el("div", "mgrid");
    (d.headline || []).forEach(function (h) {
      grid.appendChild(el("div", "mcard",
        '<div class="k">' + esc(h.label) + '</div><div class="v num">' + fmtHead(h) + "</div>"));
    });
    body.appendChild(grid);

    var ms = d.morningstar;
    if (ms && ms.fair_value) {
      var fv = ms.fair_value, v = fv.verdict || "";
      var tone = /under/i.test(v) ? "pos" : /over/i.test(v) ? "neg" : "warn";
      var wrap = el("div"); wrap.style.cssText = "display:grid;grid-template-columns:180px 1fr;gap:18px;margin-top:16px";
      wrap.appendChild(el("div", null,
        '<div style="background:var(--' + tone + '-weak);border:1px solid var(--line);border-radius:9px;padding:13px;text-align:center">' +
        '<div class="eyebrow">Fair Value</div>' +
        '<div class="num ' + tone + '" style="font-size:22px;font-weight:800;margin-top:6px">' + esc(v) + "</div>" +
        (fv.estimate ? '<div class="num" style="font-size:13px;color:var(--ink-2);margin-top:4px">est. Rs ' + num(fv.estimate, 0) +
          (fv.ratio ? " · " + Number(fv.ratio).toFixed(2) + "×" : "") + "</div>" : "") +
        '<div class="fresh" style="margin-top:6px">sector-median P/E × EPS</div></div>'));
      var ranks = el("div");
      ranks.appendChild(el("div", "eyebrow", "Peer percentile — " + esc(ms.sector || "sector")));
      var peer = el("div", "peer");
      (ms.ranks || []).forEach(function (r) {
        var p = r.percentile == null ? 0 : Math.round(r.percentile);
        var tn = p >= 60 ? "pos" : p >= 40 ? "warn" : "neg";
        peer.appendChild(el("div", "row",
          "<span>" + esc(r.label) + '</span><div class="track"><span class="fill" style="width:' + p +
          "%;background:var(--" + tn + ')"></span><span class="med" style="left:50%"></span></div>' +
          '<span class="pv num ' + tn + '">' + p + "th</span>"));
      });
      ranks.appendChild(peer);
      wrap.appendChild(ranks);
      body.appendChild(wrap);

      var ps = (ms.ranks || []).map(function (r) { return r.percentile; }).filter(function (x) { return x != null; });
      var score = ps.length ? Math.round(ps.reduce(function (a, b) { return a + b; }, 0) / ps.length) : 50;
      var stone = score >= 60 ? "pos" : score >= 45 ? "warn" : "neg";
      $("fundScore").textContent = v || (score + "/100");
      $("fundScore").className = "desk-score sc-" + stone;
      setVerdict("fund", score, v || "—", stone);

      if (/under/i.test(v)) opps.push({ cls: "good", ic: "↑", text: "<b>Undervalued</b> at " + (fv.ratio ? Number(fv.ratio).toFixed(2) + "× fair value" : "vs sector") + (fv.estimate ? " (est. Rs " + num(fv.estimate, 0) + ")" : "") + ".", src: "morningstar.fair_value" });
      if (/over/i.test(v)) risks.push({ cls: "bad", ic: "↓", text: "<b>Overvalued</b> vs sector-median P/E.", src: "morningstar.fair_value" });
      (ms.ranks || []).forEach(function (r) {
        if (r.percentile != null && r.percentile >= 80)
          opps.push({ cls: "good", ic: "★", text: "<b>" + esc(r.label) + "</b> in top " + (100 - Math.round(r.percentile)) + "% of " + esc(ms.sector || "sector") + ".", src: "morningstar.ranks" });
      });
      flushRO();
    } else {
      $("fundScore").textContent = "no research";
      setVerdict("fund", "n/a", "no data", "neu");
    }
  }).catch(function () {
    renderOverview(null);
    $("fundBody").innerHTML = '<div class="notice">No fundamentals feed for <b>' + esc(SYM) + "</b>.</div>";
    $("fundScore").textContent = "n/a"; setVerdict("fund", "n/a", "no data", "neu");
  });

  /* ---------- ⑤ FLOORSHEET ----------
   * stock_wise returns TOP-10 buy/sell rows and per-broker positive net
   * positions (holdings). Market-wide buy always equals sell, so there is no
   * "net market position" — the honest metrics are broker accumulation and
   * side concentration, which is exactly what we show. */
  Promise.all([
    getJSON("/floorsheet/api/stockwise/?symbol=" + encodeURIComponent(SYM) + "&range=1m&view=shares"),
    getJSON("/floorsheet/api/meta/").catch(function () { return null; })
  ]).then(function (res) {
    var d = res[0], meta = res[1];
    if (!d || !d.ok) throw 0;
    var names = (meta && meta.broker_names) || {};
    function bname(key) {
      var n = names[key] || names[String(key)];
      return n ? "#" + key + " " + n : "Broker " + key;
    }

    var body = $("flowBody"); body.innerHTML = "";
    var buy = d.buy || [], sell = d.sell || [], holds = d.holdings || [];
    var accQty = holds.reduce(function (a, r) { return a + (r.quantity || 0); }, 0);
    var top3buy = buy.slice(0, 3).reduce(function (a, r) { return a + (r.pct || 0); }, 0);
    var top3sell = sell.slice(0, 3).reduce(function (a, r) { return a + (r.pct || 0); }, 0);

    var summary = el("div", "mgrid"); summary.style.marginBottom = "14px";
    summary.innerHTML =
      '<div class="mcard"><div class="k">Broker Accumulation (1M)</div><div class="v num pos">' + num(accQty, 0) + '</div><div class="sub">' + holds.length + " net-long brokers (top 10)</div></div>" +
      '<div class="mcard"><div class="k">Top Buyer</div><div class="v num pos">' + (buy[0] ? pct(buy[0].pct, 1) : "—") + '</div><div class="sub">' + (buy[0] ? esc(bname(buy[0].key)) : "no activity") + "</div></div>" +
      '<div class="mcard"><div class="k">Top Seller</div><div class="v num neg">' + (sell[0] ? pct(sell[0].pct, 1) : "—") + '</div><div class="sub">' + (sell[0] ? esc(bname(sell[0].key)) : "no activity") + "</div></div>" +
      '<div class="mcard"><div class="k">Top-3 Concentration</div><div class="v num">' + pct(top3buy, 0) + " / " + pct(top3sell, 0) + '</div><div class="sub">buy side / sell side</div></div>';
    body.appendChild(summary);

    function col(title, rows, tone, unit) {
      var c = el("div", "btcol");
      c.appendChild(el("div", "cap", "<span>" + title + '</span><span class="neu">' + unit + "</span>"));
      var max = rows.length ? rows[0].pct || 1 : 1;
      rows.slice(0, 3).forEach(function (r, i) {
        c.appendChild(el("div", "brow",
          '<span class="rk">' + (i + 1) + "</span>" +
          '<div><div class="bn">' + esc(bname(r.key)) + '</div><div class="mini" style="width:' + Math.max(8, (r.pct / max) * 100) + "%;background:var(--" + tone + ')"></div></div>' +
          '<span class="num ' + tone + '">' + pct(r.pct, 1) + "</span>"));
      });
      if (!rows.length) c.appendChild(el("div", "loading", "No activity."));
      return c;
    }
    var bt = el("div", "btwrap");
    bt.appendChild(col("Top Buying Brokers", buy, "pos", "% of buy side"));
    bt.appendChild(col("Top Selling Brokers", sell, "neg", "% of sell side"));
    body.appendChild(bt);
    body.appendChild(el("div", "fresh",
      "Window: 1 month · shares · top-10 brokers per side. Buy and sell totals always match market-wide; read conviction from concentration and per-broker accumulation."));

    // Verdict: which side is more concentrated = which side has conviction.
    var diff = top3buy - top3sell;
    var tone = diff > 5 ? "pos" : diff < -5 ? "neg" : "warn";
    var label = diff > 5 ? "Buy-side concentrated" : diff < -5 ? "Sell-side concentrated" : "Balanced flow";
    $("flowScore").textContent = label;
    $("flowScore").className = "desk-score sc-" + (tone === "warn" ? "warn" : tone);
    setVerdict("flow", pct(Math.abs(diff), 0), label, tone);

    if (top3sell >= 50) risks.push({ cls: "warnc", ic: "≈", text: "Selling concentrated — top 3 brokers hold " + pct(top3sell, 0) + " of the sell side.", src: "stock_wise sell concentration" });
    if (top3buy >= 50) opps.push({ cls: "good", ic: "◆", text: "Concentrated accumulation — top 3 brokers take " + pct(top3buy, 0) + " of the buy side.", src: "stock_wise buy concentration" });
    flushRO();
  }).catch(function () {
    $("flowBody").innerHTML = '<div class="notice">No floorsheet activity for <b>' + esc(SYM) + "</b> in this window.</div>";
    $("flowScore").textContent = "n/a"; setVerdict("flow", "n/a", "no data", "neu");
  });

  /* ---------- ④ FINANCIAL STATEMENTS (all reported quarters) ----------
   * Rows are the line items that matter for this company's SECTOR (BFIs get
   * equity/loans/NII/impairment/distributable profit/NPL…, other sectors their
   * own headline metrics); columns are every quarter on file, newest first. */
  (function statements() {
    var tabsBox = $("kfTabs"), table = $("kfTable"), meta = $("kfMeta"), note = $("kfNote");
    if (!table) return;

    /* Wide tables (a company can have 50+ quarters) are panned by dragging —
     * hunting for a horizontal scrollbar under a 60vh box is painful with a
     * mouse. Shift+wheel scrolls horizontally too. */
    (function dragToPan() {
      var wrap = table.parentNode;
      if (!wrap || !wrap.classList.contains("kf-wrap")) return;
      var down = false, startX = 0, startY = 0, startL = 0, startT = 0, moved = false;

      wrap.addEventListener("mousedown", function (e) {
        if (e.button !== 0) return;
        down = true; moved = false;
        startX = e.pageX; startY = e.pageY;
        startL = wrap.scrollLeft; startT = wrap.scrollTop;
        wrap.classList.add("kf-dragging");
      });
      window.addEventListener("mousemove", function (e) {
        if (!down) return;
        var dx = e.pageX - startX, dy = e.pageY - startY;
        if (!moved && Math.abs(dx) + Math.abs(dy) < 3) return;  // let real clicks through
        moved = true;
        e.preventDefault();
        wrap.scrollLeft = startL - dx;
        wrap.scrollTop = startT - dy;
      });
      window.addEventListener("mouseup", function () {
        down = false;
        wrap.classList.remove("kf-dragging");
      });
      wrap.addEventListener("wheel", function (e) {
        if (!e.shiftKey || !e.deltaY) return;
        wrap.scrollLeft += e.deltaY;
        e.preventDefault();
      }, { passive: false });
    })();

    function fmtVal(v, fmt) {
      if (v == null || isNaN(v)) return "—";
      if (fmt === "pct") return (v * 100).toFixed(2) + "%";
      if (fmt === "rs000") return Math.round(v).toLocaleString();
      return Number(v).toLocaleString(undefined, { maximumFractionDigits: 2 });
    }

    table.innerHTML = '<tbody><tr><td class="kf-empty">Loading statements…</td></tr></tbody>';

    // Distinguish "the desk has no data" from "the request failed" — reporting a
    // network/404 as "nothing stored" sends you looking in the wrong place.
    function fail(msg) {
      if (tabsBox) tabsBox.style.display = "none";
      table.innerHTML = '<tbody><tr><td class="kf-empty">' + esc(msg) + "</td></tr></tbody>";
      if (meta) { meta.textContent = "n/a"; meta.className = "desk-score sc-neu"; }
      if (note) note.textContent = "";
    }

    getJSON("/stock/api/keyfin/?symbol=" + encodeURIComponent(SYM)).then(function (d) {
      if (!d || !d.ok || !d.groups || !d.groups.length) {
        fail((d && d.error) ||
          ("No financial statements stored for " + SYM + ". Sync this company from the Workbench to populate them."));
        return;
      }

      if (tabsBox) tabsBox.style.display = "";
      var periods = d.periods || [];
      if (meta) {
        meta.textContent = periods.length + " quarters";
        meta.className = "desk-score sc-neu";
      }
      if (note) {
        note.textContent = "Sector: " + d.sector +
          (d.curated ? " · sector-specific line items" : " · top-level statement rows") +
          " · amounts in Rs '000 unless shown as a ratio. Newest quarter first" +
          (periods.length > 6 ? " — drag the table sideways to see older quarters." : ".");
      }

      function render(group) {
        var head = '<thead><tr><th class="kf-first">' + esc(group.title) + "</th>" +
          periods.map(function (p, i) {
            return '<th class="' + (i === 0 ? "kf-new" : "") + '"><span class="kf-yr">' +
              esc(p.fy) + '</span><span class="kf-q">Q' + p.quarter + "</span>" +
              (i === 0 ? '<span class="kf-new-chip">Latest</span>' : "") + "</th>";
          }).join("") + "</tr></thead>";

        var body = group.rows.map(function (r) {
          return "<tr><td class=\"kf-first\">" + esc(r.label) + "</td>" +
            periods.map(function (p, i) {
              var v = r.values[p.key];
              var neg = (v != null && !isNaN(v) && v < 0) ? " kf-neg" : "";
              return '<td class="' + (i === 0 ? "kf-new" : "") + neg + '">' +
                fmtVal(v, r.fmt) + "</td>";
            }).join("") + "</tr>";
        }).join("");

        table.innerHTML = head + "<tbody>" + body + "</tbody>";
      }

      // One tab per available statement; first is shown by default.
      tabsBox.innerHTML = "";
      d.groups.forEach(function (g, i) {
        var b = el("button", "kf-tab" + (i === 0 ? " active" : ""), esc(g.title));
        b.type = "button";
        b.addEventListener("click", function () {
          [].forEach.call(tabsBox.querySelectorAll(".kf-tab"), function (x) {
            x.classList.toggle("active", x === b);
          });
          render(g);
        });
        tabsBox.appendChild(b);
      });
      render(d.groups[0]);
    }).catch(function (err) {
      // A rejected fetch means the request itself failed (offline, 404, 500) —
      // or a stale page calling an endpoint this server build doesn't have.
      fail("Couldn't load statements for " + SYM +
        (err ? " (request failed: " + err + ")" : "") + ". Reload the page and try again.");
    });
  })();

  /* ---------- AI Narrative (Gemini, on-demand, server-cached) ---------- */
  (function aiNarrative() {
    var btn = $("aiGenBtn"), out = $("aiNarrative");
    if (!btn || !out) return;
    btn.addEventListener("click", function () {
      btn.disabled = true; btn.textContent = "Generating…";
      out.innerHTML = '<div class="loading">Asking Gemini to read ' + esc(SYM) + "'s structure…</div>";
      getJSON("/stock/api/ai/?symbol=" + encodeURIComponent(SYM)).then(function (d) {
        if (d && d.analysis_html) {
          out.innerHTML = '<div class="ai-narrative">' + d.analysis_html + "</div>" +
            '<div class="ai-meta">Generated by ' + esc(d.model || "AI") + (d.provider ? " · " + esc(d.provider) : "") +
            (d.cached ? " · cached for the trading day" : "") +
            " — from this symbol's support/resistance metrics &amp; recent price path.</div>";
          btn.textContent = "↻ Regenerate";
        } else {
          out.innerHTML = '<div class="notice">' + esc((d && d.error) || "No narrative returned.") + "</div>";
          btn.textContent = "✨ Generate";
        }
        btn.disabled = false;
      }).catch(function () {
        out.innerHTML = '<div class="notice">Could not reach the AI service. Try again.</div>';
        btn.textContent = "✨ Generate"; btn.disabled = false;
      });
    });
  })();
})();
