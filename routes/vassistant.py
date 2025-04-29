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

def rebuildinit():
    with open("data/config/config.json", "r") as file:
        config = json.load(file)
    config["thread_id"] = ""
    with open("data/config/config.json", "w") as config_file:
            json.dump(config, config_file, indent=4)
    initialize()

@vassistant.route("/chat/", methods=["POST"])
def chat():
    message = request.args.get('message')
    thread_id = session["thread_id"]
    assistant_id = session["assistant_id"]

    try:
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        rebuildinit()
        return {
            "response": "Please ask again because the assistant has run into error.",
            "message_received": message
        }


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

    try:
        # status "requires_action" means that the assistant decided it needs to call an external tool
        # assistant gives us names of tools it needs, we call the corresponding function and return the data back to the assistant
        if run.status == "requires_action":
            print("Run requires action, assistant wants to use a tool.")

            # Get the latest messages
            messages = openai.beta.threads.messages.list(thread_id=thread_id)

            for msg in messages.data:
                if msg.role == "assistant":
                    # Loop through all content blocks inside the assistant message
                    for content in msg.content:
                        if content.type == "text":
                            print("Assistant said:", content.text.value)

                        elif content.type == "function_call":
                            func = content.function_call
                            func_name = func.name
                            # func.arguments is already a JSON string, so we parse it
                            try:
                                args = json.loads(func.arguments)
                                print(f"Assistant called: {func_name} with args: {args}")
                            except json.JSONDecodeError:
                                print("Failed to decode function call arguments.")

            # Process tool calls
            if run.required_action:
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    user_id = session["user_id"]

                    type = args.get("type")
                    breed = args.get("breed")
                    gender = args.get("gender")
                    color = args.get("color")
                    name = args.get("pet_name")
                    age = args.get("age")
                    branch = args.get("location")
                    approve = args.get("approve")
                    if approve == "approved":
                        approve = 1
                    elif approve == "rejected":
                        approve = -1
                    note = args.get("note")

                    if session["user_role"] == "client":
                        if func_name == "adopt":
                            print("  adopt called")
                            output = fassist.adopt(user_id, name, note)
                        elif func_name == "donate_pet":
                            print("  donate_pet called")
                            output = fassist.donate_pet(type, breed, gender, color, name, age , branch)
                        elif func_name == "check_user_existing_adopt":
                            print(" check_user_existing_adopt called ")
                            output = fassist.check_user_existing_adopt(user_id)
                        elif func_name == "check_adoption_status":
                            print(" check_adoption_status called ")
                            output = fassist.check_adoption_status_for_client(name)
                        elif func_name == "status_reason":
                            print(" status_reason called ")
                            output = fassist.status_reason(name)
                        else:
                            output = "You are not authorized."
                            print("Unknown function call")
                            print(f"  Generated output: {output}")
                    elif session["user_role"] == "coordinator":
                        if func_name == "approve":
                            print(" approve called ")
                            output = fassist.approve(user_id, name, approve, note)
                        elif func_name == "check_approval":
                            print("  check_approval called ")
                            output = fassist.check_coordinator_approvals(user_id)
                        elif func_name == "donate_pet":
                            print("  donate_pet called ")
                            output = fassist.donate_pet(type, breed, gender, color, name, age , branch)
                        elif func_name == "modify_status":
                            print(" modify_status called ")
                            output = fassist.modify_status(user_id, name, approve, note)
                        elif func_name == "check_adoption_status":
                            print(" check_adoption_status called ")
                            output = fassist.check_adoption_status_for_client(name)
                        elif func_name == "status_reason":
                            print(" status_reason called ")
                            output = fassist.status_reason(name)
                        else:
                            output = " You are not authorized. "
                            print("Unknown function call")
                            print(f"  Generated output: {output}")
                    else:
                        output = " Unknown user role "
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
    except Exception as e:
        print(f"An error occurred: {e}")
        rebuildinit()
        return {
            "response": "Please contact an administrator because the assistant has run into error.",
            "message_received": message
        }

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
    if not chat_log:
        return jsonify({
            "thread_id": thread_id,
            "message": "This thread is new. There is no conversation history."
        })

    return jsonify({
            "thread_id": thread_id,
            "conversation_history": chat_log
        })

