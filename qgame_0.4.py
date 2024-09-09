import pygame
import matplotlib
matplotlib.use("Agg")
import numpy as np
import sympy as sp
import os
import sys
import matplotlib.pyplot as plt
import tempfile



def main():
    # Configuración de Pygame
    pygame.init()

    # Dimensiones de la ventana
    WIDTH, HEIGHT = 600, 600+100
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Quantum Tic-Tac-Toe")

    # Colores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GRAY = (200, 200, 200)
    DARK_GRAY = (100, 100, 100)

    # Dimensiones de la cuadrícula
    GRID_SIZE = 3
    CELL_SIZE = WIDTH // GRID_SIZE

    # Fuentes
    FONT = pygame.font.SysFont("comicsans", 40)
    SMALLFONT = pygame.font.SysFont("comicsans", 25)

    clock = pygame.time.Clock()

    # Pygame classes and functions:
    class Button:
        def __init__(self, text, x, y, width, height, inactive_color, active_color, action=None):
            self.text = text
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.inactive_color = inactive_color
            self.active_color = active_color
            self.action = action

        def draw(self, screen, mouse_pos, click):
            if self.is_hovered(mouse_pos):
                pygame.draw.rect(screen, self.active_color, (self.x, self.y, self.width, self.height))
                if click[0] == 1 and self.action is not None:
                    return self.action
            else:
                pygame.draw.rect(screen, self.inactive_color, (self.x, self.y, self.width, self.height))

            draw_text(self.text, SMALLFONT, BLACK, screen, self.x + self.width // 2, self.y + self.height // 2)

        def is_hovered(self, mouse_pos):
            return self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height

    class Slider:
        def __init__(self, name, min_value, max_value, step, x, y, width, height):
            self.name = name
            self.min_value = min_value
            self.max_value = max_value
            self.step = step
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.handle_x = self.x  # Posición inicial del handle
            self.value = min_value

        def draw(self, screen):
            # Dibujar la línea del deslizador
            pygame.draw.line(screen, GRAY, (self.x, self.y), (self.x + self.width, self.y), 5)
            
            # Dibujar el "handle"
            handle_center = (self.handle_x, self.y)
            pygame.draw.circle(screen, BLUE, handle_center, 15)
            
            # Mostrar el valor seleccionado
            value_text = SMALLFONT.render(f"{self.name}: {self.value}", True, BLACK)
            screen.blit(value_text, (self.x + self.width // 2 - value_text.get_width() // 2, self.y + 50))

        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.is_over_handle(event.pos):
                    self.update_handle_position(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Si el botón izquierdo del ratón está presionado
                    if self.is_over_handle(event.pos):
                        self.update_handle_position(event.pos)

        def is_over_handle(self, pos):
            handle_rect = pygame.Rect(self.handle_x - 15, self.y - 15, 30, 30)
            return handle_rect.collidepoint(pos)

        def update_handle_position(self, pos):
            new_x = max(self.x, min(pos[0], self.x + self.width))  # Limitar el movimiento del handle dentro del rango
            self.handle_x = new_x
            
            # Calcular el valor basado en la posición del handle
            relative_position = (self.handle_x - self.x) / self.width
            steps = int(relative_position * ((self.max_value - self.min_value) // self.step))
            self.value = self.min_value + steps * self.step
            
    class Selector:
        def __init__(self, x, y, width, height, options):
            self.x = x
            self.y = y
            self.width = width//2
            self.height = height
            self.options = options
            self.selected_option = options[0]  # Opción inicial
            self.active_color = BLUE
            self.inactive_color = DARK_GRAY

        def draw(self, screen):
            # Dibujar las opciones como botones
            for index, option in enumerate(self.options):
                button_rect = pygame.Rect(self.x + index * (self.width), self.y, self.width, self.height)
                color = self.active_color if option == self.selected_option else self.inactive_color
                pygame.draw.rect(screen, color, button_rect)
                draw_text(option, SMALLFONT, WHITE, screen, button_rect.centerx, button_rect.centery)

        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                for index, option in enumerate(self.options):
                    button_rect = pygame.Rect(self.x + index * (self.width + 20), self.y, self.width, self.height)
                    if button_rect.collidepoint(event.pos):
                        self.selected_option = option

    def render_latex_to_image(expression,colors, fontsize=15, dpi=100):
        fig, ax = plt.subplots(figsize=(1, 1), dpi=dpi)
        xpos=0
        for ket,col in zip(expression,colors):
            text_obj=ax.text(xpos, 0, f"${ket}$",color=col, fontsize=fontsize, ha='left', va='center')
            bbox = text_obj.get_window_extent()  # Obtiene el bbox en puntos de pantalla
            text_width = bbox.width / dpi  # Convierte a pulgadas
            xpos += (text_width+0.2)
        ax.axis('off')  # Oculta los ejes

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            fig.savefig(tmpfile.name, bbox_inches='tight', pad_inches=0, transparent=True)
            plt.close(fig)
            print(tmpfile.name)
            return tmpfile.name 

    def draw_text(text, font, color, surface, x, y):
        textobj = font.render(text, True, color)
        textrect = textobj.get_rect()
        textrect.center = (x, y)
        surface.blit(textobj, textrect)

    def draw_turn(turn,progress):
        turn_text = f"Turn: {turn.player}"
        text_1 =   SMALLFONT.render(turn_text, 1, BLACK)
        WIN.blit(text_1, (WIDTH // 2 - text_1.get_width() // 2-150, 10))

        if progress == '>:3':
            progress_text = progress
        else:
            progress_text = f"Progress: {progress[0]}/{progress[1]}"

        text_2 = SMALLFONT.render(progress_text, 1, BLACK)
        WIN.blit(text_2, (WIDTH // 2 - text_2.get_width() // 2+150, 10))
        
    def draw_winner(winner):
        winner_text = f"{winner}"
        text = FONT.render(winner_text, 1, BLACK)
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, 10))

    def draw_grid():
        WIN.fill(WHITE)
        for x in range(1, GRID_SIZE):
            pygame.draw.line(WIN, BLACK, (x * CELL_SIZE, 100), (x * CELL_SIZE, HEIGHT), 3)
            pygame.draw.line(WIN, BLACK, (0, x * CELL_SIZE+100), (WIDTH, x * CELL_SIZE+100), 3)

    def draw_state(grid):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                state = grid[i, j]
                if state.collapsed:
                    text = FONT.render(state.collapsed, 1, RED if state.collapsed == 'X' else BLUE)
                    WIN.blit(text, (j * CELL_SIZE + CELL_SIZE // 3, i * CELL_SIZE + CELL_SIZE // 4+100))
                else:
                    # Generar la expresión LaTeX solo con los kets con coeficientes no nulos
                    expression = []
                    colors=[]
                    
                    if state.coefs['X'] != 0:
                        expression.append(f"{sp.latex(state.coefs['X'])}|X\\rangle")
                        colors.append('red')
                    if state.coefs['O'] != 0:
                        expression.append(f"{sp.latex(state.coefs['O'])}|O\\rangle")
                        colors.append('blue')
                    if state.coefs['O'] != 0 and state.coefs['X'] != 0:
                        expression.insert(1,' + ')
                        colors.insert(1,'black')

                    if expression:  # Si hay algo que mostrar
                        img_path = render_latex_to_image(expression,colors, fontsize=20)
                        img = pygame.image.load(img_path)
                        WIN.blit(img, (j * CELL_SIZE + 10, i * CELL_SIZE + 20+100))
                        os.remove(img_path)
                        


    # Backend classes and functions:
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

    def grid_full(moves_log):
        grid_set=set(((0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)))
        log_set=set(moves_log)
        return log_set == grid_set


    # Screens:
    def config():
        buttons = [
            Button("Standard Rules", WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 50, GRAY, DARK_GRAY, action="standard"),
            Button("Custom Rules", WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 50, GRAY, DARK_GRAY, action="custom"),
            Button("Hardcore", WIDTH // 2 - 150, HEIGHT // 2 + 90, 300, 50, GRAY, DARK_GRAY, action="hardcore"),
            Button("Quit", WIDTH // 2 - 150, HEIGHT // 2 + 160, 300, 50, GRAY, DARK_GRAY, action="quit")
        ]
        exit = False
        while True and not exit:
            WIN.fill(WHITE)
            draw_text('Quantum Tic-Tac-Toe', FONT, BLACK, WIN, WIDTH // 2, HEIGHT // 4)

            mouse_pos = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()

            for button in buttons:
                action = button.draw(WIN, mouse_pos, click)
                if action:
                    if action == "quit":
                        pygame.quit()
                        sys.exit()

                    else:
                        if action == 'standard':
                            rules,exit = stardard_settings_menu()

                        if action == 'custom':
                            rules,exit = custom_settings_menu()

                        if action == 'hardcore':
                            rules,exit = hardcore_settings_menu()

            
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        return rules

    def custom_settings_menu():
        slider1 = Slider('Number of turns',min_value=10, max_value=30, step=2, x=WIDTH//2 - WIDTH//4, y=100, width=WIDTH//2, height=30)
        slider2 = Slider('Cell freezing time (turns)',min_value=0, max_value=8, step=1, x=WIDTH//2 - WIDTH//4, y=100+130, width=WIDTH//2, height=30)
        category_selector = Selector(x=WIDTH//2 - WIDTH//4, y=100+130+130, width=WIDTH//2, height=50, options=["X Starts", "O Starts"])
        
        while True:
            WIN.fill(WHITE)
            slider1.draw(WIN)
            slider2.draw(WIN)
            category_selector.draw(WIN)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                slider1.handle_event(event)
                slider2.handle_event(event)
                category_selector.handle_event(event)
                
            # Mostrar botón de confirmación
            mouse_pos = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            
            play_button = pygame.Rect(WIDTH // 2 - 75+90, HEIGHT - 100, 150, 50)
            pygame.draw.rect(WIN, DARK_GRAY, play_button)
            draw_text("Play", SMALLFONT, WHITE, WIN, play_button.centerx, play_button.centery)
            
            back_button = pygame.Rect(WIDTH // 2 - 75 -90, HEIGHT - 100, 150, 50)
            pygame.draw.rect(WIN, DARK_GRAY, back_button)
            draw_text("Back", SMALLFONT, WHITE, WIN, back_button.centerx, back_button.centery)

            if play_button.collidepoint(mouse_pos) and click[0]:
                rules = {'xstart':category_selector.selected_option == 'X' ,'max_turns': slider1.value,'last_moves': slider2.value}
                WIN.fill(WHITE)
                return rules,True   # Regresar el valor seleccionado cuando se presiona el botón de confirmación
            
            if back_button.collidepoint(mouse_pos) and click[0]:
                rules = None
                WIN.fill(WHITE)
                return rules,False   # Regresar el valor seleccionado cuando se presiona el botón de confirmación
            

            pygame.display.update()

    def stardard_settings_menu():
        while True:
            WIN.fill(WHITE)
            draw_text("Standard rules:", FONT, BLACK, WIN, WIDTH // 2, HEIGHT // 4)
            draw_text("Game lasts for 14 turns", SMALLFONT, BLACK, WIN, WIDTH // 2, HEIGHT // 3+50)
            draw_text("Cells freeze for 1 turn after being played", SMALLFONT, BLACK, WIN, WIDTH // 2, HEIGHT // 3+100)
            draw_text("X starts!", SMALLFONT, BLACK, WIN, WIDTH // 2, HEIGHT // 3+150)
            
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # Mostrar botón de confirmación
            mouse_pos = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            
            play_button = pygame.Rect(WIDTH // 2 - 75+90, HEIGHT - 100, 150, 50)
            pygame.draw.rect(WIN, DARK_GRAY, play_button)
            draw_text("Play", SMALLFONT, WHITE, WIN, play_button.centerx, play_button.centery)
            
            back_button = pygame.Rect(WIDTH // 2 - 75 -90, HEIGHT - 100, 150, 50)
            pygame.draw.rect(WIN, DARK_GRAY, back_button)
            draw_text("Back", SMALLFONT, WHITE, WIN, back_button.centerx, back_button.centery)

            if play_button.collidepoint(mouse_pos) and click[0]:
                rules = {'xstart':True ,'max_turns': 14,'last_moves': 1}
                WIN.fill(WHITE)
                return rules,True   # Regresar el valor seleccionado cuando se presiona el botón de confirmación
            
            if back_button.collidepoint(mouse_pos) and click[0]:
                rules = None
                WIN.fill(WHITE)
                return rules,False   # Regresar el valor seleccionado cuando se presiona el botón de confirmación
            

            pygame.display.update()

    def hardcore_settings_menu():
        category_selector = Selector(x=WIDTH//2 - WIDTH//4, y=HEIGHT // 3+150, width=WIDTH//2, height=50, options=["X Starts", "O Starts"])
            
        while True:
            WIN.fill(WHITE)
            draw_text("Hardcore mode:", FONT, BLACK, WIN, WIDTH // 2, HEIGHT // 4)
            draw_text("Game finishes once the grid is full", SMALLFONT, BLACK, WIN, WIDTH // 2, HEIGHT // 3+50)
            draw_text("Cells freeze for 1 turn after being played", SMALLFONT, BLACK, WIN, WIDTH // 2, HEIGHT // 3+100)
            #draw_text("X starts!", SMALLFONT, BLACK, WIN, WIDTH // 2, HEIGHT // 3+150)
            category_selector.draw(WIN)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                category_selector.handle_event(event)
            # Mostrar botón de confirmación
            
            mouse_pos = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            
            play_button = pygame.Rect(WIDTH // 2 - 75+90, HEIGHT - 100, 150, 50)
            pygame.draw.rect(WIN, DARK_GRAY, play_button)
            draw_text("Play", SMALLFONT, WHITE, WIN, play_button.centerx, play_button.centery)
            
            back_button = pygame.Rect(WIDTH // 2 - 75 -90, HEIGHT - 100, 150, 50)
            pygame.draw.rect(WIN, DARK_GRAY, back_button)
            draw_text("Back", SMALLFONT, WHITE, WIN, back_button.centerx, back_button.centery)

            if play_button.collidepoint(mouse_pos) and click[0]:
                rules = {'xstart':category_selector.selected_option == 'X'  ,'max_turns': -137,'last_moves': 1} # -137 being used as an indicator for Hardcore mode
                WIN.fill(WHITE)
                return rules,True   # Regresar el valor seleccionado cuando se presiona el botón de confirmación
            
            if back_button.collidepoint(mouse_pos) and click[0]:
                rules = None
                WIN.fill(WHITE)
                return rules,False   # Regresar el valor seleccionado cuando se presiona el botón de confirmación
            

            pygame.display.update()



    def game(rules):
        xstart=rules['xstart']
        max_turns=rules['max_turns']
        last_moves=rules['last_moves']
        run = True
        hardcore = max_turns == -137

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

        turn = TurnClass(xstart=xstart)
        moves_log = []
        
        progress=((len(moves_log)+1),max_turns) if not hardcore else '>:3'
        draw_turn(turn,progress)
        pygame.display.update()

        while run and ((hardcore and (not grid_full(moves_log))) or len(moves_log) < max_turns ) :
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    sys.exit()

                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // CELL_SIZE
                    row = (pos[1]-100) // CELL_SIZE

                    if grid[row, col].collapsed is None and grid[row, col].probs[turn.player] < 1 and ((row,col) not in moves_log[len(moves_log)-last_moves:]) and row>=0:
                        grid[row, col].move(turn)
                        moves_log.append((row, col))
                        turn.switch()

            if ((hardcore and (not grid_full(moves_log))) or len(moves_log) < max_turns ):
                draw_grid()
                draw_state(grid)
                progress=((len(moves_log)+1),max_turns) if not hardcore else '>:3'
                draw_turn(turn,progress)
                pygame.display.update()
            else:
                break

        draw_grid()
        draw_state(grid)
        pygame.display.update()
        pygame.time.wait(1000)

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
        back=False
        # Espera para mostrar el resultado final
        while not back:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            mouse_pos = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            
            back_button = pygame.Rect(WIDTH // 2 - 50 // 2+150,20,150, 50)
            #back_button = pygame.Rect(WIDTH // 2 - 75 -90, HEIGHT - 100, 150, 50)
            pygame.draw.rect(WIN, DARK_GRAY, back_button)
            draw_text("Back", SMALLFONT, WHITE, WIN, back_button.centerx, back_button.centery)
            pygame.display.update()
            if back_button.collidepoint(mouse_pos) and click[0]:
                back=True   # Regresar el valor seleccionado cuando se presiona el botón de confirmación
        
        

    # main flux
    while True:
        rules = config()
        game(rules)
    

if __name__ == "__main__":
    main()
