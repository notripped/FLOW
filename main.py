# main.py
import uuid
from memory import SharedMemory
from agents.invoiceprocess import InvoiceProcessingAgent
from agents.jsonagent import JSONAgent
from agents.emailagent import EmailAgent
from agents.classifier import InvoiceClassifierAgent
import json

# Optional: Initialize your LLM if you are using it
# from llm_integration import LLM
# llm_instance = LLM()
shared_memory = SharedMemory()
invoice_agent = InvoiceProcessingAgent(shared_memory)
json_agent = JSONAgent(shared_memory)
email_agent = EmailAgent(shared_memory)
#invoice_classifier_agent = InvoiceClassifierAgent(shared_memory, llm_instance if 'llm_instance' in locals() else None)

def main(llm_instance=None, type=None, file_path=None):
    if type is None or file_path is None:
        print("Error: 'type' and 'file_path' must be provided to the main function.")
        return

    try:
        with open(file_path, 'r') as f:
            input_data = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    interaction_id = str(uuid.uuid4())
    shared_memory.initialize_context(interaction_id)

    if type == "plain":
        results = invoice_agent.process_invoice(input_data, "text", interaction_id)
        print(json.dumps(results, indent=2, default=str))
        shared_memory.print_all_memory()
    elif type == "json":
        results = json_agent.process_json(input_data, interaction_id)
        print(json.dumps(results, indent=2, default=str))
        shared_memory.print_all_memory()
    elif type == "email":
        results = email_agent.process_email(input_data, interaction_id)
        print(json.dumps(results, indent=2, default=str))
        shared_memory.print_all_memory()
    else:
        print("No suitable invoice processing agent found for the given format.")

    shared_memory.print_all_memory()
    print("-" * 30)

if __name__ == "__main__":
    invoice_type = input("Enter type of invoice (plain, email, json): ").lower()
    file_path = input("Enter the path to the invoice file: ")
    main(type=invoice_type, file_path=file_path)