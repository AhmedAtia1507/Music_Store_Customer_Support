
from langgraph.graph import StateGraph, START
from Utils.GraphInnerState import GraphInnerState
from Graph.CustomerPreferences import CustomerPreferences
from Graph.CustomerVerification import CustomerVerification
from langgraph.prebuilt import create_react_agent
from Databases.MusicDatabase import MusicDatabase
from Databases.CustomerDatabase import CustomerDatabase
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_groq import ChatGroq
from langmem.short_term import SummarizationNode
from langchain_core.messages.utils import count_tokens_approximately
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

class CustomerQueryGraph:
    def __init__(self, model_name: str = "openai/gpt-oss-120b"):
        self.model_name = model_name
        self.verification = CustomerVerification(model_name=model_name)
        self.preferences = CustomerPreferences(model_name=model_name)
        self.musicDatabase = MusicDatabase()
        self.customerDatabase = CustomerDatabase()
        self.music_catalog_agent = None  # Placeholder for music catalog agent
        self.invoice_info_agent = None  # Placeholder for invoice information agent
        self.supervisor_agent = None  # Placeholder for supervisor agent

        self.checkpointer = InMemorySaver()
        self.memory_store = InMemoryStore()

    def create_multi_agent_system(self):
        self.music_catalog_agent = create_react_agent(
            model=ChatGroq(model=self.model_name),
            tools=[
                self.musicDatabase.get_albums_by_artist,
                self.musicDatabase.get_tracks_by_artist,
                self.musicDatabase.get_songs_by_genre,
                self.musicDatabase.check_for_track,
                self.musicDatabase.check_for_album,
                self.musicDatabase.check_for_artist,
                self.musicDatabase.get_all_artists,
                self.musicDatabase.get_all_genres,
                self.musicDatabase.get_all_albums,
                self.musicDatabase.search_tracks,
                self.musicDatabase.search_albums
            ],
            prompt=ChatPromptTemplate.from_messages([
                ("system", """
                You are a music catalog assistant. You have access to a music database and can provide information about artists, albums, tracks, and genres. \n\n
                INSTRUCTIONS:\n
                - Always use the provided tools to get information from the music database. Do not make up information.\n
                - If the user asks for recommendations, suggest music from the music database based on their preferences provided in the graph state.\n
                - If the user asks for information about a specific artist, album, track, or genre, use the appropriate tool to fetch the information from the music database.\n
                - If the tool returns nothing for a query, respond with "No data found" instead of making up information.\n
                - Summarize the music information if there are multiple items as bullet points.\n
                - After you are done with your tasks, respond to the supervisor directly.\n
                """),
                MessagesPlaceholder("messages")
            ]),
            name="Music_Catalog_Agent",
            state_schema=GraphInnerState
        )
        
        self.invoice_info_agent = create_react_agent(
            model=ChatGroq(model=self.model_name),
            tools=[
                self.customerDatabase.get_invoices_by_customer_sorted_by_date,
                self.customerDatabase.get_invoices_sorted_by_unit_price,
                self.customerDatabase.get_employee_name_by_invoice_and_customer_id
            ],
            prompt=ChatPromptTemplate.from_messages([
                ("system", """
                You are an invoice information assistant. You have access to a customer database and can provide information about customer invoices.
                INSTRUCTIONS:
                - Customer ID is {customer_id}. You will find it in the graph state
                - Always use the provided tools to get information from the customer database. Do not make up information.
                - If the user asks for information about their invoices, use the appropriate tool to fetch the information.\n
                - If the tool returns nothing for a query, respond with "No data found" instead of making up information.\n
                - Summarize the invoice information if there are multiple invoices.\n
                - After you are done with your tasks, respond to the supervisor directly.\n
                """),
                MessagesPlaceholder("messages")
            ]),
            name="Invoice_Information_Agent",
            state_schema=GraphInnerState
        )

        supervisor_builder = create_supervisor(
            model=ChatGroq(model=self.model_name),
            agents=[self.music_catalog_agent, self.invoice_info_agent],
            prompt=ChatPromptTemplate.from_messages([
                ("system", """
                You are supervisor agent overseeing two specialized agents:\n
                1. Music Catalog Agent: Handles inquiries about music artists, albums, tracks, and genres.\n
                2. Invoice Information Agent: Manages questions related to customer invoices and billing details.\n\n
                INSTRUCTIONS:\n
                - Customer ID is {customer_id}. You will find it in the graph state. It needs to be included in all relevant queries.\n
                - Analyze the user's request and determine which specialized agent is best suited to handle it.\n
                - Delegate the task to the appropriate agent.\n
                - If the user's request involves multiple topics, break it down and assign each part to the relevant agent.\n
                - Do not attempt to answer the user's request directly; always use the specialized agents.\n
                - Assign work to one agent at a time and wait for their response before proceeding.\n
                - Once all parts of the user's request have been addressed by the specialized agents, compile their responses into a coherent final answer.\n
                - Ensure that the final response is clear, concise, and directly addresses the user's original request.
                """),
                MessagesPlaceholder("messages")
            ]),
            state_schema=GraphInnerState,
            add_handoff_back_messages=True,
            output_mode="last_message"
        )
        self.supervisor_agent = supervisor_builder.compile()
    
    def should_verify_customer(self, state: GraphInnerState) -> bool:
        if "customer_id" not in state or state["customer_id"] is None:
            return True
        return False

    def build_graph(self):
        if not self.music_catalog_agent or not self.invoice_info_agent or not self.supervisor_agent:
            self.create_multi_agent_system()

        self.summarization_node = SummarizationNode(
            model=ChatGroq(model=self.model_name),
            max_tokens=8000,
            token_counter=count_tokens_approximately,
            max_tokens_before_summary=4000,
            max_summary_tokens=4000,
        )

        graphBuilder = StateGraph(GraphInnerState)
        graphBuilder.add_node("summarize_conversation", self.summarization_node)
        graphBuilder.add_node("verify_customer", self.verification.verify_customer)
        graphBuilder.add_node("extract_preferences", self.preferences.extract_preferences)
        graphBuilder.add_node("supervisor_agent", self.supervisor_agent)
        graphBuilder.add_node("save_preferences", self.preferences.save_preferences)

        graphBuilder.add_edge(START, "summarize_conversation")

        graphBuilder.add_edge("verify_customer", "extract_preferences")
        graphBuilder.add_edge("extract_preferences", "supervisor_agent")
        graphBuilder.add_edge("supervisor_agent", "save_preferences")

        graphBuilder.add_conditional_edges("summarize_conversation", self.should_verify_customer, {
            True: "verify_customer",
            False: "extract_preferences"
        })
        return graphBuilder.compile(checkpointer=self.checkpointer, store=self.memory_store)
    
