# time и jwt для создания токена
import time
from datetime import timedelta
from jwt import encode, decode


# FastAPI
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import HTTPException


# база данных
import sqlite3


# pydentic схемы
from schemes import Form, Token



# константы для создания токена на 30 минут
TOKEN_MINUTES, SECRET_KEY, ALGORITHM  = 30, "secret-key", "HS256"

# создание токена
def create_access_token(subject: str, expires_delta=None) -> str:
    expire = time.time() + (expires_delta or  timedelta(minutes=TOKEN_MINUTES)).total_seconds()
    to_encode = {"sub": subject, "exp": expire}
    return encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



# подключение к FastAPI
app = FastAPI()

# путь к статическим файлам таким как CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# отправка любой найденной ошибки FastAPI
@app.exception_handler(HTTPException)
async def http_exception_handler(req, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message":  exc.detail,
            "status_code": exc.status_code
        }
    )

# подключение к базе данных
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

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS posts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            username VARCHAR(16)
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

@app.get("/forum", tags=["lincs"], response_class=HTMLResponse)
def to_support(request: Request):
    context = get_posts(request)
    return templates.TemplatesResponse("pages/forum.html", context)



# авторизация формы
@app.post("/auth")
async def auth(data: Form):
    con, cursor = conectDB()

    user = cursor.execute(
        """
        SELECT username, password FROM users WHERE username = ?
        """,
        (data.username,)
    ).fetchall()

    print(cursor.execute("select username, password from users").fetchall())

    if not user:
        raise HTTPException(status_code=400, detail="username not found")

    password = user[0][1]
    if data.password != password:
        raise HTTPException(status_code=400, detail="Incorrect password")
    else:
        token = create_access_token(data.username)
        token = Token(access_token=token)
        return token


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
        raise HTTPException(status_code=400, detail="username already exists")
    cursor.execute(
        '''
        INSERT INTO users (username, password) VALUES (?, ?)
        ''',
        (data.username, data.password)
    )
    con.commit()
    con.close()


@app.post("/check_token")
def check_token(data: Token):
    payload = decode(data.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    expires_at = payload["exp"]
    username = payload["sub"]
    print(expires_at, username)
    print(time.time() >= expires_at)
    if time.time() >= expires_at:
        raise HTTPException(detail="Token expired", status_code=404)
    print(data.access_token)
    return {"status": "ok"}, username


app.post("/add_post")
def add_post(data: Post):
    con, cursor = conectDB()

    payload = decode(data.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload["sub"]
    cursor.execute(
        '''
        INSERT INTO posts (content, username) VALUES (?, ?)
        ''',
        (data.content, username)
    )

    con.commit()
    con.close()

def get_posts(request):
    con, cursor = conectDB()
    posts = cursor.execute(
        "SELECT * FROM posts"
    ).fetchall()

    context = {
        "request": request,
        "posts": []
    }

    for i in range(len(posts)):
        context["posts"].append(
            {
                "content": [1],
                "username": [2]
            }
        )

    return context




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