import streamlit as st
from langgraph.types import Command
import logging
import os

# Import your components
from Graph.CustomerQueryGraph import CustomerQueryGraph
from langchain_core.messages import HumanMessage, AIMessage

# Configure logging
logging.basicConfig(filename="app.log", level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamlitCustomerSupportApp:
    """
    Streamlit application for music store customer support using CustomerQueryGraph
    """
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Music Store Customer Support",
            page_icon="🎵",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'threads' not in st.session_state:
            st.session_state.threads = ["Default Thread"]
            st.session_state.messages = {"Default Thread": []}
        
        if 'query_graph' not in st.session_state:
            st.session_state.query_graph = None
        
        if 'compiled_graph' not in st.session_state:
            st.session_state.compiled_graph = None

        if 'awaiting_verification' not in st.session_state:
            st.session_state.awaiting_verification = False
    
    @st.cache_resource
    def get_query_graph(_self, model_name: str = "openai/gpt-oss-120b"):
        """Initialize and cache the CustomerQueryGraph"""
        try:
            st.session_state.query_graph = CustomerQueryGraph(model_name=model_name)
            compiled_graph = st.session_state.query_graph.build_graph()
            return compiled_graph
        except Exception as e:
            logger.error(f"Error initializing CustomerQueryGraph: {e}")
            st.error(f"Failed to initialize customer support system: {e}")
            return None
    
    def render_sidebar(self):
        """Render the sidebar with app information and controls"""
        with st.sidebar:
            st.title("🎵 Music Store Support")
            
            st.markdown("---")
            
            st.session_state.model_name = st.selectbox (
                "Select Language Model",
                options=["openai/gpt-oss-120b", "openai/gpt-oss-20b", "moonshotai/kimi-k2-instruct-0905", "meta-llama/llama-4-maverick-17b-128e-instruct"],
                index=0
            )
            st.session_state.api_key = st.text_input(
                "Enter your Groq API Key",
                type="password"
            )
            if st.session_state.api_key:
                os.environ["GROQ_API_KEY"] = st.session_state.api_key
                st.success("API Key set successfully!")
                if st.session_state.query_graph is None or st.session_state.query_graph.model_name != st.session_state.model_name:
                    with st.spinner("Loading customer support system..."):
                        st.session_state.compiled_graph = self.get_query_graph(model_name=st.session_state.model_name)
                else:
                    st.info("Customer support system is already loaded with the selected model.")
            else:
                st.warning("Please enter your Groq API Key to enable the support system.")
            
            st.markdown("---")
            st.session_state.current_thread_id = st.selectbox(
                "Select Conversation Thread",
                options=st.session_state.threads if 'threads' in st.session_state else [],
                index=0
            )
            if st.button("Add New Thread"):
                new_thread_id = f"Thread {len(st.session_state.threads) + 1}"
                st.session_state.threads.append(new_thread_id)
    
    def display_chat_messages(self):
        """Display chat messages in the main area"""
        if st.session_state.current_thread_id not in st.session_state.messages:
            st.session_state.messages[st.session_state.current_thread_id] = []
        
        for message in st.session_state.messages[st.session_state.current_thread_id]:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.markdown(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.markdown(message.content)
                        

    def handle_user_input(self, user_input: str):
        """Process user input through the CustomerQueryGraph"""
        if not st.session_state.compiled_graph:
            st.error("Customer support system is not available. Please try again later.")
            return
        
        try:
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.messages[st.session_state.current_thread_id].append(HumanMessage(content=user_input))
            # Show thinking indicator
            with st.chat_message("assistant"):
                with st.spinner("Processing your request..."):
                    response = None
                    # Check if awaiting verification
                    if st.session_state.awaiting_verification:
                        response = st.session_state.compiled_graph.invoke(
                            Command(resume=user_input),
                            config={"configurable": {"thread_id": st.session_state.current_thread_id}}
                        )
                        st.session_state.awaiting_verification = False
                    else:
                        # Invoke the graph with user input
                        response = st.session_state.compiled_graph.invoke(
                            {"messages": [HumanMessage(content=user_input)]},
                            config={"configurable": {"thread_id": st.session_state.current_thread_id}}
                        )
                    
                    # Handle interrupts (customer verification)
                    if response.get("__interrupt__"):
                        interrupt_msg = response["__interrupt__"][-1].value
                        st.markdown(f"🔐 {interrupt_msg}")
                        st.session_state.awaiting_verification = True
                    else:
                        # Display the assistant's response
                        st.markdown(response["messages"][-1].content)
                        st.session_state.messages[st.session_state.current_thread_id].append(AIMessage(content=response["messages"][-1].content))
        
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            error_msg = "I apologize, but I encountered an error processing your request. Please try again."
            
            with st.chat_message("assistant"):
                st.error(error_msg)

    def render_main_chat_interface(self):
        """Render the main chat interface"""
        st.title("🎵 Music Store Customer Support")
        
        # Display chat messages
        self.display_chat_messages()
        
        # Chat input
        if user_input := st.chat_input("Ask me about our music catalog or your account..."):
            self.handle_user_input(user_input)
    
    def run(self):
        """Main app entry point"""
        try:
            # Render sidebar
            self.render_sidebar()
            
            # Check if compiled graph is available
            if not st.session_state.compiled_graph:
                st.error("🚫 Customer support system is currently unavailable. Please check your configuration.")
                st.stop()
            
            # Render main chat interface
            self.render_main_chat_interface()
            
        except Exception as e:
            logger.error(f"Error running app: {e}")
            st.error("An unexpected error occurred. Please refresh the page and try again.")

def main():
    """Main function to run the Streamlit app"""
    app = StreamlitCustomerSupportApp()
    app.run()

if __name__ == "__main__":
    main()