import time
from core_analysis.services import broker_analytics as ba

t = time.time()
m = ba.meta()
print("meta ok=%s latest=%s brokers=%d symbols=%d sectors=%d  %.1fs" % (
    m["ok"], m["latest_date"], len(m["brokers"]), len(m["symbols"]), len(m["sectors"]), time.time() - t))
b = m["brokers"][0] if m["brokers"] else None
sym = m["symbols"][0]["symbol"] if m["symbols"] else None
print("sample broker=%s symbol=%s" % (b, sym))

f = ba.broker_favorites(b, "today", "shares")
print("favorites buy=%d sell=%d" % (len(f["buy"]), len(f["sell"])))
print("  top buy:", f["buy"][0] if f["buy"] else None)

sw = ba.stock_wise(sym, "today", "shares")
print("stockwise buy=%d sell=%d hold=%d" % (len(sw["buy"]), len(sw["sell"]), len(sw["holdings"])))
print("  top buy broker:", sw["buy"][0] if sw["buy"] else None)
print("  top holding:", sw["holdings"][0] if sw["holdings"] else None)

nh = ba.net_holding(b, "today")
print("netholding items=%d" % len(nh["items"]))
print("  sample:", nh["items"][0] if nh["items"] else None)

tr = ba.trend(sym, "buy")
print("trend points=%d (with close=%d)" % (
    len(tr["points"]), sum(1 for p in tr["points"] if p["close"] is not None)))
