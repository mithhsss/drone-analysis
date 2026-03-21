"""
Unit tests for MCP Server tools.
Mocks rag_bridge functions so tests run without a live Pinecone connection.
"""

import pytest
from unittest.mock import patch

MOCK_RAG_RESULTS = [
    {"text": "Sample drone spec chunk for testing.", "score": 0.92, "source": "drone_models.csv",
     "source_type": "csv", "category": "drone_specs", "citation_label": "drone_models.csv (row 1)",
     "record_id": "D001", "chunk_index": "", "section_heading": "", "row_index": 1},
    {"text": "Another chunk about regulations.", "score": 0.88, "source": "regulations.csv",
     "source_type": "csv", "category": "regulation", "citation_label": "regulations.csv (row 3)",
     "record_id": "R003", "chunk_index": "", "section_heading": "", "row_index": 3},
]


@pytest.fixture(autouse=True)
def mock_rag():
    with patch("mcp_server.rag_bridge.query_pinecone", return_value=MOCK_RAG_RESULTS), \
         patch("mcp_server.rag_bridge.query_pinecone_filtered", return_value=MOCK_RAG_RESULTS), \
         patch("mcp_server.rag_bridge.format_citations", return_value=["drone_models.csv (row 1)", "regulations.csv (row 3)"]):
        yield


class TestFlightTime:
    def test_flight_time_basic(self):
        from mcp_server.tools.flight_time import calculate_flight_time
        result = calculate_flight_time(battery_mah=5000, drone_weight_kg=1.5)
        assert "estimated_flight_time_minutes" in result
        assert result["estimated_flight_time_minutes"] > 0
        assert "citations" in result

    def test_flight_time_heavy_payload(self):
        from mcp_server.tools.flight_time import calculate_flight_time
        result = calculate_flight_time(battery_mah=5000, drone_weight_kg=2.0, payload_kg=5.0)
        assert len(result["warnings"]) > 0
        assert result["total_weight_kg"] == 7.0

    def test_flight_time_high_wind(self):
        from mcp_server.tools.flight_time import calculate_flight_time
        no_wind = calculate_flight_time(battery_mah=5000, drone_weight_kg=1.5, wind_speed_kmh=0)
        high_wind = calculate_flight_time(battery_mah=5000, drone_weight_kg=1.5, wind_speed_kmh=30)
        assert high_wind["estimated_flight_time_minutes"] < no_wind["estimated_flight_time_minutes"]


class TestROI:
    def test_roi_profitable(self):
        from mcp_server.tools.roi_calc import calculate_roi
        result = calculate_roi(use_case="agriculture", drone_cost_inr=300000,
                               monthly_operational_cost_inr=15000, monthly_revenue_inr=50000)
        assert result["verdict"] == "Profitable"
        assert "citations" in result

    def test_roi_not_viable(self):
        from mcp_server.tools.roi_calc import calculate_roi
        result = calculate_roi(use_case="hobby", drone_cost_inr=500000,
                               monthly_operational_cost_inr=40000, monthly_revenue_inr=30000)
        assert result["verdict"] == "Not viable"

    def test_roi_breakeven_never(self):
        from mcp_server.tools.roi_calc import calculate_roi
        result = calculate_roi(use_case="hobby", drone_cost_inr=500000,
                               monthly_operational_cost_inr=50000, monthly_revenue_inr=50000)
        assert result["breakeven_months"] == "Never"


class TestCompliance:
    def test_compliance_nano(self):
        from mcp_server.tools.compliance_checker import check_compliance
        result = check_compliance(drone_weight_kg=0.1, use_type="recreational", location="Mumbai")
        assert result["drone_category"] == "Nano"
        assert result["is_compliant"] is True

    def test_compliance_small_no_licence(self):
        from mcp_server.tools.compliance_checker import check_compliance
        result = check_compliance(drone_weight_kg=5.0, use_type="commercial",
                                  location="Delhi", has_remote_pilot_licence=False)
        assert result["is_compliant"] is False
        assert "Remote Pilot Licence" in result["missing_permits"]


class TestDroneSelector:
    def test_drone_selector_returns_dict(self):
        from mcp_server.tools.drone_selector import select_drone
        result = select_drone(use_case="agriculture", budget_inr=200000)
        assert "search_criteria" in result
        assert "recommendations" in result
        assert "citations" in result
        assert "rag_sources_used" in result
