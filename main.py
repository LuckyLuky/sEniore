import os
from flask import Flask
from flask import render_template  # !Important

app = Flask(__name__)


@app.route('/')
def index():
    return render_template ('layout.html')

@app.route('/registrace')
def registrace():
    return render_template ('registrace.html')

@app.route('/prehled')
def prehled():
    return render_template ('prehled.html')

@app.route('/sluzby')
def sluzby():
    return render_template ('sluzby.html')


if __name__ == '__main__':
    app.debug = True
    host = os.environ.get('IP', '127.0.0.1')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)