from ursina import *
from ursina.audio import Audio
import random

app = Ursina()
camera.orthographic = True
camera.fov = 10

def setup():
    global car, road1, road2, pair, enemies, game_over_text, restart_button, start_button, score_text, score, background, title_text, background_sound, collision_sound, highscore_text, score_timer, score_interval, highscore

    # Inisialisasi background
    background = Entity(
        model='quad',
        texture='assets/background.png',  # Ganti dengan path ke tekstur background Anda
        scale=(20, 15),
        z=2
    )

    # Inisialisasi judul
    title_text = Text(
        text='Road Racer 2D',  # Ganti dengan judul game Anda
        origin=(0, 0),
        scale=5,
        position=(0, 0.3),
        color=color.black
    )

    # Inisialisasi mobil
    car = Entity(
        model='quad',
        texture='assets/car.png',
        collider='box',
        scale=(2, 1),
        rotation_z=-90,
        y=-3,
        z=-1,  # Pastikan mobil di depan background
        enabled=False  # Disable until the game starts
    )

    # Inisialisasi jalan
    road1 = Entity(
        model='quad',
        texture='assets/road.png',
        scale=15,
        z=1,
        enabled=False,  # Disable until the game starts
        start_y=0
    )
    road2 = duplicate(road1, y=15)
    road2.start_y = 15
    pair = [road1, road2]

    # Inisialisasi musuh
    enemies = []

    # Inisialisasi skor
    score = 0
    highscore = 0
    score_timer = 2  # Timer untuk mengontrol kecepatan peningkatan skor
    score_interval = 0  # Interval waktu dalam detik untuk peningkatan skor
    score_text = Text(f'Score: {score}', origin=(0, 0), scale=2, position=(-0.7, 0.45), color=color.white, visible=False)

    # Teks game over dan tombol restart
    game_over_text = Text("Game Over", origin=(0, 0), scale=2, color=color.red, visible=False)
    restart_button = Button(text='Restart', color=color.azure, scale=(0.1, 0.05), position=(0, -0.1), visible=False)
    restart_button.on_click = restart_game

    # Teks highscore
    highscore_text = Text("", origin=(0, 0), scale=2, position=(0, -0.3), color=color.yellow, visible=False)

    # Tombol mulai
    start_button = Button(text='Mulai', color=color.green, scale=(0.1, 0.05), position=(0, 0))
    start_button.on_click = start_game

    # Inisialisasi background sound
    background_sound = Audio('sound/background-sound.mp3', loop=True, autoplay=True)  # Ganti dengan path ke file audio Anda

    # Inisialisasi efek suara tabrakan
    collision_sound = Audio('sound/tabrakan.mp3', autoplay=False)  # Ganti dengan path ke file audio tabrakan Anda

def start_game():
    global car, road1, road2, pair, start_button, game_over_text, restart_button, score_text, score, title_text, score_timer, highscore_text

    # Reset game state
    game_over_text.visible = False
    restart_button.visible = False
    highscore_text.visible = False
    score = 0
    score_timer = 2
    score_text.text = f'Score: {score}'
    score_text.visible = True

    # Enable game entities
    car.enabled = True
    for road in pair:
        road.enabled = True

    # Sembunyikan judul segera setelah tombol "Mulai" diklik
    title_text.visible = False

    start_button.visible = False  # Hide start button
    new_enemy()

def new_enemy():
    val = random.uniform(-2, 2)
    new = duplicate(
        car,
        texture='assets/enemy.png',
        x=2 * val,
        y=25,
        color=color.random_color(),
        rotation_z=90 if val < 0 else -90
    )
    new.collider = 'box'  # Ensure enemies have colliders
    enemies.append(new)
    invoke(new_enemy, delay=2)  # Adjusted delay to 1 second

def create_explosion(position):
    explosion = Entity(
        model='quad',
        texture='assets/efek-ledakan.png',  # Pastikan Anda memiliki tekstur ledakan
        scale=3,
        position=position,
        color=color.orange,
        z=-1  # Pastikan ledakan di depan background
    )
    destroy(explosion, delay=0.5)  # Hancurkan ledakan setelah 0.5 detik

def update():
    global score, score_timer
    if not car.enabled:
        return

    car.x -= held_keys['a'] * 5 * time.dt
    car.x += held_keys['d'] * 5 * time.dt

    for road in pair:
        road.y -= 6 * time.dt
        if road.y < -15:
            road.y += 30

    for enemy in enemies:
        if enemy.x < 0:
            enemy.y -= 10 * time.dt
        else:
            enemy.y -= 5 * time.dt
        if enemy.y < -10:
            enemies.remove(enemy)
            destroy(enemy)

    # Update score based on time
    score_timer += time.dt
    if score_timer >= score_interval:
        score += 1
        score_text.text = f'Score: {score}'
        score_timer = 2  # Reset timer

    # Periksa tabrakan
    for enemy in enemies:
        if car.intersects(enemy).hit:
            create_explosion(car.position)  # Panggil efek ledakan di posisi mobil
            collision_sound.play()  # Mainkan efek suara tabrakan
            car.shake()
            game_over()
            break  # Hentikan loop setelah tabrakan terdeteksi

def game_over():
    global enemies, score_text, highscore_text, highscore

    # Update highscore jika perlu
    if score > highscore:
        highscore = score

    # Tampilkan highscore jika perlu
    show_highscore()

    for enemy in enemies:
        destroy(enemy)
    enemies.clear()
    car.disable()
    score_text.visible = False
    game_over_text.visible = True
    restart_button.visible = True

def restart_game():
    global car, road1, road2, enemies, game_over_text, restart_button, start_button, score, score_text, title_text

    # Destroy all enemies
    for enemy in enemies:
        destroy(enemy)
    enemies.clear()

    # Reset car position and state
    car.enabled = False
    car.x = 0
    car.y = -3

    # Reset road position
    for road in pair:
        road.y = road.start_y

    # Reset score
    score = 0
    score_text.text = f'Score: {score}'

    # Sembunyikan tombol restart dan teks game over
    game_over_text.visible = False
    restart_button.visible = False

    # Otomatis mulai game setelah reset
    start_game()

def show_highscore():
    global highscore, highscore_text

    # Tampilkan highscore
    highscore_text.text = f'Highscore: {highscore}'
    highscore_text.visible = True

setup()
app.run()
