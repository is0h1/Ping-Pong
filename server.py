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
        while self.countdown > 0:
            time.sleep(1)
            with self.lock:
                self.countdown -= 1
                self.broadcast_state()

        while not self.game_over:
            with self.lock:
                self.ball['x'] += self.ball['vx']
                self.ball['y'] += self.ball['vy']

                if self.ball['y'] <= 60 or self.ball['y'] >= HEIGHT:
                    self.ball['vy'] *= -1
                    self.sound_event = "wall_hit"

                if (self.ball['x'] <= 40 and self.paddles[0] <= self.ball['y'] <= self.paddles[0] + 100) or \
                    (self.ball['x'] >= WIDTH - 40 and self.paddles[1] <= self.ball['y'] <= self.paddles[1] + 100):
                    self.ball['vx'] *= -1
                    self.sound_event = 'platform_hit'

                if self.ball['x'] < 0:
                    self.score[1] += 1
                    self.reset_ball()
                elif self.ball['x'] > WIDTH:
                    self.score[0] += 1
                    self.reset_ball()

                if self.score[0] >= 10:
                    self.game_over = True
                    self.winner = 0
                elif self.scores[1] >= 10:
                    self.game_over = True
                    self.winner = 1

                self.broadcast_state()
                self.sound_event = None
            time.sleep(0.016)

    def reset_ball(self):
        self.ball = {
            "x": WIDTH // 2,
            "y": HEIGHT // 2,
            "vx": BALL_SPEED * random.choice([-1, 1]),
            "vy": BALL_SPEED * random.choice([-1, 1])
        }

    def accept_player(self):

        print("Очікуємо гравця 0...")
        conn, _ = self.server.accept()
        self.clients[0] = conn
        conn.sendall(b"0\n")
        self.connected[0] = True
        print("Гравець 0 приєднався")
        threading.Thread(target=self.handle_client, agrs=(0,), daemon=True).start()


        print("Очікуємо гравця 1 (5 секунд)...")
        self.server.settimeout(5)
        try:
            conn, _ = self.server.accept()
            self.clients[1] = conn
            conn.sendall(b"1\n")
            self.connected[1] = True
            print("Гравець 1 приєднався")
            threading.Thread(target=self.handle_client, agrs=(1, ), daemon=True).start()
        except socket.timeout:
            print("Другий гравець не підключився. Активую бота.")
            self.bot_active = True
            self.connected[1] = True
            threading.Thread(target=self.run_bot, daemon=True).start()
        finally:
            self.server.settimeout(None)
