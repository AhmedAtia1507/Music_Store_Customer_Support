import os
import uuid
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from Utils.GraphInnerState import GraphInnerState
from langgraph.store.base import BaseStore
from langgraph.graph import MessagesState
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


load_dotenv()

class CustomerPreferences:
    def __init__(self, model_name: str = "gpt-4o"):
        # self.preferenceModel = ChatGroq(model=model_name)
        self.preferenceModel = ChatOpenAI(model=model_name)

    
    def extract_preferences(self, state : GraphInnerState, store: BaseStore) -> GraphInnerState:
        """Extract customer preferences from their input."""
        items = store.search(
            (state["customer_id"], "preferences")
        )
        preferences = "\n".join(item.value["text"] for item in items)
        preferences = f"## Preferences of user\n{preferences}" if preferences else ""
        print("Extracted Preferences:", preferences)
        return {"loaded_preferences": preferences}

    def save_preferences(self, state : GraphInnerState, store: BaseStore) -> MessagesState:
        """Save customer preferences to the vector store."""
        print(state)
        prompt = ChatPromptTemplate.from_messages([
        ("system", """
            You are an assistant that extracts and summarizes customer music preferences.
            Rules:
            - Record any artist, band, or genre the customer mentions.
            - Here is a list of genres to consider:
            ["Alternative", "Alternative & Punk", "Blues", "Bossa Nova", "Classical", "Comedy", "Drama", "Easy Listening", "Electronica/Dance", "Heavy Metal", "Hip Hop/Rap", "Jazz", "Latin", "Metal", "Opera", "Pop", "R&B/Soul", "Reggae", "Rock", "Rock And Roll", "Sci Fi & Fantasy", "Science Fiction", "Soundtrack", "TV Shows", "World"]
            - Distinguish the type of mention:
                * If the customer explicitly likes/enjoys/loves → record as "Customer likes ... So he might like ..." (mention the genre that fits best from the list)
                * If the customer asks about or is curious → record as "Customer asked about ... Maybe he likes ..." (mention the genre that fits best from the list)
                * If the customer explicitly dislikes/hates → record as "Customer dislikes ... So he might not like ..." (mention the genre that fits best from the list)
            - Always write in the third person.
            - If the input has no music-related mentions, respond with "No preferences found."
            - Avoid repeating items already listed in previous preferences.
            - Always write one short, meaningful sentence capturing only the new mentions.
        """),
        ("user", """
            Customer's input:
            {input}

            Previous preferences:
            {previous_preferences}
        """)
        ])
        last_human_message = next(
            (msg for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)),
            None,  # default if no HumanMessage found
        )
        last_human_message_content = last_human_message.content if last_human_message else ""
        message = prompt.invoke({
            "input": last_human_message_content,
            "previous_preferences": state["loaded_preferences"]
        })
        print(message)
        response = self.preferenceModel.invoke(
            message
        )
        print("Preference Extraction Response:", response)
        if response.content.strip().lower() != "no preferences found.":
            preference_id = str(uuid.uuid4())
            store.put(
                (state["customer_id"], "preferences"),
                preference_id,
                {"text": response.content.strip()},
            )
        
        return state
        