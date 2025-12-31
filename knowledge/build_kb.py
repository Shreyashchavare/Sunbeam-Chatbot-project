import hashlib
from loaders.sunbeam_unified_loader import SunbeamUnifiedLazyLoader
from knowledge.vectorstore import get_vectorstore

def doc_id(doc):
    return hashlib.md5(
        (doc.page_content + str(doc.metadata)).encode()
    ).hexdigest()

def build_kb():
    loader = SunbeamUnifiedLazyLoader()
    db = get_vectorstore()

    docs = list(loader.lazy_load())
    ids = [doc_id(d) for d in docs]

    db.add_documents(docs, ids=ids)
    db.persist()

    print(f"✅ KB built with {len(docs)} documents")

if __name__ == "__main__":
    build_kb()