import time
import hashlib
from loaders.sunbeam_unified_loader import SunbeamUnifiedLazyLoader
from knowledge.vectorstore import get_vectorstore

ONE_WEEK = 60 * 60 * 24 * 7

def doc_id(doc):
    return hashlib.md5(
        (doc.page_content + str(doc.metadata)).encode()
    ).hexdigest()

def auto_update():
    while True:
        print("🔄 Refreshing KB...")

        db = get_vectorstore()
        db.delete(where={"source": "sunbeam"})

        loader = SunbeamUnifiedLazyLoader()
        docs = list(loader.lazy_load())
        ids = [doc_id(d) for d in docs]

        db.add_documents(docs, ids=ids)
        db.persist()

        print("✅ KB refreshed cleanly")
        time.sleep(ONE_WEEK)

if __name__ == "__main__":
    auto_update()