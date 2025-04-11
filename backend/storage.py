import mysql.connector
from mysql.connector import Error

#  Conexión a la base de datos
def create_connection():
     connection = None
     try:
         # Conectamos a la base de datos
         connection = mysql.connector.connect(
             host="127.0.0.1",
             user="root",
             password="",
             database="db_gdocumental"
         )
     except Error as e:
         print(f"Error: '{e}'")
     return connection



# RUTAS DE USUARIOS - CRUD 


def get_user(str_name_user: str, str_password: str):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Consulta para obtener el usuario, su contraseña, permisos y área
    query = """
        SELECT str_name_user, str_password
        FROM tbl_users
        WHERE str_name_user = %s
    """

    # Ejecutar la consulta
    cursor.execute(query, (str_name_user,))
    user = cursor.fetchone()

    # Cerrar conexión
    cursor.close()
    connection.close()

    # Verificar si el usuario existe y si la contraseña coincide
    if user and str_password == user['str_password']:
        # Retornar datos completos del usuario
        return {
            "username": user["str_name_user"]
        }

    # Retornar None si la validación falla
    return None

# Función para obtener los usuarios desde la base de datos
def get_users():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Consulta para obtener los usuarios
    query = """
        SELECT id, str_name_user AS username, str_password AS password, str_email AS email
        FROM tbl_users
    """
    cursor.execute(query)
    users = cursor.fetchall()

    # Cerrar la conexión
    cursor.close()
    connection.close()

    return users


    
def delete_user(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    try:
        # Verificar si el usuario existe
        check_query = "SELECT id FROM tbl_users WHERE id = %s"
        cursor.execute(check_query, (user_id,))
        user = cursor.fetchone()  # Si existe, fetchone devolverá el usuario

        if not user:  # Si no existe el usuario
            print(f"Usuario con ID {user_id} no encontrado.")
            return False  # Usuario no encontrado

        # Si el usuario existe, proceder a eliminarlo
        query = "DELETE FROM tbl_users WHERE id = %s"
        cursor.execute(query, (user_id,))
        connection.commit()  # Confirmar los cambios
        success = cursor.rowcount > 0  # Verificar si se eliminó el usuario
        return success  # Retorna True si se eliminó, False si no

    except Exception as e:
        connection.rollback()  # Revertir en caso de error
        print(f"Error al eliminar el usuario: {e}")
        return False

    finally:
        cursor.close()  # Cerrar el cursor
        connection.close()  # Cerrar la conexión



# Función para agregar un usuario a la base de datos
def add_user(str_name_user: str, str_email: str, str_password: str, id_permission: int, id_area: int):
    connection = create_connection()
    cursor = connection.cursor()

    try:
        # Verificar si el usuario ya existe
        query_check = "SELECT id FROM tbl_users WHERE str_name_user = %s"
        cursor.execute(query_check, (str_name_user,))
        existing_user = cursor.fetchone()

        if existing_user:
            return {"success": False, "message": "El usuario ya existe"}

        # Insertar nuevo usuario
        query_insert = """
            INSERT INTO tbl_users (str_name_user, str_email, str_password, id_permission, id_area)
            VALUES (%s, %s, %s, %s, %s) 
        """
        cursor.execute(query_insert, (str_name_user, str_email, str_password, id_permission, id_area))
        connection.commit()

        return {"success": True, "message": "Usuario creado correctamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

    finally:
        cursor.close()
        connection.close()
        