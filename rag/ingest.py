"""
Drone India Intelligence — Data Ingestion Script
=================================================
PATTERN NOTES (Task 1 findings):
  a) Gemini embedding: google.generativeai via genai.embed_content(model="models/gemini-embedding-001", content=text)
  b) PDF metadata: source (filename), category, page_number
  c) rag_bridge returns: text, score, source
  d) Pinecone index: "drone-intelligence", dimension=768
  e) This script keeps all original PDF ingestion logic untouched (lines below).
     CSV and text ingestion are added AFTER the existing code.
"""

import os
import csv
import glob
import time
import re
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Check for API Keys
pinecone_api_key = os.getenv("PINECONE_API_KEY")
gemini_api_key = os.getenv("GOOGLE_API_KEY")

if not pinecone_api_key or not gemini_api_key:
    print("Error: Please set PINECONE_API_KEY and GOOGLE_API_KEY in your .env file.")
    exit(1)

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)
index_name = "drone-intelligence"

# Check if index exists, for this script we assume the user has created it in the console
if index_name not in pc.list_indexes().names():
    print(f"Warning: Index '{index_name}' does not exist in your Pinecone account.")
    print("Please create it in the console with dimension=768 (for gemini-embedding-exp-03-07 or similar Gemini models).")
    exit(1)

# Get direct index reference for CSV/text upserts
index = pc.Index(index_name)

# Initialize Gemini Embeddings (Langchain wrapper — used by PDF ingestion)
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

# Configure google.generativeai for direct embedding calls (CSV/text ingestion)
genai.configure(api_key=gemini_api_key)

# Chunking Configuration (for PDFs)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)


# ===========================================================================
# EXISTING PDF INGESTION — DO NOT MODIFY
# ===========================================================================

def ingest_pdfs(source_dir: str):
    """
    Reads PDFs from the source directory, chunks them using the optimal configuration,
    adds required metadata, and upserts them to the Pinecone index.
    """
    pdf_files = glob.glob(os.path.join(source_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {source_dir}.")
        return

    vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    
    for pdf_path in pdf_files:
        print(f"Processing {pdf_path}...")
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Adding custom metadata before splitting
        filename = os.path.basename(pdf_path)
        
        # Simple categorization logic based on filename keywords
        category = "general"
        if "rule" in filename.lower() or "dgca" in filename.lower():
            category = "regulation"
        elif "spec" in filename.lower() or "manual" in filename.lower():
            category = "technical_spec"
            
        for doc in documents:
            doc.metadata["source"] = filename
            doc.metadata["category"] = category
            # PyPDFLoader automatically adds 'page' metadata
            if 'page' in doc.metadata:
                doc.metadata["page_number"] = doc.metadata['page'] + 1 # 1-indexed

        # Split documents into chunks
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks for {filename}.")
        
        # Upsert chunks into Pinecone
        vector_store.add_documents(chunks)
        print(f"Successfully upserted {filename} to Pinecone.")


# ===========================================================================
# HELPER: Embed text using Gemini (same model as PDF ingestion)
# ===========================================================================

def embed_text(text: str) -> list[float]:
    """
    Generate embedding using the same Gemini model used throughout the project.
    Uses: genai.embed_content(model="models/gemini-embedding-001", content=text)
    """
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
    )
    return result["embedding"]


# ===========================================================================
# CITATION METADATA BUILDERS
# ===========================================================================

def build_csv_citation(filename: str, row_index: int, row_dict: dict, category: str) -> dict:
    """Build citation metadata for a CSV row, matching PDF citation style."""
    # Try common ID fields in order
    record_id = ""
    for id_field in ["rule_id", "drone_id", "usecase_id", "company_id",
                     "institute_id", "flight_id"]:
        if id_field in row_dict and row_dict[id_field]:
            record_id = row_dict[id_field]
            break
    if not record_id:
        record_id = str(row_index)

    return {
        "source": filename,
        "source_type": "csv",
        "category": category,
        "row_index": row_index,
        "record_id": record_id,
        "citation_label": f"{filename} (row {row_index})",
    }


def build_txt_citation(filename: str, chunk_index: int, chunk_text: str) -> dict:
    """
    Build citation metadata for a text document chunk.
    Detects section headings by scanning for ALL-CAPS lines.
    """
    section_heading = "General"
    lines = chunk_text.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped) < 80 and stripped == stripped.upper() and any(c.isalpha() for c in stripped):
            section_heading = stripped.title()
            break

    return {
        "source": filename,
        "source_type": "text_document",
        "category": "document",
        "chunk_index": chunk_index,
        "section_heading": section_heading,
        "citation_label": f"{filename} (chunk {chunk_index}, section: {section_heading})",
    }


# ===========================================================================
# CSV INGESTION
# ===========================================================================

def ingest_csv(filepath, category: str, text_builder_fn):
    """
    Ingest a CSV file into Pinecone with citation metadata.
    Each row becomes one vector.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"  SKIP: {filepath} not found.")
        return

    filename = filepath.name
    print(f"\nIngesting {filename} (category: {category})...")

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)
    batch = []

    for row_index, row in enumerate(rows, start=1):
        try:
            text = text_builder_fn(row)
        except KeyError as e:
            print(f"  WARN: Missing column {e} in row {row_index}, skipping.")
            continue

        embedding = embed_text(text)
        citation = build_csv_citation(filename, row_index, row, category)
        metadata = {**citation, "text": text}
        vector_id = f"{category}_{row_index}"

        batch.append({"id": vector_id, "values": embedding, "metadata": metadata})

        if len(batch) >= 10:
            index.upsert(vectors=[(v["id"], v["values"], v["metadata"]) for v in batch])
            print(f"  Ingested rows up to {row_index}/{total}")
            batch = []
            time.sleep(1)  # Rate limit protection

    # Upsert remaining
    if batch:
        index.upsert(vectors=[(v["id"], v["values"], v["metadata"]) for v in batch])
        print(f"  Ingested rows up to {total}/{total}")

    print(f"  Done: {total} rows from {filename}")


# ===========================================================================
# TEXT DOCUMENT INGESTION
# ===========================================================================

def ingest_txt_chunks(filepath, chunk_size: int = 800, overlap: int = 100):
    """
    Ingest a text file into Pinecone using sliding window chunking.
    Tries to break at sentence boundaries (". ").
    """
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"  SKIP: {filepath} not found.")
        return

    filename = filepath.name
    stem = filepath.stem
    print(f"\nIngesting {filename}...")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = []
    start = 0
    while start < len(content):
        end = start + chunk_size
        if end < len(content):
            # Try to break at sentence boundary
            break_at = content.rfind(". ", start, end)
            if break_at > start:
                end = break_at + 2  # Include the ". "
        chunk = content[start:end].strip()
        if len(chunk) >= 50:
            chunks.append(chunk)
        start = end - overlap

    batch = []
    for i, chunk in enumerate(chunks):
        embedding = embed_text(chunk)
        citation = build_txt_citation(filename, i, chunk)
        metadata = {**citation, "text": chunk}
        vector_id = f"doc_{stem}_{i}"

        batch.append({"id": vector_id, "values": embedding, "metadata": metadata})
        print(f"  Chunk {i}: section={citation['section_heading']}, chars={len(chunk)}")

        if len(batch) >= 5:
            index.upsert(vectors=[(v["id"], v["values"], v["metadata"]) for v in batch])
            batch = []
            time.sleep(1)  # Rate limit protection

    if batch:
        index.upsert(vectors=[(v["id"], v["values"], v["metadata"]) for v in batch])

    print(f"  Done: {len(chunks)} chunks from {filename}")


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    DATA_RAW = Path(os.path.dirname(__file__)) / ".." / "data" / "raw"
    DATA_RAW = DATA_RAW.resolve()

    # Ensure directories exist
    os.makedirs(DATA_RAW, exist_ok=True)
    os.makedirs(DATA_RAW / "text_docs", exist_ok=True)

    # --- Existing PDF ingestion ---
    print("=== INGESTING PDFs ===")
    ingest_pdfs(str(DATA_RAW))

    # --- CSV ingestion ---
    print("\n=== INGESTING CSVs ===")

    ingest_csv(DATA_RAW / "drone_models.csv", "drone_specs",
        lambda r: (
            f"Drone model: {r['model_name']} by {r['manufacturer']} ({r['manufacturer_country']}). "
            f"Category: {r['category']}. Weight: {r['weight_kg']}kg. "
            f"Max payload: {r['max_payload_kg']}kg. Battery: {r['battery_mah']}mAh. "
            f"Flight time: {r['max_flight_time_min']} minutes. Range: {r['max_range_km']}km. "
            f"Price: INR {r['price_inr']} (USD {r['price_usd']}). "
            f"DGCA category: {r['dgca_category']}. Made in India: {r['made_in_india']}. "
            f"Use cases: {r['use_cases']}."
        )
    )

    ingest_csv(DATA_RAW / "regulations.csv", "regulation",
        lambda r: (
            f"DGCA Regulation: {r['rule_title']}. Category: {r['category']}. "
            f"Description: {r['description']} "
            f"Applicable to: {r['applicable_to']}. "
            f"Penalty: INR {r['penalty_inr']} - {r['penalty_description']}. "
            f"Source: {r['source']}. Effective: {r['effective_date']}."
        )
    )

    ingest_csv(DATA_RAW / "use_cases_roi.csv", "use_case_roi",
        lambda r: (
            f"Drone use case: {r['use_case_name']} in {r['sector']} sector. "
            f"{r['description']} "
            f"Recommended drone: {r['recommended_drone_category']} category. "
            f"Average drone cost: INR {r['avg_drone_cost_inr']}. "
            f"Monthly operational cost: INR {r['monthly_operational_cost_inr']}. "
            f"Monthly revenue: INR {r['monthly_revenue_inr']}. "
            f"Break-even: {r['breakeven_months']} months. "
            f"ROI year 1: {r['roi_year1_percent']}%. ROI year 3: {r['roi_year3_percent']}%. "
            f"States: {r['state_adoption']}."
        )
    )

    ingest_csv(DATA_RAW / "companies_startups.csv", "company",
        lambda r: (
            f"Indian drone company: {r['company_name']}, founded {r['founded_year']}, "
            f"in {r['headquarters']}. Type: {r['type']}. Focus: {r['focus_area']}. "
            f"Funding: INR {r['funding_raised_cr']} crore. Employees: {r['employees']}. "
            f"Key product: {r['key_product']}. Clients: {r['notable_clients']}."
        )
    )

    ingest_csv(DATA_RAW / "training_institutes.csv", "training_institute",
        lambda r: (
            f"Drone training institute: {r['institute_name']} in {r['city']}, {r['state']}. "
            f"DGCA approved: {r['dgca_approved']}. Courses: {r['courses_offered']}. "
            f"Duration: {r['duration_days']} days. Fee: INR {r['fee_inr']}. "
            f"Facilities: {r['facilities']}."
        )
    )

    ingest_csv(DATA_RAW / "synthetic_flight_data.csv", "flight_record",
        lambda r: (
            f"Flight record: {r['drone_model']} in {r['state']}, {r['district']}. "
            f"Use case: {r['use_case']}. Date: {r['date']}. "
            f"Duration: {r['flight_duration_min']} minutes. "
            f"Distance: {r['distance_covered_km']}km. "
            f"Area covered: {r['area_covered_acres']} acres. "
            f"Weather: {r['weather_condition']}. Wind: {r['wind_speed_kmh']}kmh. "
            f"Mission success: {r['mission_success']}. Incidents: {r['incidents']}."
        )
    )

    # --- Text document ingestion ---
    print("\n=== INGESTING TEXT DOCUMENTS ===")
    TEXT_DOCS = DATA_RAW / "text_docs"
    for txt_file in sorted(TEXT_DOCS.glob("*.txt")):
        ingest_txt_chunks(txt_file)

    # --- Final stats ---
    stats = index.describe_index_stats()
    print(f"\n{'='*60}")
    print(f"INGESTION COMPLETE")
    print(f"Total vectors in Pinecone: {stats.total_vector_count}")
    print(f"{'='*60}")
