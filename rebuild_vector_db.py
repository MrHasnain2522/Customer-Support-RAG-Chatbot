"""
Rebuild FAISS Vector Database - Fixed for FAISSVectorStore
"""
import os
import sys

def rebuild_faiss():
    """Rebuild FAISS from knowledge base"""
    
    print("🔄 Rebuilding FAISS Vector Database...")
    print("=" * 60)
    
    # Step 1: Check knowledge base
    kb_path = "knowledge_base/documents"
    if not os.path.exists(kb_path):
        os.makedirs(kb_path, exist_ok=True)
        print(f"❌ Error: {kb_path} was missing (now created). Add files there!")
        return False
    
    files = [f for f in os.listdir(kb_path) if f.endswith(('.pdf', '.txt', '.md'))]
    if not files:
        print(f"❌ Error: No documents in {kb_path}")
        return False
    
    print(f"✓ Found {len(files)} documents:")
    for f in files:
        print(f"  - {f}")
    
    # Step 2: Import modules
    try:
        from app.rag.document_loader import DocumentLoader
        from app.rag.embeddings import EmbeddingService
        from app.rag.faiss_store import FAISSVectorStore
        print("\n✓ Modules imported successfully")
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    
    # Step 3: Load and Chunk documents
    try:
        print("\n📄 Loading and chunking documents...")
        loader = DocumentLoader()
        # Ensure we use load_and_chunk_documents to match your current system
        documents = loader.load_and_chunk_documents(chunk_size=500, chunk_overlap=50)
        print(f"✓ Created {len(documents)} text chunks")
        
        if not documents:
            print("❌ No content extracted!")
            return False
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return False
    
    # Step 4: Generate embeddings
    try:
        print("\n🧮 Generating embeddings...")
        embedder = EmbeddingService()
        
        # FIX: Your system uses 'text', not 'content'
        texts = [doc['text'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        
        # FIX: Your EmbeddingService uses .encode()
        embeddings = embedder.encode(texts)
        
        print(f"✓ Generated {len(embeddings)} embeddings")
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        return False
    
    # Step 5: Build FAISS index
    try:
        print("\n🔨 Building FAISS index...")
        store = FAISSVectorStore()
        # FIX: Passing data to match FAISSVectorStore.add_documents(embeddings, texts, metadatas)
        store.add_documents(embeddings, texts, metadatas)
        
        # Save index
        store.save() # Uses default path defined in your FAISSVectorStore
        
        print(f"✓ FAISS index built and saved successfully")
    except Exception as e:
        print(f"❌ Error building index: {e}")
        return False
    
    # Step 6: Verify
    try:
        print("\n🧪 Verifying index...")
        test_query = "suits"
        test_embedding = embedder.encode(test_query)
        results = store.search(test_embedding, k=1)
        
        if results:
            print(f"✓ Verification successful!")
            print(f"📋 Sample Result: {results[0]['text'][:80]}...")
    except Exception as e:
        print(f"⚠️ Verification warning: {e}")
    
    print("\n" + "=" * 60)
    print("✅ FAISS Vector Database Rebuilt Successfully!")
    return True

if __name__ == '__main__':
    success = rebuild_faiss()
    sys.exit(0 if success else 1)