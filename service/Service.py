# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from pathlib import Path
import datetime, os

import myAzureOpenAI

app = Flask(__name__)
CORS(app)
app.config["CORS_HEADERS"] = "Content-Type, Qs-PageCode, Cache-Control"


def print_info(param, streaming=False):
    print(f"streaming: {streaming}")
    print(f"azure_endpoint: {param['azure_endpoint']}")
    print(f"api_key: {param['api_key']}")
    print(f"api_version: {param['api_version']}")
    print(f"model_name: {param['model_name']}")
    print(f"temperature: {param['temperature']}")
    print(f"max_tokens: {param['max_tokens']}")
    print(f"user_prompt: {param['user_prompt']}")


def save_image(image, img_path):
    if image:
        uploads_folder_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "uploads"
        )
        if not os.path.exists(uploads_folder_path):
            os.makedirs(uploads_folder_path)
        keep_latest_files(uploads_folder_path, 3)
        hash_name = str(hash(datetime.datetime.now()))
        image.filename = f"{hash_name}.jpg"
        img_path = os.path.join(uploads_folder_path, image.filename)
        image.save(img_path)
        print(f"Save image to {img_path}")
    return img_path


def keep_latest_files(folder_path, num_files_to_keep=10):
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"{folder_path} is not exist.")
        return

    files = [(file, os.path.getmtime(file)) for file in folder.glob("*")]
    sorted_files = sorted(files, key=lambda x: x[1], reverse=True)
    for file_path, _ in sorted_files[num_files_to_keep:]:
        os.remove(file_path)
        print(f"Remove {file_path}")


@app.route("/")
def index():
    return "Server ready"


@app.route("/save_user_image", methods=["POST"])
def save_gpt_image():
    image = request.files.get("user_image", None)
    try:
        img_path = None
        if image:
            img_path = save_image(image, img_path)

        hashed_file_name = os.path.basename(img_path)
        return jsonify({"hashed_file_name": hashed_file_name})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/get_gpt_response", methods=["POST"])
def gpt():
    azure_endpoint = request.form.get("azure_endpoint")
    api_key = request.form.get("api_key")
    api_version = request.form.get("api_version")
    model_name = request.form.get("model_name")
    temperature = request.form.get("temperature")
    max_tokens = request.form.get("max_tokens")
    user_prompt = request.form.get("user_prompt")
    image = request.files.get("image", None)
    print_info(request.form)

    try:
        img_path = None
        if image:
            img_path = save_image(image, img_path)
        myParam = {
            "azure_endpoint": azure_endpoint,
            "api_key": api_key,
            "api_version": api_version,
            "model_name": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "message": user_prompt,
        }
        res = myAzureOpenAI.get_gpt_response(myParam, img_path)
        return jsonify({"data": res})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/get_gpt_response_streaming", methods=["GET"])
def gpt_stream():
    azure_endpoint = request.args.get("azure_endpoint")
    api_key = request.args.get("api_key")
    api_version = request.args.get("api_version")
    model_name = request.args.get("model_name")
    temperature = request.args.get("temperature")
    max_tokens = request.args.get("max_tokens")
    user_prompt = request.args.get("user_prompt")
    hashed_file_name = request.args.get("hashed_file_name")

    img_path = None
    if hashed_file_name:
        img_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "uploads", hashed_file_name
        )

    print_info(request.args, streaming=True)

    try:
        myParam = {
            "azure_endpoint": azure_endpoint,
            "api_key": api_key,
            "api_version": api_version,
            "model_name": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "message": user_prompt,
        }
        res = myAzureOpenAI.get_gpt_response_stream(myParam, img_path)
        return Response(stream_with_context(res), mimetype="text/event-stream")
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8787)
