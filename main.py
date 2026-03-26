# time и jwt для создания токена
import time
from datetime import timedelta
from jwt import encode, decode


# FastAPI
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates


# база данных
import sqlite3


# pydentic схемы
from schemes import Form, Token, Post, Coment, Reaction



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


templates = Jinja2Templates(directory="pages")


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

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS comments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            username VARCHAR(16),
            post_id DEFUELT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id)
        );
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS reactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INT,
            username VARCHAR(16),
            like DEFUELT NULL,
            dislike DEFUELT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id)
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
def to_forum(request: Request):
    context = get_posts(request)
    return templates.TemplateResponse("forum.html", context)

@app.get("/comments/{post_id}", tags=["lincs"], response_class=HTMLResponse)
def to_comments(request: Request):
    context = get_comments(request)
    return templates.TemplateResponse("comments.html", context)



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


@app.post("/add_post")
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
    cursor.execute(
        '''
        INSERT INTO reactions (post_id, username) VALUES (?, ?)
        ''',
        (data.content, username)
    )
    
    con.commit()
    con.close()

@app.post("/add_comment")
def add_post(data: Coment):
    con, cursor = conectDB()

    payload = decode(data.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload["sub"]
    cursor.execute(
        '''
        INSERT INTO comments (content, username, post_id) VALUES (?, ?, ?)
        ''',
        (data.comment, username, data.post_id)
    )
    
    con.commit()
    con.close()

@app.post("/add_reaction")
def add_post(data: Reaction):
    con, cursor = conectDB()

    payload = decode(data.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload["sub"]
    cursor.execute(
        '''
        INSERT INTO reactions (username, post_id, like, dislike) VALUES (?, ?, ?, ?)
        ''',
        (username, data.post_id, data.reaction[0], data.reaction[1],) 
    )
    
    con.commit()
    con.close()

def get_posts(request):
    con, cursor = conectDB()
    posts = cursor.execute(
        """
        SELECT
        posts.id, 
        posts.content,
        posts.username,
        SUM(reactions.like),
        SUM(reactions.dislike),
        (SUM(reactions.like) - SUM(reactions.dislike)) as total FROM posts
        LEFT JOIN reactions
        ON posts.id = reactions.post_id
        GROUP BY posts.id
        ORDER BY total DESC
        """
    ).fetchall()
    print(posts)
    context = {
        "request": request,
        "posts": []
    }

    for i in range(len(posts)):
        context["posts"].append(
            {
                "id": posts[i][0],
                "content": posts[i][1],
                "username": posts[i][2],
                "likes_count": posts[i][3] if posts[i][3] else 0,
                "dislikes_count": posts[i][4] if posts[i][4] else 0
            }
        )

    return context

def get_comments(request):
    con, cursor = conectDB()
    coments = cursor.execute(
        """
        SELECT * FROM comments
        JOIN posts ON comments.post_id = posts.id
        WHERE posts.id = comments.post_id AND posts.id = ?
        ORDER BY id DESC
        """, (request.path_params["post_id"],)
    ).fetchall()
    print(request.path_params["post_id"])
    context = {
        "request": request,
        "comments": []
    }

    for i in range(len(coments)):
        print(coments[i])
        context["comments"].append(
            {
                "id": coments[i][0],
                "content": coments[i][1],
                "username": coments[i][2],
                "post_id": coments[i][3]
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