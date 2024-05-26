import base64, os
from datetime import datetime
from openai import AzureOpenAI
import json


def get_gpt_response(myParam, img_path=None):
    encoded_image = None

    if img_path:
        # 檢查檔案是否存在
        if not os.path.exists(img_path):
            raise Exception(f"File not found: {img_path}")

        with open(img_path, "rb") as file:
            encoded_image = base64.b64encode(file.read()).decode("ascii")

    client = AzureOpenAI(
        azure_endpoint=myParam.get("azure_endpoint"),
        api_key=myParam.get("api_key"),
        api_version=myParam.get("api_version"),
    )

    user_messages = {
        "role": "user",
        "content": [],
    }
    if encoded_image:
        user_messages["content"].append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
            }
        )
    user_messages["content"].append({"type": "text", "text": myParam.get("message")})

    start_time = datetime.now()

    response = client.chat.completions.create(
        model=myParam.get("model_name"),
        max_tokens=int(myParam.get("max_tokens")),
        temperature=float(myParam.get("temperature")),
        messages=[
            {"role": "system", "content": "You are a helper assistant."},
            user_messages,
        ],
    )

    end_time = datetime.now()
    response_time = end_time - start_time

    total_tokens = response.usage.total_tokens
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens

    return {
        "response": response.choices[0].message.content,
        "response_time": response_time.total_seconds(),
        "total_tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


def get_gpt_response_stream(myParam, img_path=None):
    try:
        encoded_image = None

        if img_path:
            # 檢查檔案是否存在
            if not os.path.exists(img_path):
                raise Exception(f"File not found: {img_path}")

            with open(img_path, "rb") as file:
                encoded_image = base64.b64encode(file.read()).decode("ascii")

        client = AzureOpenAI(
            azure_endpoint=myParam.get("azure_endpoint"),
            api_key=myParam.get("api_key"),
            api_version=myParam.get("api_version"),
        )

        user_messages = {
            "role": "user",
            "content": [],
        }
        if encoded_image:
            user_messages["content"].append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                }
            )
        user_messages["content"].append({"type": "text", "text": myParam.get("message")})

        response = client.chat.completions.create(
            model=myParam.get("model_name"),
            max_tokens=int(myParam.get("max_tokens")),
            temperature=float(myParam.get("temperature")),
            messages=[
                {"role": "system", "content": "You are a helper assistant."},
                user_messages,
            ],
            stream=True,
        )

        for chunk in response:
            if chunk.choices:
                res = chunk.choices[0].delta.content
                if res:
                    print(res, end="")
                    yield f"data: {json.dumps(res)}\n\n"

        res = "End of stream"
        yield f"data: {json.dumps(res)}\n\n"
    except Exception as e:
        print(e)
        yield f"data: {json.dumps(str(e))}\n\n"

        res = "End of stream"
        yield f"data: {json.dumps(res)}\n\n"