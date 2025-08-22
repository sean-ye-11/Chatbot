from flask import Flask, request, render_template
from adv_bot_oop import Chatbot

app = Flask(__name__, static_folder="public", static_url_path="/public")
system_content = "You are an AI assistant."
bot = Chatbot(system_content)

# Use GET method to deal with path /
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form.get("query", "")
        if query:
            bot.get_response(query, "gpt-4.1-nano", 100)
    return render_template("index.html", history=bot.conversation_history)

if __name__ == "__main__":
    app.run()



 
    