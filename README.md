# Starry Night

**Starry Night** is a turn-based combat game built using Pygame and Tkinter. Players choose a character, use strategy to attack or defend, and utilize abilities and items in an engaging animated battle system.

## Features

- Turn-based battle system with strategic choices
- Multiple characters (Meepo, Visor, Dunky) with unique abilities and sprites
- Animated sprite attacks and visual effects
- GUI-based main menu using Tkinter
- Data collection: total damage, healing, parries, etc.
- Sound effects for actions and animations
- Visualization of player performance and statistics

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Watcharapat-P/compro2_final_project_Starry_Night
   cd compro2_final_project_Starry_Night

2. **Install dependencies**:
   ```bash
   ## Make sure you have Python 3.8+ installed. Then run:
   pip install -r requirements.txt
   
3. **Run the game**:
   ```bash
   ## Launch the main menu using:
   python main_menu.py

## Controls
- Use buttons on the screen to choose actions (Attack, Ability, Item, Defend).

- Turns alternate between the player and enemy.

- Hover and click with your mouse.

- To parry press your M1(left-click) or M2(right-click) during the right moment to parry the attack

## Folder Structure
- combat_turn_based.py - Main Pygame battle loop

- main_menu.py - Tkinter GUI to launch the game

- attribute.py - Character stats and ability logic

- screenshots/ - Contains gameplay/ and visualization/ subfolders

- sfx/ - Contains the sound effect that being used in the game 

- combat_log.csv - Contains the data gathered from the game

- LICENSE - Project license

- DESCRIPTION.md - Detailed description with UML and concept

- proposal.pdf - Original project proposal *(I decided to deviate from the proposal a bit)*

## YouTube Video
5-minute presentation: https://youtu.be/YOUR_VIDEO_LINK