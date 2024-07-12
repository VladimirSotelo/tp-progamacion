from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from datetime import datetime, date
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from hashlib import md5

class Usuario(BaseModel):
    username: str
    password: str

class Tarea(BaseModel):
    titulo: str
    descripcion: str
    estado: str

# Base de datos
class AdminTarea:
    def __init__(self):
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Tareas (
                id INTEGER PRIMARY KEY,
                titulo TEXT,
                descripcion TEXT,
                estado TEXT,
                fecha_creada DATE,
                fecha_actualizada DATE
            )
        ''')
        conn.commit()
        conn.close()
    
    def agregar_tarea(self, tarea: Tarea) -> int:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        
        cursor.execute('''SELECT id FROM Tareas ORDER BY id DESC ''')
        new_id = cursor.fetchall()
        
        if new_id != []:
            id = new_id[0][0] + 1
        else:
            id = 0
        
        cursor.execute('''
            INSERT INTO Tareas (id, titulo, descripcion, estado, fecha_creada, fecha_actualizada)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (id, tarea.titulo, tarea.descripcion, tarea.estado, datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')))
        
        conn.commit()
        conn.close()
        
        return id

    def traer_tarea(self, tarea_id: int) -> Tarea:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Tareas WHERE id = ?', (tarea_id,))
        tarea_data = cursor.fetchone()
        if tarea_data:
            tarea = {
                'ID': tarea_data[0],
                'Titulo': tarea_data[1],
                'Descripcion': tarea_data[2],
                'Estado': tarea_data[3],
                'fecha_creada': tarea_data[4],
                'fecha_actualizada': tarea_data[5]
            }
            conn.close()
            return tarea
        else:
            conn.close()
            raise HTTPException(status_code=404, detail='Tarea no encontrada')

    def actualizar_estado_tarea(self, tarea_id: int, estado: str):
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE Tareas SET estado = ?, fecha_actualizada = ? WHERE id = ?',
                       (estado, datetime.now().strftime('%Y-%m-%d'), tarea_id))
        conn.commit()
        conn.close()

    def eliminar_tarea(self, tarea_id: int):
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Tareas WHERE id = ?', (tarea_id,))
        conn.commit()
        conn.close()

    def traer_todas_tareas(self) -> List[Tarea]:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Tareas')
        tareas_data = cursor.fetchall()
        tareas = []
        for tarea_data in tareas_data:
            tarea = {
                'ID': tarea_data[0],
                'Titulo': tarea_data[1],
                'Descripcion': tarea_data[2],
                'Estado': tarea_data[3],
                'fecha_creada': tarea_data[4],
                'fecha_actualizada': tarea_data[5]
            }
            tareas.append(tarea)
        conn.close()
        return tareas


# API
app = FastAPI()
admin_tarea = AdminTarea()


class Settings(BaseModel):
    authjwt_secret_key: str = 'token'
    authjwt_access_token_expires = 3600


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.post('/login')
async def login(user: Usuario, Authorize: AuthJWT = Depends()):
    password_encrypt = md5('Admin'.encode()).hexdigest()
   
    if user.username != 'Admin' or user.password != password_encrypt:
        raise HTTPException(status_code=401, detail='bad username or password')

    access_token = Authorize.create_access_token(subject=user.username)
    return {'access_token': access_token}


@app.post('/tareas')
async def add_task(tarea: Tarea, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    try:
        task_id = admin_tarea.agregar_tarea(tarea)
        return {'message': f'Tarea agregada exitosamente con ID {task_id}'}
    except:
        raise HTTPException(status_code=500, detail='Error al agregar tarea')


@app.get('/get-all-tasks')
async def get_all_tasks(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    try:
        tasks = admin_tarea.traer_todas_tareas()
        return tasks
    except:
        raise HTTPException(
            status_code=500, detail='Error al obtener todas las tareas')


@app.get('/search-task/{task_id}')
async def search_task(task_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    try:
        task = admin_tarea.traer_tarea(task_id)
        return task
    except:
        raise HTTPException(status_code=404, detail='Tarea no encontrada')


@app.put('/update-status/{task_id}')
async def update_status_task(task_id: int, new_status: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    try:
        admin_tarea.actualizar_estado_tarea(task_id, new_status)
        return {'message': 'Estado de tarea actualizado correctamente'}
    except:
        raise HTTPException(status_code=500, detail='Error al actualizar estado de tarea')


@app.delete('/delete-task/{task_id}')
async def delete_task(task_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    try:
        admin_tarea.eliminar_tarea(task_id)
        return {'message': 'Tarea eliminada correctamente'}
    except:
        raise HTTPException(status_code=500, detail='Error al eliminar tarea')

#Main
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
    