from tkinter import *
import tkinter.ttk as ttk
import sqlite3
import datetime
import tkinter.messagebox
import re

# Conectar con base de datos de los gastos
conn = sqlite3.connect("gastos6.db")
cur = conn.cursor()


# Crear ventana
ventana = Tk()
ventana.title("Gestor De Gastos Por Uriel55")
ventana.geometry("950x650+180+10")
ventana.resizable(False,False)
ventana.config(background='#99061f')

icono = PhotoImage(file='imgs/money_icon.png')
ventana.iconphoto(True, icono)


# Verificar la entrada de la fecha
def fecha_valida(fecha_string):
    # Verifica que la fecha tenga el formato YYYY-MM-DD
    fecha_formato = re.compile(r'\d{4}-\d{2}-\d{2}')
    if fecha_formato.match(fecha_string):
        return True
    else:
        return False

# Guardar un gasto nuevo
def guardarNuevo():
    # Recoger datos de las entradas
    fecha = nuevo_fecha.get()
    nuevo_fecha.delete(0,END)
    
    descripcion = nuevo_descripcion.get()
    nuevo_descripcion.delete(0,END)
    
    precio = nuevo_precio.get()
    nuevo_precio.delete(0,END)
    
    categoria = nuevo_categoria.get()
    nuevo_categoria.delete(0,END)
    
    # Validar formato de la fecha ingresada
    validacion_fecha = fecha_valida(fecha)
    
    if precio.isdigit() and validacion_fecha:

        # Insertar nuevo gasto en la base de datos
        cur.execute("INSERT INTO gastos (fecha, descripcion, categoria, precio) VALUES (?,?,?,?)", (fecha, descripcion, categoria, precio))
        conn.commit()
        
        # Actualizar vista de los gastos
        nuevoReg = "SELECT * FROM gastos ORDER BY id DESC LIMIT 1"
        cur.execute(nuevoReg)
        ultimoReg = cur.fetchone()

        tree.insert("", "end", text=ultimoReg[0], values=(ultimoReg[1], ultimoReg[2], ultimoReg[3], str(ultimoReg[4])+" $"))
        
        # Actualizar gasto total
        global gastoTot
        gastoTot += float(precio)
        totalGasto.config(text=str(gastoTot)+" $")
    
    else:
        tkinter.messagebox.showwarning("Advertencia", "Entrada no válida")


# Confiramar si un valor existe en la base de datos
def confirmar_busqueda(valor,columna):
    consulta = f"SELECT count(*) FROM gastos WHERE {columna} = ?"
    cur.execute(consulta, (valor,))
    resultado = cur.fetchone()[0]
    
    return resultado > 0

# Busqueda de un gasto
def filtrar_buscar():
    # Recoger datos de las entradas
    descripcion = nuevo_descripcion.get()
    categoria = nuevo_categoria.get()
    precio = nuevo_precio.get()
    
    fecha = nuevo_fecha.get()
    
    # Consultar elementos de la base de datos que coincidan con los datos ingresados
    consulta_gastos = "SELECT * FROM gastos WHERE 1=1"
    consulta_total = "SELECT SUM(precio) FROM gastos WHERE 1=1"
    
    # Consultar por fecha
    if fecha:
        if confirmar_busqueda(fecha,"fecha"):
            fecha_separada = fecha.split("-")
            año = fecha_separada[0]
            mes = fecha_separada[1]

            consulta_gastos += f" AND strftime('%Y-%m',fecha) = '{año}-{mes}'"
            consulta_total += f" AND strftime('%Y-%m',fecha) = '{año}-{mes}'"

        else:
            tkinter.messagebox.showwarning("Advertencia", "Valor No Encontrado")
    
    # Consultar por descripción  
    if descripcion:
        if confirmar_busqueda(descripcion,"descripcion"):
            consulta_gastos += f" AND descripcion = '{descripcion}'"
            consulta_total += f" AND descripcion = '{descripcion}'"
        else:
            tkinter.messagebox.showwarning("Advertencia", "Valor No Encontrado")
    
    # Consultar por categoria
    if categoria:
        if confirmar_busqueda(categoria,"categoria"):
            consulta_gastos += f" AND categoria = '{categoria}'"
            consulta_total += f" AND categoria = '{categoria}'"
        else:
            tkinter.messagebox.showwarning("Advertencia", "Valor No Encontrado")
    
    # Consultar por precio  
    if precio:
        if confirmar_busqueda(precio,"precio"):
            consulta_gastos += f" AND precio = {precio}"
            consulta_total += f" AND precio = {precio}"
        else:
            tkinter.messagebox.showwarning("Advertencia", "Valor No Encontrado")

    cur.execute(consulta_gastos)
    resultados = cur.fetchall()
    
    # Actualizar vista de los gastos
    tree.delete(*tree.get_children())
    
    for resultado in resultados:
        tree.insert("", "end", text=resultado[0], values=(resultado[1], resultado[2], resultado[3], str(resultado[4])+" $"))
    
    # Actualizar gasto total
    cur.execute(consulta_total)
    total = cur.fetchall()
    gastoTot = total[0][0]
    
    totalGasto.config(text=str(gastoTot)+" $")
    


# Obtener la fecha actual para asignársela a un gasto
def obtenerFechaActual():
    fechaActual = datetime.datetime.now().strftime("%Y-%m-%d")
    nuevo_fecha.insert(0, fechaActual)
    
    
# Limpiar las entradas
def limpiarEntradas():
    nuevo_fecha.delete(0, "end")
    nuevo_descripcion.delete(0, "end")
    nuevo_categoria.delete(0, "end")
    nuevo_precio.delete(0, "end")
    
    
# Seleccionar item de la vista de gastos
def seleccionar_gasto(event):
    seleccion_item = tree.selection()[0]
 
    seleccion_id = tree.item(seleccion_item)["text"]

    cur.execute("SELECT * FROM gastos WHERE id=?", (seleccion_id,))
    result = cur.fetchone()
    
    
    nuevo_fecha.delete(0, END)
    nuevo_fecha.insert(0, result[1])
    nuevo_descripcion.delete(0, END)
    nuevo_descripcion.insert(0, result[2])
    nuevo_categoria.delete(0, END)
    nuevo_categoria.insert(0, result[3])
    nuevo_precio.delete(0, END)
    nuevo_precio.insert(0, result[4])
    
    botonEliminar.config(state=ACTIVE)
    
    return result
    
    

# Eliminar un gasto
def eliminar_gasto():
    gasto = seleccionar_gasto(event=True)
    
    # Consulta a la base de datos en base al gasto seleccionado
    consulta = "DELETE FROM gastos WHERE id = ?"
    
    # Eliminar item seleccionado de la vista de gastos
    cur.execute(consulta, (gasto[0],))
    conn.commit()
    
    # Actualizar la vista de gastos
    cur.execute("SELECT * FROM gastos")
    gastos = cur.fetchall()
    gastos = gastos[::-1] 
    
    global gastoTot
    
    # Actualizar gasto total
    gastoTot -= float(gasto[4])
    totalGasto.config(text=str(gastoTot)+" $")
    
    tree.delete(*tree.get_children())
    for gasto in gastos:
        tree.insert("", 0, text=gasto[0], values=(gasto[1], gasto[2], gasto[3], str(gasto[4])+" $"))
        
        
    botonEliminar.config(state=DISABLED)
        

# Simular dinero extra
def descontar_gasto():
    global gastoTot
    modific = modificacion.get()
    if modific.isdigit():
        gastoTot -= float(modific)
        totalGasto.config(text=str(gastoTot)+" $")
    
# Simular gasto extra
def duplicar_gasto():
    global gastoTot
    modific = modificacion.get()
    if modific.isdigit():
        gastoTot += float(modific)
        totalGasto.config(text=str(gastoTot)+" $")
    
# Mostrar el gasto total real de los elementos en la base de datos
def restaurar_gasto_total():
    global gastoTot
    cur.execute("SELECT SUM(precio) FROM gastos")
    result = cur.fetchone()
    gastoTot = result[0]
    totalGasto.config(text=str(gastoTot)+" $")

# Cerrar y salir del programa
def salir():
    exit()
    



# Cuadro para la vista de gastos
cuadro1 = Frame(ventana, bd=3, width=10, height=980, bg="#32405b")
cuadro1.place(x=0,y=0)

# Cuadro de vista para elementos separados por columnas
tree = ttk.Treeview(cuadro1, style="mystyle.Treeview")
style = ttk.Style()
style.configure("mystyle.Treeview", background="#32405b", foreground="white")

tree["columns"] = ("one", "two", "three", "four")
tree.column("#0", width=189, minwidth=150, stretch=NO)
tree.column("one", width=189, minwidth=150, stretch=NO)
tree.column("two", width=189, minwidth=150, stretch=NO)
tree.column("three", width=189, minwidth=150, stretch=NO)
tree.column("four", width=189, minwidth=150, stretch=NO)
tree.pack()

tree.heading("#0", text="Id", anchor=W)
tree.heading("one", text="Fecha", anchor=W)
tree.heading("two", text="Descripcion", anchor=W)
tree.heading("three", text="Categoria", anchor=W)
tree.heading("four", text="Cantidad", anchor=W)

# Mostrar todos los gastos actuales
cur.execute("SELECT * FROM gastos")
gastos = cur.fetchall()
gastos = gastos[::-1] 
for gasto in gastos:
    tree.insert("", 0, text=gasto[0], values=(gasto[1], gasto[2], gasto[3], str(gasto[4])+" $"))


# Seleccionar item de la vista de gastos
tree.bind("<<TreeviewSelect>>", lambda event: seleccionar_gasto(event))


# Cuadro para el ingreso de datos
cuadro2 = Frame(ventana, width=480, height=400, bg="green")
cuadro2.place(x=0,y=250)

# Ingreso de descripciones
ingreso_descripcion = Label(cuadro2, text="Nombre De Articulo:", font="Arial 12 bold", bg='green')
ingreso_descripcion.place(x=5,y=19)

nuevo_descripcion = StringVar()
nuevo_descripcion= Entry(cuadro2, width=20, font="arial 12",bd=0)
nuevo_descripcion.place(x=200,y=20)
nuevo_descripcion.focus()

# Ingreso de precios
ingreso_precio = Label(cuadro2, text="Precio:", font="Arial 12 bold", bg='green')
ingreso_precio.place(x=5,y=59)

nuevo_precio = StringVar()
nuevo_precio= Entry(cuadro2, width=20, font="arial 12",bd=0)
nuevo_precio.place(x=200,y=60)
nuevo_precio.focus()

# Ingreso de categorias
ingreso_categoria = Label(cuadro2, text="Categoría:", font="Arial 12 bold", bg='green')
ingreso_categoria.place(x=5,y=99)

nuevo_categoria = StringVar()
nuevo_categoria= Entry(cuadro2, width=20, font="arial 12",bd=0)
nuevo_categoria.place(x=200,y=100)
nuevo_categoria.focus()

# Ingreso de fechas
ingreso_fecha = Label(cuadro2, text="Fecha De Adquisición:", font="Arial 12 bold", bg='green')
ingreso_fecha.place(x=5,y=139)

nuevo_fecha = StringVar()
nuevo_fecha= Entry(cuadro2, width=20, font="arial 12",bd=0)
nuevo_fecha.place(x=200,y=140)
nuevo_fecha.focus()

botonFecha = Button(cuadro2, text="Fecha Actual", width=25, command=obtenerFechaActual)
botonFecha.place(x=200,y=162)



# Opciones de ingreso de datos
botonGuardar = Button(cuadro2, text="Guardar", width=9, command=guardarNuevo)
botonGuardar.place(x=150,y=230)

botonBuscar = Button(cuadro2, text="Buscar", width=9, command=filtrar_buscar)
botonBuscar.place(x=150,y=270)

botonLimpiar = Button(cuadro2, text="Limpiar", width=9, command=limpiarEntradas)
botonLimpiar.place(x=150,y=310)

botonEliminar = Button(cuadro2, text="Eliminar", width=9, command=eliminar_gasto, state=DISABLED)
botonEliminar.place(x=150,y=350)

botonSalir = Button(cuadro2, text="Salir", width=9, command=salir)
botonSalir.place(x=10,y=350)


# Cuadro para gasto total
cuadro3 = Frame(ventana, width=450, height=400, bg="blue")
cuadro3.place(x=500,y=250)

totalGastoTexto = Label(cuadro3, text="Total:", font="Arial 30 bold", bg='blue', fg='#99061f')
totalGastoTexto.place(x=10,y=20)

# Obtener suma de los precios de todos los gastos
cur.execute("SELECT SUM(precio) FROM gastos")
result = cur.fetchone()
gastoTot = result[0]

# Mostrar la suma de todos los precios
totalGasto = Label(cuadro3, text=f"{gastoTot} $", font="Arial 15 bold", width=12, height=6, bg='#99061f')
totalGasto.place(x=10,y=70)

# Ingreso de dinero extra
ingreso_operar = Label(cuadro3, text="Modificar", font="Arial 15 bold", bg='blue')
ingreso_operar.place(x=245,y=20)

# Modificaciones al gasto total
modificacion = StringVar()
modificacion = Entry(cuadro3, width=20, font="arial 12",bd=0)
modificacion.place(x=250,y=50)
modificacion.focus()

botonSumar = Button(cuadro3, text="Sumar", width=9, height=3, command=duplicar_gasto, background='#056b73')
botonSumar.place(x=250,y=100)

botonRestar = Button(cuadro3, text="Restar", width=9, height=3, command=descontar_gasto, background='#056b73')
botonRestar.place(x=350,y=100)

# Volver a mostrar suma de todos los precios
botonRestaurar = Button(cuadro3, text="Restaurar", width=14, height=3, command=restaurar_gasto_total, background='#02c6d4')
botonRestaurar.place(x=280,y=180)


# Imagenes
imagen1 = PhotoImage(file='imgs/bolsa.png').subsample(4)
etiqImg1 = Label(cuadro2, image=imagen1, bg='green')
etiqImg1.place(x=300,y=250)


imagen2 = PhotoImage(file='imgs/calcu.png').subsample(4)
etiqImg2 = Label(cuadro3, image=imagen2, bg='blue')
etiqImg2.place(x=20,y=250)


imagen3 = PhotoImage(file='imgs/calcu2.png').subsample(6)
etiqImg3 = Label(cuadro3, image=imagen3, bg='blue')
etiqImg3.place(x=310,y=290)

ventana.mainloop()
