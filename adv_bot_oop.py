from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from temperature import get_temperature
import os
import json

# Load the API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

class Chatbot:
    def __init__(self, system_content):
        # conversation_history is for human to read and used in save_conversation method
        self.conversation_history = []
        # machine_history is for AI to generate accuate replies.
        # machine_history will be substituted into the client.chat.completions.create method to generate replies.
        self.machine_history = []
        # set the system content by prompt engineering
        self.system = [{"role": "system", "content": system_content}]
        # store the tool definition
        self.tools = [{
            "type": "function",
            "function": {
                "name": "get_temperature",
                "description": "Get current temperature for provided coordinates in celsius.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"}
                    },
                    "required": ["latitude", "longitude"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }]
    
    def get_response(self, user_input, model, max_token):
        # Append query into the conversation_history
        self.conversation_history.append({"role": "user", "content": user_input})
        # Append query into the machine_history
        self.machine_history.append({"role": "user", "content": user_input})
        # response_1 - first chat completion
        response_1 = client.chat.completions.create(
        model=model,
        messages=self.system + self.machine_history,
        max_tokens=max_token,
        tools=self.tools
        )
        # Check whether tool is required in response_1
        tool_calls = response_1.choices[0].message.tool_calls
        # If tool_calls is NOT None, tool is required
        # We will to do function calling!!!!
        if tool_calls != None:
            # Append response_1.choices[0].message into the machine_history
            self.machine_history.append(response_1.choices[0].message)
            # Multiple tool calls may be required for query like: current temperature of Hong Kong and Singapore
            for tool_call in tool_calls:
                # Get the inputs for the get_temperature function
                args = json.loads(tool_call.function.arguments)
                # Substitute the inputs gotten from the above into the get_temperature function
                result = get_temperature(args["latitude"], args["longitude"])
                # Append a tool dictionary 
                self.machine_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
            # response_2 - second chat completion
            response_2 = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=self.system + self.machine_history,
            tools=self.tools
            )
            # The reply after using function calling
            reply = response_2.choices[0].message.content
            # Append the above reply into the machine_history
            self.machine_history.append({"role": "assistant", "content": reply})
            # Append the above reply into the conversation_history
            self.conversation_history.append({"role": "assistant", "content": reply})
        else:
            # If tool_calls is None, tool is NOT required
            # We don't do function calling!!!!
            # The usual reply without using function calling
            reply = response_1.choices[0].message.content
            # Append the above reply into the machine_history
            self.machine_history.append({"role": "assistant", "content": reply})
            # Append the above reply into the conversation_history
            self.conversation_history.append({"role": "assistant", "content": reply})
        return reply
    
    def clear_history(self):
        self.conversation_history = []
        self.machine_history = []
        print("Conversation History Cleared!")

    # Only conversation_history is considered!
    # Reason: people just care the query and reply. They don't want to know what function calling is...
    def save_conversation(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        filename = f"conversation_{timestamp}.txt"
        with open(filename, "w") as f:
            # Consider conversation_history
            for message in self.conversation_history:
                role = message["role"]
                content = message["content"]
                if role == "user":
                    f.write(f"You: {content} \n")
                else:
                    f.write(f"Bot: {content} \n")
        return filename

def main():
    # set the system content
    system_content = "You are a pikachu."
    chatbot = Chatbot(system_content)
    print("Welcome to the Chatbot")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Bot: Goodbye! See you next time.")
            break
        elif user_input.lower() == "clear_history":
            chatbot.clear_history()
        elif user_input.lower() == "save_history":
            chatbot.save_conversation()
        else:
            reply = chatbot.get_response(user_input, "gpt-4.1-nano", 200)
            print(f"Bot: {reply}")

if __name__ == "__main__":
    main()

