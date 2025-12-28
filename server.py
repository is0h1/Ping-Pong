import socket
import json
import threading
import time
import random

WIDTH, HEIGHT = 800, 600
BALL_SPEED = 5
PADDLE_SPEED = 10
COUNTDOWN = 3

class GameServer:
    def __init__(self, host='localhost', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        print(" Server started")

        self.clients = {0: None, 1: None}
        self.connected = {0: False, 1: False}
        self.lock = threading.Lock()
        self.reset_game_state()
        self.sound_event = None
        self.bot_active = False

    def reset_game_state(self):
        self.paddles = {0: 250, 1: 250}
        self.score = [0, 0]
        self.ball = {
            "x": WIDTH // 2,
            "y": HEIGHT // 2,
            "vx": BALL_SPEED * random.choice([-1, 1]),
            "vy": BALL_SPEED * random.choice([-1, 1])
        }
        self.countdown = COUNTDOWN_START
        self.game_over = False
        self.winner = None

    def handle_client(self, pid):
        conn = self.clients[pid]
        try:
            while True:
                data = conn.recv(64).decode()
                with self.lock:
                    if data == "UP":
                        self.paddles[pid] = max(60, self.paddles[pid] - PADDLE_SPEED)
                    elif data == "DOWN"
                        self.paddles[pid] = min(HEIGHT - 100, self.paddles[pid] + PADDLE_SPEED)
        except:
            with self.lock:
                self.connected[pid] = False
                self.game_over = True
                self.winner = -1 - pid if not self.bot_active else 0
                print(f"Гравець {pid} відключився. Переміг гравець {self.winner}.")

    def run_bot(self):
        print("Бот активований")

        while self.countdown > 0 and not self.game_over:
            time.sleep(0.1)

        while not self.game_over:
            with self.lock:
                ball_y = self.ball["y"]
                paddle_y = self.paddles[1]

                if ball_y < paddle_y + 45:
                    self.paddles[1] = max(60, paddle_y - BALL_SPEED)
                elif ball_y > paddle_y + 55:
                    self.paddles[1] = min(HEIGHT - 100, paddle_y + PADDLE_SPEED)
            time.sleep(0.016)

    def broadcast(self):
        state = json.dumps({
            "paddles": self.paddles,
            "ball": self.ball,
            "score": self.score,
            "countdown": max(self.countdown, 0)
            "winner": self.winner, if self.game_over else None,
            "sound_event": self.sound_event
        }) + "\n"
        for pid, conn in self.clients.items():
            if conn:
                try:
                    conn.sendall(state.encode())
                except:
                    self.connected[pid] = False
                    
    def ball_logic (self):
