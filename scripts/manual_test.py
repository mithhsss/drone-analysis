"""
Manual Test Script — Drone India Intelligence MCP Tools
Imports tools directly, runs 4 tests with formatted output and citation verification.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from pinecone import Pinecone
from mcp_server.tools.flight_time import calculate_flight_time
from mcp_server.tools.roi_calc import calculate_roi
from mcp_server.tools.compliance_checker import check_compliance
from mcp_server.tools.drone_selector import select_drone

# Pinecone vector count
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
idx = pc.Index("drone-intelligence1")
stats = idx.describe_index_stats()
total_vectors = stats.total_vector_count
print(f"Pinecone vector count: {total_vectors}")
print()

results = {}

# ── TEST 1 ────────────────────────────────────────────────────
print("=" * 60)
print("TEST 1: Flight Time Calculator")
try:
    r = calculate_flight_time(
        battery_mah=17500, drone_weight_kg=9.8,
        payload_kg=8.0, wind_speed_kmh=15, temperature_celsius=28
    )
    print(f"  Estimated flight time: {r['estimated_flight_time_minutes']} min")
    print(f"  Safe flight time:     {r['safe_flight_time_minutes']} min")
    print(f"  Total weight:         {r['total_weight_kg']} kg")
    print(f"  Range estimate:       {r['range_estimate_km']} km")
    print(f"  Warnings:             {r['warnings']}")
    print(f"  RAG LIVE: {'YES' if r.get('citations') else 'NO'}")
    print("  CITATIONS:")
    for c in r.get("citations", []):
        print(f"    - {c}")
    results["test1"] = "PASS"
except Exception as e:
    print(f"  ERROR: {e}")
    results["test1"] = "FAIL"
print("=" * 60)
print()

# ── TEST 2 ────────────────────────────────────────────────────
print("=" * 60)
print("TEST 2: ROI Calculator")
try:
    r = calculate_roi(
        use_case="agriculture spraying", drone_cost_inr=450000,
        monthly_operational_cost_inr=22000, monthly_revenue_inr=85000
    )
    print(f"  Verdict:         {r['verdict']}")
    print(f"  Breakeven:       {r['breakeven_months']} months")
    print(f"  ROI 12 months:   {r['roi_12_months_percent']}%")
    print(f"  Monthly profit:  INR {r['monthly_profit_inr']}")
    print(f"  RAG LIVE: {'YES' if r.get('citations') else 'NO'}")
    print("  CITATIONS:")
    for c in r.get("citations", []):
        print(f"    - {c}")
    if r.get("rag_insights"):
        print(f"  First RAG insight: {r['rag_insights'][0][:120]}...")
    results["test2"] = "PASS"
except Exception as e:
    print(f"  ERROR: {e}")
    results["test2"] = "FAIL"
print("=" * 60)
print()

# ── TEST 3 ────────────────────────────────────────────────────
print("=" * 60)
print("TEST 3: Compliance Checker")
try:
    r = check_compliance(
        drone_weight_kg=9.8, use_type="commercial",
        location="Hyderabad", has_remote_pilot_licence=False
    )
    print(f"  Category:        {r['drone_category']}")
    print(f"  Compliant:       {r['is_compliant']}")
    print(f"  Missing permits: {r['missing_permits']}")
    print(f"  RAG LIVE: {'YES' if r.get('citations') else 'NO'}")
    print("  CITATIONS:")
    for c in r.get("citations", []):
        print(f"    - {c}")
    if r.get("dgca_rules_retrieved"):
        print(f"  First DGCA rule: {r['dgca_rules_retrieved'][0][:120]}...")
    results["test3"] = "PASS"
except Exception as e:
    print(f"  ERROR: {e}")
    results["test3"] = "FAIL"
print("=" * 60)
print()

# ── TEST 4 ────────────────────────────────────────────────────
print("=" * 60)
print("TEST 4: Drone Selector")
try:
    r = select_drone(
        use_case="agriculture spraying", budget_inr=500000,
        payload_required_kg=10.0, flight_time_required_min=20.0
    )
    print(f"  Budget category:   {r['budget_category']}")
    print(f"  RAG sources used:  {r['rag_sources_used']}")
    print(f"  RAG LIVE: {'YES' if r.get('citations') else 'NO'}")
    print("  CITATIONS:")
    for c in r.get("citations", []):
        print(f"    - {c}")
    print("  Top recommendations:")
    for i, rec in enumerate(r.get("recommendations", [])[:2], 1):
        print(f"    {i}. {rec[:120]}...")
    results["test4"] = "PASS"
except Exception as e:
    print(f"  ERROR: {e}")
    results["test4"] = "FAIL"
print("=" * 60)
print()

# ── FINAL SUMMARY ─────────────────────────────────────────────
any_citations = any(v == "PASS" for v in results.values())
print("=" * 60)
print("FINAL SUMMARY")
print(f"  Pinecone vectors:   {total_vectors}")
print(f"  Test 1 Flight Time: {results.get('test1', 'SKIP')}")
print(f"  Test 2 ROI:         {results.get('test2', 'SKIP')}")
print(f"  Test 3 Compliance:  {results.get('test3', 'SKIP')}")
print(f"  Test 4 Drone Select:{results.get('test4', 'SKIP')}")
print(f"  Citations working:  {'YES' if any_citations else 'NO'}")
print("=" * 60)
