from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

def get_clinical_ai_agent():
    # 1. Load the Knowledge Base we built in Step 2
    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(persist_directory="./data/chroma_db", embedding_function=embedding_function)
    
    # 2. Setup the Retriever (It finds relevant papers)
    retriever = db.as_retriever(search_kwargs={"k": 3}) # Get top 3 most relevant papers
    
    # 3. Setup Llama 3 (The Brain)
    llm = OllamaLLM(model="llama3")
    
    # 4. Create the Chain using LCEL (LangChain Expression Language)
    prompt = ChatPromptTemplate.from_template(
        "You are a clinical geneticist. Answer: {question}"
    )
    qa_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return qa_chain

def analyze_variant(variant_description):
    agent = get_clinical_ai_agent()
    
    prompt = f"""
    You are a clinical geneticist assistant. 
    Context: {variant_description}
    
    Task: specific clinical implications of this variant based ONLY on the provided research context.
    If the context doesn't mention it, say "No clinical evidence found in local database."
    """
    
    response = agent.invoke(prompt)
    return response