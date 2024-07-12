# Creacion de una aplicacion utilizando FastAPI y SQLlite:
  
  La aplicacion se basa en la administracion de tareas en formato lista, la cual utiliza una interfaz grafica (TKinter) para facilitar la interaccion con el usuario.
  
  La aplicacion se ejecuta en un servidor locar, integrado en FastAPI `Uvicorn`.
  
  Para poder realizar las acciones en la interfaz grafica tienes que iniciar secion, de lo contrario no dejara realizar dichas acciones. 
  
  La interfaz interactua con FastApi y le pide informacion a la base de datos, con esta interaccion el usuario puede: Crear, Actualizar, Ver y Eliminar las tareas.


## Requisitos para la utilizacion de la APP e Interfaz.

  1. Antes de ejecutar los archivos se debe instalar los requerimientos nesecarios para el uso de las funciones:
      ```pip
      pip install -r requirements.txt
      ```
  2. Se debe ejecutar el archivo que contiene el servidor, la APIrest y la base de datos `app.py`
  
  3. Se debe ejecurtar el archivo de la interfaz grafica `Interfaz.py`
  
  4. Para poder entre se requiere iniciar secion, por defecto el usuario y contraseña son **`Admin`**. 
