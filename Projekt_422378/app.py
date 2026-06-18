from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1>Witaj w chmurze! Projekt 4.0 dziala na AKS!</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)