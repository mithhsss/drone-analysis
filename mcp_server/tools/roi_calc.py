"""
ROI Calculator Tool for MCP
Calculates ROI, break-even, and profitability for drone business operations in India.
"""

from mcp_server.rag_bridge import query_pinecone


def calculate_roi(
    use_case: str,
    drone_cost_inr: float,
    monthly_operational_cost_inr: float,
    monthly_revenue_inr: float,
    financing_months: int = 0,
) -> dict:
    """
    Calculate ROI for a drone business operation.

    Args:
        use_case: Type of drone business (e.g., "agriculture", "surveying").
        drone_cost_inr: Cost of the drone in INR.
        monthly_operational_cost_inr: Monthly operational cost in INR.
        monthly_revenue_inr: Expected monthly revenue in INR.
        financing_months: If > 0, drone cost is spread over these months.

    Returns:
        Dict with ROI calculations, verdict, year-wise breakdown, and RAG insights.
    """
    rag_insights: list[str] = []

    # Query RAG for context
    try:
        rag_results = query_pinecone(
            f"drone ROI {use_case} India revenue business case",
            top_k=5,
        )
        rag_insights = [r["text"][:200] for r in rag_results]
    except RuntimeError:
        rag_insights = ["RAG system unavailable — using formula-only calculation."]

    # Adjust operational cost if financing
    effective_monthly_cost = monthly_operational_cost_inr
    if financing_months > 0:
        effective_monthly_cost += drone_cost_inr / financing_months

    # Core calculations
    monthly_profit = monthly_revenue_inr - effective_monthly_cost

    # Breakeven
    if monthly_profit > 0:
        breakeven_months = round(drone_cost_inr / monthly_profit, 1)
    else:
        breakeven_months = "Never"

    # ROI calculations
    roi_12_months = ((monthly_profit * 12 - drone_cost_inr) / drone_cost_inr) * 100
    roi_36_months = ((monthly_profit * 36 - drone_cost_inr) / drone_cost_inr) * 100

    # Verdict
    if roi_12_months > 20:
        verdict = "Profitable"
    elif roi_12_months >= 0:
        verdict = "Marginal"
    else:
        verdict = "Not viable"

    # Year-wise breakdown
    year_wise = []
    for year in range(1, 4):
        months = year * 12
        cumulative_profit = (monthly_profit * months) - drone_cost_inr
        roi_percent = (cumulative_profit / drone_cost_inr) * 100
        year_wise.append(
            {
                "year": year,
                "cumulative_profit_inr": round(cumulative_profit, 2),
                "roi_percent": round(roi_percent, 1),
            }
        )

    return {
        "breakeven_months": breakeven_months,
        "roi_12_months_percent": round(roi_12_months, 1),
        "roi_36_months_percent": round(roi_36_months, 1),
        "monthly_profit_inr": round(monthly_profit, 2),
        "total_investment_inr": round(drone_cost_inr, 2),
        "verdict": verdict,
        "rag_insights": rag_insights,
        "year_wise": year_wise,
    }
