from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import HTTPException
import sqlite3


from schemes import Form

# подключение к FastAPI
app = FastAPI()

# путь к статическим файлам таким как CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# подключение к базе данных
def conectDB():
    con = sqlite3.connect("data.db")
    cursor = con.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(16),
            password VARCHAR(16)
        );
        '''
    )
    return con, cursor


# ссылки на все страницы
@app.get("/", tags=["lincs"])
def root():
    return FileResponse("pages/main.html")

@app.get("/sign_in", tags=["lincs"])
def to_sign():
    return FileResponse("pages/sign_in.html")

@app.get("/sign_up", tags=["lincs"])
def to_create():
    return FileResponse("pages/sign_up.html")

@app.get("/info", tags=["lincs"])
def to_support():
    return FileResponse("pages/info.html")


# авторизация формы
@app.post("/auth")
async def auth(data: Form):
    return JSONResponse({
        "username": data.username,
        "password": data.password
    })

# регестрация формы
@app.post("/registr")
async def reg(data: Form):
    con, cursor = conectDB()
    
    username = cursor.execute(
        '''
        SELECT username FROM users WHERE username = ?
        ''',
        (data.username,)
    
    ).fetchall()
    con.commit()
    
    print(username, data.username)
    if username:
        raise HTTPException(status_code=400, detail="username alredy exists")
    cursor.execute(
        '''
        INSERT INTO users (username, password) VALUES (?, ?)
        ''',
        (data.password, data.username)
    )
    con.commit()
    con.close()
    



# запуск веб приложения
if __name__ == "__main__":
    conectDB()
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8657,
        reload=True
    )