"""
Orbital Globe Lab - controle gestual local.
Python 3.11 + OpenCV + MediaPipe.
A webcam é processada apenas neste computador. Somente comandos são enviados ao navegador.
Pressione Q ou ESC na janela da câmera para encerrar.
"""
import argparse
import asyncio
import math
import os
import threading
import time
import webbrowser
from pathlib import Path

import cv2
import mediapipe as mp
from aiohttp import web

ROOT = Path(__file__).resolve().parent
CLIENTS = set()
LOOP = None
READY = threading.Event()


async def websocket(request):
    # Não aceite conexões vindas de sites desconhecidos.
    origin = request.headers.get("Origin", "")
    if origin and origin not in {
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    }:
        raise web.HTTPForbidden(text="Origem nao autorizada")
    ws = web.WebSocketResponse(heartbeat=20)
    await ws.prepare(request)
    CLIENTS.add(ws)
    try:
        async for msg in ws:
            pass  # O navegador não envia ações para a câmera.
    finally:
        CLIENTS.discard(ws)
    return ws


async def index(request):
    return web.FileResponse(ROOT / "index.html")


async def send_gesture(payload):
    for ws in tuple(CLIENTS):
        if not ws.closed:
            try:
                await ws.send_json(payload)
            except (ConnectionError, RuntimeError):
                CLIENTS.discard(ws)


def publish(action, **values):
    if LOOP is None or not CLIENTS:
        return
    asyncio.run_coroutine_threadsafe(
        send_gesture({"type": "gesture", "action": action, **values}), LOOP
    )


async def start_server():
    global LOOP
    LOOP = asyncio.get_running_loop()
    app = web.Application()
    app.router.add_get("/ws", websocket)
    app.router.add_get("/", index)
    app.router.add_static("/", str(ROOT), show_index=False)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8000)
    await site.start()
    READY.set()
    while True:
        await asyncio.sleep(3600)


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def detect_state(landmarks, zoom_started):
    fingers = sum(
        landmarks[tip].y < landmarks[pip].y - 0.015
        for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]
    )
    palm_width = max(distance(landmarks[5], landmarks[17]), 0.045)
    pinch = distance(landmarks[4], landmarks[8]) / palm_width
    if fingers <= 1 and pinch > 0.72:
        return "pause", pinch
    if pinch < (1.25 if zoom_started else 0.73):
        return "zoom", pinch
    if fingers >= 2:
        return "rotate", pinch
    return "pause", pinch


def run_camera(index):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_ANY)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print("ERRO: webcam nao encontrada. Verifique permissoes e indice --camera.")
        return 1

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    hands_api = mp.solutions.hands
    drawing = mp.solutions.drawing_utils
    prev_position = None
    prev_pinch = None
    prev_mode = None
    last_seen = True
    last_publish = 0.0
    print("Webcam ativa. Q / ESC fecha. Apenas movimentos sao enviados ao navegador.")

    try:
        with hands_api.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.65,
            min_tracking_confidence=0.55,
        ) as hands:
            while True:
                ok, image = cap.read()
                if not ok:
                    print("Aviso: falha na leitura da webcam.")
                    time.sleep(0.05)
                    continue
                image = cv2.flip(image, 1)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                rgb.flags.writeable = False
                result = hands.process(rgb)
                rgb.flags.writeable = True

                mode = "SEM MAO"
                now = time.monotonic()
                if result.multi_hand_landmarks:
                    hand = result.multi_hand_landmarks[0]
                    lm = hand.landmark
                    mode, pinch = detect_state(lm, prev_mode == "zoom")
                    drawing.draw_landmarks(image, hand, hands_api.HAND_CONNECTIONS)
                    position = (lm[9].x, lm[9].y)
                    if mode != prev_mode:
                        prev_position = None
                        prev_pinch = None
                    if now - last_publish > 0.04:
                        if mode == "rotate" and prev_position:
                            dx = max(-0.11, min(0.11, position[0] - prev_position[0]))
                            dy = max(-0.11, min(0.11, position[1] - prev_position[1]))
                            publish("rotate", dx=round(dx, 5), dy=round(dy, 5))
                        elif mode == "zoom" and prev_pinch is not None:
                            delta = max(-0.1, min(0.1, pinch - prev_pinch))
                            if abs(delta) > 0.007:
                                publish("zoom", delta=round(delta, 5))
                        else:
                            publish("pause")
                        last_publish = now
                    prev_position = position
                    prev_pinch = pinch
                    prev_mode = mode
                    last_seen = True
                else:
                    prev_position = None
                    prev_pinch = None
                    prev_mode = None
                    if last_seen:
                        publish("lost")
                        last_seen = False

                cv2.rectangle(image, (0, 0), (image.shape[1], 64), (5, 17, 26), -1)
                cv2.putText(image, "ORBITAL GLOBE / CONTROLE DE MAOS", (15, 22),
                            cv2.FONT_HERSHEY_SIMPLEX, .55, (114, 245, 234), 1, cv2.LINE_AA)
                cv2.putText(image, "GESTO: " + mode.upper() + " | Q/ESC para sair", (15, 49),
                            cv2.FONT_HERSHEY_SIMPLEX, .57, (246, 240, 194), 1, cv2.LINE_AA)
                cv2.imshow("Orbital Globe Lab - Webcam (local)", image)
                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord("q")):
                    break
    finally:
        cap.release()
        cv2.destroyAllWindows()
    return 0


def main():
    parser = argparse.ArgumentParser(description="Controlar globo 3D com webcam")
    parser.add_argument("--camera", type=int, default=0, help="Indice da camera, padrao 0")
    args = parser.parse_args()
    threading.Thread(target=lambda: asyncio.run(start_server()), daemon=True).start()
    if not READY.wait(8):
        raise RuntimeError("Servidor nao inicializou. A porta 8000 pode estar ocupada.")
    print("Globo disponivel em http://127.0.0.1:8000")
    webbrowser.open("http://127.0.0.1:8000")
    return run_camera(args.camera)


if __name__ == "__main__":
    raise SystemExit(main())
