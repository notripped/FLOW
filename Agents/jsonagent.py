# agents/json_agent.py
import json
from typing import Dict, Any, List

class JSONAgent:
    def __init__(self, memory):
        self.memory = memory
        # Define the target schema for reformatting
        self.target_schema = {
            "id": "invoiceNumber",
            "date": "invoiceDate",
            "vendor_name": "seller.Name",
            "vendor_address": "seller.Address",
            "customer_name": "buyer.Name",
            "customer_address": "buyer.Address",
            "items": [
                {
                    "product": "description",
                    "qty": "quantity",
                    "unit_price": "unitPrice",
                    "line_total": "amount",
                    "tax_amount": "tax"
                }
            ],
            "total_amount": "totalAmount",
            "currency": "currency"
            # Add more fields as needed in your target schema
        }


    def process_json(self, json_payload: str, interaction_id: str) -> Dict[str, Any]:
        """
        Processes a JSON payload, extracts data based on the target schema,
        and flags anomalies or missing fields.
        """
        self.memory.initialize_context(interaction_id)
        extracted_data = {}
        anomalies = []

        try:
            data = json.loads(json_payload)
        except json.JSONDecodeError as e:
            error_message = f"Error decoding JSON payload: {e}"
            self.memory.store_data(interaction_id, 'json_processing_error', error_message)
            return {"error": error_message}

        extracted_data = self._extract_data(data, self.target_schema)
        anomalies = self._flag_anomalies(data, self.target_schema, extracted_data)

        processing_results = {
            "extracted_data": extracted_data,
            "anomalies": anomalies
        }

        self.memory.store_data(interaction_id, 'json_processing_results', processing_results)
        return processing_results

    def _get_nested_value(self, data: Dict[str, Any], keys: List[str]) -> Any:
        if not data or not keys:
            return None
        key_to_find = keys[0].lower()
        for k, v in data.items():
            if k.lower() == key_to_find:
                if len(keys) == 1:
                    return v
                elif isinstance(v, dict):
                    return self._get_nested_value(v, keys[1:])
        return None

    def _extract_data(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        extracted = {}
        for target_field, source_path in schema.items():
            if isinstance(source_path, str):
                value = self._get_nested_value(data, source_path.split('.'))
                if value is not None:
                    extracted[target_field] = value
            elif isinstance(source_path, list) and target_field == 'items':
                extracted['items'] = []
                items_key_options = ["lineitems", "items", "products", "details"]  # Lowercase options
                found_items_key = None
                for key in data:
                    if key.lower() in items_key_options:
                        found_items_key = key
                        break

                if found_items_key and isinstance(data.get(found_items_key), list):
                    for item in data[found_items_key]:
                        item_data = {}
                        for item_target_field, item_source_path in source_path[0].items():
                            item_value = self._get_nested_value(item, item_source_path.split('.'))
                            if item_value is not None:
                                item_data[item_target_field] = item_value
                        if item_data:
                            extracted['items'].append(item_data)
        return extracted
    def _find_list_path(self, schema: Dict[str, Any], data: Dict[str, Any]) -> str or None:
        """Helper to find the path to the list of items in the source JSON."""
        for key in ["lineItems", "items", "products", "details"]:
            if key in data:
                return key
        return None

    def _flatten_json(self, json_data: Dict[str, Any], parent_key='', sep='.') -> Dict[str, Any]:
        """Helper to flatten a JSON structure to easily check for keys."""
        items = []
        for k, v in json_data.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_json(v, new_key, sep=sep).items())
            elif isinstance(v, list) and k == 'items':
                # Don't flatten the items list itself, but check its target structure
                if v:
                    if isinstance(v[0], dict):
                        items.extend(self._flatten_json(v[0], new_key + '[0]', sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _get_nested_value(self, data: Dict[str, Any], keys: List[str]) -> Any:
        """Recursively gets a value from a nested dictionary based on a list of keys."""
        if not data or not keys:
            return None
        key = keys[0]
        if key in data:
            if len(keys) == 1:
                return data[key]
            elif isinstance(data[key], dict):
                return self._get_nested_value(data[key], keys[1:])
        return None

    def _flag_anomalies(self, data: Dict[str, Any], schema: Dict[str, Any], extracted: Dict[str, Any]) -> List[str]:
        """
        Flags missing fields and potentially type mismatches or unexpected values
        (basic anomaly detection).
        """
        anomalies = []
        for target_field, source_path in schema.items():
            if target_field not in extracted:
                anomalies.append(f"Missing field: {target_field} (mapped from '{source_path}')")
            # Add more sophisticated anomaly detection here, e.g.,
            # - Check data types against expected types
            # - Check for unexpected values (if you have known valid sets)
            # - Implement basic range checks for numerical values
        return anomalies

# Example of how you might use this agent in your main.py:
# if __name__ == "__main__":
#     from memory import SharedMemory
#     memory = SharedMemory()
#     json_agent = JSONAgent(memory)
#     interaction_id = "test_json_001"
#
    dummy_json_payload = """
    {
      "invoiceNumber": "INV-123",
      "invoiceDate": "2025-05-29",
      "seller": {
        "Name": "Tech Solutions Inc.",
        "Address": "777 Innovation Plaza"
      },
      "buyer": {
        "Name": "Global Corp",
        "Address": "888 World HQ"
      },
      "lineItems": [
        {
          "description": "Laptop",
          "quantity": 2,
          "unitPrice": 1200.00,
          "amount": 2400.00,
          "tax": 200.00
        },
        {
          "description": "Mouse",
          "quantity": 5,
          "unitPrice": 25.00,
          "amount": 125.00,
          "tax": 10.00
        }
      ],
      "totalAmount": 2735.00,
      "currency": "USD",
      "extraField": "someValue"
    }
    """
#
#     results = json_agent.process_json(dummy_json_payload, interaction_id)
#     print(json.dumps(results, indent=2))
#     memory.print_all_memory()
#
#     missing_field_json = """
#     {
#       "invoiceNumber": "INV-456",
#       "seller": {
#         "Name": "Data Systems Ltd."
#       },
#       "buyer": {
#         "Name": "Alpha Industries"
#       },
#       "totalAmount": 1000.00,
#       "currency": "EUR"
#     }
#     """
#
#     results_missing = json_agent.process_json(missing_field_json, "test_json_002")
#     print("\n--- Processing JSON with Missing Fields ---")
#     print(json.dumps(results_missing, indent=2))
#     memory.print_all_memory()