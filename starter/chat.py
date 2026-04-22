import warnings
warnings.filterwarnings("ignore", message="Field.*conflict with protected namespace")

from azure.keyvault.secrets import <TODO 1: use SecretClient library to connect to Azure Key Vault>
from azure.identity import DeviceCodeCredential

from agents.structured_data_agent import <TODO 2: use Structured Data Agent>
from agents.unstructured_data_agent import <TODO 3: use Unstructured Data Agent>
from agents.multimodal_data_agent import <TODO 4: use Multimodal DataA gent>

# ============================================================
#  Secrets
# ============================================================

keyVaultName = <TODO 5: name of your key vault deployed in Azure>
KVUri = <TODO 6: uri of the key vault you deployed in Azure>

print("Connecting to Azure for authentication.")

credential = <TODO 7: use Interactive Browser Credential Azure authentication> 
client = SecretClient(vault_url=KVUri, credential=credential)

# ============================================================
# Structured Data Agent Secrets
# ============================================================

<TODO 8: define all your secrets stored in the Azure key vault for each of the resources>

structuredazureendpoint = retrieved_secret = client.get_secret("XXXXXX").value
structuredazureapikey = retrieved_secret = client.get_secret("XXXXXX").value
structuredpostgresqlpassword = retrieved_secret = client.get_secret("XXXXXX").value
structuredpostgresqluser = retrieved_secret = client.get_secret("XXXXXX").value
structuredpostgresqldbname = retrieved_secret = client.get_secret("XXXXXX").value
structuredpostgresqlhost = retrieved_secret = client.get_secret("XXXXXX").value

unstructuredmongourl = retrieved_secret = client.get_secret("XXXXXX").value
unstructureddbname = retrieved_secret = client.get_secret("XXXXXX").value
unstructuredcollectionname = retrieved_secret = client.get_secret("XXXXXX").value
unstructuredazureendpoint = retrieved_secret = client.get_secret("XXXXXX").value
unstructuredazurekey = retrieved_secret = client.get_secret("XXXXXX").value

multimodalazureconnstring = retrieved_secret = client.get_secret("mXXXXXX").value
multimodalazurecontentsafetyendpoint = retrieved_secret = client.get_secret("XXXXXX").value
multimodalazurecontentsafetykey = retrieved_secret = client.get_secret("XXXXXX").value

# ============================================================
#  Chat Manager
# ============================================================

class AgentChatManager:
    def __init__(self):
        self.<TODO 9: load _load_agents()>

    # -------------------------
    #  Agents
    # -------------------------
    def <TODO 10: define the _load_agents method to initialize each of the agents with the appropriate secrets and parameters>

        print("\nLoading Structured Data Agent")
        print("-------------------------------")
        self.structured = <TODO 11: initialize the structured data agent with the appropriate parameters, including the database connection parameters and Azure LLM parameters>
            azure_endpoint=structuredazureendpoint,
            api_key=structuredazureapikey,
            deployment="gpt-4.1-mini",
            db_config={
                "host": structuredpostgresqlhost,
                "dbname": structuredpostgresqldbname,
                "user": structuredpostgresqluser,
                "password": structuredpostgresqlpassword,
                "port": 5432,
            }
        )

        print("\nLoading Unstructured Data Agent")
        print("---------------------------------")
        self.unstructured = <TODO 12: initialize the unstructured data agent with the appropriate parameters, including MongoDB connection parameters, Azure LLM parameters, and ChromaDB local storage path>
            mongo_uri=unstructuredmongourl,
            db_name=unstructureddbname,
            collection_name=unstructuredcollectionname,
            chroma_path="./data/chroma_db_storage",
            azure_endpoint=unstructuredazureendpoint,
            azure_key=unstructuredazurekey,
            azure_api_version="2023-06-01-preview",
            embedding_deployment="text-embedding-ada-002",
            chat_deployment="gpt-4.1-mini",
        )
        self.unstructured.build_index()

        print("\nLoading Multimodal Data Agent")
        print("-------------------------------")
        self.multimodal = <TODO 13: initialize the multimodal data agent with the appropriate parameters, including Azure Blob Storage connection parameters and Azure content safety moderation parameters>
            azure_conn_str=multimodalazureconnstring,
            container_name="houses",
            content_safety_endpoint=multimodalazurecontentsafetyendpoint,
            content_safety_key=multimodalazurecontentsafetykey
        )

    # -------------------------
    #  Routing
    # -------------------------
    def _route_query(self, user_message: str) -> str:
        """
        Route user query to one of:
        - structured
        - unstructured
        - multimodal

        This is a rule-based router. You can extend it later.
        """
        msg = user_message.lower().strip()

        multimodal_keywords = [
            "house like mine",
            "find me a house like mine",
            "show me a house like mine",
            "similar house",
            "similar image",
            "image",
            "photo",
            "picture",
            "looks like",
            "visual",
        ]

        structured_keywords = [
            "demographic",
            "demographics",
            "price",
            "home price",
            "most expensive",
            "average",
            "median",
            "count",
            "how many",
            "highest",
            "lowest",
            "neighborhood",
            "income",
            "population",
            "sql",
            "database",
        ]

        unstructured_keywords = [
            "permit",
            "approved",
            "document",
            "documents",
            "text",
            "restaurant",
            "permit approved",
            "notes",
            "report",
            "permit document",
        ]

        # Priority 1: multimodal
        if any(keyword in msg for keyword in multimodal_keywords):
            return <TODO 14: return the name of the multimodal agent>

        # Priority 2: unstructured
        if any(keyword in msg for keyword in unstructured_keywords):
            return <TODO 15: return the name of the unstructured agent>

        # Priority 3: structured
        if any(keyword in msg for keyword in structured_keywords):
            return <TODO 16: return the name of the structured agent>

        # Default fallback
        return "unstructured"

    # -------------------------
    #  Agent wrappers
    # -------------------------
    def _run_structured(self, prompt: str) -> str:
        result = self.structured.ask(prompt, verbose=False, run_bias_audit=True)

        if isinstance(result, dict):
            return result.get("response", str(result))

        return str(result)

    def _run_unstructured(self, prompt: str) -> str:
        result = self.unstructured.ask(prompt, run_pii_audit=True)

        if isinstance(result, dict):
            return result.get("response", str(result))

        return str(result)

    def _run_multimodal(self, prompt: str) -> str:
        """
        Right now your original code ignored the prompt and always used
        query-house-2.jpg. Keeping that behavior here for parity.
        """
        query_image = "query-house-2.jpg" # You can change this to "query-house-1.jpg" to test with the other image
        matches, query_img = self.multimodal.find_similar(query_image)

        print("\nTop matches:")
        for score, path, address in matches:
            print(f"{address} | similarity: {score:.4f}")

        self.multimodal.show_results(query_img, matches)

        if not matches:
            return "I could not find similar houses."

        lines = ["Here are the top similar houses I found:"]
        for score, path, address in matches[:5]:
            lines.append(f"- {address} (similarity: {score:.4f})")

        return "\n".join(lines)

    # -------------------------
    #  Chat Interface
    # -------------------------
    def chat(self, user_message: str) -> str:
        route = self._route_query(user_message)
        print(f"[Router] Selected agent: {route}")

        try:
            if route == <TODO 17: check if the route is the structured agent>:
                return self._run_structured(user_message)

            if route == <TODO 18: check if the route is the unstructured agent>:
                return self._run_unstructured(user_message)

            if route == <TODO 19: check if the route is the multimodal agent>:
                return self._run_multimodal(user_message)

            return "I could not determine the correct agent."
        except Exception as e:
            return f"An error occurred while processing your request with the {route} agent: {e}"


# ============================================================
#  Run Chat
# ============================================================

if __name__ == "__main__":
    banner = r"""
                                   /\ 
                                  /  \ 
                                 /____\ 
                ________________/______\_______________________
               /                                               \
              /_________________________________________________\
             |   ____      ____      ____      ____      ____   |
             |  | ▇▇ |    | ▇▇ |    | ▇▇ |    | ▇▇ |    | ▇▇ |  |
             |  | ▇▇ |    | ▇▇ |    | ▇▇ |    | ▇▇ |    | ▇▇ |  |
             |  |____|    |____|    |____|    |____|    |____|  |
             |                                                  |
             |        NEIGHBORHOOD INSIGHTS & DATA ASSISTANT    |
             |__________________________________________________|
    """
    print(banner)
    print("\n This AI-powered assistant provides automatically generated responses. "
          "Please use discretion, as answers may contain inaccuracies or errors.\n")
    print("Data comes from a structured demographics database, permit documents in NoSQL, and images stored in Azure.")
    print("Data remains in its original systems and is not copied into the assistant.")
    print("Embeddings and other AI artifacts are generated at runtime and are not permanently stored.")

    chat = AgentChatManager()

    print("\n\n--------------------------------")
    print("\n Agent Chat Ready.\n")
    print("Here are some examples of questions you can ask:")
    print("  - Which demographic group has the most expensive homes?")
    print("  - Was a permit approved for a restaurant in any of the neighborhoods?")
    print("  - Find me a house like mine")
    print("\n Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            break

        answer = chat.chat(user_input)
        print(f"Agent: {answer}\n")