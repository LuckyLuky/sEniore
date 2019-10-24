import os
from flask import Flask, g, request, url_for, render_template, redirect
from flask import render_template
from jinja2 import exceptions  
import psycopg2

app = Flask('seniore')

def get_db():
  
  # https://devcenter.heroku.com/articles/heroku-postgresql#connecting-in-python
    database_url = os.environ['DATABASE_URL']
  #database_url = os.environ["DATABASE_URL"]
    con = psycopg2.connect(database_url, sslmode='require')
    g.db = con
    return g.db


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

@app.route('/database')
def database():
  db_connection = get_db()
  cursor = db_connection.execute('select first_name, surname from users limit 10')
  entries = cur.fetchall()
  for row in entries:
    print("Name: " + row[1] + ", surname: " + row[2])



if __name__ == '__main__':
    app.debug = True
    host = os.environ.get('IP', '127.0.0.1')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)