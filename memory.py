# memory.py
class SharedMemory:
    def __init__(self):
        self.memory = {}  # Using an in-memory dictionary for simplicity

    def initialize_context(self, interaction_id: str):
        if interaction_id not in self.memory:
            self.memory[interaction_id] = {}
        print(f"Memory initialized for interaction ID: {interaction_id}")

    def store_data(self, interaction_id: str, key: str, value):
        if interaction_id in self.memory:
            self.memory[interaction_id][key] = value
            print(f"Stored '{key}' for interaction ID '{interaction_id}'")
        else:
            print(f"Warning: Interaction ID '{interaction_id}' not found in memory. Cannot store '{key}'.")

    def retrieve_data(self, interaction_id: str, key: str):
        if interaction_id in self.memory and key in self.memory[interaction_id]:
            return self.memory[interaction_id][key]
        return None

    def get_context(self, interaction_id: str):
        return self.memory.get(interaction_id)

    def print_all_memory(self):
        print("\n--- Current Shared Memory Contents ---")
        for interaction_id, context in self.memory.items():
            print(f"Interaction ID: {interaction_id}")
            for key, value in context.items():
                print(f"  {key}: {value}")
        print("--------------------------------------")