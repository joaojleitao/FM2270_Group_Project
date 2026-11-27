"""The notebook's inline functions must match app/strategy.py.

1. Same set of function names, and identical code (compared as parsed syntax trees, so
   comments and formatting don't matter but any logic change does).
2. Identical numerical results on the same synthetic inputs (skipped while the functions are still stubs).
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
    assert set(notebook_functions()) == set(module_functions())


@pytest.mark.parametrize("name", sorted(module_functions()))
def test_identical_code(name):
    nb = notebook_functions()[name]
    assert ast.dump(nb) == ast.dump(module_functions()[name]), f"{name} differs between notebook and app/strategy.py"


def load_notebook_namespace():
    """Execute the notebook's function definitions (only) into a fresh namespace."""
    ns = {"np": np, "pd": pd}
    mod = ast.Module(body=list(notebook_functions().values()), type_ignores=[])
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
    try:
        w_mod = strategy.inverse_vol_weights(rets, month_ends, 252)
    except NotImplementedError:
        pytest.skip("strategy functions are still stubs (pending group approval)")
    w_nb = nb["inverse_vol_weights"](rets, month_ends, 252)
    pd.testing.assert_frame_equal(w_mod, w_nb)

    bt_mod = strategy.backtest(rets, w_mod, 10)
    bt_nb = nb["backtest"](rets, w_nb, 10)
    pd.testing.assert_frame_equal(bt_mod, bt_nb)

    rf = pd.Series(0.001, index=bt_mod.index)
    bench = bt_mod["gross"] * 0.5
    pd.testing.assert_frame_equal(pd.DataFrame(strategy.performance_table(bt_mod["net"], bench, rf)),
                                  pd.DataFrame(nb["performance_table"](bt_nb["net"], bench, rf)))
