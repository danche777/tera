def random_post():
    from openai import OpenAI

    from promt import PROMT

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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"
    )
    promt = PROMT + "\n\n" + "напиши пост на любую тему, которая тебе нравится. Главное — чтобы он выглядел максимально естественно, как будто его написал реальный человек на форуме. Не старайся писать красиво, просто отвечай, как тебе кажется правильным." 
    response = client.chat.completions.create(
        model="openrouter/elephant-alpha",
        messages=[
            {"role": "user", "content": promt}
        ]
    )

    return response.choices[0].message.content