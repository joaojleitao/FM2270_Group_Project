"""The notebook's inline functions must match app/strategy.py.

1. Same set of function names, and identical code (compared as parsed syntax trees, so
   comments and formatting don't matter but any logic change does).
2. Identical numerical results on the same synthetic inputs.
"""
import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebook" / "FM2270_backtest.ipynb"
MODULE = ROOT / "app" / "strategy.py"


def notebook_functions():
    """Collect top-level function definitions from the notebook's code cells (skipping !pip / %magic lines)."""
    cells = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]
    code = []
    for c in cells:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        code.append("\n".join(l for l in src.splitlines() if not l.lstrip().startswith(("!", "%"))))
    tree = ast.parse("\n\n".join(code))
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def module_functions():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def test_same_function_names():
    # every shared calculation function is in the notebook (the notebook may add small helpers of its own,
    # e.g. for robustness loops, that the app does not need)
    missing = set(module_functions()) - set(notebook_functions())
    assert not missing, f"functions missing from the notebook: {missing}"


@pytest.mark.parametrize("name", sorted(module_functions()))
def test_identical_code(name):
    nb = notebook_functions()[name]
    assert ast.dump(nb) == ast.dump(module_functions()[name]), f"{name} differs between notebook and app/strategy.py"


def load_notebook_namespace():
    """Execute the notebook's function definitions (only) into a fresh namespace."""
    ns = {"np": np, "pd": pd}
    shared = [f for name, f in notebook_functions().items() if name in module_functions()]
    mod = ast.Module(body=shared, type_ignores=[])
    exec(compile(mod, str(NOTEBOOK), "exec"), ns)
    return ns


def test_identical_results_on_synthetic_data():
    import sys
    sys.path.insert(0, str(ROOT / "app"))
    import strategy

    rng = np.random.default_rng(2270)
    dates = pd.bdate_range("2015-01-01", "2018-12-31")
    rets = pd.DataFrame(rng.normal(0.0003, [0.01, 0.004, 0.009], (len(dates), 3)),
                        index=dates, columns=["SPY", "IEF", "GLD"])
    month_ends = rets.groupby(rets.index.to_period("M")).tail(1).index
    nb = load_notebook_namespace()
    w_mod = strategy.inverse_vol_weights(rets, month_ends, 252)
    w_nb = nb["inverse_vol_weights"](rets, month_ends, 252)
    pd.testing.assert_frame_equal(w_mod, w_nb)

    bt_mod = strategy.backtest(rets, w_mod, 10)
    bt_nb = nb["backtest"](rets, w_nb, 10)
    pd.testing.assert_frame_equal(bt_mod, bt_nb)

    for name in ["gross", "net"]:          # fixed-weight benchmark path too
        fw = strategy.fixed_weights(month_ends, {"SPY": 0.6, "IEF": 0.4})
        pd.testing.assert_frame_equal(strategy.backtest(rets, fw, 25), nb["backtest"](rets, nb["fixed_weights"](month_ends, {"SPY": 0.6, "IEF": 0.4}), 25))
    rf = pd.Series(0.001, index=bt_mod.index)
    bench = bt_mod["gross"] * 0.5
    pd.testing.assert_series_equal(pd.Series(strategy.performance_table(bt_mod["net"], bench, rf)),
                                  pd.Series(nb["performance_table"](bt_nb["net"], bench, rf)))


def test_backtest_against_independent_loop():
    """Gross returns must equal a plain day-by-day holdings loop; weights must not use future data."""
    import sys
    sys.path.insert(0, str(ROOT / "app"))
    import strategy

    rng = np.random.default_rng(7)
    dates = pd.bdate_range("2015-01-01", "2017-12-31")
    rets = pd.DataFrame(rng.normal(0.0003, [0.01, 0.004, 0.009], (len(dates), 3)),
                        index=dates, columns=["SPY", "IEF", "GLD"])
    rd = strategy.rebalance_dates(rets, "M")
    w = strategy.inverse_vol_weights(rets, rd, 126)
    # no look-ahead: truncating the data after t does not change the weights at t
    t = w.index[5]
    pd.testing.assert_series_equal(strategy.inverse_vol_weights(rets.loc[:t], [t], 126).loc[t], w.loc[t])
    # independent loop: hold dollar positions, rebalance at the close of each decision date
    hold, values = None, {}
    for d in rets.index[rets.index >= w.index[0]]:
        if hold is not None:
            hold = hold * (1 + rets.loc[d])
        if d in w.index and d < rets.index[-1]:
            value = 1.0 if hold is None else hold.sum()
            hold = w.loc[d] * value
        values[d] = hold.sum()
    v = pd.Series(values)
    month_end = v.groupby(v.index.to_period("M")).tail(1)
    loop = (month_end / month_end.shift(1) - 1).iloc[1:]
    bt = strategy.backtest(rets, w, 0)
    np.testing.assert_allclose(bt["gross"].values, loop.values, atol=1e-12)
    np.testing.assert_allclose(bt["net"].values, bt["gross"].values, atol=1e-12)   # zero cost -> net = gross


def test_performance_formulas_by_hand():
    """Sharpe, beta, alpha and IR on a tiny hand-checkable example (monthly, log returns)."""
    import sys
    sys.path.insert(0, str(ROOT / "app"))
    import strategy

    idx = pd.date_range("2020-01-31", periods=4, freq="31D")
    port = pd.Series(np.expm1([0.02, -0.01, 0.03, 0.00]), index=idx)    # log returns 2%, -1%, 3%, 0%
    bench = pd.Series(np.expm1([0.01, -0.02, 0.02, 0.01]), index=idx)
    rf = pd.Series(0.0, index=idx)
    p = strategy.performance_table(port, bench, rf)
    r, rb = np.array([0.02, -0.01, 0.03, 0.00]), np.array([0.01, -0.02, 0.02, 0.01])
    beta = np.cov(r, rb)[0, 1] / np.var(rb, ddof=1)
    assert np.isclose(p["Beta (not annualized)"], beta)
    assert np.isclose(p["Alpha (annualized)"], 12 * (r.mean() - beta * rb.mean()))
    assert np.isclose(p["Sharpe ratio"], np.sqrt(12) * r.mean() / r.std(ddof=1))
    assert np.isclose(p["Information ratio"], np.sqrt(12) * (r - rb).mean() / (r - rb).std(ddof=1))
    assert np.isclose(p["Max drawdown"], 1 - np.exp(-0.01))           # peak after month 1, then -1% log
