"""Turns Actions into IBKR orders with ib_async (pip install ib_async; the maintained successor of ib_insync).

Written against the TWS API's documented order fields; not run against a live TWS / IB Gateway from here, so start on
the paper account (port 7497 TWS paper / 4002 Gateway paper) and check every order type once before going live.
"""
from .manage import Action


class IBKR:
    def __init__(self, host="127.0.0.1", port=7497, client_id=17, trigger_method=0, dry_run=True):
        """trigger_method: how IBKR triggers stops (0 default, 1 double bid/ask, 2 last, 3 double last, 4 bid/ask,
        7 last or bid/ask, 8 mid-point). Set it on purpose: tight 1-1.5% stops get hit by a single bad print on "last".
        dry_run: print the orders instead of sending them"""
        self.host, self.port, self.client_id, self.trigger_method, self.dry_run = host, port, client_id, trigger_method, dry_run
        self.ib = None
        self.stops = {}            # symbol -> the resting stop order's Trade

    # ---- connection and account -------------------------------------------------------------------------------
    def connect(self):
        from ib_async import IB          # imported here: the rest of lukbot runs without it
        self.ib = IB()
        self.ib.connect(self.host, self.port, clientId=self.client_id)
        return self

    def account(self) -> dict:
        """NetLiquidation, GrossPositionValue, ExcessLiquidity, Cushion, BuyingPower (USD)"""
        want = {"NetLiquidation", "GrossPositionValue", "ExcessLiquidity", "Cushion", "BuyingPower"}
        out = {}
        for v in self.ib.accountSummary():
            if v.tag in want and v.currency in ("USD", ""):
                out[v.tag] = float(v.value)
        return out

    def positions(self) -> dict:
        """symbol -> signed shares at IBKR (reconcile with the bot's own state on every (re)connect)"""
        return {p.contract.symbol: int(p.position) for p in self.ib.positions()}

    def excess_after(self, symbol: str, side: str, qty: int, price: float):
        """IBKR's own margin check: the excess liquidity if this order filled (whatIfOrder); None if unavailable"""
        from ib_async import LimitOrder
        try:
            st = self.ib.whatIfOrder(self._contract(symbol), LimitOrder(side, qty, price))
            return float(st.equityWithLoanAfter) - float(st.maintMarginAfter)
        except Exception:
            return None

    def _contract(self, symbol):
        from ib_async import Stock
        c = Stock(symbol, "SMART", "USD")
        self.ib.qualifyContracts(c)
        return c

    # ---- orders -----------------------------------------------------------------------------------------------
    def execute(self, actions: list):
        """send a list of Actions in order (an entry and its stop arrive together as a bracket)"""
        i = 0
        while i < len(actions):
            a = actions[i]
            if a.tag == "entry" and i + 1 < len(actions) and actions[i + 1].tag == "stop":
                self._bracket(a, actions[i + 1])
                i += 2
                continue
            self._one(a)
            i += 1

    def _order(self, a: Action):
        from ib_async import Order
        o = Order(action=a.kind if a.kind in ("BUY", "SELL") else "SELL", totalQuantity=a.qty, orderType=a.order_type,
                  tif="DAY", outsideRth=False, orderRef=f"lukbot:{a.tag}")
        if a.price is not None:
            o.lmtPrice = a.price
        if a.stop is not None:
            o.auxPrice = a.stop
        if a.order_type in ("STP", "STP LMT"):
            o.triggerMethod = self.trigger_method
        return o

    def _bracket(self, entry: Action, stop: Action):
        if self.dry_run:
            print("DRY", entry, "\n    +", stop)
            return
        c = self._contract(entry.symbol)
        parent = self._order(entry)
        parent.orderId = self.ib.client.getReqId()
        parent.transmit = False
        child = self._order(stop)
        child.parentId, child.tif, child.transmit = parent.orderId, "GTC", True
        self.ib.placeOrder(c, parent)
        self.stops[entry.symbol] = self.ib.placeOrder(c, child)

    def _one(self, a: Action):
        if self.dry_run:
            print("DRY", a)
            return
        if a.kind == "CANCEL":
            t = self.stops.pop(a.symbol, None)
            if t is not None:
                self.ib.cancelOrder(t.order)
            return
        if a.kind == "MODIFY_STOP":
            t = self.stops.get(a.symbol)
            if t is None:
                raise RuntimeError(f"{a.symbol}: no resting stop to modify; reconcile before trading")
            t.order.auxPrice, t.order.totalQuantity = a.stop, a.qty
            self.stops[a.symbol] = self.ib.placeOrder(t.contract, t.order)
            return
        self.ib.placeOrder(self._contract(a.symbol), self._order(a))

    def kill(self):
        """the kill switch: cancel every open order that is not a protective stop (entries, trims, MOCs)"""
        if self.dry_run:
            print("DRY kill switch")
            return
        for t in self.ib.openTrades():
            if not (t.order.orderRef or "").endswith(":stop"):
                self.ib.cancelOrder(t.order)
