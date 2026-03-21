"""
Live integration tests — require running Pinecone connection.
Run with: pytest tests/test_live_rag.py -v -m integration
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from mcp_server.rag_bridge import query_pinecone, query_pinecone_filtered, format_citations
from mcp_server.tools.compliance_checker import check_compliance

pytestmark = pytest.mark.integration


def test_pinecone_connection():
    chunks = query_pinecone("drone India agriculture")
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert "text" in chunks[0]
    assert "citation_label" in chunks[0]
    assert "source" in chunks[0]


def test_citation_label_present():
    chunks = query_pinecone("DGCA regulations pilot licence")
    for chunk in chunks:
        assert chunk["citation_label"] != ""
        assert chunk["source"] != "unknown"


def test_csv_data_retrieved():
    chunks = query_pinecone_filtered("agriculture drone spraying ROI profit", "use_case_roi")
    assert len(chunks) > 0
    assert any("use_cases_roi" in c["source"] for c in chunks)


def test_regulation_citations():
    chunks = query_pinecone_filtered("DGCA drone weight registration licence", "regulation")
    assert len(chunks) > 0
    citations = format_citations(chunks)
    assert any("regulations.csv" in c for c in citations)
    assert any("row" in c for c in citations)


def test_text_doc_section_heading():
    chunks = query_pinecone_filtered("airspace zones green yellow red", "document")
    if len(chunks) > 0:
        assert "section_heading" in chunks[0]


def test_compliance_tool_live_with_citations():
    result = check_compliance(15.0, "commercial", "Delhi", False)
    assert result["drone_category"] == "Small"
    assert len(result["citations"]) > 0
    assert any("regulations.csv" in c for c in result["citations"])
