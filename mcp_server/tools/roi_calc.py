"""
ROI Calculator Tool for MCP
Calculates ROI, break-even, and profitability for drone business operations in India.
"""

from mcp_server.rag_bridge import query_pinecone_filtered, format_citations, format_rag_output


def calculate_roi(
    use_case: str,
    drone_cost_inr: float,
    monthly_operational_cost_inr: float,
    monthly_revenue_inr: float,
    financing_months: int = 0,
) -> dict:
    """
    Calculates the Return on Investment (ROI), break-even timeline, and profitability for a drone use case in India. 
    Returns financial metrics including monthly profit, break-even months, and 12-to-36 month ROI percentages.
    """
    rag_insights: list[str] = []
    citations: list[str] = []
    sources: list[str] = []

    # Query RAG for use-case ROI context
    try:
        chunks = query_pinecone_filtered(
            f"drone ROI {use_case} India revenue profit case study break-even",
            category="use_case_roi", top_k=5,
        )
        rag_insights = [c["text"] for c in chunks]
        citations = format_citations(chunks)
        sources = list(set(c["source"] for c in chunks))
    except Exception:
        rag_insights = ["RAG system unavailable — using formula-only calculation."]

    # Adjust for financing
    effective_monthly_cost = monthly_operational_cost_inr
    if financing_months > 0:
        effective_monthly_cost += drone_cost_inr / financing_months

    monthly_profit = monthly_revenue_inr - effective_monthly_cost

    if monthly_profit > 0:
        breakeven_months = round(drone_cost_inr / monthly_profit, 1)
    else:
        breakeven_months = "Never"

    roi_12 = ((monthly_profit * 12 - drone_cost_inr) / drone_cost_inr) * 100
    roi_36 = ((monthly_profit * 36 - drone_cost_inr) / drone_cost_inr) * 100

    if roi_12 > 20:
        verdict = "Profitable"
    elif roi_12 >= 0:
        verdict = "Marginal"
    else:
        verdict = "Not viable"

    year_wise = []
    for year in range(1, 4):
        months = year * 12
        cum_profit = (monthly_profit * months) - drone_cost_inr
        roi_pct = (cum_profit / drone_cost_inr) * 100
        year_wise.append({
            "year": year,
            "cumulative_profit_inr": round(cum_profit, 2),
            "roi_percent": round(roi_pct, 1),
        })

    return {
        "breakeven_months": breakeven_months,
        "roi_12_months_percent": round(roi_12, 1),
        "roi_36_months_percent": round(roi_36, 1),
        "monthly_profit_inr": round(monthly_profit, 2),
        "total_investment_inr": round(drone_cost_inr, 2),
        "verdict": verdict,
        "rag_insights": rag_insights,
        "citations": citations,
        "sources": sources,
        "year_wise": year_wise,
    }
