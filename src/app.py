import os
import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
#openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"
print(openai.api_key)

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        feel_input = request.form["feel_input"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(feel_input),
            temperature=0.6,
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(feel_input):
    return """Suggest three names for an animal that is a superhero.

Animal: Cat
Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
Animal: Dog
Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
Animal: {}
Names:""".format(
        feel_input.capitalize()
    )
