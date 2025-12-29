# 🐧 Hey, That's My Fish!

A digital implementation of the classic strategy board game, built with Python and the [Arcade](https://api.arcade.academy/en/latest/) library.

## 🎮 Game Overview

In this game, you compete against an AI opponent to catch the most fish! Navigate your penguins across a shrinking ice floe composed of hexagonal tiles. Each tile has 1, 2, or 3 fish. When a penguin leaves a tile, that tile (and its fish) is removed from the board.

## ✨ Features

- **Hexagonal Grid System**: Authentic movement and board layout.
- **Smart AI Opponent**: Challenge yourself against a computer player.
- **Dynamic Gameplay**: The board changes with every move as tiles disappear.
- **Sound Effects & Music**: Immersive audio experience.
- **Score Tracking**: Real-time score updates.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- `pip` package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mayur-k-s/fish_game.git
   cd fish_game
   ```

2. **Install dependencies:**
   ```bash
   pip install arcade
   ```

### Running the Game

Execute the main script to start playing:

```bash
python hey_thatsmyfish.py
```

## 🕹️ How to Play

### Phase 1: Placement
- You have **3 penguins** to place.
- Click on any tile with **1 fish** to place your penguin.
- You and the AI will take turns placing penguins.

### Phase 2: Fishing
- Click on one of your penguins to select it (Yellow highlight).
- Valid moves will be highlighted in **Green**.
- Click a valid target tile to move.
- You collect the fish from the tile you started on!
- **Movement Rules**: Penguins move in a straight line until they hit an obstacle (another penguin or a hole). You cannot jump over other penguins or gaps.

## 🏆 Winning condition
The game ends when neither player can move. The player with the highest total fish count wins!

---
*Created by [Mayur-k-s](https://github.com/Mayur-k-s)*