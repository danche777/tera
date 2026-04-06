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
from schemes import Form, Token, Post, Coment, Reaction, DeletePost



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

@app.get("/forum/{username}", tags=["lincs"], response_class=HTMLResponse)
def to_forum(request: Request, username):
    context = get_posts(request, username)
    return templates.TemplateResponse("forum.html", context)

@app.get("/comments/{post_id}", tags=["lincs"], response_class=HTMLResponse)
def to_comments(request: Request):
    context = get_comments(request)
    return templates.TemplateResponse("comments.html", context)

@app.get("/account/{username}", tags=["lincs"], response_class=HTMLResponse)
def to_account(request: Request, username: str):
    context = get_personal_posts(request, username)
    return templates.TemplateResponse("account.html", context)

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

    (cursor.execute("select username, password from users").fetchall())

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

# проверка токена на валидность и срок годности
@app.post("/check_token")
def check_token(data: Token):
    payload = decode(data.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    expires_at = payload["exp"]
    username = payload["sub"]

    if time.time() >= expires_at:
        raise HTTPException(detail="Token expired", status_code=404)
    return {"status": "ok"}, username

# добавление поста
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

# добавление комментария
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

# реакция на пост (лайк или дизлайк)
@app.post("/add_reaction")
def add_post(data: Reaction):
    con, cursor = conectDB()

    payload = decode(data.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    
    username = payload["sub"]
    post_id = data.post_id
    like = data.reaction[0]
    dislike = data.reaction[1]

    reaction_state = cursor.execute(
        """
        SELECT
            like,
            dislike
        FROM reactions
        WHERE username = ? AND post_id = ?
        """,
        (username, post_id,)
    ).fetchall()

    

    print(f'username: {username} {reaction_state}')
    # print(reaction_state[0][0], like, reaction_state[0][1], dislike)
    print(reaction_state == [])
    if reaction_state == []:
        cursor.execute(
            '''
            INSERT INTO reactions (username, post_id, like, dislike) VALUES (?, ?, ?, ?)
            ''',
            (username, post_id, like, dislike,) 
        )
    elif reaction_state[0][0] == like and reaction_state[0][1] == dislike:
        cursor.execute(
            '''
            DELETE FROM reactions WHERE username = ? AND post_id = ?
            ''',
        (username, post_id,)
        )
    else:
        cursor.execute(
            '''
            UPDATE reactions SET like = ?, dislike = ? WHERE username = ? AND post_id = ?
            ''',
            (like, dislike, username, post_id,)
        )

    
    con.commit()
    con.close()

@app.delete("/delete_post/{post_id}")
def delete_post(data: DeletePost):
    con, cursor = conectDB()

    post_id = data.post_id
    cursor.execute(
        '''
        DELETE FROM posts WHERE id = ?
        ''',
        (post_id,)
    )
    cursor.execute(
        '''
        DELETE FROM reactions WHERE post_id = ?
        ''',
        (post_id,)
    )
    cursor.execute(
        '''
        DELETE FROM comments WHERE post_id = ?
        ''',
        (post_id,)
    )
    
    con.commit()
    con.close()

# получение всех постов с количеством лайков и дизлайков
def get_posts(request, username):
    con, cursor = conectDB()
    print(username)
    posts = cursor.execute(
        """
        SELECT
            posts.id,
            posts.content,
            posts.username,
            COALESCE(SUM(reactions.like) - SUM(reactions.dislike), 0) as total,
            IF(reactions.username = ?,
                IF(reactions.like == '1', 'like',
                    IF (reactions.dislike == '1', 'dislike', 'null')
            ), 'null') as personal_reaction
        FROM posts
        LEFT JOIN reactions
        ON posts.id = reactions.post_id
        GROUP BY posts.id
        ORDER BY total DESC
        """,  (username,)
    ).fetchall()
    print([i for i in posts ])
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
                "total": posts[i][3],
                "personal_reaction": posts[i][4],
            }
        )
        print(posts[i][4])

    return context

# получение всех постов конкретного пользователя с количеством лайков и дизлайков
def get_personal_posts(request, username):
    con, cursor = conectDB()
    posts = cursor.execute(
        """
        SELECT
            posts.id,
            posts.content,
            posts.username,
            SUM(reactions.like),
            SUM(reactions.dislike)
        FROM posts 
        LEFT JOIN reactions ON posts.id = reactions.post_id
        WHERE posts.username = ?
        GROUP BY posts.id
        """, (request.path_params["username"],)
    ).fetchall()
    context = {
        "request": request,
        "posts": [],
        "username": username
    }
    
    for i in range(len(posts)):
        context["posts"].append(
            {
                "id": posts[i][0],
                "content": posts[i][1],
                "username": username,
                "likes_count": posts[i][3],
                "dislikes_count": posts[i][4]
            }
        )
    return context

# получение всех комментариев к конкретному посту
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

    context = {
        "request": request,
        "comments": []
    }

    for i in range(len(coments)):

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