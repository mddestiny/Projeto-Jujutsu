from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def ficha():
    if request.method == "POST":
        dados = request.form
        return render_template("index.html", dados=dados)
    return render_template("index.html", dados=None)

if __name__ == "__main__":
    app.run(debug=True)