# agents/invoice_processing_agent.py
import google.generativeai as genai
import os
import json
from documentextract import extract_text_from_pdf
from typing import Dict, List
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
class InvoiceProcessingAgent:
    def __init__(self, memory):
        self.memory = memory

    def process_json_invoice(self, invoice_data: Dict, interaction_id: str) -> Dict:
        """Processes invoice data provided in JSON format."""
        extracted_data = {}
        # Implement logic to extract fields based on expected JSON structure
        # This will be highly dependent on the specific JSON schema of your invoices
        extracted_data['invoice_number'] = invoice_data.get('invoiceNumber')
        extracted_data['invoice_date'] = invoice_data.get('invoiceDate')
        extracted_data['seller'] = invoice_data.get('seller')
        extracted_data['buyer'] = invoice_data.get('buyer')
        extracted_data['line_items'] = invoice_data.get('lineItems')
        extracted_data['total_amount'] = invoice_data.get('totalAmount')

        self.memory.store_data(interaction_id, 'extracted_invoice_data', extracted_data)
        return extracted_data

    def process_text_invoice(self, invoice_text: str, interaction_id: str) -> Dict:
        """Processes invoice data provided as plain text."""
        extracted_data = {}
        # This is where you would use an LLM to extract information from the unstructured text.
        # You'll need to design effective prompts.

        prompt =  prompt = f"""You are an expert at extracting information from invoices.Extract the following details from the text below and return them as a JSON object. If a piece of information is not found, use null.

Invoice Number: Look for a phrase like "Invoice Number:", "Invoice #:", or "Bill Number:".
Invoice Date: Look for a date associated with the invoice, often near the invoice number or header. Use YYYY-MM-DD format if possible.
Seller Name: Identify the name of the company issuing the invoice.(It can also be labelled as Seller or Vendor)
Buyer Name: Identify the name of the company or person being billed.(It can also be labelled as Buyer or Customer)
Subtotal: Find the amount before taxes and discounts.
Total Tax Amount: Find the total amount of tax.
Discount: Find any discount applied.
Shipping Handling: Find any shipping or handling fees.
Total Amount Due: Find the final amount the buyer owes, often labeled "Total", "Amount Due", etc.
Currency: Identify the currency used (e.g., USD, EUR).

Line Items: Extract the details of each itemized charge. For each item, identify the "description", "quantity", "unit price", "amount", and "tax" (if applicable). Return these as a JSON array of objects.


        Invoice Text:
        ```
        {invoice_text}
        ```
        txt Output:
        """
        # Assuming you have a method to interact with your LLM
        llm_response = self._call_llm(prompt)
        print(llm_response)
                # Implement logic to parse the LLM response and extract the structured data
        try:
            # Attempt to parse the LLM's response as JSON
            llm_extracted_data = json.loads(llm_response)
            extracted_data.update(llm_extracted_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response as JSON: {e}")
            print(f"LLM Raw Response: {llm_response}")
            extracted_data['parsing_error'] = str(e)
            extracted_data['raw_llm_output'] = llm_response  # Store raw output for debugging

        self.memory.store_data(interaction_id, 'extracted_invoice_data_text', extracted_data)
        return extracted_data

    # Optional: If you want the agent to handle raw PDFs (more complex)
    # def process_pdf_invoice(self, pdf_path: str, interaction_id: str) -> Dict:
    #     """Processes invoice data from a PDF file."""
    #     invoice_text = extract_text_from_pdf(pdf_path)
    #     return self.process_text_invoice(invoice_text, interaction_id)

    def _call_llm(self, prompt: str) -> str:
        try:
            response = model.generate_content(prompt)
            if hasattr(response, 'candidates') and response.candidates and \
                    hasattr(response.candidates[0], 'content') and \
                    hasattr(response.candidates[0].content, 'parts') and \
                    response.candidates[0].content.parts:
                llm_text = response.candidates[0].content.parts[0].text.strip()
                # Remove potential ```json and ``` delimiters
                llm_text = llm_text.removeprefix("```json").removesuffix("```").strip()
                return llm_text
            else:
                print("Warning: Could not extract text from LLM response.")
                return ""
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return ""
        # """Placeholder for your LLM interaction."""
        # # Replace this with your actual LLM API call (e.g., OpenAI, Hugging Face Transformers)
        # print(f"Calling LLM with prompt: {prompt}")
        # return "LLM Response Placeholder - Implement actual LLM call here"

    def validate_extracted_data(self, extracted_data: Dict) -> List[str]:
        """Performs basic validation on the extracted data."""
        errors = []
        if not extracted_data.get('invoice_number'):
            errors.append("Invoice number is missing.")
        if not extracted_data.get('invoice_date'):
            errors.append("Invoice date is missing.")
        if not extracted_data.get('total_amount'):
            errors.append("Total amount is missing.")
        if not extracted_data.get('line_items'):
            errors.append("Line items are missing.")
        # Add more validation rules as needed (e.g., data type checks, format checks)
        return errors

    def format_for_downstream(self, extracted_data: Dict) -> Dict:
        """Formats the extracted data into a consistent schema for other systems."""
        formatted_data = {
            'invoice_id': extracted_data.get('invoice_number'),
            'issue_date': extracted_data.get('invoice_date'),
            'vendor': extracted_data.get('seller'),
            'customer': extracted_data.get('buyer'),
            'items': extracted_data.get('line_items'),
            'total': extracted_data.get('total_amount'),
            'currency': extracted_data.get('currency') # You might need to extract this as well
            # Add other relevant fields in your desired target schema
        }
        return formatted_data

    def process_invoice(self, input_data: str, format: str, interaction_id: str) -> Dict:
        """Main entry point for processing invoices, handles different formats."""
        self.memory.initialize_context(interaction_id)
        extracted_data = {}
        if format == 'json':
            try:
                invoice_json = json.loads(input_data)
                extracted_data = self.process_json_invoice(invoice_json, interaction_id)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for interaction ID: {interaction_id}")
                # Handle the error appropriately
                return {'error': 'Invalid JSON format'}
        elif format == 'text':
            extracted_data = self.process_text_invoice(input_data, interaction_id)
        elif format == 'pdf':
            # Ideally, the Classifier would have extracted text already
            print("Warning: Received raw PDF in InvoiceProcessingAgent. Consider text extraction before routing.")
            # You might add PDF text extraction here as a fallback
            # extracted_data = self.process_pdf_invoice(input_data, interaction_id)
            return {'error': 'Raw PDF processing not fully implemented in this agent.'}
        else:
            return {'error': f'Unsupported format: {format}'}

        validation_errors = self.validate_extracted_data(extracted_data)
        if validation_errors:
            print(f"Validation errors for interaction ID {interaction_id}: {validation_errors}")
            self.memory.store_data(interaction_id, 'invoice_validation_errors', validation_errors)

        formatted_data = self.format_for_downstream(extracted_data)
        self.memory.store_data(interaction_id, 'formatted_invoice_data', formatted_data)

        return formatted_data