import faiss
import numpy as np

from pypdf import PdfReader

from models.embeddings import create_embedding


# --------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------

def extract_text_from_pdf(uploaded_file):
    """
    Extract text from an uploaded PDF file.
    """

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# --------------------------------------------------
# TEXT CHUNKING
# --------------------------------------------------

def split_text(text, chunk_size=500, overlap=100):
    """
    Split text into smaller overlapping chunks.
    """

    if not text:
        return []

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# --------------------------------------------------
# CREATE VECTOR STORE
# --------------------------------------------------

def create_vector_store(chunks):
    """
    Create a FAISS vector store from text chunks.
    """

    if not chunks:
        raise ValueError(
            "No text chunks were available to create the vector store."
        )

    embeddings = []

    for chunk in chunks:

        if not chunk or not isinstance(chunk, str):
            continue

        embedding = create_embedding(chunk)

        if embedding is None:
            raise ValueError(
                "Embedding generation returned None for a document chunk."
            )

        embeddings.append(embedding)

    if not embeddings:
        raise ValueError(
            "No valid embeddings were generated from the document."
        )

    embeddings = np.array(
        embeddings,
        dtype="float32"
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index, chunks


# --------------------------------------------------
# SEARCH VECTOR STORE
# --------------------------------------------------

def search_vector_store(
    query,
    index,
    chunks,
    top_k=3
):
    """
    Find the most relevant chunks for a query.
    """

    # Prevent invalid values from reaching the Gemini embedding API.
    if query is None:
        raise ValueError(
            "RAG query is None. A valid user question is required."
        )

    if not isinstance(query, str):
        query = str(query)

    query = query.strip()

    if not query:
        raise ValueError(
            "RAG query is empty. A valid user question is required."
        )

    if index is None:
        raise ValueError(
            "FAISS vector index is not available."
        )

    if not chunks:
        raise ValueError(
            "No document chunks are available for RAG search."
        )

    query_embedding = create_embedding(query)

    if query_embedding is None:
        raise ValueError(
            "Embedding generation returned None for the user query."
        )

    query_embedding = np.array(
        [query_embedding],
        dtype="float32"
    )

    distances, indices = index.search(
        query_embedding,
        min(top_k, len(chunks))
    )

    results = []

    for index_number in indices[0]:

        if index_number != -1:

            results.append(
                chunks[index_number]
            )

    return results


# --------------------------------------------------
# RAG ANSWER
# --------------------------------------------------

def generate_rag_answer(
    query,
    index,
    chunks,
    generate_response
):
    """
    Generate an answer using retrieved PDF chunks.
    """

    # Validate the query before doing any embedding work.
    if query is None:
        raise ValueError(
            "RAG received an empty user query."
        )

    if not isinstance(query, str):
        query = str(query)

    query = query.strip()

    if not query:
        raise ValueError(
            "RAG received an empty user query."
        )

    relevant_chunks = search_vector_store(
        query,
        index,
        chunks
    )

    context = "\n\n".join(
        relevant_chunks
    )

    prompt = f"""
You are an AI assistant for a salon.

Answer the user's question using ONLY
the information provided in the context below.

If the answer cannot be found in the context,
say that the information is not available
in the uploaded document.

Do not invent information.

CONTEXT:
{context}

USER QUESTION:
{query}

ANSWER:
"""

    answer = generate_response(prompt)

    return answer
