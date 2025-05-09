from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tiendita_jm61_user:xstC4ioYv3LTZHTUMCjIJGbtSJ0sCr49@dpg-d0balv95pdvs73cgr1l0-a.oregon-postgres.render.com/tiendita_jm61'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'mitiendita-2025'

db = SQLAlchemy(app)

from app import routes, filters  # Importa las rutas y filtros

