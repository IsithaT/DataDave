from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from functioncalls import *
from llm import (
    load_api_key,
    initialize_client,
    create_assistant,
    create_thread,
    send_message,
    run_assistant,
    list_messages,
)
import json
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize OpenAI client and assistant
api_key = load_api_key()
client = initialize_client(api_key)
assistant = create_assistant(client)

# Store active thread information
active_threads = {}


@socketio.on("connect")
def handle_connect():
    """
    Handles new client connections to the WebSocket server.
    Logs when a new client establishes a connection.
    """
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    """
    Handles client disconnections from the WebSocket server.
    Logs when a client terminates their connection.
    """
    print("Client disconnected")


@socketio.on("join_thread")
def handle_join_thread(data):
    """
    Allows a client to join a specific chat thread room.
    Args:
        data: Dictionary containing thread_id to join
    Emits a status message confirming the room join operation.
    """
    thread_id = data.get("thread_id")
    if thread_id:
        join_room(thread_id)
        emit("status", {"msg": f"Joined thread {thread_id}"})


@socketio.on("create_thread")
def handle_create_thread():
    """
    Creates a new chat thread and adds it to active_threads.
    Creates a new room for the thread and adds the client to it.
    Emits thread creation confirmation with the new thread ID.
    """
    thread = create_thread(client)
    active_threads[thread.id] = {"messages": []}
    join_room(thread.id)
    emit("thread_created", {"thread_id": thread.id, "status": "created"})


@socketio.on("send_message")
def handle_send_message(data):
    thread_id = data.get("thread_id")
    message_content = data.get("message")

    if not thread_id or not message_content:
        emit("error", {"msg": "Missing thread_id or message"})
        return

    try:
        # Send message
        message = send_message(client, thread_id, message_content)
        emit(
            "message_sent",
            {"thread_id": thread_id, "message": message_content, "role": "user"},
            room=thread_id,
        )

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant.id,
            instructions="Provide a clear and helpful response",
        )

        # Poll for run completion and handle function calls
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id
            )

            if run_status.status == "requires_action":
                tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(
                        f"Calling function: {function_name} with args: {function_args}"
                    )

                    if function_name == "calculateMean":
                        result = calculateMean(**function_args)
                        tool_outputs.append(
                            {"tool_call_id": tool_call.id, "output": str(result)}
                        )

                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs
                )
                continue

            if run_status.status == "completed":
                break

            time.sleep(1)

        # Get and broadcast response
        messages = list_messages(client, thread_id)
        emit(
            "message_received",
            {
                "thread_id": thread_id,
                "messages": [
                    {"role": msg.role, "content": msg.content[0].text.value}
                    for msg in messages.data
                ],
            },
            room=thread_id,
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        emit("error", {"msg": str(e)})


@socketio.on("clear_thread")
def handle_clear_thread(data):
    """
    Clears all messages in a specific chat thread.
    Args:
        data: Dictionary containing thread_id to clear
    Emits a status message confirming the thread clear operation.
    """
    thread_id = data.get("thread_id")
    if thread_id in active_threads:
        active_threads[thread_id]["messages"] = []
        emit(
            "thread_cleared",
            {"thread_id": thread_id, "status": "cleared"},
            room=thread_id,
        )
    else:
        emit("error", {"msg": "Invalid thread_id"})


@socketio.on("send_csv")
def handle_send_csv(data):
    thread_id = data.get("thread_id")
    csv_content = data.get("csvContent")

    try:
        # Parse CSV headers
        headers = getFirstRowFromCSV(csv_content)
        dataRow = getFirstDataRowFromCSV(csv_content)
        print(f"Processing CSV with headers: {headers}")

        # Store CSV content globally for function calls
        setcsv(csv_content)

        # Send confirmation to client
        emit(
            "csv_processed",
            {"thread_id": thread_id, "headers": headers},
            room=thread_id,
        )

        # Initialize conversation with CSV context
        message = send_message(
            client,
            thread_id,
            f"I've loaded a CSV file. It is ready to be analyzed.",
        )
        print(dataRow)

        # Run initial analysis
        run = run_assistant(
            client,
            thread_id,
            assistant.id,
            f"Please acknowledge the CSV data and ask how you can help analyze it. An example row of data is {dataRow}",
        )
        # Get and send response
        messages = list_messages(client, thread_id)
        emit(
            "message_received",
            {
                "messages": [
                    {"role": msg.role, "content": msg.content[0].text.value}
                    for msg in messages.data
                ]
            },
            room=thread_id,
        )

    except Exception as e:
        print(f"CSV Processing Error: {str(e)}")
        emit("error", {"msg": f"Error processing CSV: {str(e)}"})


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)
