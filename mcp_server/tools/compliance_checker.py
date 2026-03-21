"""
Compliance Checker Tool for MCP
Checks Indian DGCA regulatory compliance for drone operations.
"""

from mcp_server.rag_bridge import query_pinecone_filtered, format_citations, format_rag_output

# DGCA weight classification — fixed Indian law
WEIGHT_CATEGORIES = [
    {"max_kg": 0.25, "category": "Nano", "registration": False, "licence": False},
    {"max_kg": 2.0, "category": "Micro", "registration": True, "licence": False},
    {"max_kg": 25.0, "category": "Small", "registration": True, "licence": True},
    {"max_kg": 150.0, "category": "Medium", "registration": True, "licence": True},
]


def _classify_drone(weight_kg: float) -> dict:
    for cat in WEIGHT_CATEGORIES:
        if weight_kg <= cat["max_kg"]:
            return cat
    return {"max_kg": float("inf"), "category": "Large", "registration": True, "licence": True}


def check_compliance(
    drone_weight_kg: float,
    use_type: str,
    location: str,
    has_remote_pilot_licence: bool = False,
) -> dict:
    """
    Checks if a drone operation complies with Indian DGCA regulations based on drone weight, use type (e.g. 'commercial' or 'recreational'), location, and license status.
    Returns compliance status, required permits, and restrictions.
    """
    dgca_rules: list[str] = []
    citations: list[str] = []

    # Query RAG for regulation context
    try:
        chunks = query_pinecone_filtered(
            f"DGCA regulations drone {drone_weight_kg}kg {use_type} permit licence {location}",
            category="regulation", top_k=5,
        )
        dgca_rules = [c["text"] for c in chunks]
        citations = format_citations(chunks)
    except Exception:
        dgca_rules = ["RAG system unavailable — using hardcoded DGCA rules only."]

    classification = _classify_drone(drone_weight_kg)
    category = classification["category"]
    needs_registration = classification["registration"]
    needs_licence = classification["licence"]

    is_commercial = use_type.lower() in ("commercial", "business", "enterprise", "professional")
    if is_commercial:
        needs_licence = True

    required_permits: list[str] = []
    if needs_registration:
        required_permits.append("DGCA Registration (UIN)")
    if needs_licence:
        required_permits.append("Remote Pilot Licence")
    if category in ("Medium", "Large"):
        required_permits.append("Type Certificate")
        required_permits.append("Special Flight Approval")
    if is_commercial:
        required_permits.append("Commercial Operating Permit")

    missing_permits: list[str] = []
    if needs_licence and not has_remote_pilot_licence:
        missing_permits.append("Remote Pilot Licence")

    restrictions: list[str] = [
        "Maximum altitude: 400 feet AGL",
        "No flight within 5 km of airports without ATC permission",
        "No flight over public gatherings or crowds",
    ]
    if category in ("Medium", "Large"):
        restrictions.append("Restricted to designated airspace corridors only")
    if not has_remote_pilot_licence and needs_licence:
        restrictions.append("Cannot operate until Remote Pilot Licence is obtained")

    is_compliant = len(missing_permits) == 0

    if is_compliant:
        recommendation = (
            f"Your {category}-category drone is compliant for {use_type} use at {location}. "
            "Ensure you carry all permits during flight operations."
        )
    else:
        recommendation = (
            f"Your {category}-category drone is NOT compliant. "
            f"You are missing: {', '.join(missing_permits)}. "
            "Apply through the DigitalSky portal before operating."
        )

    return {
        "drone_category": category,
        "is_compliant": is_compliant,
        "required_permits": required_permits,
        "missing_permits": missing_permits,
        "restrictions": restrictions,
        "dgca_rules_retrieved": dgca_rules,
        "citations": citations,
        "recommendation": recommendation,
    }
