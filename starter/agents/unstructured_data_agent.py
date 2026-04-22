from bson import ObjectId
from pymongo import MongoClient

from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

from presidio_analyzer import AnalyzerEngine

class UnstructuredDataAgent:
    """
    MongoDB + Chroma + Azure OpenAI RAG pipeline
    """

    # ============================================
    # INIT
    # ============================================
    def __init__(
        self,
        mongo_uri: str,
        db_name: str,
        collection_name: str,
        chroma_path: str,
        azure_endpoint: str,
        azure_key: str,
        azure_api_version: str,
        embedding_deployment: str,
        chat_deployment: str,
        collection_label: str = "rag_collection",
        temperature: float = 0.0,
    ):
        # Mongo
        <TODO 1: initialize the MongoDB client and collection using the provided parameters>

        # Embeddings
        self.embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=<TODO 2: pass the azure endpoint for embeddings>,
            azure_deployment=<TODO 3: pass the deployment name for embeddings>,
            openai_api_version=azure_api_version,
            api_key=<TODO 4: pass the azure key for embeddings>,
        )

        # Vector DB
        self.vector_db = Chroma(
            collection_name=<TODO 5: pass the collection label for Chroma>,
            embedding_function=self.embeddings,
            persist_directory=chroma_path,
        )

        # Chat model
        self.llm = AzureChatOpenAI(
            <TODO 6: pass required parameters to initialize AzureChatOpenAI for the chat model>
        )

    # ============================================
    # BUILD VECTOR INDEX
    # ============================================
    def build_index(self):
        print("Loading documents from MongoDB...")

        docs = list(self.mongo_coll.find({}, {"_id": 1, "content": 1}))

        texts = []
        ids = []
        metadatas = []

        for <TODO 7: runs through all documents>
            doc_id = str(d["_id"])
            text = d.get("content", "").strip()

            if not text:
                continue

            texts.append(text)
            ids.append(doc_id)
            metadatas.append({"mongo_id": doc_id})

        if not texts:
            print("No documents found to index.")
            return

        print(f"Embedding {len(texts)} documents...")

        self.vector_db.add_texts(
            texts=texts,
            ids=ids,
            metadatas=metadatas,
        )

        print("Vector index built.")
        print("Vector DB size:", self.vector_db._collection.count())

    # ============================================
    # RAG QUERY
    # ============================================
    def ask(self, question: str, k: int = 3, run_pii_audit=True):
        results = self.vector_db.similarity_search(question, k=k)

        context_chunks = []
        source_docs = []

        for doc in results:
            mongo_id = doc.metadata.get("mongo_id")

            try:
                <TODO 8: retrieve the full document from MongoDB using the mongo_id>
            except Exception:
                mongo_doc = None

            if mongo_doc and mongo_doc.get("content"):
                <TODO 9: extract the content from the mongo_doc and append to context_chunks>

                # store full document metadata for transparency
                source_docs.append({
                    "mongo_id": str(mongo_doc["_id"]),
                    "content": content
                })

        if not context_chunks:
            return {
                "answer": "No relevant documents found.",
                "sources": []
            }

        context_text = "\n\n".join(context_chunks)

        prompt = f"""
Use the following documents as context:

{context_text}

Question: {question}

Answer clearly and concisely:
"""

        response = self.llm.invoke(prompt)

        if run_pii_audit:
            print("\n" + "=" * 80)
            print("Using Unstrucutred Data stored in MongoDB database to answer question")
            print("Seraching for PII data in source documents")
            print("=" * 80)
            self.__contains_pii(str(source_docs))

        return <TODO: return the response content>


    # ============================================
    # OPTIONAL — RESET VECTOR DB
    # ============================================
    def reset_index(self):
        print("Clearing vector database...")
        <TODO 10: clear the Chroma collection to reset the vector index>
        print("Vector DB cleared.")

    # ============================================
    # PRIVATE METHODS 
    # ============================================

    def __contains_pii(self,text: str) -> bool:
        analyzer = AnalyzerEngine()

        results = analyzer.analyze(
            text=text,
            language="en"
        )

        if results:
            seen = set()  # track unique PII
            print("\nWARNING: PII detected:")
            for r in results:
                # skip URLs
                if r.entity_type == "URL" or r.score < 0.85:
                    continue
                pii_text = text[r.start:r.end]
                if pii_text not in seen:
                    <TODO 11: add the detected PII text to the seen set to avoid duplicates>
                    print(f"- {r.entity_type}: '{pii_text}' (confidence={r.score:.2f})")
            print("\n")
            return True

        print("\n No PII detected.\n")
        return False
