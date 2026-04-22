import warnings
warnings.filterwarnings("ignore", message="Field.*conflict with protected namespace")

from azure.keyvault.secrets import SecretClient
from azure.identity import InteractiveBrowserCredential

from langchain_openai import AzureChatOpenAI
from nemoguardrails import <TODO 1: use LLMRails and RailsConfig libraries>
from nemoguardrails.actions import action

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
nemoazureendpoint = retrieved_secret = client.get_secret("XXXXXX").value
nemoazurekey = retrieved_secret = client.get_secret("XXXXXX").value

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
        self._<TODO 9: load guardrails>
        self._<TODO 10: load_agents()>
        self._<TODO 11: register_actions()>

    # -------------------------
    #  Guardrails
    # -------------------------
    def _load_guardrails(self):
        # Configure the Azure LLM parameters
        azure_llm = AzureChatOpenAI(
            <TODO 12: pass the Azure LLM parameters>
        )
        config = RailsConfig.from_path("./config")
        self.rails = LLMRails(config, llm=azure_llm, verbose=False)

    # -------------------------
    #  Agents
    # -------------------------
    def _load_agents(self):

        print("\nLoading Strucutred Data Agent")
        print("-------------------------------")
        self.structured = StructuredDataAgent(
            azure_endpoint=structuredazureendpoint,
            api_key=structuredazureapikey,
            deployment="gpt-4.1-mini",
            db_config={
                <TODO 13: pass the database connection parameters for the structured data agent: host, database name, user, password, port (5432)>
            }
        )

        print("\nLoading Unstrucutred Data Agent")
        print("---------------------------------")
        self.unstructured = UnstructuredDataAgent(
            <TODO 14: pass the connection parameters for the unstructured data agent: mongo_uri, database name, collection name, chroma path for local storage of the vector database, Azure endpoint and key for generating embeddings and moderating content>
            mongo_uri=XXXXXXX,
            db_name=uXXXXXXX,
            collection_name=XXXXXXX,
            chroma_path=XXXXXX,
            azure_endpoint=XXXXXX,
            azure_key=XXXXXX,
            azure_api_version="2023-06-01-preview",
            embedding_deployment="text-embedding-ada-002",
            chat_deployment="gpt-4.1-mini",
        )
        self.unstructured.build_index()

        print("\nLoading Multimodal Data Agent")
        print("-------------------------------")
        self.multimodal = MultimodalDataAgent(
            <TODO 15: pass the connection parameters for the multimodal data agent: Azure connection string for accessing the blob storage where the images are stored, and Azure endpoint and key for content safety moderation>
            azure_conn_str=XXXXXXX,
            container_name=XXXXXXX,
            content_safety_endpoint = XXXXXXX,
            content_safety_key = XXXXXXX
        )

    # -------------------------
    #  Register Guardrail Actions
    # -------------------------
    def _register_actions(self):

        @action(name="structuredDataAction()")
        async def structured_action(prompt):
            result = <TODO 16: call the ask method> 
            return result["response"]

        @action(name="unstructuredDataAction()")
        async def unstructured_action(prompt):
            return <TODO 17: call the ask method with PII enabled>

        @action(name="multimodalDataAction()")
        async def multimodal_action(prompt):
            query_image = <TODO 18: assign one of two available images in the project root folder> 
            matches, query_img = <TODO 19: call the image similarity method> 
            print("\nTop matches:")
            for score, path, address in matches:
                print(f"{address} | similarity: {score:.4f}")
            self.multimodal.show_results(query_img, matches)
            return matches

        <TODO 20: register the actions with the guardrails instance>
        self.rails.register_action(structured_action, "XXXXXXXXX")
        self.rails.register_action(unstructured_action, "XXXXXXXXX")
        self.rails.register_action(multimodal_action, "XXXXXXXXX")

    # -------------------------
    #  Chat Interface
    # -------------------------
    def chat(self, user_message: str):
        messages = [{"role": "user", "content": user_message}]
        response = self.rails.generate(messages=messages)
        return response["content"]


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
    print("\n This AI-powered assistant provides automatically generated responses. " \
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
