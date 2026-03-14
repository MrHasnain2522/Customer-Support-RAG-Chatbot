# rebuild_faiss.py
import sys
import os
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

# ── Step 1: Delete old FAISS index ───────────
import shutil
if os.path.exists("vector_stores/faiss"):
    shutil.rmtree("vector_stores/faiss")
    print("✅ Old FAISS index deleted")

os.makedirs("vector_stores/faiss", exist_ok=True)

# ── Step 2: Import correct class ─────────────
from app import create_app
from app.rag.faiss_store  import FAISSVectorStore   # ✅ correct class name
from app.rag.embeddings   import EmbeddingService
from app.rag.document_loader import DocumentLoader

app = create_app()

with app.app_context():
    # ── Step 3: Load documents ────────────────
    print("📂 Loading documents from knowledge_base/...")
    loader    = DocumentLoader()
    documents = loader.load_all()
    print(f"📄 Loaded {len(documents)} documents")

    # ── Step 4: Generate OpenAI embeddings ────
    print("🔄 Generating OpenAI embeddings...")
    embedder   = EmbeddingService()
    dimension  = embedder.get_dimension()
    print(f"📐 Dimension: {dimension}")

    texts      = [doc["content"] for doc in documents]
    embeddings = embedder.encode(texts)
    print(f"✅ Embeddings shape: {embeddings.shape}")

    # ── Step 5: Save new FAISS index ──────────
    print("💾 Saving new FAISS index...")
    store = FAISSVectorStore(dimension=dimension)
    store.add_documents(documents, embeddings)
    store.save("vector_stores/faiss")

    print("🚀 FAISS rebuilt successfully!")
    print(f"📐 Dimension  : {dimension}")
    print(f"📄 Documents  : {len(documents)}")