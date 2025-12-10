import os
from Bio import Entrez
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 1. Setup Email for NCBI (Required by BioPython)
Entrez.email = "your.email@example.com"  # Replace with your email

def fetch_pubmed_abstracts(gene_list):
    """Fetches recent abstracts for specific genes to build our Knowledge Base."""
    print(f"🔬 Fetching research for genes: {gene_list}...")
    documents = []
    
    for gene in gene_list:
        # Search for recent papers (last 2 years) on this gene + "mutation"
        term = f"{gene}[Title/Abstract] AND (mutation[Title/Abstract] OR variant[Title/Abstract])"
        handle = Entrez.esearch(db="pubmed", term=term, retmax=10, sort="relevance")
        record = Entrez.read(handle)
        id_list = record["IdList"]
        
        if not id_list:
            continue
        
        # Fetch details
        handle = Entrez.efetch(db="pubmed", id=",".join(id_list), retmode="xml")
        papers = Entrez.read(handle)
        
        for paper in papers['PubmedArticle']:
            try:
                title = paper['MedlineCitation']['Article']['ArticleTitle']
                abstract_list = paper['MedlineCitation']['Article']['Abstract']['AbstractText']
                abstract = " ".join(abstract_list)
                
                # Create a Document object for RAG
                doc_content = f"Gene: {gene}\nTitle: {title}\nAbstract: {abstract}"
                documents.append(Document(page_content=doc_content, metadata={"source": "PubMed", "gene": gene}))
            except KeyError:
                continue # Skip papers with no abstract
                
    print(f"✅ Downloaded {len(documents)} medical abstracts.")
    return documents

def build_vector_db():
    # A. Fetch Data
    genes_of_interest = ["BRCA1", "TP53", "EGFR", "KRAS"]
    raw_docs = fetch_pubmed_abstracts(genes_of_interest)
    
    # B. Split Text (Chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(raw_docs)
    
    # C. Embed & Store (Using Free Local Embeddings)
    print("🧠 Embedding data into ChromaDB (Local Vector Store)...")
    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Persist to disk so we don't have to rebuild every time
    db = Chroma.from_documents(docs, embedding_function, persist_directory="./data/chroma_db")
    print("🎉 Knowledge Base Built! Saved to ./data/chroma_db")

if __name__ == "__main__":
    build_vector_db()