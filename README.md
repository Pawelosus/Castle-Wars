# Castle Wars (fan project)

This project is a fan-made adaptation of the original game Castle Wars, created by m0rkeulv. It's main use is for testing different AI agents.
It has been rewritten from scratch in Python, using PyQt6 for GUI.

## Overview

Castle Wars is a strategy game where players build castles and compete against each other. This fan project aims to recreate the core gameplay mechanics of the original game and add extra functionalities on top of it, featuring AI that learns over time. **This project is still under development**.


<p align="center">
  <img width="600" alt="Castle Wars gameplay preview" src="https://github.com/user-attachments/assets/773fd8e8-8ea5-4551-a1c9-ad5b182869dd" />
</p>

## Features

- **Gameplay Mechanics** Core gameplay mechanics of the game have been recreated.
- **Custom Card Decks** Players can customize their card decks and store them in files for later use.
- **AI Opponents** Multiple AI opponents are available, including rule-based, MCTS, and neural network agents.
- **Game Logging** Every game is automatically logged to the `logs/` directory for review and AI training purposes


## Usage
> Requires Python 3.9 or above

1. Clone the repository:

`git clone https://github.com/Pawelosus/Castle-Wars.git`

2. Navigate to the project directory:

`cd Castle-Wars`

3. Install dependencies:

`pip install -r requirements.txt`

4. Run the game:

`python main.py`

## Contributing

Contributions are welcome! If you'd like to contribute to the project, please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature-name`
3. Make your changes and commit them: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## Acknowledgements

- Original game: [Castle Wars by m0rkeulv](https://cdn.m0rkeulv.net/games/html5/cwo/normal.html)
