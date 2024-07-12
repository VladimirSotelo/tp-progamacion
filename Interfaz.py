from tkinter import Tk, Label, Entry, Button, Listbox, Scrollbar, END
from tkinter.messagebox import showinfo,showerror
from tkinter.ttk import Frame,Style
import requests
import hashlib
import json
from datetime import datetime

class Persona:
    def __init__(self, id=None, nombre=None, apellido=None, fecha_nacimiento=None,dni=None):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        if fecha_nacimiento != None:
            self.fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        else:
            self.fecha_nacimiento = None
        self.dni = dni

class Usuario(Persona):
    def __init__(self, id=None, nombre=None, apellido=None, fecha_nacimiento=None, dni=None, contraseña="", nombre_usuario=""):
        super().__init__(id=id, nombre=nombre, apellido=apellido, fecha_nacimiento=fecha_nacimiento, dni=dni)
        self.contraseña = hashlib.md5(contraseña.encode()).hexdigest()
        self.nombre_usuario = nombre_usuario
        self.ultimo_accesos = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> dict:
        return {
            "username": self.nombre_usuario,
            "password": self.contraseña
        }
    def ultimo_acceso(self):
        return self.ultimo_accesos
        
        

class AppGUI(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.host = "127.0.0.1"
        self.port = 8000
        self.URL=f"http://{self.host}:{self.port}"
        self.TOKEN = ''
        self.autor = ''
        self.master = master
        self.master.title('Administrador de Tareas')
        self.master.geometry('600x400+350+150')


        self.con2 = Frame(master)
        self.con2.pack(side="top")
        self.con = Frame(master)
        self.con.pack(side="right")
        


        self.label_titulo = Label(self.con, text='Título:')
        self.label_titulo.pack()
        self.entry_titulo = Entry(self.con)
        self.entry_titulo.pack()

        self.label_descripcion = Label(self.con, text='Descripción:')
        self.label_descripcion.pack()
        self.entry_descripcion = Entry(self.con)
        self.entry_descripcion.pack()

        self.label_estado = Label(self.con, text='Estado:')
        self.label_estado.pack()
        self.entry_estado = Entry(self.con)
        self.entry_estado.pack()

        self.button_agregar = Button(
            self.con, text='Agregar Tarea', command=self.agregar_tarea)
        self.button_agregar.pack()


        self.button_ver = Button(
            self.con, text='Ver Tarea', command=self.ver_tarea)
        self.button_ver.pack()

        self.button_actualizar = Button(
            self.con, text='Actualizar Estado', command=self.actualizar_estado)
        self.button_actualizar.pack()

        self.button_eliminar = Button(
            self.con, text='Eliminar Tarea', command=self.eliminar_tarea)
        self.button_eliminar.pack()

        self.label_usuario = Label(self.con2, text='Usuario:')
        self.label_usuario.place(x=660, y=300)
        self.label_usuario.pack()
        self.entry_usuario = Entry(self.con2)
        self.entry_usuario.place(x=624, y=325)
        self.entry_usuario.pack()
        
        self.label_contraseña = Label(self.con2, text='Contraseña:')
        self.label_contraseña.place(x=655, y=350)
        self.label_contraseña.pack()
        self.entry_contraseña = Entry(self.con2, show='*')
        self.entry_contraseña.place(x=624, y=375)
        self.entry_contraseña.pack()
        
        self.button_login = Button(self.con2, text='Iniciar sesión', command=self.login)
        self.button_login.place(x=650, y=400)
        self.button_login.pack()
        
        if self.TOKEN != '':
            self.actualizar_lista_tareas()

        self.label_tareas = Label(master, text='Tareas:')
        self.label_tareas.pack(anchor="w")

        self.listbox_tareas = Listbox(master)
        self.listbox_tareas.pack(side='left', fill='both')

        self.scrollbar_tareas = Scrollbar(master)
        self.scrollbar_tareas.pack(side='left', fill='y')

        self.listbox_tareas.config(yscrollcommand=self.scrollbar_tareas.set,bg="lightgrey")
        self.scrollbar_tareas.config(command=self.listbox_tareas.yview,bg="lightgrey")
        



    def login(self):
        try:
            self.autor = self.entry_usuario.get() 
            usuario = Usuario(nombre_usuario= self.autor, contraseña=self.entry_contraseña.get())
            user_dict = usuario.to_dict()
            user_json = json.dumps(user_dict)
            r = requests.post(url=self.URL+'/login', data=user_json)
            if r.status_code == 200:
                token = r.json()
                self.TOKEN = token["access_token"]
                showinfo(
                    "Éxito", f"Inicio de sesión exitoso. Último acceso: {usuario.ultimo_acceso()}.")
                self.entry_usuario.delete(0, END)
                self.entry_contraseña.delete(0, END)
                self.actualizar_lista_tareas()
            elif r.status_code == 401:
                showerror(
                    "ERROR", f"El usuario o contaseña son incorrectos.")
        except Exception as e:
            showerror("Error", str(e))

    def agregar_tarea(self):
        titulo = self.entry_titulo.get()
        descripcion = self.entry_descripcion.get()
        estado = self.entry_estado.get()
        headers = {"Authorization": f"Bearer {self.TOKEN}"}
        tarea = {
            'titulo': titulo,
            'descripcion': descripcion,
            'estado': estado
        }
        tarea_json = json.dumps(tarea)
        r = requests.post(url=self.URL+'/tareas',
                          data=tarea_json, headers=headers)
        if r.status_code == 200:
            response = r.json()
            self.actualizar_lista_tareas()
            showinfo('Tarea Agregada', f'{response["message"]}.')
            self.entry_titulo.delete(0,END)
            self.entry_descripcion.delete(0,END)
            self.entry_estado.delete(0,END)
        elif self.TOKEN == '':
            showerror('Iniciar Sesion', f"Para Agregar una tarea\ndebe iniciar sesion.")

    def ver_tarea(self):
        seleccion = self.listbox_tareas.curselection()
        headers = {"Authorization": f"Bearer {self.TOKEN}"}
        if seleccion:
            tarea_id = int(self.listbox_tareas.get(seleccion))
            r = requests.get(
                url=self.URL+f'/search-task/{tarea_id}', headers=headers)
            tarea = r.json()
            if r.status_code == 200:
                showinfo('Ver Tarea', f'ID: {tarea["ID"]}\nTítulo: {tarea["Titulo"]}\nDescripción: {tarea["Descripcion"]}\n'
                         f'Estado: {tarea["Estado"]}\nFecha Creada: {tarea["fecha_creada"]}\n'
                         f'Fecha Actualizada: {tarea["fecha_actualizada"]}')
            elif self.TOKEN == '':
                showerror('Inicar Sesion', f"Primero debe iniciar sesion.")
        else:
            showinfo('Ver Tarea', 'Seleccione una tarea de la lista.')

    def actualizar_estado(self):
        seleccion = self.listbox_tareas.curselection()
        if seleccion:
            headers = {"Authorization": f"Bearer {self.TOKEN}"}
            tarea_id = int(self.listbox_tareas.get(seleccion))
            estado = self.entry_estado.get()
            r = requests.put(
                url=self.URL+f'/update-status/{tarea_id}?new_status={estado}', headers=headers)
            if r.status_code == 200:
                self.actualizar_lista_tareas()
                showinfo('Estado Actualizado',
                         f'Se actualizó el estado de la tarea con ID {tarea_id}')
                self.entry_estado.delete(0,END)
            elif self.TOKEN == '':
                showerror('Iniciar Sesion', f"Primero debe Iniciar Sesion.")
        else:
            showerror('Actualizar Estado', 'Seleccione una tarea de la lista.')

    def eliminar_tarea(self):
        seleccion = self.listbox_tareas.curselection()
        if seleccion:
            headers = {"Authorization": f"Bearer {self.TOKEN}"}
            tarea_id = int(self.listbox_tareas.get(seleccion))
            r = requests.delete(url=self.URL+f'/delete-task/{tarea_id}', headers=headers)
            if r.status_code == 200:
                self.actualizar_lista_tareas()
                showinfo('Tarea Eliminada',
                         f'Se eliminó la tarea con ID {tarea_id}')
            elif self.TOKEN == '':
                showerror('Iniciar Sesion', f"Primero debe iniciar sesion.")
        else:
            showinfo('Eliminar Tarea', 'Seleccione una tarea de la lista.')

    def actualizar_lista_tareas(self):
        self.listbox_tareas.delete(0, END)
        headers = {"Authorization": f"Bearer {self.TOKEN}"}
        r = requests.get(url=self.URL+'/get-all-tasks', headers=headers)
        tareas = r.json()
        if r.status_code == 200:
            for tarea in tareas:
                self.listbox_tareas.insert(END, tarea['ID'])


def run_app():
    root = Tk()
    AppGUI(root).pack()
    root.mainloop()

if __name__ == '__main__':
    run_app()