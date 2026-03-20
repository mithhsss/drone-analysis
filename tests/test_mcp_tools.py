"""
Unit tests for MCP Server tools.
Mocks rag_bridge.query_pinecone so tests run without a live Pinecone connection.
"""

import pytest
from unittest.mock import patch, MagicMock

# Mock RAG results fixture
MOCK_RAG_RESULTS = [
    {"text": "Sample drone specification document chunk for testing purposes with relevant context.", "score": 0.92, "source": "specs.pdf"},
    {"text": "Another chunk about drone regulations and flight time calculations.", "score": 0.88, "source": "regulations.pdf"},
]


@pytest.fixture(autouse=True)
def mock_rag():
    """Auto-mock query_pinecone for all tests."""
    with patch("mcp_server.rag_bridge.query_pinecone", return_value=MOCK_RAG_RESULTS):
        yield


# ── Flight Time Tests ─────────────────────────────────────────────────────────

class TestFlightTime:
    def test_flight_time_basic(self):
        from mcp_server.tools.flight_time import calculate_flight_time

        result = calculate_flight_time(battery_mah=5000, drone_weight_kg=1.5)

        assert "estimated_flight_time_minutes" in result
        assert "safe_flight_time_minutes" in result
        assert "total_weight_kg" in result
        assert "range_estimate_km" in result
        assert "warnings" in result
        assert "rag_context" in result
        assert result["estimated_flight_time_minutes"] > 0

    def test_flight_time_heavy_payload(self):
        from mcp_server.tools.flight_time import calculate_flight_time

        result = calculate_flight_time(
            battery_mah=5000, drone_weight_kg=2.0, payload_kg=5.0
        )

        assert len(result["warnings"]) > 0
        assert result["total_weight_kg"] == 7.0

    def test_flight_time_high_wind(self):
        from mcp_server.tools.flight_time import calculate_flight_time

        no_wind = calculate_flight_time(battery_mah=5000, drone_weight_kg=1.5, wind_speed_kmh=0)
        high_wind = calculate_flight_time(battery_mah=5000, drone_weight_kg=1.5, wind_speed_kmh=30)

        assert high_wind["estimated_flight_time_minutes"] < no_wind["estimated_flight_time_minutes"]
        assert "High wind reduces flight time" in high_wind["warnings"]


# ── ROI Tests ─────────────────────────────────────────────────────────────────

class TestROI:
    def test_roi_profitable(self):
        from mcp_server.tools.roi_calc import calculate_roi

        result = calculate_roi(
            use_case="agriculture",
            drone_cost_inr=300000,
            monthly_operational_cost_inr=15000,
            monthly_revenue_inr=50000,
        )

        assert result["verdict"] == "Profitable"
        assert result["monthly_profit_inr"] > 0
        assert result["roi_12_months_percent"] > 20
        assert len(result["year_wise"]) == 3

    def test_roi_not_viable(self):
        from mcp_server.tools.roi_calc import calculate_roi

        result = calculate_roi(
            use_case="hobby",
            drone_cost_inr=500000,
            monthly_operational_cost_inr=40000,
            monthly_revenue_inr=30000,
        )

        assert result["verdict"] == "Not viable"
        assert result["roi_12_months_percent"] < 0

    def test_roi_breakeven_never(self):
        from mcp_server.tools.roi_calc import calculate_roi

        result = calculate_roi(
            use_case="hobby",
            drone_cost_inr=500000,
            monthly_operational_cost_inr=50000,
            monthly_revenue_inr=50000,
        )

        assert result["breakeven_months"] == "Never"


# ── Compliance Tests ──────────────────────────────────────────────────────────

class TestCompliance:
    def test_compliance_nano(self):
        from mcp_server.tools.compliance_checker import check_compliance

        result = check_compliance(
            drone_weight_kg=0.1,
            use_type="recreational",
            location="Mumbai",
        )

        assert result["drone_category"] == "Nano"
        assert result["is_compliant"] is True
        assert len(result["missing_permits"]) == 0

    def test_compliance_small_no_licence(self):
        from mcp_server.tools.compliance_checker import check_compliance

        result = check_compliance(
            drone_weight_kg=5.0,
            use_type="commercial",
            location="Delhi",
            has_remote_pilot_licence=False,
        )

        assert result["drone_category"] == "Small"
        assert result["is_compliant"] is False
        assert "Remote Pilot Licence" in result["missing_permits"]


# ── Drone Selector Tests ─────────────────────────────────────────────────────

class TestDroneSelector:
    def test_drone_selector_returns_dict(self):
        from mcp_server.tools.drone_selector import select_drone

        result = select_drone(use_case="agriculture", budget_inr=200000)

        assert "search_criteria" in result
        assert "recommendations" in result
        assert "budget_category" in result
        assert "key_considerations" in result
        assert "rag_sources_used" in result
        assert isinstance(result["recommendations"], list)
