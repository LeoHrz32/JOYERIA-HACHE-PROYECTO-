## 🚀 Como ejecutarlo en local

Necesitarás tener instalado ``` python 3.12.6``` y tener acceso a una terminal para seguir los siguientes pasos:
>
1. Necesitamos clonar el proyecto añadiendo la siguiente linea de comando en una terminal
```
git clone https://github.com/LeoHrz32/Gestion-de-PDFS-Estudiantiles
```
>
2. Instalamos un entorno virtual (En caso de no tener uno).
```
python -m venv nombre_del_entorno
```
3. Creamos el archivo de dependencias o requerimientos.

```
pip freeze > requirements.txt

```
4. Instalar dependencias desde requirements.txt
```
pip install -r requirements.txt

```

5. Activamos el entorno virtual
```
.\env\Scripts\activate

```
6. Navegamos a la carpeta Backend y Luego ejecutamos el proyecto con un puerto.
  ```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
``` 
