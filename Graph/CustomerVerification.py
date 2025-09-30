from ast import List
from typing import Optional
from langgraph.types import interrupt
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from Databases.CustomerDatabase import CustomerDatabase
from Utils.GraphInnerState import GraphInnerState
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import MessagesState

class CustomerData(BaseModel):
    """
    Represents customer data for verification.
    """
    customer_id: Optional[str] = Field(..., description="The unique identifier for the customer.")
    customer_phone_number: Optional[str] = Field(..., description="The phone number of the customer.")
    customer_email: Optional[str] = Field(..., description="The email address of the customer.")

class CustomerVerification:
    def __init__(self, model_name: str = "gpt-4o"):
        self.customer_db = CustomerDatabase()
        self.verificationModel = ChatOpenAI(model=model_name).with_structured_output(CustomerData)

    
    def verify_customer(self, state : GraphInnerState) -> GraphInnerState:
        """Verify customer identity based on provided information."""
        print("Verifying customer...")
        system_prompt = """
            Your mission is to extract customer identification details from their input. Only respond with the structured data.
            The customer may provide their customer ID, phone number, or email address.
            If the input does not contain any identifiable information, respond with empty fields."""
        structured_response = self.verificationModel.invoke(
            [
                SystemMessage(content=system_prompt),
                *[message for message in state["messages"]]
            ]
        )
        print("Structured Response:", structured_response)
        
        customerDetails = self.customer_db.get_customer_details (
            customer_id=structured_response.customer_id,
            phone_number=structured_response.customer_phone_number,
            email=structured_response.customer_email
        )
        while not customerDetails:
            interrupt_result = ""
            if not structured_response:
                interrupt_result = interrupt("Could not parse the response. Please provide the information in the correct format.")
            else:
                interrupt_result = interrupt("Please provide your phone number or email for verification.")
            print("Interrupt Result:", interrupt_result)
            structured_response = self.verificationModel.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=interrupt_result)
                ]
            )
            customerDetails = self.customer_db.get_customer_details (
                customer_id=structured_response.customer_id,
                phone_number=structured_response.customer_phone_number,
                email=structured_response.customer_email
            )
            print("Re-attempted Customer Details:", customerDetails)
        print("Customer Details:", customerDetails)
        return {"customer_id": str(customerDetails["customer_id"]) if customerDetails["customer_id"] is not None else None}