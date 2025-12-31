import sys
import os
import hashlib

# SQLite Fix for Windows
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

# --------------------------------------------------
# Ensure project root is on PYTHONPATH
# --------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from loaders.sunbeam_unified_loader import SunbeamUnifiedLazyLoader
from knowledge.vectorstore import get_vectorstore

# --------------------------------------------------
# Stable document ID generator
# --------------------------------------------------
def doc_id(doc):
    return hashlib.md5(
        (doc.page_content + str(doc.metadata)).encode()
    ).hexdigest()

# --------------------------------------------------
# Build Knowledge Base
# --------------------------------------------------
def build_kb():
    loader = SunbeamUnifiedLazyLoader()
    db = get_vectorstore()

    # lazy_load() already returns a generator of Document
    docs = list(loader.lazy_load())
    ids = [doc_id(d) for d in docs]

    if docs:
        print(f"🧹 Clearing existing data...")
        try:
            db.delete(where={"source": "sunbeam"})
        except Exception:
            pass # Collection might be empty or filter valid only if data exists

        print(f"📥 Indexing {len(docs)} documents...")
        db.add_documents(docs, ids=ids)
        print(f"✅ KB built with {len(docs)} documents")

# --------------------------------------------------
if __name__ == "__main__":
    build_kb()
