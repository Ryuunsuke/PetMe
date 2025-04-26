from flask import request, jsonify, Blueprint, session 
import json
import openai
import time

from functions import fassist

vassistant = Blueprint('vassistant', __name__)

#initialize the assistant to check whether there is existing thread or not
def initialize():
    with open("data/config/tools.json", "r") as file:
        tools = json.load(file)
    with open("data/config/config.json", "r") as file:
        config = json.load(file)
    with open("data/config/assistant_instructions.txt", "r") as f:
        assistant_instructions = f.read()

    openai.api_key = config['api_key']

    thread_id = config['thread_id']
    assistant_id = config['assistant_id']
    print("(BEFORE) Thread ID: ", thread_id)
    if thread_id == "":
        thread = openai.beta.threads.create()
        print(f"Thread created with ID: {thread.id}")

        thread_id = thread.id
        config["thread_id"] = thread_id

        assistant = openai.beta.assistants.create(
            name="Pet Adoption Assistant",
            instructions=assistant_instructions,
            model="gpt-4o-mini",
            tools=tools
        )
        assistant_id = assistant.id
        config["assistant_id"] = assistant_id

        with open("data/config/config.json", "w") as config_file:
            json.dump(config, config_file, indent=4)

        message = "new"
    else:
        message = "old"
    
    session["thread_id"] = thread_id
    session["assistant_id"] = assistant_id

    return message

@vassistant.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message")
    thread_id = session["thread_id"]
    assistant_id = session["assistant_id"]

    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

    # Run the assistant
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Wait for the run to complete
    attempt = 1
    while run.status != "completed":
        print(f"Run status: {run.status}, attempt: {attempt}")
        run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        if run.status == "requires_action":
            break

        if run.status == "failed":
            # Handle the error message if it exists
            if hasattr(run, 'last_error') and run.last_error is not None:
                error_message = run.last_error.message
            else:
                error_message = "No error message found..."

            print(f"Run {run.id} failed! Status: {run.status}\n  thread_id: {run.thread_id}\n  assistant_id: {run.assistant_id}\n  error_message: {error_message}")
            print(str(run))

        attempt += 1
        time.sleep(5)

    # status "requires_action" means that the assistant decided it needs to call an external tool
    # assistant gives us names of tools it needs, we call the corresponding function and return the data back to the assistant
    if run.status == "requires_action":
        print("Run requires action, assistant wants to use a tool")
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        for msg in messages.data:
            if msg.role == "assistant" and msg.content[0].type == "text":
                print("Assistant said:", msg.content[0].text.value)

            elif msg.role == "assistant" and msg.content[0].type == "function_call":
                func = msg.content[0].function_call
                func_name = func.name
                args = json.loads(func.arguments)
                print(f"Assistant called: {func_name} with args: {args}")


        # Process tool calls
        if run.required_action:
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:

                user_id = session["user_Id"]
                type = args["type"]
                breed = args["breed"]
                gender = args["gender"]
                color = args["color"]
                name = args["pet_name"]
                age = args["age"]
                branch = args["branch"]
                approve = args["approve"]
                note = args["note"]

                if tool_call.function.name == "adopt":
                    print("  adopt called")
                    output = fassist.adopt(user_id, name, note)
                elif tool_call.function.name == "donate_pet":
                    print("  donate_pet called")
                    output = fassist.donate_pet(type, breed, gender, color, name, age , branch)
                elif tool_call.function.name == "approve" and session["user_role"] == "coordinator":
                    output = fassist.approve(session["user_id"], name, approve, note)
                else:
                    output = "You are not authorized."
                    print("Unknown function call")
                print(f"  Generated output: {output}")

                # submit the output back to assistant
                openai.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=[{
                        "tool_call_id": tool_call.id,
                        "output": str(output)
                    }]
                )

    if run.status == "requires_action":

        # After submitting tool outputs, we need to wait for the run to complete, again
        run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        attempt = 1
        while run.status not in ["completed", "failed"]:
            print(f"Run status: {run.status}, attempt: {attempt}")
            time.sleep(2)
            run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            attempt += 1

    if run.status == "completed":
        # Retrieve and print the assistant's response
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        final_answer = messages.data[0].content[0].text.value
        print(f"=========\n{final_answer}")
    elif run.status == "failed":
        # Handle the error message if it exists
        if hasattr(run, 'last_error') and run.last_error is not None:
            error_message = run.last_error.message
        else:
            error_message = "No error message found..."

        print(f"Run {run.id} failed! Status: {run.status}\n  thread_id: {run.thread_id}\n  assistant_id: {run.assistant_id}\n  error_message: {error_message}")
        print(str(run))
    else:
        print(f"Unexpected run status: {run.status}")

    return {
        "response": final_answer,
        "message_received": message
    }

@vassistant.route("/history", methods=["GET"])
def history():
    message = initialize()
    thread_id = session["thread_id"]
    print("(AFTER) Thread ID: ", thread_id)
    if message == "new":
        return jsonify({
            "thread_id": thread_id,
            "message": "This thread is new. There is no conversation history."
        })

    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    chat_log = [
        {"role": msg.role, "content": msg.content[0].text.value}
        for msg in reversed(messages.data)
    ]

    return jsonify({
            "thread_id": thread_id,
            "conversation_history": chat_log
        })

