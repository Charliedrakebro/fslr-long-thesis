"""Checks that the model reproduces company guidance and behaves sensibly."""
from src.model import implied_terminal_asp, load_config, project, value

CFG = load_config()


def test_2026_matches_guidance():
    y26 = project(CFG, "base")[0]
    assert 4.9 <= y26["revenue"] <= 5.2            # net sales guidance $4.9-5.2bn
    assert 2.4 <= y26["gross_profit_reported"] <= 2.6   # gross profit guidance $2.4-2.6bn
    assert 2.10 <= y26["credit_45x"] <= 2.19       # 45X guidance $2.10-2.19bn


def test_2027_eps_close_to_consensus():
    eps27 = project(CFG, "base")[1]["eps"]
    assert abs(eps27 - 24.30) / 24.30 < 0.05       # consensus FY27 EPS ~$24.30


def test_45x_ends_after_2032():
    assert CFG["credit_45x"]["phase"].get(2033, 0.0) == 0.0


def test_scenarios_ordered():
    bear, base, bull = (value(CFG, n).per_share for n in ("bear", "base", "bull"))
    assert bear < base < bull


def test_implied_asp_reproduces_price():
    from src.model import scaled_asp_path
    a = implied_terminal_asp(CFG)
    v = value(CFG, "base", scaled_asp_path(CFG, a)).per_share
    assert abs(v - CFG["market"]["share_price"]) < 0.5
