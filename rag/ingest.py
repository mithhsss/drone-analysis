import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

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


# Initialize Gemini Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

# Chunking Configuration
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

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

if __name__ == "__main__":
    raw_data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    # Ensure raw directory exists
    os.makedirs(raw_data_dir, exist_ok=True)
    
    print(f"Looking for PDFs in {raw_data_dir}...")
    ingest_pdfs(raw_data_dir)
    print("Ingestion complete.")
