from openai import OpenAI
import time
import os

from main import conectDB

from promt import post_promt
from promt import comment_promt



def post_comment():


    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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"
    )


    def random_post():
        promt = post_promt

        try:
            response = client.chat.completions.create(
                model="openrouter/elephant-alpha",
                messages=[{"role": "user",
                        "content": promt}])
        except Exception:
            for i in range(10):
                time.sleep(0.1)
                print(f"Retrying... ({i+1}/10)")
            return random_post()

        return response.choices[0].message.content


    def random_comment(post):
        promt = f"{comment_promt}\n{post}"
        
        try:
            response = client.chat.completions.create(
                model="openrouter/elephant-alpha",
                messages=[{"role": "user",
                        "content": promt}])
        except Exception:
            for i in range(10):
                time.sleep(0.3)
                print(f"Retrying... ({i+1}/10)")
            return random_comment(post)
        
        return response.choices[0].message.content

    def random_username():
        promt = "придумай уникальный ник для соцсети на английском языке (1 слово)"

        try:
            response = client.chat.completions.create(
                model="openrouter/elephant-alpha",
                messages=[{"role": "user",
                        "content": promt}])
        except Exception:
            for i in range(10):
                time.sleep(0.3)
                print(f"Retrying... ({i+1}/10)")
            return random_username()
        
        return response.choices[0].message.content


    post = random_post()
    comment = random_comment(post)

    post_username = random_username()
    comment_username = random_username()


    con, cursor = conectDB()
    cursor.execute(
        '''
        INSERT INTO posts (content, username) VALUES (?, ?)
        ''',
        (post, post_username)
    )

    cursor.execute(
        '''
        INSERT INTO reactions (post_id, username) VALUES (
        (SELECT id FROM posts where content = ?), ?
        )
        ''',
        (post, post_username)
    )

    con.commit()
    con.close()



    con, cursor = conectDB()
    now = time.localtime()

    post_id = cursor.execute('SELECT id FROM posts WHERE content = ?', (post,)).fetchall()[0][0]
    formatted_time = time.strftime("%H:%M", now)
    formatted_date = time.strftime("%Y.%m.%d", now)

    cursor.execute(
        '''
        INSERT INTO comments (content, username, post_id, time, date) VALUES (?, ?, ?, ?, ?)
        ''',
        (comment, comment_username, post_id, formatted_time, formatted_date)
    )

    con.commit()
    con.close()

count_of_posts = 0

while True:
    count_of_posts += 1

    post_comment()

    print(f"Post {count_of_posts} created successfully!")
    time.sleep(3)
    for i in range(10):
        print(f"Waiting... ({i+1}/10)")
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')
    
