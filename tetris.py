# coding: utf8

# импортируем библиотеку пигуейм и модуль рандома

import pygame
import random

# определяем размеры игрового поля и шрифта, который будет использоваться в игре

SCREEN_X = 400
SCREEN_Y = 800

FONT_SIZE = 20

# значение поворота направо и налево

RIGHT = 0
LEFT = 1

# фон

#BACKGROUND = 'fon.png'
BACKGROUND_COLOR = (0, 0, 0)

# количество блоков по горизонтали, размер блока, количество блока по вертикали, начальная
# скорость падения блока в количестве тактов (чем больше значение - тем меньше скорость)

NUMBER_OF_BLOCKS_HORIZONTAL = 10

BLOCK_SIZE = SCREEN_X // NUMBER_OF_BLOCKS_HORIZONTAL

NUMBER_OF_BLOCKS_VERTICAL = SCREEN_Y // BLOCK_SIZE

INITIAL_SPEED = 100

# формы фигур

FORMS = [["***", " * "], ["***", "  *"], ["***", "*  "], ["** ", " **"], [" **", "** "], ["****"], ["**", "**"]]

# класс блока, имеет размер и цвет

class Block:
    def __init__(self, color):
        self.sur = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.sur.fill(color) 

# класс фигуры, состоит из формы блоков, имеет цвет, определяется случайно при создании фигуры, и 
# координаты (в абсолютных величинах!, т.е. в пикселях от верхнего левого края экрана)
# начальное положение фигуры - примерно посередине экрана по иксу и чуть ниже верха по игреку

class Figure:
    def __init__(self, form):
        self.x = (NUMBER_OF_BLOCKS_HORIZONTAL - 2) * BLOCK_SIZE // 2
        self.y = BLOCK_SIZE
        self.form = FORMS[form]
        self.color = (random.randint(5, 255), random.randint(5, 255), random.randint(5, 255))

# вывод фигуры на экран

    def render(self, where):
        for j in range(len(self.form)):
            for i in range(len(self.form[0])):
                if self.form[j][i] == '*':
                    where.blit(Block(self.color).sur, (self.x + BLOCK_SIZE*i, self.y + BLOCK_SIZE*j))

# поворот фигуры, для поворота сначала инвертируем фигуру по х или по y, в зависимости от направления, 
# а затем транспонируем (зеркально отображаем относительно диагонали)

    def rotate(self, where):
        if where == RIGHT:
            self.form = [[self.form[j][i] for j in range(len(self.form))] for i in range(len(self.form[0])-1,-1,-1)]
        elif where == LEFT:
            self.form = [[self.form[j][i] for j in range(len(self.form)-1,-1,-1)] for i in range(len(self.form[0]))]

# класс главного ящика, в котором падают фигуры, в начале он пустой '', черного цвета (в принципе, можно было ограничиться
# одним только цветом, но вдруг (!) я захочу сделать еще и черные фигуры или переделать тетрис для игры в текстовом режиме

class Box:
    def __init__(self):
        self.box = [[' ' for _ in range(NUMBER_OF_BLOCKS_HORIZONTAL)] for _ in range(NUMBER_OF_BLOCKS_VERTICAL)]
        self.color = [[(0,0,0) for _ in range(NUMBER_OF_BLOCKS_HORIZONTAL)] for _ in range(NUMBER_OF_BLOCKS_VERTICAL)]

# проверка, не сталкивается ли фигура с ящиком: -
# - если опустилась ниже дна, то столкновение, 
# - если произошло наложение фигуры и заполненной клетки ящика, то столкновение

    def check_collision(self, figure, x, y):
        if y >= NUMBER_OF_BLOCKS_VERTICAL - len(figure) + 1: 
            return True
        for i in range(len(figure[0])):
            for j in range(len(figure)):
                if figure[j][i] == '*' and self.box[y + j][x + i] == '*':
                    return True
        return False

# падение фигуры. Пока она с чем-то не столкнется, опускать вниз, если столкнулась - поднять на одну клетку,
# после чего заполнить соответственные клетки ящика нужными цветами и знаками наличия фигуры,
# после чего удалить заполненные линии и вернуть счет (если есть)

    def drop(self, figure, x, y, color):

        while not self.check_collision(figure, x, y):
            y += 1
        y -= 1

        for i in range(len(figure[0])):
            for j in range(len(figure)):
                if figure[j][i] == '*':
                    self.box[y + j][x + i] = '*'
                    self.color[y + j][x + i] = color

        return self.remove_lines()

# удаление целых линий и прибавление счета, если целый ряд в ящике состоит из заполненных ячеек - удалить его,
# создать новый сверху, счет убранных линий в конце вернуть квадратичным - чем больше линий за один раз убрали,
# тем больше очков добавляется
# кроме того если скорость (глобальная перменная) меньше максимальной - увеличить ее за каждую линию
                             	
    def remove_lines(self):
        score = 0
        for j in range(NUMBER_OF_BLOCKS_VERTICAL):
            temp = 0
            for i in range(NUMBER_OF_BLOCKS_HORIZONTAL):
                if self.box[j][i] == '*':
                    temp += 1
            if temp == NUMBER_OF_BLOCKS_HORIZONTAL:
                global speed
                if speed > 1: 
                    speed -= 1
                self.box.remove(self.box[j])
                self.box.insert(0, [' ' for _ in range(NUMBER_OF_BLOCKS_HORIZONTAL)])
                score += 1
        return(score*score)

# отрисовка ящика

    def render(self, where):
        for j in range(NUMBER_OF_BLOCKS_VERTICAL):
            for i in range(NUMBER_OF_BLOCKS_HORIZONTAL):
                if self.box[j][i] == '*':
                    where.blit(Block(self.color[j][i]).sur, (BLOCK_SIZE*i, BLOCK_SIZE*j))

# главная функция - процесс игры, получает на входе текущий счет, на выходе возвращяет счет после игры

def main(score):

# запуск таймера, создание пустого ящика, фигуры пока еще нет, обнуление счетчика, который будет определять, 
# когда сдвигать фигуру вниз

    timer = pygame.time.Clock()
    exit = False

    box = Box()

    no_figure = True
    coord = 0

    while not exit:

# фон, без картинки, отрисовка ящика

#        fon = pygame.image.load(BACKGROUND)
        fon = pygame.Surface((SCREEN_X, SCREEN_Y))
        fon.fill(BACKGROUND_COLOR) 

        screen.blit(fon, (0, 0))

        box.render(screen)

# если фигуры нет - согдать фигуру случайной формы, обнулить счетчик скорости, если фигура с чем-то столкнулась - выйти из игры

        if no_figure:
            fig = Figure(random.randint(0, len(FORMS)-1))
            no_figure = False
            coord = 0
            if box.check_collision(fig.form, fig.x // BLOCK_SIZE, fig.y // BLOCK_SIZE):
                exit = True

# блок управления. глобальный выход из цикла и из игры без результата по нажатию крестика

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit = True
                global new_game
                new_game = False

# при нажатии пробела - сбросить фигуру и добавить очки за линии, отметить, что фигуры активной больше нет,
# при нажатии на вверх-вниз повернуть фигуру вправо-влево, если она выйдет за пределы экрана или с чем-то столкнется - 
# тут же вернуть назад,
# при нажатии на вправо-влево если она не выйдет за пределы экрана и ни с чем при этом не столкнется - передвинуть
# вправо-влево на размер блока

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    score += box.drop(fig.form, fig.x // BLOCK_SIZE, fig.y // BLOCK_SIZE, fig.color)
                    no_figure = True
                elif event.key == pygame.K_UP:
                    fig.rotate(RIGHT)
                    if fig.x > SCREEN_X - len(fig.form[0])*BLOCK_SIZE or box.check_collision(fig.form, fig.x // BLOCK_SIZE, fig.y // BLOCK_SIZE): 
                        fig.rotate(LEFT)
                elif event.key == pygame.K_DOWN:
                    fig.rotate(LEFT)
                    if fig.x > SCREEN_X - len(fig.form[0])*BLOCK_SIZE or box.check_collision(fig.form, fig.x // BLOCK_SIZE, fig.y // BLOCK_SIZE): 
                        fig.rotate(RIGHT)
                elif event.key == pygame.K_LEFT:
                    if fig.x >= BLOCK_SIZE and not box.check_collision(fig.form, (fig.x - BLOCK_SIZE) // BLOCK_SIZE, fig.y // BLOCK_SIZE):
                        fig.x -= BLOCK_SIZE
                elif event.key == pygame.K_RIGHT:
                    if fig.x <= SCREEN_X - (1 + len(fig.form[0]))*BLOCK_SIZE and not box.check_collision(fig.form, (fig.x + BLOCK_SIZE) // BLOCK_SIZE, fig.y // BLOCK_SIZE):
                        fig.x += BLOCK_SIZE

# нарисовать фигуру

        fig.render(screen)

# если счетчик равен скорости - сдвинуть фигуру на один шаг вниз, если она при этом с чем-то столкнется - поднять вверх на 1 клетку 
# и сбросить вниз, обнулить счетчик скорости

        if coord == speed: 
            fig.y += BLOCK_SIZE
            if box.check_collision(fig.form, fig.x // BLOCK_SIZE, fig.y // BLOCK_SIZE):
                box.drop(fig.form, fig.x // BLOCK_SIZE, (fig.y - BLOCK_SIZE) // BLOCK_SIZE, fig.color)
                no_figure = True
            coord = 0

# увеличить счетчик скорости на единицу

        coord += 1

# добавляем счет в угол экрана

        score_font = pygame.font.SysFont("comicsansms", FONT_SIZE)
        result = score_font.render("Счет: " + str(score), 1, (0, 0, 255))
        screen.blit(result, (0, 0))

        window.blit(screen, (0, 0))
        timer.tick()
        pygame.display.flip()

# возвращяет счет после игры

    return score

# заключительный экран, получает на входе текущий счет, на выходе выдает (в консоль и на экран), 
# нужно ли начать новую игру (да или нет)

def end(score):

    print("Ваш итоговый счет {}".format(score))

#    fon = pygame.image.load(BACKGROUND)
    fon = pygame.Surface((SCREEN_X, SCREEN_Y))
    fon.fill(BACKGROUND_COLOR) 

    screen.blit(fon, (0, 0))

#    box.render(screen)
#    fig.render(screen)


    while True:

# обработка событий, если нажата кнопка n - запустить новую игру, любая другая клавиша - выйти

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n: 
                    return True
                else:
                    return False

# инициировать шрифты, вывести на экран большим шрифтом результат и маленьким информацию о том, что нажимать

        score_font = pygame.font.SysFont("comicsansms", 20)
        result   = score_font.render("Ваш итоговый счет {}.".format(score), 1, (255,0,0))
        result_2 = score_font.render("Нажимте N чтоб начать новую игру ", 1, (255,255,0))
        result_3 = score_font.render("или любую другую клавишу чтоб выйти.", 1, (255,255,0))
        screen.blit(result,   (0, SCREEN_Y//2   ))
        screen.blit(result_2, (0, SCREEN_Y//2+25))
        screen.blit(result_3, (0, SCREEN_Y//2+50))
 
        window.blit(screen, (0, 0))
        pygame.display.flip()


if __name__ == '__main__':

# создаем главное окно, даем ему название, создаем экран на главном окне, где все будет происходить, задаем условия выхода из цикла
# инициализируем шрифты

    window = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
    pygame.display.set_caption('Тетрис')
    screen = pygame.Surface((SCREEN_X, SCREEN_Y))
    pygame.font.init()

# главный цикл игры, обнуляем счет, скорость, запускаем игру, получаем счет на выходе, запускаем итоговый экран от счета, который определяет,
# нужно ли начинать с начала игру

    new_game = True

    while new_game:
        speed = INITIAL_SPEED
        score = 0
        score = main(score)
        if new_game:
            new_game = end(score) 
