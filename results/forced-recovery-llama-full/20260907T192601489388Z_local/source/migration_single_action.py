"""Opt-in named-tool transport for servers that ignore parallel_tool_calls=False.

The model selects an action inside one constrained named function. This changes
the model-facing interface, not the tools' authorization or execution semantics.
"""

INTERFACE_VERSION = "named-single-action-v1"
DISPATCH = "submit_action"


def dispatch_schema(registered_tools):
    choices = []
    for tool in registered_tools:
        choices.append({
            "type": "object",
            "properties": {
                "name": {"type": "string", "enum": [tool.name]},
                "parameters": tool.args_schema.model_json_schema(),
            },
            "required": ["name", "parameters"],
            "additionalProperties": False,
        })
    return {
        "type": "function",
        "function": {
            "name": DISPATCH,
            "description": "Select exactly one of the available actions by name and supply its parameters. The action will execute before your next decision.",
            "parameters": {"type": "object", "anyOf": choices},
        },
    }


class SingleActionResponder:
    def __init__(self, model, registered_tools):
        self.names = {tool.name for tool in registered_tools}
        self.bound = model.bind_tools(
            [*registered_tools, dispatch_schema(registered_tools)],
            tool_choice={"type": "function", "function": {"name": DISPATCH}},
            parallel_tool_calls=False,
        )

    def invoke(self, messages):
        raw = self.bound.invoke(messages)
        response = raw.model_copy(deep=True)
        response.additional_kwargs["single_action_transport"] = {
            "version": INTERFACE_VERSION, "raw_response": raw.model_dump(mode="json"),
        }
        # Never pick the first of multiple calls or repair malformed arguments.
        # Returning the unchanged call makes the pilot's validator reject it and
        # retain the complete provider response in the invalid-trial journal.
        calls = raw.tool_calls
        if raw.invalid_tool_calls or len(calls) != 1 or calls[0]["name"] != DISPATCH:
            # Even a valid direct action violates the requested transport.
            response.invalid_tool_calls.append({"name": DISPATCH, "args": "",
                "id": None, "error": "Expected exactly one submit_action call",
                "type": "invalid_tool_call"})
            return response
        args = calls[0]["args"]
        if (set(args) != {"name", "parameters"} or not isinstance(args.get("name"), str)
                or args["name"] not in self.names or not isinstance(args["parameters"], dict)):
            return response
        response.tool_calls = [{"name": args["name"], "args": args["parameters"],
                                "id": calls[0]["id"], "type": "tool_call"}]
        # Outgoing history describes the executed action, not the transport.
        response.additional_kwargs.pop("tool_calls", None)
        return response
