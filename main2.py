# main.py
import uuid
from memory import SharedMemory
from agents.invoiceprocess import InvoiceProcessingAgent
from agents.jsonagent import JSONAgent
from agents.emailagent import EmailAgent
from agents.classifier import InvoiceClassifierAgent
import json

def main():
    shared_memory = SharedMemory()
    invoice_agent = InvoiceProcessingAgent(shared_memory)
    json_agent = JSONAgent(shared_memory)
    email_agent = EmailAgent(shared_memory)
    classifier_agent = InvoiceClassifierAgent(shared_memory)

    file_path = input("Enter the path to the invoice file, or 'exit':\n")
    if file_path.lower() == 'exit':
        return

    raw_input = InvoiceClassifierAgent.read_file_content(file_path)

    if raw_input is not None:
        interaction_id = str(uuid.uuid4())
        shared_memory.initialize_context(interaction_id)

        classification = classifier_agent.classify_invoice(raw_input, interaction_id)
        print(f"\nClassification: {classification}")

        target_agent = classifier_agent.route_invoice(raw_input, classification, interaction_id)

        if target_agent == "invoice_agent":
            results = invoice_agent.process_invoice(raw_input, "text",interaction_id)
            print(f"\nPlain Invoice Agent Results:\n{json.dumps(results, indent=2, default=str)}")
        elif target_agent == "json_agent":
            results = json_agent.process_json(raw_input, interaction_id)
            print(f"\nJSON Invoice Agent Results:\n{json.dumps(results, indent=2, default=str)}")
        elif target_agent == "email_agent":
            results = email_agent.process_email(raw_input, interaction_id)
            print(f"\nEmail Invoice Agent Results:\n{json.dumps(results, indent=2, default=str)}")
        else:
            print("No suitable agent found for the given format.")

        shared_memory.print_all_memory()
        print("-" * 30)
    else:
        print("Could not read invoice data from the file.")

if __name__ == "__main__":
    main()