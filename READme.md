"" 
# Sudoku

A Sudoku game I made in Python with Pygame. Has a menu, difficulty selection,
animated grid drawing, timer, sound, and an auto-solver if you get stuck.

I built this mostly to practice OOP, so the code is split into a few classes
(GameStateManager, Renderer, SudokuBoard, etc.) rather than being one giant
script. There are also quite a lot of unit tests because I kept breaking
things while refactoring.

## What's in it

- Four difficulties: easy, medium, hard, very hard
- Grid is drawn line by line with a small animation on startup and when you
  enter a game
- Numbers you type in are validated — invalid ones show up in red
- Timer in the top right while you're playing
- Hover and click highlights on cells
- Press SPACE to auto-solve (it asks whether you want the solution instantly
  or animated)
- Background music and a few sound effects, but the game works fine without
  them (it just stays silent)
- Same goes for fonts — if the .ttf files aren't there, it falls back to
  whatever pygame picks by default

## Running it

You need Python 3.9+ and pygame.

```
pip install pygame
python sudoku.py
```

Two optional command line flags:

```
python sudoku.py --test         # full test suite, verbose
python sudoku.py --quick-test   # just run unittest with less output
```

## Assets

The game looks for these files in the same folder:

Fonts:
- `SEASRN__.ttf`
- `RobotoSlab-Bold.ttf`
- `TypeWrongSmudgedBold.ttf`

Sounds:
- `backgroundMusic.ogg`
- `click.ogg`
- `move.ogg`
- `congratulation.ogg`
- `gameStart.ogg`
- `gameOver.ogg`

If they're missing it still runs — just with system fonts and no audio. I
didn't include the actual files here because I'm not sure about their licenses.

It also expects `solver.py` and `boards.py` next to `sudoku.py`:

- `solver.py` should export `isFull(board)`, `possible(board, x, y, n)` and
  `autosolve(board)`
- `boards.py` should export `giveBoard(difficulty)` returning a 9x9 list

If those aren't importable the game falls back to an empty board so you can
still try the UI.

## Controls

- ENTER on the intro screen to get to the menu
- Click an empty cell to select it
- Type 1–9 to place a number
- SPACE to bring up the auto-solve dialog
- There's a `[main menu]` button in the top left during a game

## How it's laid out

The main classes are:

- `SudokuGame` — owns the pygame loop and the other managers
- `GameStateManager` — a state machine for the menus, gameplay, and popups.
  Handles events and rendering per state.
- `Renderer` — draws the grid, animates it, renders text (with a small cache
  so it doesn't re-render the same string every frame)
- `SudokuBoard` — holds the original puzzle, the player's entries, and the
  combined board. Also does move validation.
- `ColorManager` — just a dict of colors and a `get_color` lookup
- `SoundManager` — loads sounds and wraps the pygame calls in try/except so a
  broken mixer doesn't kill the game

States are: `intro`, `main_menu`, `play_menu`, `game_board`, `gameplay`,
`solver`, `confirm_popup`, `autosolve_popup`.

## Tests

There are 54 tests across 7 test classes. They're all in `sudoku.py` at the
bottom (I know, not ideal — probably should be in a separate file at some
point). They cover:

- ColorManager lookups and defaults
- SoundManager with mocked pygame mixer (including the case where files are
  missing)
- Renderer geometry and text caching
- SudokuBoard state and validation
- GameStateManager transitions and event handling
- The main game loop
- A few edge cases (None input, zero-sized screen, etc.)

Run them with:

```
python sudoku.py --test
```

## Things I might add later

- A proper highscore or save/load
- Animation for the auto-solver (right now both "solution" and "animation"
  do the same thing — solve immediately)
- Pull the tests out into `tests/`

## License

MIT.
