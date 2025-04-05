## Function

Actual function written in Python.

```python
def get_current_weather(location: str, unit: str = 'celsius') -> dict:
    """
    Retrieves the current weather for a specified location.

    Parameters:
    - location (str): The city and state, e.g., 'San Francisco, CA'.
    - unit (str, optional): Temperature unit, either 'celsius' or 'fahrenheit'. Defaults to 'celsius'.

    Returns:
    - dict: A dictionary containing weather details such as temperature and conditions.
    """
    pass  # Implementation goes here
```

## JSON Representation

This is what the LLM gets:

```json
{
  "name": "get_current_weather",
  "description": "Retrieve the current weather for a specified location.",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "The city and state, e.g., 'San Francisco, CA'."
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "Temperature unit."
      }
    },
    "required": ["location"]
  }
}
```

## Function Call

This is how the LLM "calls" it:

```json
{
  "name": "get_current_weather",
  "arguments": {
    "location": "San Francisco, CA",
    "unit": "celsius"
  }
}
```
