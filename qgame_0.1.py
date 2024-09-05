import pygame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import sympy as sp
import tempfile
import os


# Definición de Clases y Funciones
class TurnClass:
    def __init__(self, xstart=True):
        if xstart:
            self.player = 'X'
            self.inactive = 'O'
        else:
            self.player = 'O'
            self.inactive = 'X'
    def switch(self):
        self.player, self.inactive = self.inactive, self.player

class State:
    def __init__(self, i, j):
        self.i = i
        self.j = j
        self.probs = {'X': 0, 'O': 0}
        self.coefs = {'X': 0, 'O': 0}
        self.on = False
        self.collapsed = None
        
    def move(self, turn, w_model='half_pow'):
        if w_model == 'half_pow':
            if self.probs[turn.player] == 0:
                if self.probs[turn.inactive] == 0:
                    self.probs[turn.player] = 1
                else:
                    self.probs = {'X': sp.Rational(1/2), 'O': sp.Rational(1/2)}
            else:
                if self.probs[turn.player] >= self.probs[turn.inactive]:
                    self.probs[turn.inactive] = sp.Rational(self.probs[turn.inactive]/2)
                    self.probs[turn.player] = 1 - self.probs[turn.inactive]
                else:
                    self.probs[turn.player] = sp.Rational(self.probs[turn.player]*2)
                    self.probs[turn.inactive] = 1 - self.probs[turn.player]
                    
            self.coefs[turn.player] = sp.sqrt(self.probs[turn.player])
            self.coefs[turn.inactive] = sp.sqrt(self.probs[turn.inactive])
            
    def collapse(self):
        if self.collapsed == None:
            if self.probs['X'] + self.probs['O'] == 0:
                self.collapsed = '-'
            elif self.probs['X'] == 1:
                self.collapsed = 'X'
            elif self.probs['O'] == 1:
                self.collapsed = 'O'
            else:
                montecarlo = np.random.uniform(low=0.0, high=1.0, size=None)
                if montecarlo < self.probs['X']:
                    self.collapsed = 'X'
                else:
                    self.collapsed = 'O'

    def __str__(self):
        if self.collapsed == None:
            return f"X: {self.coefs['X']}, O: {self.coefs['O']}"
        else:
            return self.collapsed

def check_winners(grid):
    Xwins = 0
    Owins = 0
    # Check rows
    for i in range(3):
        row = grid[i, :]
        if np.all(row == 'X'):
            Xwins += 1
        elif np.all(row == 'O'):
            Owins += 1 
    # Check columns
    for j in range(3):
        col = grid[:, j]
        if np.all(col == 'X'):
            Xwins += 1
        elif np.all(col == 'O'):
            Owins += 1 
    # Check diagonals
    diagonal = grid.diagonal()
    antidiagonal = np.fliplr(grid).diagonal()
    if np.all(diagonal == 'X'):
        Xwins += 1
    elif np.all(diagonal == 'O'):
        Owins += 1 
    if np.all(antidiagonal == 'X'):
        Xwins += 1
    elif np.all(antidiagonal == 'O'):
        Owins += 1 
    winner_state = State(None, None)
    
    if Owins==Xwins:
        return 'Tie'
    if Owins<Xwins:
        return 'X won!'
    if Owins>Xwins:
        return 'O won!'

# Configuración de Pygame
pygame.init()

# Dimensiones de la ventana
WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Tic-Tac-Toe")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Dimensiones de la cuadrícula
GRID_SIZE = 3
CELL_SIZE = WIDTH // GRID_SIZE

# Fuentes
FONT = pygame.font.SysFont("comicsans", 40)

def render_latex_to_image(expression, fontsize=20, dpi=100):
    fig, ax = plt.subplots(figsize=(1, 1), dpi=dpi)
    ax.text(0.5, 0, f"${expression}$", fontsize=fontsize, ha='center', va='center')
    ax.axis('off')  # Oculta los ejes

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close(fig)
        return tmpfile.name
def draw_turn(turn):
    turn_text = f"Turn: {turn.player}"
    text = FONT.render(turn_text, 1, BLACK)
    WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, 5))
    
def draw_winner(winner):
    winner_text = f"{winner}"
    text = FONT.render(winner_text, 1, BLACK)
    WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, 10))

def draw_grid():
    WIN.fill(WHITE)
    for x in range(1, GRID_SIZE):
        pygame.draw.line(WIN, BLACK, (x * CELL_SIZE, 0), (x * CELL_SIZE, HEIGHT), 3)
        pygame.draw.line(WIN, BLACK, (0, x * CELL_SIZE), (WIDTH, x * CELL_SIZE), 3)

def draw_state(grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            state = grid[i, j]
            if state.collapsed:
                text = FONT.render(state.collapsed, 1, RED if state.collapsed == 'X' else BLUE)
                WIN.blit(text, (j * CELL_SIZE + CELL_SIZE // 3, i * CELL_SIZE + CELL_SIZE // 4))
            else:
                # Generar la expresión LaTeX solo con los kets con coeficientes no nulos
                expression = []
                if state.coefs['X'] != 0:
                    expression.append(f"{sp.latex(state.coefs['X'])}|X\\rangle")
                if state.coefs['O'] != 0:
                    expression.append(f"{sp.latex(state.coefs['O'])}|O\\rangle")
                
                latex_expression = " + ".join(expression)
                
                if latex_expression:  # Si hay algo que mostrar
                    img_path = render_latex_to_image(latex_expression, fontsize=20)
                    img = pygame.image.load(img_path)
                    WIN.blit(img, (j * CELL_SIZE + 10, i * CELL_SIZE + 20))
                    os.remove(img_path)



def main():
    run = True
    clock = pygame.time.Clock()

    # Inicialización de Grid y Turno
    state00 = State(0, 0)
    state01 = State(0, 1)
    state02 = State(0, 2)
    state10 = State(1, 0)
    state11 = State(1, 1)
    state12 = State(1, 2)
    state20 = State(2, 0)
    state21 = State(2, 1)
    state22 = State(2, 2)
    grid = np.array([[state00, state01, state02], [state10, state11, state12], [state20, state21, state22]])

    turn = TurnClass(xstart=True)
    moves_log = []
    max_turns = 14

    while run and len(moves_log) < max_turns:
    
        draw_turn(turn)
        pygame.display.update()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                col = pos[0] // CELL_SIZE
                row = pos[1] // CELL_SIZE

                if grid[row, col].collapsed is None and grid[row, col].probs[turn.player] < 1:
                    grid[row, col].move(turn)
                    moves_log.append([row, col])
                    turn.switch()

        draw_grid()
        draw_state(grid)
        pygame.display.update()
        
    pygame.time.wait(500)
    print("Wave Function Collapse")
    for i in range(3):
        for j in range(3):
            grid[i, j].collapse()
            draw_grid()
            draw_state(grid)
            pygame.display.update()
            pygame.time.wait(500)

    grid_collapsed=np.array([[state00.collapsed,state01.collapsed,state02.collapsed],[state10.collapsed,state11.collapsed,state12.collapsed],[state20.collapsed,state21.collapsed,state22.collapsed]])

    winner = check_winners(grid_collapsed)
    
    draw_winner(winner)
    pygame.display.update()

    # Espera para mostrar el resultado final
    pygame.time.wait(6000)

    pygame.quit()

if __name__ == "__main__":
    main()
