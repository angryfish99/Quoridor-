# Quoridor - AI Agent Remake

A Python implementation of the strategy board game **Quoridor**, featuring a graphical user interface and a challenging AI opponent.

## 🎮 Features

*   **Single Player vs AI**: Play against an intelligent AI agent powered by Minimax with Alpha-Beta pruning and A* pathfinding.
*   **Interactive GUI**: Built with Pygame for a smooth and responsive experience.
*   **Game Menu**: Start new games, load existing ones, or quit easily.
*   **Save/Load System**: Save your progress and resume later (uses text-based algebraic notation).
*   **Visuals**: Clean interface with clear move indicators and wall placement.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/angryfish99/Quoridor-.git
    cd Quoridor-
    ```

2.  **Set up a virtual environment (Recommended):**
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 How to Run

Execute the main script to start the game:

```bash
python main.py
```

## 🕹️ Controls

*   **Mouse**: Click to move pawns or place walls.
*   **Wall Placement**:
    *   Click between squares to place a wall.
    *   Walls can be placed horizontally or vertically (functionality depends on specific UI implementation, usually right-click or a toggle key to rotate).
*   **Menus**: Use the mouse to interact with menu buttons.

## 🧠 AI Details

The AI opponent uses the Minimax algorithm with Alpha-Beta pruning to decide its moves. It evaluates board states based on path lengths (calculated via A*) to the goal for both itself and the player, aiming to minimize its own distance while maximizing the opponent's.

## 📂 Project Structure

*   `main.py`: Entry point of the application.
*   `src/`: Contains the source code.
    *   `ai.py`: AI logic and decision making.
    *   `game.py` / `models.py`: Core game logic and state management.
    *   `ui.py`: User interface and rendering.
    *   `pathfinding.py`: Pathfinding algorithms.
*   `assets/`: Game assets (images, fonts, etc.).

## 📝 License

This project is open-source.
