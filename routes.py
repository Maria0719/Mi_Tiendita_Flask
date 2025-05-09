from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Product, Gasto
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/index')
def index():
    products = Product.query.all()
    return render_template('index.html', productos=products)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            precio_compra = float(request.form['precio_compra'])
            ganancia_percent = float(request.form['ganancia'])
            stock = int(request.form['stock'])
            categoria = request.form['categoria']

            precio_venta = precio_compra * (1 + ganancia_percent / 100)

            nuevo_producto = Product(
                nombre=nombre,
                precio_compra=precio_compra,
                precio_venta=precio_venta,
                stock=stock,
                categoria=categoria
            )

            db.session.add(nuevo_producto)
            db.session.commit()
            flash('Producto agregado exitosamente!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Ocurrió un error al agregar el producto: {e}', 'danger')
            return redirect(url_for('agregar'))

    return render_template('agregar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    producto = Product.query.get_or_404(id)
    if request.method == 'POST':
        try:
            producto.nombre = request.form['nombre']
            precio_compra = float(request.form['precio_compra'])
            ganancia_percent = float(request.form['ganancia'])
            producto.precio_compra = precio_compra
            producto.precio_venta = precio_compra * (1 + ganancia_percent / 100)
            producto.stock = int(request.form['stock'])
            producto.categoria = request.form['categoria']

            db.session.commit()
            flash('Producto actualizado exitosamente!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Ocurrió un error al actualizar el producto: {e}', 'danger')
            return redirect(url_for('editar', id=id))

    return render_template('editar.html', producto=producto)

@app.route('/eliminar_producto/<int:id>', methods=['POST'])
def eliminar_producto(id):
    producto = Product.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado exitosamente!', 'success')
    return redirect(url_for('index'))

@app.route('/ganancias')
def ganancias():
    productos = Product.query.all()
    gastos = Gasto.query.all()

    valor_total_compra = sum(p.precio_compra * p.stock for p in productos)
    valor_total_venta = sum(p.precio_venta * p.stock for p in productos)
    total_ganancia = valor_total_venta - valor_total_compra
    total_gastos = sum(g.valor for g in gastos)
    ganancia_final = total_ganancia - total_gastos

    return render_template('ganancias.html', 
                valor_compra_total=valor_total_compra, 
                valor_venta_total=valor_total_venta, 
                total_gastos=total_gastos, 
                ganancias_total=ganancia_final)

@app.route('/graficas')
def graficas():
    productos = Product.query.all()
    gastos = Gasto.query.all()

    sns.set_style('whitegrid')

    datos_productos = []
    for p in productos:
        if p.precio_compra > 0:
            porcentaje = ((p.precio_venta - p.precio_compra) / p.precio_compra) * 100
        else:
            porcentaje = 0
        datos_productos.append({
            "nombre": p.nombre,
            "precio_compra": p.precio_compra,
            "precio_venta": p.precio_venta,
            "stock": p.stock,
            "ganancia_porcentaje": porcentaje,
            "ganancia_total": (p.precio_venta - p.precio_compra) * p.stock
        })

    df = pd.DataFrame(datos_productos)
    total_gastos = sum(g.valor for g in gastos)
    ganancia_bruta = df["ganancia_total"].sum()
    ganancia_neta = ganancia_bruta - total_gastos

    # Gráfica 1: porcentaje de ganancia
    fig1, ax1 = plt.subplots(figsize=(max(10, len(df) * 1.2), 6))
    colores = sns.color_palette("Purples", len(df))
    sns.barplot(x="nombre", y="ganancia_porcentaje", data=df, ax=ax1, palette=colores)
    ax1.set_ylim(0, 110)
    ax1.set_title("Porcentaje de Ganancia por Producto", fontsize=14, weight="bold")
    ax1.set_ylabel("Ganancia (%)")
    ax1.set_xlabel("Producto")
    ax1.tick_params(axis='x', rotation=30)
    for i, row in df.iterrows():
        ax1.text(i, row["ganancia_porcentaje"] + 2, f'{row["ganancia_porcentaje"]:.0f}%', ha='center', fontsize=10, color='black')
    fig1.subplots_adjust(top=0.85, bottom=0.2)
    buf1 = io.BytesIO()
    fig1.savefig(buf1, format='png')
    buf1.seek(0)
    grafica1 = base64.b64encode(buf1.getvalue()).decode('utf-8')
    plt.close(fig1)

    # Gráfica 2: resumen financiero
    df_finanzas = pd.DataFrame({
        "Categoría": ["Ganancia Bruta", "Gastos", "Ganancia Neta"],
        "Valor": [ganancia_bruta, total_gastos, ganancia_neta]
    })
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    colores = ["#4caf50", "#f44336", "#2196f3"]
    sns.barplot(x="Categoría", y="Valor", data=df_finanzas, ax=ax2, palette=colores)
    ax2.set_title("Resumen Financiero")
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format='png')
    buf2.seek(0)
    grafica2 = base64.b64encode(buf2.getvalue()).decode('utf-8')
    plt.close(fig2)

    return render_template('graficas.html', grafica1=grafica1, grafica2=grafica2)

@app.route('/gastos')
def gastos():
    lista_gastos = Gasto.query.all()
    total = sum(g.valor for g in lista_gastos)
    return render_template('gastos.html', gastos=lista_gastos, total=total)

@app.route('/agregar_gasto', methods=['GET', 'POST'])
def agregar_gasto():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        valor = float(request.form['valor'])
        nuevo_gasto = Gasto(descripcion=descripcion, valor=valor)
        db.session.add(nuevo_gasto)
        db.session.commit()
        flash('Gasto agregado correctamente', 'success')
        return redirect(url_for('gastos'))
    return render_template('agregar_gasto.html')

@app.route('/editar_gasto/<int:id>', methods=['GET', 'POST'])
def editar_gasto(id):
    gasto = Gasto.query.get_or_404(id)
    if request.method == 'POST':
        gasto.descripcion = request.form['descripcion']
        gasto.valor = float(request.form['valor'])
        db.session.commit()
        flash('Gasto actualizado exitosamente!', 'success')
        return redirect(url_for('gastos'))
    return render_template('editar_gasto.html', gasto=gasto)

@app.route('/eliminar_gasto/<int:id>', methods=['POST'])
def eliminar_gasto(id):
    gasto = Gasto.query.get_or_404(id)
    db.session.delete(gasto)
    db.session.commit()
    flash('Gasto eliminado exitosamente!', 'success')
    return redirect(url_for('gastos'))