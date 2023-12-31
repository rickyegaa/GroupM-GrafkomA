from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
from random import randrange
from time import sleep
import pygame
from pygame import mixer

# Inisialisasi Variabel
window = 0
width, height = 600, 600
field_width, field_height = 50, 50

snake = [(25, 7), (25, 6), (25, 5)]
level = 1
snake_dir = (0, 1)
interval = 300
food = [(25, 25)]
red_food = [(randrange(3, 47), randrange(3, 45)) for _ in range(5)] # Tambahkan variabel untuk makanan merah
state = 'up'
current_direction = (0, 1)
score = 0
collision = False
r, g, b = 1, 1, 1
high_score = 0
pygame.init()
mixer.init()

# Load suara ular memakan makanan Kuning
eating_sound = mixer.Sound("./Assets/Beep1.wav")

# Load suara ular memakan makanan Merah
eating_sound2 = mixer.Sound("./Assets/Beep.wav")  

# Load suara ular menabrak dinding
collision_sound = mixer.Sound("./Assets/gameOver.wav") 

# Fungsi Untuk Mengatur Tampilan 2D Pada Jendela Permainan
def custom_2D_gameWindow(internal_width, internal_height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, internal_width, 0, internal_height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

# Fungsi Membuat Map/Arena Batas Bidang Permainan
def board():
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_QUADS)
    glVertex2f(2, 2)
    glVertex2f(3, 2)
    glVertex2f(3, 45)
    glVertex2f(2, 45)
    glEnd()
    glBegin(GL_QUADS)
    glVertex2f(2, 46)
    glVertex2f(2, 45)
    glVertex2f(48, 45)
    glVertex2f(48, 46)
    glEnd()
    glBegin(GL_QUADS)
    glVertex2f(47, 45)
    glVertex2f(48, 45)
    glVertex2f(48, 2)
    glVertex2f(47, 2)
    glEnd()
    glBegin(GL_QUADS)
    glVertex2f(2, 2)
    glVertex2f(2, 3)
    glVertex2f(48, 3)
    glVertex2f(48, 2)
    glEnd()

# Fungsi Untuk Menampilkan Skor Pada Jendela Permainan
def score_display():
    glColor3f(0, 1, 0)
    glRasterPos2f(1, 47)
    score_str = "Score : {}  |  Level : {}".format(score, level)
    for char in score_str:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

# Fungsi Untuk Menampilkan Layar Game Over
def game_over_display():
    global high_score
    glColor3f(1, 0, 0)
    glRasterPos2f(field_width // 2 - 5, field_height // 2 + 2)
    game_over_str = "Game Over"
    for char in game_over_str:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))

    # Tampilkan skor dan skor tertinggi
    glColor3f(0, 1, 0)
    glRasterPos2f(field_width // 2 - 6, field_height // 3 + 6)
    final_score_str = f"High Score : {score}"
    for char in final_score_str:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))

    # Perbarui skor tertinggi jika skor saat ini lebih tinggi
    if score > high_score:
        high_score = score

    glutSwapBuffers()
    sleep(5)
    reset_game()

# Fungsi Untuk Menggambar Persegi Panjang Dengan Sudut Kiri Atas di (x, y), lebar Width, dan Tinggi Height.
def draw_rect(x, y, width, height):
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

# Fungsi Untuk Menggambar Seluruh Tubuh Ular
def draw_snake():
    global r, g, b
    for i, (x, y) in enumerate(snake):
        # Hitung warna berdasarkan indeks segmen
        segment_color = (1 - i / len(snake), g, b)

        # Set warna untuk segmen saat ini
        glColor3f(*segment_color)
        draw_rect(x, y, 1, 1)

    head = snake[0]

    # Cek apakah kepala ular menabrak dinding atau tubuhnya sendiri
    if (
        head[0] == 2 or head[0] == 47 or
        head[1] == 2 or head[1] == 45 or
        head in snake[1:]
    ):
        r, g, b = 1, 0, 0  
    else:
        r, g, b = 1, 1, 1

# Fungsi untuk Menggambar Makanan Ular
def draw_food():
    glColor3f(1, 1, 0)
    draw_rect(food[0][0], food[0][1], 1, 1)

def draw_all_red_food():
    glColor3f(1, 0, 0)
    for pos in red_food:
        draw_rect(pos[0], pos[1], 1, 1)

# Fungsi Untuk Menggambar Semua Elemen Tampilan Permainan Seperti Makanan, Ular, Skor, dan Batasan Bidang.
def draw_display():
    global collision
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    custom_2D_gameWindow(field_width, field_height)
    draw_food()
    draw_all_red_food()  # Tambahkan pemanggilan untuk menggambar makanan merah
    draw_snake()
    board()
    score_display()
    glutSwapBuffers()

# Fungsi untuk memutar suara makanan saat ular memakan makanan kuning
def play_eating_sound():
    eating_sound.play()

# Fungsi untuk memutar suara makanan saat ular memakan makanan merah
def play_eating_sound2():    
    eating_sound2.play()

# Fungsi untuk memutar suara tabrakan saat ular menabrak dinding
def play_collision_sound():
    collision_sound.play()

def move_snake():
    global snake, snake_dir, food, score, collision, r, g, b, level, interval, red_food

    # Perbarui posisi kepala ular berdasarkan arah
    new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])

    # Cek tabrakan dengan dinding
    if (
        new_head[0] == 2 or new_head[0] == 47 or
        new_head[1] == 2 or new_head[1] == 45
    ):
        collision = True
        play_collision_sound()

    # Cek tabrakan dengan tubuh ular
    head = snake[0]
    for i in range(1, len(snake)):
        body = snake[i]
        if new_head == body:
            # Ular bertabrakan dengan tubuhnya sendiri
            # Kurangi panjang ular menjadi 1
            snake = [new_head]
            
            # Kurangi skor sebanyak 1
            score = max(0, score - 1)
            break

    # Cek apakah ular memakan makanan
    if new_head == food[0]:
        score += 1
        play_eating_sound()

        # Jika skor adalah kelipatan 5, tingkatkan level
        if score % 5 == 0:
            level += 1
            interval -= 50  # Atur interval agar permainan menjadi lebih cepat

        # Posisi makanan baru harus di dalam dinding
        food = [(randrange(3, 47), randrange(3, 45))]

    # Cek apakah ular memakan makanan merah
    if new_head in red_food:
        score = max(0, score - 1)
        play_eating_sound2()
        red_food.remove(new_head)
        red_food.append((randrange(3, 47), randrange(3, 45)))

    # Tambahkan kepala baru pada posisi depan
    snake.insert(0, new_head)

    # Hapus ekor ular jika panjang ular lebih dari skor
    if len(snake) > score + 2:
        snake.pop()
        
def reset_game():
    global snake, level, snake_dir, interval, food, red_food, state, current_direction, score, collision, r, g, b
    snake = [(25, 7), (25, 6), (25, 5)]
    level = 1
    snake_dir = (0, 1)
    interval = 300
    food = [(25, 25)]
    red_food = [(randrange(3, 47), randrange(3, 45))]  # Tambahkan makanan merah pada reset
    state = 'up'
    current_direction = (0, 1)
    score = 0
    collision = False
    r, g, b = 1, 1, 1

# Fungsi untuk memutuskan apakah harus menampilkan layar game over pada tampilan permainan 
def draw_game_over_display():
    if score >= 30:
        # Tampilkan pesan Congratulations saat mencapai skor 30
        glColor3f(0, 1, 0)
        glRasterPos2f(field_width // 2 - 8, field_height // 2 + 2)
        congrats_str = "Congratulations The Finish Game"
        for char in congrats_str:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        glutSwapBuffers()
        sleep(5)
        reset_game()
    elif collision:
        game_over_display()
    else:
        draw_display()

# Fungsi callback untuk mengatur logika permainan
def game_logic(value):
    global interval, collision, red_food

    if not collision:
        move_snake()

    glutTimerFunc(interval, game_logic, 0)
    glutPostRedisplay()

    if collision or score >= 30:
        draw_game_over_display()

    # Cek kondisi Game Over
    if collision:
        draw_game_over_display()

# Fungsi callback untuk menanggapi input kursor panah
def special_key_input(key, x, y):
    global snake_dir, current_direction

    if key == GLUT_KEY_UP and current_direction != (0, -1):
        snake_dir = (0, 1)
        current_direction = (0, 1)
    elif key == GLUT_KEY_DOWN and current_direction != (0, 1):
        snake_dir = (0, -1)
        current_direction = (0, -1)
    elif key == GLUT_KEY_LEFT and current_direction != (1, 0):
        snake_dir = (-1, 0)
        current_direction = (-1, 0)
    elif key == GLUT_KEY_RIGHT and current_direction != (-1, 0):
        snake_dir = (1, 0)
        current_direction = (1, 0)

# Inisialisasi GLUT
if __name__ == "__main__":
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(0, 0)
    glutCreateWindow("Snake Slither (Group M : Grafika Komputer A)")
    glutDisplayFunc(draw_display)
    glutIdleFunc(draw_display)
    glutSpecialFunc(special_key_input)
    glutTimerFunc(interval, game_logic, 0)
    glutMainLoop()
