from app import db

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio_compra = db.Column(db.Float, nullable=False)  # Asegúrate de que sea un float
    precio_venta = db.Column(db.Float, nullable=False)    # Asegúrate de que sea un float
    stock = db.Column(db.Integer, nullable=False)         # Asegúrate de que sea un entero
    categoria = db.Column(db.String(50))

    def __repr__(self):
        return f"<Product {self.nombre}>"


class Gasto(db.Model):
    __tablename__ = 'gastos'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Gasto {self.descripcion}: ${self.valor}>"
