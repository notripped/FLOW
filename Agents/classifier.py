# agents/classifier_agent.py
import json
import re
import uuid
from typing import Dict, Any
from memory import SharedMemory  # Import your SharedMemory class
# from llm_integration import LLM  # Assuming you have a module for LLM interaction

class InvoiceClassifierAgent:
    def __init__(self, memory: SharedMemory, llm=None):
        """
        Initializes the InvoiceClassifierAgent, focused on invoice processing.

        Args:
            memory: An instance of the SharedMemory class for logging.
            llm: An instance of your LLM integration class (optional).
        """
        self.memory = memory
        self.llm = llm

    def classify_invoice(self, raw_input: str, interaction_id: str) -> Dict[str, str]:
        """
        Classifies the format of the raw input as it relates to invoices
        and attempts to determine a specific invoice processing intent.

        Args:
            raw_input: The raw input string (content of file, email, or JSON).
            interaction_id: A unique ID for this interaction.

        Returns:
            A dictionary containing the identified format and a specific
            invoice processing intent (e.g., "process_plain_invoice",
            "process_json_invoice", "process_email_invoice").
        """
        format = self._detect_invoice_format(raw_input)
        #intent = self._classify_invoice_intent_with_llm(raw_input, format) if self.llm else f"process_{format}_invoice"

        self.memory.store_data(interaction_id, "invoice_format", format)
        #self.memory.store_data(interaction_id, "invoice_intent", intent)
        return {"format": format}
        # return {"format": format, "intent": intent}

    def route_invoice(self, raw_input: str, classification: Dict[str, str], interaction_id: str) -> str or None:
        """
        Routes the input to the appropriate invoice processing agent
        based on the classification.

        Args:
            raw_input: The raw input string.
            classification: The dictionary containing the identified format and intent.
            interaction_id: A unique ID for this interaction.

        Returns:
            The name of the agent to route to (e.g., "invoice_agent", "json_agent", "email_agent"),
            or None if no suitable agent is found.
        """
        format = classification.get("format")
        # intent = classification.get("intent")

        # if format == "plain_invoice" and "plain" in intent:
        #     return "invoice_agent"
        # elif format == "json" and "json" in intent:
        #     return "json_agent"
        # elif format == "email" and "email" in intent:
        #     return "email_agent"
        # return None

        if format == "plain_invoice":
            return "invoice_agent"
        elif format == "json":
            return "json_agent"
        elif format == "email":
            return "email_agent"
        else:
            return None

    def _detect_invoice_format(self, raw_input: str) -> str:
        """
        Detects the format of the input, specifically for invoices.

        Args:
            raw_input: The raw input string.

        Returns:
            The detected format ("json", "email", "plain_invoice", or "unknown").
        """
        if raw_input.startswith("{") and raw_input.endswith("}"):
            try:
                json.loads(raw_input)
                # Add more specific checks for invoice-related fields in JSON if needed
                return "json"
            except json.JSONDecodeError:
                pass
        elif "From:" in raw_input and "Invoice Number:" in raw_input:
            return "email"
        elif "Invoice Number:" in raw_input :
            return "plain_invoice"
        return "unknown"

    def read_file_content(file_path: str) -> str or None:
        """Helper method to read content from a file."""
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    # def _classify_invoice_intent_with_llm(self, raw_input: str, format: str) -> str:
    #     """
    #     Classifies the specific invoice processing intent of the input using an LLM.
    #
    #     Args:
    #         raw_input: The raw input string.
    #         format: The detected format of the input.
    #
    #     Returns:
    #         The predicted specific invoice processing intent as a string.
    #     """
    #     if not self.llm:
    #         return f"process_{format}_invoice"
    #
    #     prompt = f"""You are an expert at classifying the specific processing intent for invoice data.
    #     The input is in '{format}' format. Analyze the content and determine the specific action to take
    #     related to invoice processing.
    #
    #     Possible intents: process_plain_invoice, process_json_invoice, process_email_invoice, extract_details.
    #
    #     Input:
    #     ```
    #     {raw_input}
    #     ```
    #
    #     Specific Invoice Processing Intent: """
    #
    #     try:
    #         llm_response = self.llm.generate_response(prompt)
    #         predicted_intent = llm_response.strip().lower().replace(" ", "_")
    #         return predicted_intent
    #     except Exception as e:
    #         print(f"Error during LLM invoice intent classification: {e}")
    #         return f"process_{format}_invoice_failed"

# Example of LLM integration (assuming you have a class for this)
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class LLM:
    def __init__(self, api_key=GEMINI_API_KEY, model_name="gemini-pro"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            # Gemini returns a response object, the text is in response.text
            return response.text
        except Exception as e:
            print(f"Error generating response from Gemini: {e}")
            return ""

# shared_memory_instance = SharedMemory()  # Create an instance
# input_data = input("Enter invoice data (plain, JSON, or email), or 'exit':\n")
# interaction_id = str(uuid.uuid4())
# shared_memory_instance.initialize_context(interaction_id)
# # Assuming InvoiceClassifierAgent needs a SharedMemory instance:
# classifier_agent_instance = InvoiceClassifierAgent(shared_memory_instance)
# classification = classifier_agent_instance.classify_invoice(input_data,interaction_id)
# print(f"\nClassification: {classification}")