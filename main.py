# time, jwt, passlib для создания токена и хеширования пароля
import time
from datetime import timedelta
from jwt import encode, decode
from passlib.context import CryptContext

# FastAPI
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

# база данных
import sqlite3


# pydentic схемы
from schemes import Form, Token, Post, Coment, Reaction, DeletePost, Count_pages



# константы для создания токена на 30 минут и хеширования пароля
TOKEN_MINUTES, SECRET_KEY, ALGORITHM  = 30, "secret-key", "HS256"

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

config = Config(".env")

oauth = OAuth(config)
oauth.register(
    name="google",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
    authorize_params={"access_type": "offline", "prompt": "consent"},
)

# создание токена
def create_access_token(subject: str, expires_delta=None) -> str:
    expire = time.time() + (expires_delta or  timedelta(minutes=TOKEN_MINUTES)).total_seconds()
    to_encode = {"sub": subject, "exp": expire}
    return encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# создания хешированного пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# верефекация пароля
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


# подключение к FastAPI
app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=config("SECRET_KEY"),
    same_site="lax",      # критично для OAuth
    https_only=False      # если ты не на HTTPS
)
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

            username TEXT UNIQUE,
            password TEXT,

            google_id TEXT UNIQUE,

            email TEXT,
            name TEXT,
            avatar TEXT
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
            time TIME,
            date DATE,
            post_id DEFAULT NULL,
            comment_id INT,
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
            like INT DEFAULT 0,
            FOREIGN KEY (post_id) REFERENCES posts(id)
        );
        '''
    )

    return con, cursor


def check_token(access_token: str, username: str):
    payload = None
    try:
        payload = decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as ex:
        raise HTTPException(detail=str(ex), status_code=403)
    expires_at = payload["exp"]
    token_username = payload["sub"]

    if username != token_username:
        raise HTTPException(detail="Can`t access", status_code=403)

    if time.time() >= expires_at:
        raise HTTPException(detail="Token expired", status_code=404)


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

from fastapi import Query

@app.get("/forum/{username}/{access_token}", tags=["lincs"], response_class=HTMLResponse)
def to_forum(
    request: Request,
    username: str,
    access_token: str,
    page_number: int
    ):
    
    try:
        check_token(access_token, username)
    except Exception:
        return FileResponse("pages/sign_in.html")
    context = get_posts(request, username, page_number)
    return templates.TemplateResponse("forum.html", context)

@app.get("/comments/{post_id}", tags=["lincs"], response_class=HTMLResponse)
def to_comments(request: Request):
    context = get_comments(request)
    return templates.TemplateResponse("comments.html", context)

@app.get("/account/{username}/{access_token}", tags=["lincs"], response_class=HTMLResponse)
def to_account(request: Request, username: str, access_token: str):
    try:
        check_token(access_token, username)
    except Exception:
        return FileResponse("pages/sign_in.html")
    context = get_personal_posts(request, username)
    return templates.TemplateResponse("account.html", context)


@app.get("/login/google")
async def login(request: Request):
    redirect_uri = request.url_for("google_auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google", name="google_auth")
async def auth_google(request: Request):
    # 1. Получаем access_token
    token = await oauth.google.authorize_access_token(request)

    # 2. Получаем данные пользователя через API Google
    resp = await oauth.google.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        token=token
    )
    user_info = resp.json()

    google_id = user_info["sub"]
    email = user_info.get("email")
    name = user_info.get("name")
    avatar = user_info.get("picture")

    con, cursor = conectDB()

    # 3. Ищем пользователя по google_id
    user = cursor.execute(
        "SELECT id FROM users WHERE google_id = ?",
        (google_id,)
    ).fetchone()

    # 4. Если нет — пробуем по email
    if not user and email:
        user = cursor.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user:
            cursor.execute(
                "UPDATE users SET google_id = ? WHERE email = ?",
                (google_id, email)
            )
            con.commit()

    # 5. Если вообще нет — создаём
    if not user:
        cursor.execute(
            """
            INSERT INTO users (google_id, email, name, avatar)
            VALUES (?, ?, ?, ?)
            """,
            (google_id, email, name, avatar)
        )
        con.commit()

    # 6. Создаём твой JWT
    email = email.split("@")[0]
    
    subject = email if email else google_id
    access_token = create_access_token(subject)
    
    response = RedirectResponse(url="/")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,  # 👈 если хочешь читать в JS
        secure=False,    # True если HTTPS
        samesite="lax"
    )
    
    response.set_cookie(
    key="username",
    value=subject,
    httponly=False,
    path="/"
    )

    # 7. Редирект
    return response

@app.get("/profile")
async def profile(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Не авторизован"}, status_code=401)
    return RedirectResponse(url="/")


# авторизация формы
@app.post("/auth")
async def auth(data: Form):
    con, cursor = conectDB()

    user = cursor.execute(
        """
        SELECT username, password FROM users WHERE username = ?
        """,
        (data.username,)
    ).fetchone()

    if not user:
        raise HTTPException(status_code=400, detail="username not found")

    db_username, db_password = user

    if not db_password:
        raise HTTPException(status_code=400, detail="Use Google login")

    if not verify_password(data.password, db_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    token = create_access_token(db_username)
    return Token(access_token=token)


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
    elif " " in data.username:
        raise HTTPException(status_code=400, detail="username spaces!")
    elif " " in data.password:
        raise HTTPException(status_code=400, detail="password spaces!")

    cursor.execute(
        '''
        INSERT INTO users (username, password) VALUES (?, ?)
        ''',
        (data.username, hash_password(data.password))
    )

    con.commit()
    con.close()

# проверка токена на валидность и срок годности
@app.post("/check_token")
def check_token_view(data: Token):
    payload = None
    try:
        payload = decode(data.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as ex:
        raise HTTPException(detail=str(ex), status_code=403)
    expires_at = payload["exp"]
    username = payload["sub"]

    if time.time() >= expires_at:
        raise HTTPException(detail="Token expired", status_code=404)
    return {"status": "ok"}

# добавление поста
@app.post("/add_post")
def add_post(data: Post):
    con, cursor = conectDB()

    payload = decode(data.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload["sub"]
    
    from tests import random_post

    content = random_post()

    cursor.execute(
        '''
        INSERT INTO posts (content, username) VALUES (?, ?)
        ''',
        (content, "test_user")
    )

    cursor.execute(
        '''
        INSERT INTO reactions (post_id, username) VALUES (
        (SELECT id FROM posts where content = ?), ?
        )
        ''',
        (content, "test_user")
    )





    # cursor.execute(
    #     '''
    #     INSERT INTO posts (content, username) VALUES (?, ?)
    #     ''',
    #     (data.content, username)
    # )
    # cursor.execute(
    #     '''
    #     INSERT INTO reactions (post_id, username) VALUES (
    #     (SELECT id FROM posts where content = ?), ?
    #     )
    #     ''',
    #     (data.content, username)
    # )
        
    con.commit()
    con.close()

# добавление комментария
@app.post("/add_comment")
def add_comment(data: Coment):
    con, cursor = conectDB()
    now = time.localtime()
    
    formatted_time = time.strftime("%H:%M", now)
    formatted_date = time.strftime("%Y.%m.%d", now)
    payload = decode(data.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload["sub"]

    cursor.execute(
        '''
        INSERT INTO comments (content, username, post_id, time, date) VALUES (?, ?, ?, ?, ?)
        ''',
        (data.comment, username, data.post_id, formatted_time, formatted_date)
    )
    
    con.commit()
    con.close()

# реакция на пост (лайк или дизлайк)
@app.post("/add_reaction")
def add_reaction(data: Reaction):
    con, cursor = conectDB()

    payload = decode(data.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    
    username = payload["sub"]
    post_id = data.post_id
    like = data.reaction

    reaction_state = cursor.execute(
        """
        SELECT
            like
        FROM reactions
        WHERE username = ? AND post_id = ?
        """,
        (username, post_id,)
    ).fetchall()

    
    if reaction_state == []:
        cursor.execute(
            '''
            INSERT INTO reactions (username, post_id, like) VALUES (?, ?, ?)
            ''',
            (username, post_id, like) 
        )
    elif str(reaction_state[0][0]) == like:
        cursor.execute(
            '''
            UPDATE reactions SET like = ? WHERE username = ? AND post_id = ?
            ''',
            (0, username, post_id,)
        )
    else:
        cursor.execute(
            '''
            UPDATE reactions SET like = ? WHERE username = ? AND post_id = ?
            ''',
            (like, username, post_id,)
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
def get_posts(request, username, page_number):
    con, cursor = conectDB()
    posts = cursor.execute(
        """
        SELECT
            posts.id,
            posts.content,
            posts.username,
            COALESCE(
            	(
	            	select sum(COALESCE(like, 0)) 
	            	from reactions where posts.id = reactions.post_id
            	), 0
            ) as total_likes,
            COALESCE(
            	(
	            	select like from reactions
	            	where posts.id = reactions.post_id 
	            	and reactions.username = ? limit 1
            	), 0
            ) as personal_likes
        FROM posts
        LIMIT ? OFFSET ?
        """,  (username, 10, page_number * 10)
    ).fetchall()
    
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
                "total_likes": posts[i][3],
                "personal_reaction": posts[i][4],
            }
        )

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
            SUM(reactions.like)
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
                "time": coments[i][3],
                "date": coments[i][4],
                "post_id": coments[i][5]
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