#!/usr/bin/env python3
"""Fixtures: prove every figure on the card is data-bound, not hand-typed."""
import json
import os
import tempfile

import build

WALLET = build.WALLET


def make_vitals(base, eth, iso):
    return {"wallet_address": WALLET.lower(), "usdc_base": base,
            "usdc_ethereum": eth, "iso_utc": iso}


def build_from(v, outdir):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(v, f)
        path = f.name
    try:
        return build.build(path, outdir)
    finally:
        os.unlink(path)


def test_figures_are_data_bound():
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        h1 = build_from(make_vitals(8.870923, 5.571513, "2026-11-18T03:58:33Z"), a)
        h2 = build_from(make_vitals(1.234567, 9.876543, "2026-01-02T00:00:00Z"), b)
        for needle in ("8.870923", "5.571513", "2026-11-18T03:58:33Z"):
            assert needle in h1, "missing from first build: " + needle
        for needle in ("1.234567", "9.876543", "2026-01-02T00:00:00Z"):
            assert needle in h2, "missing from second build: " + needle
        assert "8.870923" not in h2 and "1.234567" not in h1, "figures not rebound"
        print("PASS figures rebind to vitals (baseline Base/ETH + timestamp)")


def test_wallet_and_contracts():
    with tempfile.TemporaryDirectory() as d:
        h = build_from(make_vitals(1.0, 2.0, "t"), d)
        assert WALLET in h
        assert build.USDC["base"].lower() in h.lower()
        assert build.USDC["ethereum"].lower() in h.lower()
        assert "0x6639" in h and "8FFd" in h, "short-form confirm hint missing"
        print("PASS wallet + both USDC contracts + short confirm hint present")


def test_qr_present_and_changes_with_address():
    s1 = build.qr_svg("0xAAA")
    s2 = build.qr_svg("0xBBB")
    assert s1.startswith("<svg") and s1.endswith("</svg>")
    assert s1.count("<rect") > 20, "QR looks empty"
    assert s1 != s2, "QR did not change with input"
    with tempfile.TemporaryDirectory() as d:
        h = build_from(make_vitals(1.0, 2.0, "t"), d)
        assert '<div class="qrcode"><svg' in h, "QR not embedded in page"
        assert os.path.getsize(os.path.join(d, "address.svg")) > 200
        print("PASS QR embedded, non-trivial, changes with address")


def test_honesty_and_no_leftover_placeholders():
    with tempfile.TemporaryDirectory() as d:
        h = build_from(make_vitals(1.0, 2.0, "t"), d)
        for needle in ("autonomous AI agent, not a human", "not x402",
                       "legible offer, unproven demand", "does not"):
            assert needle in h, "honesty marker missing: " + needle
        assert "__" not in h, "unreplaced placeholder remains"
        print("PASS non-human disclosure + not-x402 + unproven-demand label; no placeholders")


def test_meta_matches_vitals():
    with tempfile.TemporaryDirectory() as d:
        build_from(make_vitals(3.5, 4.5, "ts"), d)
        meta = json.load(open(os.path.join(d, "meta.json")))
        assert meta["baseline"] == {"base": 3.5, "ethereum": 4.5}
        assert meta["wallet"].lower() == WALLET.lower()
        print("PASS meta.json baseline mirrors the input snapshot")


if __name__ == "__main__":
    test_figures_are_data_bound()
    test_wallet_and_contracts()
    test_qr_present_and_changes_with_address()
    test_honesty_and_no_leftover_placeholders()
    test_meta_matches_vitals()
    print("ALL 5 FIXTURES PASS")
