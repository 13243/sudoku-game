import time
import random
import copy
import pygame as pg
from pygame import mixer
from typing import List, Tuple, Optional, Dict, Any
from abc import ABC, abstractmethod
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

try:
    from solver import *
    from boards import giveBoard
except ImportError:
    def giveBoard(difficulty):
        return [[0]*9 for _ in range(9)]


class ColorManager:

    COLOR_MAP = {
        'green': (40, 160, 30),
        'black': (20, 20, 20),
        'white': (240, 240, 240),
        'dimWhite': (150, 150, 150),
        'red': (170, 10, 10),
        'orange': (190, 80, 20),
        'grey': (80, 80, 80),
        'dimGrey': (40, 40, 40),
        'veryDimGrey': (30, 30, 30)
    }

    @classmethod
    def get_color(cls, color_name: str) -> Tuple[int, int, int]:
        return cls.COLOR_MAP.get(color_name, (0, 0, 0))


class SoundManager:

    def __init__(self):
        self.sounds = {}
        try:
            pg.mixer.music.load("backgroundMusic.ogg")
            self.sounds = {
                'click': pg.mixer.Sound("click.ogg"),
                'move': pg.mixer.Sound("move.ogg"),
                'congratulation': pg.mixer.Sound("congratulation.ogg"),
                'gameStart': pg.mixer.Sound("gameStart.ogg"),
                'gameOver': pg.mixer.Sound("gameOver.ogg")
            }
        except:
            self.sounds = {}

    def play_background_music(self) -> None:
        try:
            pg.mixer.music.play(-1)
        except:
            pass

    def play_sound(self, sound_name: str) -> None:
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass

    def pause_background_music(self) -> None:
        try:
            pg.mixer.music.pause()
        except:
            pass

    def unpause_background_music(self) -> None:
        try:
            pg.mixer.music.unpause()
        except:
            pass


class Renderer:

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        if not pg.font.get_init():
            pg.font.init()

        self.fonts = self._load_fonts()
        self.text_cache = {}

        self.shell_positions = self._calculate_shell_positions()
        self.shell_boundaries = self._calculate_shell_boundaries()

    def _load_fonts(self) -> Dict[str, Dict[str, Any]]:
        fonts = {}
        try:
            fonts = {
                'sudoku': {'font': pg.font.Font("SEASRN__.ttf", 100), 'big_size': 100},
                'main_menu': {'font': pg.font.Font("RobotoSlab-Bold.ttf", 30), 'big_size': 30},
                'play': {'font': pg.font.Font("RobotoSlab-Bold.ttf", 50), 'big_size': 65},
                'numbers': {'font': pg.font.Font('TypeWrongSmudgedBold.ttf', 35), 'big_size': 45},
                'numbers_red': {'font': pg.font.Font('TypeWrongSmudgedBold.ttf', 35), 'big_size': 35},
                'clock': {'font': pg.font.Font("TypeWrongSmudgedBold.ttf", 35), 'big_size': 35}
            }
        except (FileNotFoundError, pg.error):
            fonts = {
                'sudoku': {'font': pg.font.SysFont(None, 100), 'big_size': 100},
                'main_menu': {'font': pg.font.SysFont(None, 30), 'big_size': 30},
                'play': {'font': pg.font.SysFont(None, 50), 'big_size': 65},
                'numbers': {'font': pg.font.SysFont(None, 35), 'big_size': 45},
                'numbers_red': {'font': pg.font.SysFont(None, 35), 'big_size': 35},
                'clock': {'font': pg.font.SysFont(None, 35), 'big_size': 35}
            }
        return fonts

    def render_text(self, text: str, font_type: str, color: str, big: bool = False) -> pg.Surface:
        cache_key = f"{text}_{font_type}_{color}_{big}"
        if cache_key in self.text_cache:
            return self.text_cache[cache_key]

        font_info = self.fonts.get(font_type, self.fonts['main_menu'])
        if big and 'big_size' in font_info:
            try:
                temp_font = pg.font.Font(font_info['font'].font, font_info['big_size'])
            except:
                temp_font = pg.font.SysFont(None, font_info['big_size'])
            surface = temp_font.render(text, True, ColorManager.get_color(color))
        else:
            surface = font_info['font'].render(text, True, ColorManager.get_color(color))

        self.text_cache[cache_key] = surface
        return surface

    def _calculate_shell_positions(self) -> List[List[Tuple[int, int]]]:
        positions = [[] for _ in range(9)]
        i = 0
        for y in range(100, 629, 66):
            for x in range(2, 531, 66):
                positions[i].append((x, y))
            i += 1
        return positions

    def _calculate_shell_boundaries(self) -> List[List[Tuple[int, int, int, int]]]:
        boundaries = [[] for _ in range(9)]
        i = 0
        for y in range(100, 629, 66):
            for x in range(2, 531, 66):
                boundaries[i].append((x, x + 66, y, y + 66))
            i += 1
        return boundaries

    def get_shell_at_position(self, mouse_x: int, mouse_y: int, board: 'SudokuBoard') -> Optional[Tuple[int, int]]:
        for y, row in enumerate(self.shell_boundaries):
            for x, (x1, x2, y1, y2) in enumerate(row):
                if x1 < mouse_x < x2 and y1 < mouse_y < y2:
                    if board.sudoku_board[y][x] == 0:
                        return self.shell_positions[y][x]
        return None

    def draw_grid(self, screen: pg.Surface, board: 'SudokuBoard') -> None:
        grey_grid_lines = True

        if board.is_full():
            grey_grid_lines = False
            for y in range(9):
                for x in range(9):
                    if not board.is_valid_move(x, y, board.current_board[y][x]):
                        grey_grid_lines = True
                        break

        color = 'grey' if grey_grid_lines else 'green'
        self._draw_grid_lines(screen, color)

    def _draw_grid_lines(self, screen: pg.Surface, color: str) -> None:
        thickness = 6
        thinness = 3

        for ver_thin_pos in range(2, 597, 66):
            pg.draw.line(screen, ColorManager.get_color('dimGrey'),
                         (ver_thin_pos, 100), (ver_thin_pos, 698), thinness)

        for hor_thin_pos in range(100, 695, 66):
            pg.draw.line(screen, ColorManager.get_color('dimGrey'),
                         (2, hor_thin_pos), (600, hor_thin_pos), thinness)

        for ver_thick_pos in range(2, 597, 198):
            pg.draw.line(screen, ColorManager.get_color(color),
                         (ver_thick_pos, 100), (ver_thick_pos, 694), thickness)

        for hor_thick_pos in range(100, 695, 198):
            pg.draw.line(screen, ColorManager.get_color(color),
                         (2, hor_thick_pos), (596, hor_thick_pos), thickness)

    def animate_grid(self, screen: pg.Surface, grid_type: str) -> None:
        screen.fill(ColorManager.get_color('black'))

        if grid_type == 'main':
            self._animate_main_grid(screen)
        elif grid_type == 'game':
            self._animate_game_grid(screen)

    def _animate_main_grid(self, screen: pg.Surface) -> None:
        thickness = 6
        thinness = 3

        screen.fill(ColorManager.get_color('black'))

        for thinY in range(0, self.screen_height + 1, 15):
            for ver_thin_pos in range(4, self.screen_width - thickness, self.screen_width // 9):
                pg.draw.line(screen, ColorManager.get_color('dimGrey'),
                             (ver_thin_pos, 0), (ver_thin_pos, thinY), thinness)
            pg.display.update()
            time.sleep(0.01)

        for thinX in range(0, self.screen_width + 1, 15):
            for hor_thin_pos in range(100, self.screen_height - 100, self.screen_width // 9):
                pg.draw.line(screen, ColorManager.get_color('dimGrey'),
                             (0, hor_thin_pos), (thinX, hor_thin_pos), thinness)
            pg.display.update()
            time.sleep(0.01)

        for thickY in range(0, self.screen_height + 1, 6):
            for ver_thick_pos in range(4, self.screen_width - thickness, 200 - 4):
                pg.draw.line(screen, ColorManager.get_color('grey'),
                             (ver_thick_pos, 0), (ver_thick_pos, thickY), thickness)
            pg.display.update()
            time.sleep(0.01)

        for thickX in range(0, self.screen_width + 1, 6):
            for hor_thick_pos in range(100, self.screen_height - 100, 200 - 2):
                pg.draw.line(screen, ColorManager.get_color('grey'),
                             (0, hor_thick_pos), (thickX, hor_thick_pos), thickness)
            pg.display.update()
            time.sleep(0.01)

    def _animate_game_grid(self, screen: pg.Surface) -> None:
        screen.fill(ColorManager.get_color('black'))

        for thinY in range(100, 698 + 1, 12):
            for ver_thin_pos in range(2, 596 + 1, 66):
                pg.draw.line(screen, ColorManager.get_color('dimGrey'),
                             (ver_thin_pos, 100), (ver_thin_pos, thinY), 3)
            pg.display.update()
            time.sleep(0.01)

        for thinX in range(2, 600 + 1, 12):
            for hor_thin_pos in range(100, 694 + 1, 66):
                pg.draw.line(screen, ColorManager.get_color('dimGrey'),
                             (2, hor_thin_pos), (thinX, hor_thin_pos), 3)
            pg.display.update()
            time.sleep(0.01)

        for thickY in range(100, 694 + 1, 6):
            for ver_thick_pos in range(2, 596 + 1, 198):
                pg.draw.line(screen, ColorManager.get_color('grey'),
                             (ver_thick_pos, 100), (ver_thick_pos, thickY), 6)
            pg.display.update()
            time.sleep(0.01)

        for thickX in range(2, 596 + 1, 6):
            for hor_thick_pos in range(100, 694 + 1, 198):
                pg.draw.line(screen, ColorManager.get_color('grey'),
                             (2, hor_thick_pos), (thickX, hor_thick_pos), 6)
            pg.display.update()
            time.sleep(0.01)


class SudokuBoard:

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        empty_row = [0] * 9
        self.sudoku_board = [empty_row[:] for _ in range(9)]
        self.user_board = [empty_row[:] for _ in range(9)]
        self.current_board = [empty_row[:] for _ in range(9)]

    def load_board(self, difficulty: str) -> None:
        self.sudoku_board = giveBoard(difficulty)
        self.user_board = [[0] * 9 for _ in range(9)]
        self.update_current_board()

    def update_current_board(self) -> None:
        self.current_board = copy.deepcopy(self.sudoku_board)
        for y in range(9):
            for x in range(9):
                if self.user_board[y][x] != 0:
                    self.current_board[y][x] = self.user_board[y][x]

    def is_full(self) -> bool:
        return isFull(self.current_board)

    def is_valid_move(self, x: int, y: int, num: int) -> bool:
        return possible(self.current_board, x, y, num)

    def set_user_number(self, x: int, y: int, num: int) -> None:
        if 0 <= x < 9 and 0 <= y < 9 and 0 <= num <= 9:
            self.user_board[y][x] = num
            self.update_current_board()

    def get_cell_value(self, x: int, y: int) -> int:
        if 0 <= x < 9 and 0 <= y < 9:
            return self.current_board[y][x]
        return 0


class GameStateManager:

    def __init__(self, game: 'SudokuGame'):
        self.game = game
        self.current_state = 'intro'
        self.state_data = {
            'intro': {'grid_drawn': False, 'animation_complete': False},
            'gameplay': {
                'selected_shell': None,
                'game_grid_switch': True,
                'reset_time': True,
                'start_time': 0,
                'congrates_played': False
            },
            'solver': {
                'game_grid_switch': True,
                'selected_shell': None
            },
            'background_state': None
        }

    def handle_events(self, event: pg.event.Event) -> None:
        if self.current_state == 'intro':
            self._handle_intro_events(event)
        elif self.current_state == 'main_menu':
            self._handle_main_menu_events(event)
        elif self.current_state == 'play_menu':
            self._handle_play_menu_events(event)
        elif self.current_state == 'game_board':
            self._handle_game_board_events(event)
        elif self.current_state == 'gameplay':
            self._handle_gameplay_events(event)
        elif self.current_state == 'solver':
            self._handle_solver_events(event)
        elif self.current_state == 'confirm_popup':
            self._handle_confirm_popup_events(event)
        elif self.current_state == 'autosolve_popup':
            self._handle_autosolve_popup_events(event)

    def update(self) -> None:
        if self.current_state == 'gameplay':
            gameplay_data = self.state_data['gameplay']
            if gameplay_data['reset_time']:
                gameplay_data['start_time'] = time.time()
                gameplay_data['reset_time'] = False

            if self.game.board.is_full() and not gameplay_data['congrates_played']:
                self.game.sound_manager.play_sound('congratulation')
                gameplay_data['congrates_played'] = True

    def render(self, screen: pg.Surface) -> None:
        if self.current_state == 'intro':
            self._render_intro(screen)
        elif self.current_state == 'main_menu':
            self._render_main_menu(screen)
        elif self.current_state == 'play_menu':
            self._render_play_menu(screen)
        elif self.current_state == 'game_board':
            self._render_game_board(screen)
        elif self.current_state == 'gameplay':
            self._render_gameplay(screen)
        elif self.current_state == 'solver':
            self._render_solver(screen)
        elif self.current_state == 'confirm_popup':
            self._render_confirm_popup(screen)
        elif self.current_state == 'autosolve_popup':
            self._render_autosolve_popup(screen)

    def change_state(self, new_state: str, background_state: str = None) -> None:
        self.current_state = new_state
        if background_state:
            self.state_data['background_state'] = background_state

    def _handle_intro_events(self, event: pg.event.Event) -> None:
        if event.type == pg.KEYUP and event.key == pg.K_RETURN:
            self.game.sound_manager.play_sound('click')
            self.game.screen.fill(ColorManager.get_color('black'))
            pg.display.update()
            self.change_state('main_menu')

    def _handle_main_menu_events(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEBUTTONUP:
            x, y = pg.mouse.get_pos()

            if 180 < x < 420 and 300 < y < 360:
                self.game.sound_manager.play_sound('click')
                self.change_state('play_menu')
            elif 150 < x < 450 and 400 < y < 460:
                self.game.sound_manager.play_sound('click')
                self.change_state('solver')
            elif 80 < x < 500 and 500 < y < 560:
                self.game.sound_manager.play_sound('click')
                self.change_state('game_board')
            elif 180 < x < 420 and 600 < y < 660:
                self.game.running = False

    def _handle_play_menu_events(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEBUTTONUP:
            x, y = pg.mouse.get_pos()

            if 50 < x < 230 and 35 < y < 75:
                self.game.sound_manager.play_sound('click')
                self.change_state('main_menu')
            elif 180 < x < 420 and 300 < y < 360:
                self._start_game('easy')
            elif 145 < x < 455 and 400 < y < 460:
                self._start_game('medium')
            elif 180 < x < 420 and 500 < y < 560:
                self._start_game('hard')
            elif 110 < x < 490 and 600 < y < 660:
                self._start_game('veryHard')

    def _handle_game_board_events(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEBUTTONUP:
            x, y = pg.mouse.get_pos()

            if 50 < x < 230 and 35 < y < 75:
                self.game.sound_manager.play_sound('click')
                self.change_state('main_menu')

    def _handle_gameplay_events(self, event: pg.event.Event) -> None:
        gameplay_data = self.state_data['gameplay']

        if event.type == pg.KEYDOWN:
            if gameplay_data['selected_shell'] and event.unicode.isdigit():
                num = int(event.unicode)
                if 0 <= num <= 9:
                    self._insert_number_gameplay(num)
                    self.game.sound_manager.play_sound('move')
            elif event.key == pg.K_SPACE:
                self.game.sound_manager.play_sound('click')
                self.change_state('autosolve_popup', 'gameplay')

        elif event.type == pg.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pg.mouse.get_pos()
            gameplay_data['selected_shell'] = self.game.renderer.get_shell_at_position(
                mouse_x, mouse_y, self.game.board)

            if 20 < mouse_x < 200 and 15 < mouse_y < 55:
                self.game.sound_manager.play_sound('click')
                self.change_state('confirm_popup', 'gameplay')

    def _handle_solver_events(self, event: pg.event.Event) -> None:
        solver_data = self.state_data['solver']

        if event.type == pg.KEYDOWN:
            if solver_data['selected_shell'] and event.unicode.isdigit():
                num = int(event.unicode)
                if 0 <= num <= 9:
                    self._insert_number_solver(num)
                    self.game.sound_manager.play_sound('move')
            elif event.key == pg.K_SPACE:
                if self._check_board_valid():
                    self.game.sound_manager.play_sound('click')
                    self.change_state('autosolve_popup', 'solver')

        elif event.type == pg.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pg.mouse.get_pos()
            solver_data['selected_shell'] = self.game.renderer.get_shell_at_position(
                mouse_x, mouse_y, self.game.board)

            if 20 < mouse_x < 200 and 15 < mouse_y < 55:
                self.game.sound_manager.play_sound('click')
                self.change_state('main_menu')

    def _handle_confirm_popup_events(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEBUTTONUP:
            x, y = pg.mouse.get_pos()

            if 130 < x < 270 and 415 < y < 460:
                self.game.sound_manager.play_sound('click')
                self.change_state(self.state_data['background_state'])
            elif 400 < x < 460 and 415 < y < 460:
                self.game.sound_manager.play_sound('click')
                self.game.sound_manager.unpause_background_music()
                self.change_state('main_menu')

    def _handle_autosolve_popup_events(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEBUTTONUP:
            x, y = pg.mouse.get_pos()

            if 130 < x < 270 and 415 < y < 460:
                self.game.sound_manager.play_sound('click')
                self.change_state(self.state_data['background_state'])
            elif 320 < x < 490 and 385 < y < 420:
                self.game.sound_manager.play_sound('click')
                self._solve_directly()
                self.change_state(self.state_data['background_state'])
            elif 310 < x < 510 and 480 < y < 520:
                self.game.sound_manager.play_sound('click')
                self.change_state(self.state_data['background_state'])
                self._solve_with_animation()

    def _start_game(self, difficulty: str) -> None:
        self.game.sound_manager.play_sound('click')
        self.game.sound_manager.pause_background_music()
        self.game.sound_manager.play_sound('gameStart')
        self.game.board.load_board(difficulty)
        self.state_data['gameplay'] = {
            'selected_shell': None,
            'game_grid_switch': True,
            'reset_time': True,
            'start_time': 0,
            'congrates_played': False
        }
        self.change_state('gameplay')

    def _insert_number_gameplay(self, num: int) -> None:
        gameplay_data = self.state_data['gameplay']
        if gameplay_data['selected_shell']:
            for y, row in enumerate(self.game.renderer.shell_positions):
                for x, pos in enumerate(row):
                    if pos == gameplay_data['selected_shell']:
                        self.game.board.set_user_number(x, y, num)
                        return

    def _insert_number_solver(self, num: int) -> None:
        solver_data = self.state_data['solver']
        if solver_data['selected_shell']:
            for y, row in enumerate(self.game.renderer.shell_positions):
                for x, pos in enumerate(row):
                    if pos == solver_data['selected_shell']:
                        self.game.board.set_user_number(x, y, num)
                        return

    def _check_board_valid(self) -> bool:
        for y in range(9):
            for x in range(9):
                if self.game.board.current_board[y][x] != 0:
                    if not self.game.board.is_valid_move(x, y, self.game.board.current_board[y][x]):
                        return False
        return True

    def _solve_directly(self) -> None:
        temp_board = copy.deepcopy(self.game.board.current_board)
        autosolve(temp_board)

        for y in range(9):
            for x in range(9):
                if temp_board[y][x] != self.game.board.sudoku_board[y][x]:
                    self.game.board.user_board[y][x] = temp_board[y][x]

        self.game.board.update_current_board()

    def _solve_with_animation(self) -> None:
        self._solve_directly()

    def _render_intro(self, screen: pg.Surface) -> None:
        intro_data = self.state_data['intro']
        if not intro_data['grid_drawn']:
            self.game.renderer.animate_grid(screen, 'main')
            intro_data['grid_drawn'] = True
            intro_data['animation_complete'] = True

        if intro_data['animation_complete']:
            sudoku_text = self.game.renderer.render_text("SUDOKU", 'sudoku', 'red')
            line_text = self.game.renderer.render_text("press [ENTER]", 'main_menu', 'green')

            screen.blit(sudoku_text, (60, 120))
            screen.blit(line_text, (200, 600))

    def _render_main_menu(self, screen: pg.Surface) -> None:
        screen.fill(ColorManager.get_color('black'))

        sudoku_text = self.game.renderer.render_text("SUDOKU", 'sudoku', 'white')
        screen.blit(sudoku_text, (60, 120))

        mouse_x, mouse_y = pg.mouse.get_pos()

        play_big = 180 < mouse_x < 420 and 300 < mouse_y < 360
        play_text = self.game.renderer.render_text("-: PLAY :-", 'play', 'white', play_big)
        screen.blit(play_text, (180 if not play_big else 150, 300 if not play_big else 280))

        solver_big = 150 < mouse_x < 450 and 400 < mouse_y < 460
        solver_text = self.game.renderer.render_text("-: SOLVER :-", 'play', 'white', solver_big)
        screen.blit(solver_text, (150 if not solver_big else 110, 400 if not solver_big else 380))

        game_board_big = 80 < mouse_x < 500 and 500 < mouse_y < 560
        game_board_text = self.game.renderer.render_text("-: GAME BOARD :-", 'play', 'white', game_board_big)
        screen.blit(game_board_text, (80 if not game_board_big else 15, 500 if not game_board_big else 480))

        exit_big = 180 < mouse_x < 420 and 600 < mouse_y < 660
        exit_text = self.game.renderer.render_text("-: EXIT :-", 'play', 'white', exit_big)
        screen.blit(exit_text, (180 if not exit_big else 150, 600 if not exit_big else 580))

    def _render_play_menu(self, screen: pg.Surface) -> None:
        screen.fill(ColorManager.get_color('black'))

        sudoku_text = self.game.renderer.render_text("SUDOKU", 'sudoku', 'white')
        screen.blit(sudoku_text, (60, 120))

        mouse_x, mouse_y = pg.mouse.get_pos()

        main_big = 50 < mouse_x < 230 and 35 < mouse_y < 75
        main_text = self.game.renderer.render_text("[main menu]", 'main_menu', 'white', main_big)
        if main_big:
            pg.draw.rect(screen, ColorManager.get_color('white'), ((50, 40), (180, 40)))
            screen.blit(main_text, (50, 35))
        else:
            screen.blit(main_text, (50, 35))

        easy_big = 180 < mouse_x < 420 and 300 < mouse_y < 360
        easy_text = self.game.renderer.render_text("-: EASY :-", 'play', 'white', easy_big)
        screen.blit(easy_text, (180 if not easy_big else 150, 300 if not easy_big else 280))

        medium_big = 145 < mouse_x < 455 and 400 < mouse_y < 460
        medium_text = self.game.renderer.render_text("-: MEDIUM :-", 'play', 'white', medium_big)
        screen.blit(medium_text, (145 if not medium_big else 100, 400 if not medium_big else 380))

        hard_big = 180 < mouse_x < 420 and 500 < mouse_y < 560
        hard_text = self.game.renderer.render_text("-: HARD :-", 'play', 'white', hard_big)
        screen.blit(hard_text, (180 if not hard_big else 150, 500 if not hard_big else 480))

        very_hard_big = 110 < mouse_x < 490 and 600 < mouse_y < 660
        very_hard_text = self.game.renderer.render_text("-: VERY HARD :-", 'play', 'white', very_hard_big)
        screen.blit(very_hard_text, (110 if not very_hard_big else 60, 600 if not very_hard_big else 580))

    def _render_game_board(self, screen: pg.Surface) -> None:
        screen.fill(ColorManager.get_color('black'))

        sudoku_text = self.game.renderer.render_text("SUDOKU", 'sudoku', 'white')
        screen.blit(sudoku_text, (60, 80))

        mouse_x, mouse_y = pg.mouse.get_pos()

        main_big = 50 < mouse_x < 230 and 35 < mouse_y < 75
        main_text = self.game.renderer.render_text("[main menu]", 'main_menu', 'white', main_big)
        if main_big:
            pg.draw.rect(screen, ColorManager.get_color('white'), ((50, 40), (180, 40)))
            screen.blit(main_text, (50, 35))
        else:
            screen.blit(main_text, (50, 35))

    def _render_gameplay(self, screen: pg.Surface) -> None:
        gameplay_data = self.state_data['gameplay']

        if gameplay_data['game_grid_switch']:
            self.game.renderer.animate_grid(screen, 'game')
            gameplay_data['game_grid_switch'] = False

        screen.fill(ColorManager.get_color('black'))
        self.game.renderer.draw_grid(screen, self.game.board)

        self._draw_gameplay_highlights(screen)
        self._draw_gameplay_numbers(screen)

        self._draw_gameplay_ui_elements(screen)
        self._draw_gameplay_timer(screen)

    def _render_solver(self, screen: pg.Surface) -> None:
        solver_data = self.state_data['solver']

        if solver_data['game_grid_switch']:
            self.game.renderer.animate_grid(screen, 'game')
            solver_data['game_grid_switch'] = False

        screen.fill(ColorManager.get_color('black'))
        self.game.renderer.draw_grid(screen, self.game.board)

        self._draw_solver_highlights(screen)
        self._draw_solver_numbers(screen)

        self._draw_solver_ui_elements(screen)

    def _render_confirm_popup(self, screen: pg.Surface) -> None:
        self._render_state_by_name(screen, self.state_data['background_state'])

        pg.draw.rect(screen, ColorManager.get_color('black'), ((0, 300), (600, 200)))

        query_text = self.game.renderer.render_text(
            "Are you sure? You will lose your progress!", 'main_menu', 'white')
        screen.blit(query_text, (50, 340))

        mouse_x, mouse_y = pg.mouse.get_pos()

        cancel_big = 130 < mouse_x < 270 and 415 < mouse_y < 460
        ok_big = 400 < mouse_x < 460 and 415 < mouse_y < 460

        cancel_text = self.game.renderer.render_text("[CANCEL]", 'main_menu', 'white', cancel_big)
        ok_text = self.game.renderer.render_text("[OK]", 'main_menu', 'white', ok_big)

        if cancel_big:
            pg.draw.rect(screen, ColorManager.get_color('white'), ((130, 420), (140, 40)))
            screen.blit(cancel_text, (130, 415))
        else:
            screen.blit(cancel_text, (130, 415))

        if ok_big:
            pg.draw.rect(screen, ColorManager.get_color('white'), ((400, 420), (60, 40)))
            screen.blit(ok_text, (400, 415))
        else:
            screen.blit(ok_text, (400, 415))

    def _render_autosolve_popup(self, screen: pg.Surface) -> None:
        self._render_state_by_name(screen, self.state_data['background_state'])

        pg.draw.rect(screen, ColorManager.get_color('black'), ((0, 300), (600, 250)))

        query_text = self.game.renderer.render_text(
            "Are you sure? You don't want to solve on your own!", 'main_menu', 'white')
        screen.blit(query_text, (10, 320))

        mouse_x, mouse_y = pg.mouse.get_pos()

        cancel_big = 130 < mouse_x < 270 and 415 < mouse_y < 460
        direct_big = 320 < mouse_x < 490 and 385 < mouse_y < 420
        animation_big = 310 < mouse_x < 510 and 480 < mouse_y < 520

        cancel_text = self.game.renderer.render_text("[CANCEL]", 'main_menu', 'white', cancel_big)
        direct_text = self.game.renderer.render_text("[SOLUTION]", 'main_menu', 'white', direct_big)
        animation_text = self.game.renderer.render_text("[ANIMATION]", 'main_menu', 'white', animation_big)

        if cancel_big:
            pg.draw.rect(screen, ColorManager.get_color('white'), ((130, 420), (140, 40)))
            screen.blit(cancel_text, (130, 415))
        else:
            screen.blit(cancel_text, (130, 415))

        if direct_big:
            pg.draw.rect(screen, ColorManager.get_color('white'), ((320, 385), (170, 35)))
            screen.blit(direct_text, (320, 380))
        else:
            screen.blit(direct_text, (320, 380))

        if animation_big:
            pg.draw.rect(screen, ColorManager.get_color('white'), ((310, 480), (200, 40)))
            screen.blit(animation_text, (310, 475))
        else:
            screen.blit(animation_text, (310, 475))

    def _render_state_by_name(self, screen: pg.Surface, state_name: str) -> None:
        if state_name == 'gameplay':
            self._render_gameplay(screen)
        elif state_name == 'solver':
            self._render_solver(screen)

    def _draw_gameplay_highlights(self, screen: pg.Surface) -> None:
        gameplay_data = self.state_data['gameplay']
        mouse_x, mouse_y = pg.mouse.get_pos()

        hover_shell = self.game.renderer.get_shell_at_position(mouse_x, mouse_y, self.game.board)
        if hover_shell:
            pg.draw.rect(screen, ColorManager.get_color('veryDimGrey'),
                         ((hover_shell[0] + 6, hover_shell[1] + 6), (56, 56)))

        if gameplay_data['selected_shell']:
            pg.draw.rect(screen, ColorManager.get_color('grey'),
                         ((gameplay_data['selected_shell'][0] + 6, gameplay_data['selected_shell'][1] + 6), (56, 56)))

    def _draw_gameplay_numbers(self, screen: pg.Surface) -> None:
        for y, row in enumerate(self.game.board.sudoku_board):
            for x, num in enumerate(row):
                if num != 0:
                    pos = self.game.renderer.shell_positions[y][x]
                    self._draw_number(screen, num, pos, 'grey', big=True)

        for y, row in enumerate(self.game.board.user_board):
            for x, num in enumerate(row):
                if num != 0:
                    pos = self.game.renderer.shell_positions[y][x]
                    is_valid = self.game.board.is_valid_move(x, y, num)
                    color = 'white' if is_valid else 'red'
                    self._draw_number(screen, num, pos, color)

    def _draw_solver_highlights(self, screen: pg.Surface) -> None:
        solver_data = self.state_data['solver']
        mouse_x, mouse_y = pg.mouse.get_pos()

        hover_shell = self.game.renderer.get_shell_at_position(mouse_x, mouse_y, self.game.board)
        if hover_shell:
            pg.draw.rect(screen, ColorManager.get_color('veryDimGrey'),
                         ((hover_shell[0] + 6, hover_shell[1] + 6), (56, 56)))

        if solver_data['selected_shell']:
            pg.draw.rect(screen, ColorManager.get_color('grey'),
                         ((solver_data['selected_shell'][0] + 6, solver_data['selected_shell'][1] + 6), (56, 56)))

    def _draw_solver_numbers(self, screen: pg.Surface) -> None:
        for y, row in enumerate(self.game.board.user_board):
            for x, num in enumerate(row):
                if num != 0:
                    pos = self.game.renderer.shell_positions[y][x]
                    is_valid = self.game.board.is_valid_move(x, y, num)
                    color = 'white' if is_valid else 'red'
                    self._draw_number(screen, num, pos, color)

    def _draw_number(self, screen: pg.Surface, num: int, pos: Tuple[int, int], color: str, big: bool = False) -> None:
        if 1 <= num <= 9:
            font_type = 'numbers_red' if color == 'red' else 'numbers'
            text = self.game.renderer.render_text(str(num), font_type, color, big)
            text_rect = text.get_rect(center=(pos[0] + 33, pos[1] + 33))
            screen.blit(text, text_rect)

    def _draw_gameplay_ui_elements(self, screen: pg.Surface) -> None:
        mouse_x, mouse_y = pg.mouse.get_pos()
        main_big = 20 < mouse_x < 200 and 15 < mouse_y < 55
        main_text = self.game.renderer.render_text("[main menu]", 'main_menu', 'white', main_big)
        if main_big:
            pg.draw.rect(screen, ColorManager.get_color('white'), ((20, 20), (180, 40)))
            screen.blit(main_text, (20, 15))
        else:
            screen.blit(main_text, (20, 15))

        space_text = self.game.renderer.render_text("Press [SPACE] to Autosolve", 'main_menu', 'grey')
        screen.blit(space_text, (110, 725))

    def _draw_solver_ui_elements(self, screen: pg.Surface) -> None:
        mouse_x, mouse_y = pg.mouse.get_pos()
        main_big = 20 < mouse_x < 200 and 15 < mouse_y < 55
        main_text = self.game.renderer.render_text("[main menu]", 'main_menu', 'white', main_big)
        if main_big:
            pg.draw.rect(screen, ColorManager.get_color('white'), ((20, 20), (180, 40)))
            screen.blit(main_text, (20, 15))
        else:
            screen.blit(main_text, (20, 15))

        space_text = self.game.renderer.render_text("Press [SPACE] to Autosolve", 'main_menu', 'grey')
        screen.blit(space_text, (110, 725))

    def _draw_gameplay_timer(self, screen: pg.Surface) -> None:
        gameplay_data = self.state_data['gameplay']
        elapsed = int(time.time() - gameplay_data['start_time'])
        minutes = elapsed // 60
        seconds = elapsed % 60
        time_text = f"{minutes}:{seconds:02d}"

        clock_text = self.game.renderer.render_text(time_text, 'clock', 'white')
        screen.blit(clock_text, (450, 30))


class SudokuGame:

    def __init__(self):
        pg.init()
        self.screen_width = 600
        self.screen_height = 800
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        pg.display.set_caption("~SUDOKU~")
        self.running = True

        self.color_manager = ColorManager()
        self.sound_manager = SoundManager()
        self.renderer = Renderer(self.screen_width, self.screen_height)
        self.board = SudokuBoard()

        self.state_manager = GameStateManager(self)

        self.sound_manager.play_background_music()

    def run(self) -> None:
        clock = pg.time.Clock()

        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                else:
                    self.state_manager.handle_events(event)

            self.state_manager.update()
            self.state_manager.render(self.screen)
            pg.display.update()
            clock.tick(60)

        pg.quit()


class TestColorManager(unittest.TestCase):

    def test_get_color_existing_colors(self):
        test_cases = [
            ('green', (40, 160, 30)),
            ('black', (20, 20, 20)),
            ('white', (240, 240, 240)),
            ('dimWhite', (150, 150, 150)),
            ('red', (170, 10, 10)),
            ('orange', (190, 80, 20)),
            ('grey', (80, 80, 80)),
            ('dimGrey', (40, 40, 40)),
            ('veryDimGrey', (30, 30, 30))
        ]

        for color_name, expected_rgb in test_cases:
            with self.subTest(color=color_name):
                result = ColorManager.get_color(color_name)
                self.assertEqual(result, expected_rgb)

    def test_get_color_nonexistent_color(self):
        test_cases = ['purple', 'yellow', 'cyan', '', 'invalid_color']

        for color_name in test_cases:
            with self.subTest(color=color_name):
                result = ColorManager.get_color(color_name)
                self.assertEqual(result, (0, 0, 0))

    def test_get_color_case_sensitivity(self):
        self.assertEqual(ColorManager.get_color('green'), (40, 160, 30))
        self.assertEqual(ColorManager.get_color('GREEN'), (0, 0, 0))
        self.assertEqual(ColorManager.get_color('Green'), (0, 0, 0))

    def test_color_map_immutability(self):
        original_map = copy.deepcopy(ColorManager.COLOR_MAP)

        ColorManager.get_color('green')
        ColorManager.get_color('nonexistent')
        ColorManager.get_color('red')

        self.assertEqual(ColorManager.COLOR_MAP, original_map)


class TestSoundManager(unittest.TestCase):

    def setUp(self):
        self.mixer_patcher = patch('pygame.mixer')
        self.mock_mixer = self.mixer_patcher.start()

        self.mock_mixer.music = MagicMock()
        self.mock_mixer.Sound.return_value = MagicMock()

        self.sound_manager = SoundManager()

    def tearDown(self):
        self.mixer_patcher.stop()

    def test_initialization_with_sound_files(self):
        self.mock_mixer.music.load.assert_called_once_with("backgroundMusic.ogg")

        expected_sound_calls = [
            ("click.ogg",), ("move.ogg",), ("congratulation.ogg",),
            ("gameStart.ogg",), ("gameOver.ogg",)
        ]

        self.assertEqual(self.mock_mixer.Sound.call_count, 5)

        expected_sound_names = ['click', 'move', 'congratulation', 'gameStart', 'gameOver']
        self.assertEqual(set(self.sound_manager.sounds.keys()), set(expected_sound_names))

    def test_initialization_without_sound_files(self):
        self.mock_mixer.music.load.side_effect = Exception("File not found")
        self.mock_mixer.Sound.side_effect = Exception("File not found")

        sound_manager = SoundManager()

        self.assertEqual(sound_manager.sounds, {})

    def test_play_background_music_success(self):
        self.sound_manager.play_background_music()

        self.mock_mixer.music.play.assert_called_once_with(-1)

    def test_play_background_music_failure(self):
        self.mock_mixer.music.play.side_effect = Exception("Playback error")

        self.sound_manager.play_background_music()

    def test_play_sound_existing(self):
        mock_sound = MagicMock()
        self.sound_manager.sounds['click'] = mock_sound

        self.sound_manager.play_sound('click')

        mock_sound.play.assert_called_once()

    def test_play_sound_nonexistent(self):
        self.sound_manager.play_sound('nonexistent_sound')

    def test_play_sound_playback_failure(self):
        mock_sound = MagicMock()
        mock_sound.play.side_effect = Exception("Playback error")
        self.sound_manager.sounds['click'] = mock_sound

        self.sound_manager.play_sound('click')

    def test_pause_and_unpause_background_music(self):
        self.sound_manager.pause_background_music()
        self.mock_mixer.music.pause.assert_called_once()

        self.sound_manager.unpause_background_music()
        self.mock_mixer.music.unpause.assert_called_once()

    def test_pause_unpause_with_errors(self):
        self.mock_mixer.music.pause.side_effect = Exception("Pause error")
        self.mock_mixer.music.unpause.side_effect = Exception("Unpause error")

        self.sound_manager.pause_background_music()
        self.sound_manager.unpause_background_music()


class TestRenderer(unittest.TestCase):

    def setUp(self):
        self.font_patcher = patch('pygame.font')
        self.draw_patcher = patch('pygame.draw')
        self.display_patcher = patch('pygame.display')

        self.mock_font = self.font_patcher.start()
        self.mock_draw = self.draw_patcher.start()
        self.mock_display = self.display_patcher.start()

        self.mock_font_instance = MagicMock()
        self.mock_font.SysFont.return_value = self.mock_font_instance
        self.mock_font.Font.return_value = self.mock_font_instance

        self.mock_surface = MagicMock()
        self.mock_font_instance.render.return_value = self.mock_surface

    def tearDown(self):
        self.font_patcher.stop()
        self.draw_patcher.stop()
        self.display_patcher.stop()

    def test_initialization(self):
        renderer = Renderer(600, 800)

        self.assertEqual(renderer.screen_width, 600)
        self.assertEqual(renderer.screen_height, 800)
        self.assertIsInstance(renderer.fonts, dict)
        self.assertIsInstance(renderer.text_cache, dict)
        self.assertIsInstance(renderer.shell_positions, list)
        self.assertIsInstance(renderer.shell_boundaries, list)

    def test_calculate_shell_positions(self):
        renderer = Renderer(600, 800)
        positions = renderer.shell_positions

        self.assertEqual(len(positions), 9)

        for row in positions:
            self.assertEqual(len(row), 9)

        self.assertEqual(positions[0][0], (2, 100))
        self.assertEqual(positions[0][1], (68, 100))

    def test_calculate_shell_boundaries(self):
        renderer = Renderer(600, 800)
        boundaries = renderer.shell_boundaries

        self.assertEqual(len(boundaries), 9)

        for row in boundaries:
            self.assertEqual(len(row), 9)

        first_boundary = boundaries[0][0]
        self.assertEqual(len(first_boundary), 4)
        self.assertEqual(first_boundary, (2, 68, 100, 166))

    def test_get_shell_at_position_valid(self):
        renderer = Renderer(600, 800)

        mock_board = MagicMock()
        mock_board.sudoku_board = [[0] * 9 for _ in range(9)]

        result = renderer.get_shell_at_position(10, 110, mock_board)
        self.assertEqual(result, renderer.shell_positions[0][0])

    def test_get_shell_at_position_non_empty_cell(self):
        renderer = Renderer(600, 800)

        mock_board = MagicMock()
        mock_board.sudoku_board = [[5] + [0]*8] + [[0]*9 for _ in range(8)]

        result = renderer.get_shell_at_position(10, 110, mock_board)
        self.assertIsNone(result)

    def test_get_shell_at_position_out_of_bounds(self):
        renderer = Renderer(600, 800)

        mock_board = MagicMock()
        mock_board.sudoku_board = [[0] * 9 for _ in range(9)]

        self.assertIsNone(renderer.get_shell_at_position(-10, -10, mock_board))
        self.assertIsNone(renderer.get_shell_at_position(1000, 1000, mock_board))
        self.assertIsNone(renderer.get_shell_at_position(10, 10, mock_board))

    def test_render_text_caching(self):
        renderer = Renderer(600, 800)

        result1 = renderer.render_text("Test", 'main_menu', 'white')
        self.assertIn("Test_main_menu_white_False", renderer.text_cache)

        result2 = renderer.render_text("Test", 'main_menu', 'white')
        self.assertEqual(result1, result2)

    def test_render_text_big_font(self):
        renderer = Renderer(600, 800)

        renderer.render_text("Test", 'main_menu', 'white', big=True)

        self.mock_font.Font.assert_called()

    def test_render_text_invalid_font_type(self):
        renderer = Renderer(600, 800)

        result = renderer.render_text("Test", 'invalid_font', 'white')
        self.assertIsNotNone(result)


class TestSudokuBoard(unittest.TestCase):

    def setUp(self):
        self.board = SudokuBoard()

    def test_initial_state(self):
        for row in self.board.sudoku_board:
            self.assertEqual(row, [0]*9)
        for row in self.board.user_board:
            self.assertEqual(row, [0]*9)
        for row in self.board.current_board:
            self.assertEqual(row, [0]*9)

    def test_reset_functionality(self):
        self.board.sudoku_board[0][0] = 5
        self.board.user_board[0][0] = 3
        self.board.current_board[0][0] = 8

        self.board.reset()

        for y in range(9):
            for x in range(9):
                self.assertEqual(self.board.sudoku_board[y][x], 0)
                self.assertEqual(self.board.user_board[y][x], 0)
                self.assertEqual(self.board.current_board[y][x], 0)

    def test_set_user_number_valid(self):
        test_cases = [
            (0, 0, 1),
            (8, 8, 9),
            (4, 4, 5),
            (0, 8, 2),
            (8, 0, 3),
        ]

        for x, y, num in test_cases:
            with self.subTest(x=x, y=y, num=num):
                self.board.set_user_number(x, y, num)
                self.assertEqual(self.board.user_board[y][x], num)
                self.assertEqual(self.board.current_board[y][x], num)

    def test_set_user_number_invalid_positions(self):
        invalid_positions = [
            (-1, 0, 1),
            (0, -1, 1),
            (9, 0, 1),
            (0, 9, 1),
            (10, 10, 1),
        ]

        for x, y, num in invalid_positions:
            with self.subTest(x=x, y=y, num=num):
                original_user_board = copy.deepcopy(self.board.user_board)
                original_current_board = copy.deepcopy(self.board.current_board)

                self.board.set_user_number(x, y, num)

                self.assertEqual(self.board.user_board, original_user_board)
                self.assertEqual(self.board.current_board, original_current_board)

    def test_set_user_number_invalid_numbers(self):
        invalid_numbers = [-1, 10, 15, 100, -5]

        for num in invalid_numbers:
            with self.subTest(num=num):
                original_user_board = copy.deepcopy(self.board.user_board)

                self.board.set_user_number(0, 0, num)

                self.assertEqual(self.board.user_board, original_user_board)

    def test_update_current_board(self):
        self.board.sudoku_board[0][0] = 5
        self.board.sudoku_board[1][1] = 3

        self.board.user_board[0][1] = 2
        self.board.user_board[1][0] = 7

        self.board.update_current_board()

        self.assertEqual(self.board.current_board[0][0], 5)
        self.assertEqual(self.board.current_board[0][1], 2)
        self.assertEqual(self.board.current_board[1][0], 7)
        self.assertEqual(self.board.current_board[1][1], 3)

    def test_get_cell_value_valid(self):
        self.board.current_board[0][0] = 5
        self.board.current_board[4][4] = 3
        self.board.current_board[8][8] = 9

        self.assertEqual(self.board.get_cell_value(0, 0), 5)
        self.assertEqual(self.board.get_cell_value(4, 4), 3)
        self.assertEqual(self.board.get_cell_value(8, 8), 9)

    def test_get_cell_value_invalid_positions(self):
        invalid_positions = [(-1, 0), (0, -1), (9, 0), (0, 9), (10, 10)]

        for x, y in invalid_positions:
            with self.subTest(x=x, y=y):
                result = self.board.get_cell_value(x, y)
                self.assertEqual(result, 0)

    @patch('__main__.giveBoard')
    def test_load_board(self, mock_giveBoard):
        test_board = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]
        mock_giveBoard.return_value = test_board

        self.board.load_board('easy')

        self.assertEqual(self.board.sudoku_board, test_board)
        for row in self.board.user_board:
            self.assertEqual(row, [0]*9)
        self.assertEqual(self.board.current_board, test_board)

    def test_is_full_empty_board(self):
        self.assertFalse(self.board.is_full())

    def test_is_full_partial_board(self):
        self.board.current_board[0][0] = 5
        self.assertFalse(self.board.is_full())

    @patch('__main__.isFull')
    def test_is_full_delegation(self, mock_isFull):
        mock_isFull.return_value = True

        result = self.board.is_full()

        mock_isFull.assert_called_once_with(self.board.current_board)
        self.assertTrue(result)

    @patch('__main__.possible')
    def test_is_valid_move_delegation(self, mock_possible):
        mock_possible.return_value = True

        result = self.board.is_valid_move(0, 0, 5)

        mock_possible.assert_called_once_with(self.board.current_board, 0, 0, 5)
        self.assertTrue(result)


class TestGameStateManager(unittest.TestCase):

    def setUp(self):
        self.mock_game = MagicMock()
        self.mock_game.sound_manager = MagicMock()
        self.mock_game.board = MagicMock()
        self.mock_game.renderer = MagicMock()
        self.mock_game.screen = MagicMock()
        self.mock_game.running = True

        self.mock_shell_positions = [[(x*66+2, y*66+100) for x in range(9)] for y in range(9)]
        self.mock_game.renderer.shell_positions = self.mock_shell_positions

        self.state_manager = GameStateManager(self.mock_game)

    def test_initial_state(self):
        self.assertEqual(self.state_manager.current_state, 'intro')
        self.assertIn('intro', self.state_manager.state_data)
        self.assertIn('gameplay', self.state_manager.state_data)
        self.assertIn('solver', self.state_manager.state_data)

    def test_change_state(self):
        self.state_manager.change_state('main_menu')
        self.assertEqual(self.state_manager.current_state, 'main_menu')

        self.state_manager.change_state('gameplay', 'main_menu')
        self.assertEqual(self.state_manager.current_state, 'gameplay')
        self.assertEqual(self.state_manager.state_data['background_state'], 'main_menu')

    @patch('pygame.display.update')
    @patch('pygame.mouse.get_pos', return_value=(300, 330))
    def test_handle_intro_events_enter_key(self, mock_get_pos, mock_display_update):
        mock_event = MagicMock()
        mock_event.type = pg.KEYUP
        mock_event.key = pg.K_RETURN

        self.state_manager.handle_events(mock_event)

        self.mock_game.sound_manager.play_sound.assert_called_with('click')
        self.mock_game.screen.fill.assert_called()
        mock_display_update.assert_called()
        self.assertEqual(self.state_manager.current_state, 'main_menu')

    @patch('pygame.mouse.get_pos')
    def test_handle_main_menu_events_play_button(self, mock_get_pos):
        mock_get_pos.return_value = (200, 330)
        mock_event = MagicMock()
        mock_event.type = pg.MOUSEBUTTONUP

        self.state_manager.current_state = 'main_menu'
        self.state_manager.handle_events(mock_event)

        self.mock_game.sound_manager.play_sound.assert_called_with('click')
        self.assertEqual(self.state_manager.current_state, 'play_menu')

    @patch('pygame.mouse.get_pos')
    def test_handle_main_menu_events_exit_button(self, mock_get_pos):
        mock_get_pos.return_value = (200, 630)
        mock_event = MagicMock()
        mock_event.type = pg.MOUSEBUTTONUP

        self.state_manager.current_state = 'main_menu'
        self.state_manager.handle_events(mock_event)

        self.assertFalse(self.mock_game.running)

    def test_start_game_functionality(self):
        with patch.object(self.state_manager, 'change_state') as mock_change_state:
            self.state_manager._start_game('easy')

            self.mock_game.sound_manager.play_sound.assert_any_call('click')
            self.mock_game.sound_manager.pause_background_music.assert_called()
            self.mock_game.sound_manager.play_sound.assert_any_call('gameStart')
            self.mock_game.board.load_board.assert_called_with('easy')
            mock_change_state.assert_called_with('gameplay')

    def test_insert_number_gameplay(self):
        self.state_manager.state_data['gameplay']['selected_shell'] = (2, 100)

        with patch.object(self.mock_game.board, 'set_user_number') as mock_set_number:
            self.state_manager._insert_number_gameplay(5)

            mock_set_number.assert_called_once()

    def test_check_board_valid(self):
        self.mock_game.board.current_board = [[0]*9 for _ in range(9)]
        self.mock_game.board.is_valid_move.return_value = True

        result = self.state_manager._check_board_valid()

        self.assertTrue(result)

    def test_check_board_invalid(self):
        self.mock_game.board.current_board = [[5] + [0]*8] + [[0]*9 for _ in range(8)]
        self.mock_game.board.is_valid_move.return_value = False

        result = self.state_manager._check_board_valid()

        self.assertFalse(result)

    def test_gameplay_update_timer_reset(self):
        self.state_manager.current_state = 'gameplay'
        self.state_manager.state_data['gameplay']['reset_time'] = True

        with patch('time.time', return_value=1000):
            self.state_manager.update()

            self.assertEqual(self.state_manager.state_data['gameplay']['start_time'], 1000)
            self.assertFalse(self.state_manager.state_data['gameplay']['reset_time'])

    def test_gameplay_update_congratulations(self):
        self.state_manager.current_state = 'gameplay'
        self.state_manager.state_data['gameplay']['congrates_played'] = False
        self.mock_game.board.is_full.return_value = True

        self.state_manager.update()

        self.mock_game.sound_manager.play_sound.assert_called_with('congratulation')
        self.assertTrue(self.state_manager.state_data['gameplay']['congrates_played'])


class TestSudokuGame(unittest.TestCase):

    def setUp(self):
        self.pg_init_patcher = patch('pygame.init')
        self.pg_display_patcher = patch('pygame.display')
        self.pg_time_patcher = patch('pygame.time')

        self.mock_pg_init = self.pg_init_patcher.start()
        self.mock_pg_display = self.pg_display_patcher.start()
        self.mock_pg_time = self.pg_time_patcher.start()

        self.mock_pg_display.set_mode.return_value = MagicMock()
        self.mock_pg_display.set_caption = MagicMock()
        self.mock_clock = MagicMock()
        self.mock_pg_time.Clock.return_value = self.mock_clock

    def tearDown(self):
        self.pg_init_patcher.stop()
        self.pg_display_patcher.stop()
        self.pg_time_patcher.stop()

    def test_initialization(self):
        with patch.object(SoundManager, 'play_background_music') as mock_play_music:
            game = SudokuGame()

            self.mock_pg_init.assert_called_once()
            self.mock_pg_display.set_mode.assert_called_with((600, 800))
            self.mock_pg_display.set_caption.assert_called_with("~SUDOKU~")

            self.assertIsInstance(game.color_manager, ColorManager)
            self.assertIsInstance(game.sound_manager, SoundManager)
            self.assertIsInstance(game.renderer, Renderer)
            self.assertIsInstance(game.board, SudokuBoard)
            self.assertIsInstance(game.state_manager, GameStateManager)

            self.assertTrue(game.running)
            mock_play_music.assert_called_once()

    def test_run_loop_quit_event(self):
        game = SudokuGame()

        mock_events = [MagicMock(type=pg.QUIT)]
        with patch('pygame.event.get', return_value=mock_events):
            with patch.object(game.state_manager, 'update') as mock_update:
                with patch.object(game.state_manager, 'render') as mock_render:
                    game.running = True
                    game.run()

                    self.assertFalse(game.running)

    def test_run_loop_normal_events(self):
        game = SudokuGame()

        mock_events = [
            MagicMock(type=pg.KEYDOWN, key=pg.K_a),
            MagicMock(type=pg.MOUSEBUTTONDOWN, pos=(100, 100))
        ]

        with patch('pygame.event.get', side_effect=[mock_events, [MagicMock(type=pg.QUIT)]]):
            with patch.object(game.state_manager, 'handle_events') as mock_handle:
                with patch.object(game.state_manager, 'update') as mock_update:
                    with patch.object(game.state_manager, 'render') as mock_render:
                        game.running = True
                        game.run()

                        mock_handle.assert_called()
                        mock_update.assert_called()
                        mock_render.assert_called()
                        self.mock_pg_display.update.assert_called()
                        self.mock_clock.tick.assert_called_with(60)


class TestEdgeCases(unittest.TestCase):

    def test_color_manager_with_none_input(self):
        result = ColorManager.get_color(None)
        self.assertEqual(result, (0, 0, 0))

    def test_sound_manager_empty_initialization(self):
        with patch('pygame.mixer.music.load', side_effect=Exception):
            with patch('pygame.mixer.Sound', side_effect=Exception):
                sound_manager = SoundManager()
                self.assertEqual(sound_manager.sounds, {})

    def test_renderer_with_zero_dimensions(self):
        renderer = Renderer(0, 0)
        self.assertEqual(renderer.screen_width, 0)
        self.assertEqual(renderer.screen_height, 0)

    def test_sudoku_board_boundary_conditions(self):
        board = SudokuBoard()

        board.set_user_number(0, 0, 1)
        board.set_user_number(8, 8, 9)

        self.assertEqual(board.user_board[0][0], 1)
        self.assertEqual(board.user_board[8][8], 9)

    def test_game_state_manager_unknown_state(self):
        manager = GameStateManager(MagicMock())
        manager.current_state = 'unknown_state'

        mock_event = MagicMock()
        manager.handle_events(mock_event)

        manager.render(MagicMock())


def run_comprehensive_tests():
    print("=" * 70)
    print("RUNNING COMPREHENSIVE SUDOKU GAME TESTS")
    print("=" * 70)

    test_cases = [
        TestColorManager,
        TestSoundManager,
        TestRenderer,
        TestSudokuBoard,
        TestGameStateManager,
        TestSudokuGame,
        TestEdgeCases,
    ]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for test_case in test_cases:
        suite.addTests(loader.loadTestsFromTestCase(test_case))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED! The game is ready to run.")
        print("=" * 70)
        return True
    else:
        print("\n✗ SOME TESTS FAILED! Please check the test output above.")
        print("=" * 70)
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        tests_passed = run_comprehensive_tests()
        if not tests_passed:
            sys.exit(1)
    elif len(sys.argv) > 1 and sys.argv[1] == "--quick-test":
        print("Running quick tests...")
        unittest.main(verbosity=1, exit=False)
    else:
        print("Running Sudoku Game...")
        print("Available commands:")
        print("  --test        Run comprehensive test suite")
        print("  --quick-test  Run basic tests")
        print("  (no args)     Run game directly")

    if len(sys.argv) <= 1 or sys.argv[1] not in ["--test", "--quick-test"]:
        game = SudokuGame()
        game.run()