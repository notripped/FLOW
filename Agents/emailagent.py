# agents/invoice_email_agent.py
import re
from typing import Dict, Any
from datetime import datetime
import json
class EmailAgent:
    def __init__(self, memory):
        self.memory = memory
    def process_email(self, email_content: str, interaction_id: str) -> Dict[str, Any]:
        """
        Accepts full email content (including headers), extracts sender, subject,
        invoice details from the body, and formats it for CRM-style usage.
        """
        sender = self._extract_sender(email_content)
        subject = self._extract_subject(email_content)
        invoice_details = self._extract_invoice_details(self._extract_email_body(email_content))

        extracted_data = {
            "sender": sender,
            "subject": subject,
            "invoice_details": invoice_details,
            "raw_content": email_content,  # Keep the full content if needed
        }

        crm_formatted_data = self._format_for_crm(extracted_data)

        processing_results = {
            "extracted_data": extracted_data,
            "crm_formatted_data": crm_formatted_data
        }

        self.memory.store_data(interaction_id, 'invoice_email_processing_results', processing_results)
        return processing_results

    def _extract_sender(self, email_content: str) -> str or None:
        """Extracts the sender's email address or name from the content."""
        sender_match = re.search(r"(From:|Sender:)\s*([^\n<>]+(?:<[^>]+>)?[^\n]*)", email_content, re.IGNORECASE)
        if sender_match:
            sender_info = sender_match.group(2).strip()
            email_match = re.search(r"<([^>]+)>", sender_info)
            if email_match:
                return email_match.group(1)
            return sender_info.split()[0] if sender_info.split() else sender_info
        return None

    def _extract_subject(self, email_content: str) -> str or None:
        """Extracts the subject line from the email content."""
        subject_match = re.search(r"Subject:\s*(.+)", email_content, re.IGNORECASE)
        return subject_match.group(1).strip() if subject_match else None

    def _extract_email_body(self, email_content: str) -> str:
        """Simple extraction of the email body after the headers.
        This might need more sophisticated handling for different email formats."""
        body_parts = email_content.split("\n\n", 1)  # Split at the first double newline
        return body_parts[1] if len(body_parts) > 1 else email_content

    def _extract_invoice_details(self, email_body: str) -> Dict[str, Any]:
        """Extracts invoice details from the specifically formatted email body."""
        details = {
            "items": []  # CRITICAL FIX: Initialize items list here
        }

        # Extract Invoice Number
        invoice_number_match = re.search(r"Invoice Number:\s*(.+)", email_body)
        details["invoice_number"] = invoice_number_match.group(1).strip() if invoice_number_match else None

        # Extract Invoice Date
        invoice_date_match = re.search(r"Invoice Date:\s*(.+)", email_body)
        details["invoice_date"] = self._parse_date(invoice_date_match.group(1).strip()) if invoice_date_match else None

        # Extract Seller/Vendor Details
        seller_match = re.search(
            r"Seller/Vendor:\s*Name:\s*(.+)\s*Address:\s*(.+)\s*Tax ID:\s*(.+)",
            email_body,
            re.DOTALL
        )
        if seller_match:
            details["vendor"] = {
                "name": seller_match.group(1).strip(),
                "address": seller_match.group(2).strip(),
                "tax_id": seller_match.group(3).strip(),
            }
        else:
            details["vendor"] = {}  # Ensure vendor is always a dict

        # Extract Buyer/Customer Details
        buyer_match = re.search(
            r"Buyer/Customer:\s*Name:\s*(.+)\s*Address:\s*(.+)\s*Tax ID:\s*(.+)",
            email_body,
            re.DOTALL
        )
        if buyer_match:
            details["customer"] = {
                "name": buyer_match.group(1).strip(),
                "address": buyer_match.group(2).strip(),
                "tax_id": buyer_match.group(3).strip(),
            }
        else:
            details["customer"] = {}  # Ensure customer is always a dict

        # Extract Line Items
        if "-------------------- LINE ITEMS -------------------" in email_body:
            line_items_parts = email_body.split("-------------------- LINE ITEMS -------------------")
            if len(line_items_parts) > 1:
                item_table_part = line_items_parts[1].split("--------------------------------------------------")
                if len(item_table_part) > 0:
                    raw_items_text = item_table_part[0]
                    # Refined regex for line items to handle potential extra spaces and ensure correct capture
                    # This regex is still sensitive to column alignment
                    line_item_matches = re.findall(
                        r"^\s*(.+?)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$",  # Added ^ $ to match whole line
                        raw_items_text, re.MULTILINE  # Use MULTILINE to match ^ $ on each line
                    )
                    for item in line_item_matches:
                        try:
                            line_item_data = {
                                "description": item[0].strip(),
                                "quantity": int(item[1]),
                                "unit_price": float(item[2]),
                                "amount": float(item[3]),
                                "tax": float(item[4]),
                            }
                            details["items"].append(line_item_data)
                        except ValueError as e:
                            print(f"Error parsing line item numerical data: {e} for item: {item}")
                            # You might want to log this item as an anomaly instead of skipping
                else:
                    print("Warning: End of line items separator not found.")
            else:
                print("Warning: Start of line items separator found but no content after.")
        else:
            print("Warning: Line items section not found in email body.")

        # Extract Totals
        totals_match = re.search(
            r"---------------------- TOTALS ----------------------\s*"
            r"Subtotal:\s*([\d\.]+)\s*"
            r"Discount:\s*([\d\.]+)\s*"
            r"Total Tax Amount:\s*([\d\.]+)\s*"
            r"Shipping/Handling:\s*([\d\.]+)\s*"
            r"--------------------------------------------------\s*"
            r"Total Amount Due:\s*([\d\.]+)\s*"
            r"Currency:\s*(\w+)",
            email_body,
            re.DOTALL
        )
        if totals_match:
            try:
                details["subtotal"] = float(totals_match.group(1))
                details["discount"] = float(totals_match.group(2))
                details["total_tax_amount"] = float(totals_match.group(3))
                details["shipping_handling"] = float(totals_match.group(4))
                details["total_amount_due"] = float(totals_match.group(5))
                details["currency"] = totals_match.group(6).strip()
            except ValueError as e:
                print(f"Error parsing total numerical data: {e} for totals match: {totals_match.groups()}")
                # You might want to log this as an anomaly
        # No 'else: details["totals"] = {}' needed here, as fields will be None if not found/parsed

        return details

    def _parse_date(self, date_str: str) -> str or None:
        """Attempts to parse a date string into YYYY-MM-DD format."""
        formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    def _format_for_crm(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Formats the extracted invoice data into a CRM-friendly structure."""
        crm_data = {
            "email_sender": extracted_data.get("sender"),
            "email_subject": extracted_data.get("subject"),
            "invoice_number": extracted_data.get("invoice_details", {}).get("invoice_number"),
            "invoice_date": extracted_data.get("invoice_details", {}).get("invoice_date"),
            "vendor_name": extracted_data.get("invoice_details", {}).get("vendor", {}).get("name"),
            "vendor_address": extracted_data.get("invoice_details", {}).get("vendor", {}).get("address"),
            "vendor_tax_id": extracted_data.get("invoice_details", {}).get("vendor", {}).get("tax_id"),
            "customer_name": extracted_data.get("invoice_details", {}).get("customer", {}).get("name"),
            "customer_address": extracted_data.get("invoice_details", {}).get("customer", {}).get("address"),
            "customer_tax_id": extracted_data.get("invoice_details", {}).get("customer", {}).get("tax_id"),
            "line_items": extracted_data.get("invoice_details", {}).get("items"),
            "subtotal": extracted_data.get("invoice_details", {}).get("subtotal"),
            "discount": extracted_data.get("invoice_details", {}).get("discount"),
            "total_tax_amount": extracted_data.get("invoice_details", {}).get("total_tax_amount"),
            "shipping_handling": extracted_data.get("invoice_details", {}).get("shipping_handling"),
            "total_amount_due": extracted_data.get("invoice_details", {}).get("total_amount_due"),
            "currency": extracted_data.get("invoice_details", {}).get("currency"),
            "email_received_at": datetime.now().isoformat(),
            "status": "New", # Default status
            "assigned_to": None,
            "notes": "Invoice details extracted from email body."
        }
        return crm_data

# Example of how you might use this agent in your main.py:
if __name__ == "__main__":
    from memory import SharedMemory
    memory = SharedMemory()
    invoice_email_agent = EmailAgent(memory)
    interaction_id = "test_invoice_email_body_001"
    memory.initialize_context(interaction_id)
    dummy_full_invoice_email = """From: Billing Department <billing@acmecorp.com>
Subject: Invoice INV-2025-001

--------------------------------------------------
                       INVOICE
--------------------------------------------------

Invoice Number: INV-2025-001
Invoice Date: 2025-05-29

Seller/Vendor:
  Name: Acme Corp
  Address: 123 Main Street, Anytown, USA 12345
  Tax ID: US123456789

Buyer/Customer:
  Name: Beta Industries
  Address: 456 Oak Avenue, Someville, USA 67890
  Tax ID: US987654321

-------------------- LINE ITEMS -------------------
Description             Quantity    Unit Price    Amount      Tax
--------------------------------------------------
Widget A                10          10.00         100.00      8.00
Gadget B                5           25.00         125.00      10.00
Service C (Hourly)      2           50.00         100.00      0.00
--------------------------------------------------

---------------------- TOTALS ----------------------
Subtotal:              325.00
Discount:              15.00
Total Tax Amount:      18.00
Shipping/Handling:     5.00
--------------------------------------------------
Total Amount Due:      333.00
Currency:              USD
--------------------------------------------------
 """
#
    results = invoice_email_agent.process_email(dummy_full_invoice_email, interaction_id)
    print(json.dumps(results, indent=2, default=str))
    memory.print_all_memory()