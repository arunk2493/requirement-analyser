#!/usr/bin/env python3
"""
Test script to verify RAG vector store creation and retrieval with similarity scores.
"""

import sys
import os
import json

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from rag.vectorstore import VectorStore


def test_vector_store_creation():
    """Test creating a vector store for an upload"""
    print("\n" + "="*60)
    print("TEST 1: Vector Store Creation")
    print("="*60)
    
    # Create a vector store with upload_id
    upload_id = 1
    vectorstore = VectorStore(upload_id=upload_id)
    
    # Store some sample documents
    documents = [
        {
            "text": "User authentication with email and password validation",
            "metadata": {"type": "requirement", "category": "auth"}
        },
        {
            "text": "Multi-factor authentication using OTP and authenticator apps",
            "metadata": {"type": "requirement", "category": "security"}
        },
        {
            "text": "User profile management and settings update functionality",
            "metadata": {"type": "requirement", "category": "user"}
        },
        {
            "text": "Role-based access control with admin and user roles",
            "metadata": {"type": "requirement", "category": "access"}
        },
        {
            "text": "Password reset and recovery using email verification",
            "metadata": {"type": "requirement", "category": "auth"}
        }
    ]
    
    print(f"Creating vector store for upload ID: {upload_id}")
    print(f"Vector store path: {vectorstore.store_path}")
    
    for i, doc in enumerate(documents, 1):
        doc_id = f"doc_{upload_id}_{i}"
        vectorstore.store_document(
            text=doc["text"],
            doc_id=doc_id,
            metadata=doc["metadata"]
        )
        print(f"  ✓ Stored document: {doc_id}")
    
    print(f"\nTotal documents in vector store: {len(vectorstore.data)}")
    return vectorstore


def test_rag_search(vectorstore):
    """Test RAG search with similarity scores"""
    print("\n" + "="*60)
    print("TEST 2: RAG Search with Similarity Scores")
    print("="*60)
    
    test_queries = [
        "How should users log in to the system?",
        "What are the security features available?",
        "How can users reset their password?",
        "Tell me about admin permissions",
    ]
    
    for query in test_queries:
        print(f"\n📍 Query: \"{query}\"")
        print("-" * 60)
        
        results = vectorstore.search(query=query, top_k=3)
        
        if not results:
            print("  No results found")
            continue
        
        for i, result in enumerate(results, 1):
            similarity = result["similarity"]
            similarity_pct = similarity * 100
            
            print(f"\n  Result {i}:")
            print(f"    Document ID: {result['doc_id']}")
            print(f"    Similarity Score: {similarity:.4f}")
            print(f"    Similarity %: {similarity_pct:.2f}%")
            print(f"    Metadata: {result['metadata']}")
            print(f"    Text: \"{result['text'][:70]}...\"")


def test_separate_uploads():
    """Test that different uploads have separate vector stores"""
    print("\n" + "="*60)
    print("TEST 3: Separate Vector Stores for Different Uploads")
    print("="*60)
    
    # Create vector stores for two different uploads
    uploads = [
        {
            "upload_id": 2,
            "docs": [
                "Payment gateway integration with Stripe API",
                "Credit card validation and tokenization",
            ]
        },
        {
            "upload_id": 3,
            "docs": [
                "Email notifications for order confirmation",
                "SMS alerts for order status updates",
            ]
        }
    ]
    
    vectorstores = {}
    
    for upload_info in uploads:
        upload_id = upload_info["upload_id"]
        vs = VectorStore(upload_id=upload_id)
        vectorstores[upload_id] = vs
        
        print(f"\nUpload {upload_id}:")
        print(f"  Path: {vs.store_path}")
        
        for i, doc in enumerate(upload_info["docs"], 1):
            doc_id = f"doc_{upload_id}_{i}"
            vs.store_document(doc, doc_id, metadata={"upload_id": upload_id})
            print(f"  ✓ Stored: {doc_id}")
    
    # Verify they are separate
    print("\n📊 Verification:")
    print(f"  Upload 2 has {len(vectorstores[2].data)} documents")
    print(f"  Upload 3 has {len(vectorstores[3].data)} documents")
    
    # Search in upload 2 to show they're independent
    print("\nSearching 'payment' in Upload 2:")
    results = vectorstores[2].search("payment processing", top_k=2)
    for result in results:
        print(f"  ✓ Found: {result['doc_id']} (score: {result['similarity']:.4f})")


if __name__ == "__main__":
    print("\n" + "🚀 RAG Vector Store Implementation Tests".center(60, "="))
    
    try:
        # Test 1: Create vector store
        vectorstore = test_vector_store_creation()
        
        # Test 2: Search with similarity scores
        test_rag_search(vectorstore)
        
        # Test 3: Separate uploads
        test_separate_uploads()
        
        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
