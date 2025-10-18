
from flask import Flask, render_template, request, jsonify, send_from_directory
from transformers import AutoModel, AutoTokenizer
from diffusers import StableDiffusionPipeline
import torch
import traceback
import os
from generator import generate_report
import socket

app = Flask(__name__)

try:
    print("Загрузка языковой модели...")
    path = 'OpenGVLab/InternVL2_5-4B'
    model = AutoModel.from_pretrained(
        path, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True,
        trust_remote_code=True, device_map="auto", max_memory={0: "15GB"}
    ).half().eval().cuda()
    tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True, use_fast=False)
    generation_config = dict(max_new_tokens=1024, do_sample=True)

    print("Загрузка модели Stable Diffusion...")
    model_id = "stabilityai/stable-diffusion-2-1-base"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    print("Все модели загружены успешно!")
except Exception as e:
    print("Ошибка при загрузке моделей:", e)
    print(traceback.format_exc())


def find_free_port(start_port=5000, max_port=5100):
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise RuntimeError("Нет свободных портов в диапазоне")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    topic = request.form.get("topic", "").strip()
    if not topic:
        return jsonify({"message": "Ошибка: тема не может быть пустой."})

    try:
        doc_path, ppt_path = generate_report(topic, model, tokenizer, generation_config, pipe)
        if not doc_path or not ppt_path:
            return jsonify({"message": "Ошибка при генерации отчёта."})

        doc_link = "/docs/" + os.path.basename(doc_path)
        ppt_link = "/docs/" + os.path.basename(ppt_path)

        return jsonify({"message": "Успешно", "doc": doc_link, "ppt": ppt_link})
    except Exception as e:
        return jsonify({"message": f"Ошибка: {str(e)}"})


@app.route('/docs/<path:filename>')
def download_file(filename):
    return send_from_directory('docs', filename, as_attachment=True)


if __name__ == "__main__":
    port = find_free_port(5050, 5100)
    print(f"Запуск сервера на порту {port}")
    app.run(port=port)
