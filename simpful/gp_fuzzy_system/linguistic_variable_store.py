from simpful import LinguisticVariable

class LinguisticVariableStore:
    def __init__(self):
        self.variables = {}

    def add_variable(self, name, variable):
        """Add a LinguisticVariable to the store."""
        if not isinstance(variable, LinguisticVariable):
            raise ValueError("Expected an instance of LinguisticVariable")
        self.variables[name] = variable

    def get_variable(self, name):
        """Retrieve a LinguisticVariable by name."""
        return self.variables.get(name)

    def has_variable(self, name):
        """Check if a LinguisticVariable exists in the store."""
        return name in self.variables

    def get_all_variables(self):
        """Return all LinguisticVariables in the store."""
        return self.variables

    def remove_variable(self, name):
        """Remove a LinguisticVariable by name."""
        if name in self.variables:
            del self.variables[name]

    def __repr__(self):
        return f"<LinguisticVariableStore with {len(self.variables)} variables>"

# # Create an instance of the store
# lv_store = LinguisticVariableStore()

# # Add a variable
# lv_store.add_variable("OXI", LV1)

# # Check if a variable exists before using it
# if lv_store.has_variable("OXI"):
#     oxi_variable = lv_store.get_variable("OXI")
#     # Do something with oxi_variable

# # Remove a variable
# lv_store.remove_variable("OXI")

# # Print all variables
# print(lv_store.get_all_variables())

# # Display the store's representation
# print(lv_store)

