from fastapi import FastAPI, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
from storage import get_user, get_users,delete_user, add_user
from pydantic import BaseModel

from storage import create_connection

from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query


app = FastAPI()


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir cualquier origen (puedes restringirlo)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

# Montar la carpeta estática para que FastAPI reconozca los archivos de estilo CSS
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../frontend/static")), name="static")


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, strUsuario: str = Form(...), strContrasenna: str = Form(...)):
    # Obtener usuario desde la función personalizada
    user = get_user(strUsuario, strContrasenna)

    # Validar existencia
    if user is None:
        raise HTTPException(status_code=401, detail="Nombre de usuario o contraseña incorrectos")

    # Redirección a una sola ruta (ejemplo: dashboard principal)
    return RedirectResponse(url="/users", status_code=303)


@app.get("/", response_class=HTMLResponse)
async def index():
    # Ruta del archivo HTML de inicio
    index_path = os.path.join(os.path.dirname(__file__), "../frontend/inicio.html")
    with open(index_path, "r", encoding="utf-8") as f:
        # Retornamos la respuesta en HTML
        return HTMLResponse(content=f.read(), status_code=200)


# RUTAS DE USUARIOS 


@app.get("/users", response_class=HTMLResponse)
async def list_users():
    # Obtener los usuarios usando la función de storage.py
    users = get_users()

    # Leer el archivo HTML
    template_path = os.path.join(os.path.dirname(__file__), "../frontend/usersTable.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Inyectar los datos de los usuarios en el HTML
    table_rows = ""
    for user in users:
        table_rows += f"""
            <tr>
                <td>{user['username']}</td>
                <td>{user['password']}</td>
                <td>{user['email']}</td>
                <td>
                    <button class="edit-btn" onclick="editUser({user['id']})">Editar</button>
                    <button class="delete-btn" onclick="deleteUser({user['id']})">Eliminar</button>
                </td>
            </tr>
        """
    
    # Reemplazamos el marcador en el HTML con las filas generadas
    html_content = html_content.replace("<!-- rows-placeholder -->", table_rows)

    return HTMLResponse(content=html_content)


@app.get("/usersJSON")
async def list_users():
    # Crear la conexión a la base de datos
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Consulta SQL para obtener los usuarios
    query = """
        SELECT id, str_name_user AS username, str_email AS email, id_permission, id_area
        FROM tbl_users
    """
    cursor.execute(query)
    users = cursor.fetchall()

    # Cerrar la conexión a la base de datos
    cursor.close()
    connection.close()

    # Retornar los usuarios en formato JSON
    return JSONResponse(content={"users": users})

@app.get("/users_paginated", response_class=JSONResponse)
async def list_users_paginated(page: int = Query(1, alias="page"), per_page: int = Query(10, alias="per_page")):
    """
    Obtiene la lista de usuarios con paginación.
    """
    # Crear la conexión a la base de datos
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Consulta SQL para obtener el total de usuarios y la paginación
    query = """
        SELECT id, str_name_user AS username,str_password AS password, str_email AS email
        FROM tbl_users
        LIMIT %s OFFSET %s
    """
    
    # Calcular el índice de inicio (OFFSET) y el número de usuarios por página (LIMIT)
    offset = (page - 1) * per_page
    cursor.execute(query, (per_page, offset))
    users = cursor.fetchall()

    # Consulta para obtener el número total de usuarios
    cursor.execute("SELECT COUNT(*) FROM tbl_users")
    total_users = cursor.fetchone()["COUNT(*)"]

    # Cerrar la conexión a la base de datos
    cursor.close()
    connection.close()

    # Calcular el número total de páginas
    total_pages = (total_users + per_page - 1) // per_page  # Redondeo hacia arriba
    
    return {
        "users": users,
        "total_users": total_users,
        "current_page": page,
        "per_page": per_page,
        "total_pages": total_pages  # Retornar el total de páginas
    }

@app.get("/users_search", response_class=JSONResponse)
async def search_users(query: str = Query(..., alias="query")):
    """
    Busca usuarios por nombre o correo sin paginación.
    """
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    search_query = """
        SELECT id, str_name_user AS username, str_email AS email, id_permission, id_area
        FROM tbl_users
        WHERE LOWER(str_name_user) LIKE %s OR LOWER(str_email) LIKE %s
    """
    
    cursor.execute(search_query, (f"%{query.lower()}%", f"%{query.lower()}%"))
    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return {"users": users}

@app.delete("/users/{user_id}")
async def delete_user_route(user_id: int):
    # Llamar a la función de eliminación de usuario
    print(f"Intentando eliminar el usuario con ID: {user_id}")
    success = delete_user(user_id)

    if success:
        # Si el usuario se eliminó con éxito, devolver un mensaje de éxito
        return JSONResponse(status_code=200, content={"message": "Usuario eliminado exitosamente"})
    else:
        # Si no se encontró el usuario o ocurrió algún error, devolver un mensaje de error
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    

# Modelo Pydantic para los datos de entrada del usuario
class UserCreate(BaseModel):
    str_name_user: str
    str_email: str
    str_password: str
    id_permission: int
    id_area: int

# Endpoint para crear el usuario
@app.post("/users/")
async def create_user(user: UserCreate):
    try:
        # Llamar a la función para agregar el usuario a la base de datos
        result = add_user(user.str_name_user, user.str_password)

        # Verificar el resultado de la función add_user
        if result["success"]:
            return JSONResponse(status_code=201, content={"message": result["message"]})
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        # Si ocurre un error inesperado, devolver un error 500
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")



# Vista para permisos de administrador
@app.get("/admin")
async def view_admin():
    # Cargar la página HTML para el administrador
    admin_page_path = os.path.join(os.path.dirname(__file__), "../frontend/viewAdmin.html")
    with open(admin_page_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)
    

    

# Ruta para manejar el logout y redirigir al login
@app.post("/logout")
async def logout(response: Response):
    # Eliminar la cookie de sesión
    response.delete_cookie("session") 
    
    # Redirigir al login
    return RedirectResponse(url="/", status_code=303)