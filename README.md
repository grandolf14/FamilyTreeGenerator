# FamilyTreeGenerator

This is a PyQt5-based desktop application for managing and visualizing family trees using a SQLite database backend. The application allows you to display, edit, and dynamically manipulate members of a family tree through a graphical interface.

## Features

- **Session Data Access**: Create new characters, generate current wheather and surrounding and access the prepared character- evnet or sessiondata.
- **NPC Management**: Create, edit and randomize characters with dynamic name and family generation.
- **Event & Session Tracking**: Keep your game world organized by linking NPCs to events and sessions.
- **Dynamic Weather System**: Season-aware weather changes with probabilistic logic.
- **In-Game Custom Calendar**: Manage time progression with the DSA-specific calendar system.
- **Draftboard Mode**: Visually connect events, notes, and characters in an interactive editor.
- **Full-Text Search**: Easily locate data using smart filters and full-text matching.
- **Auto Save/Load**: Persists session data automatically between uses.

## Installation

1. **Install Requirements**:
   Make sure Python 3, SQLite3 and PyQt5 are installed.

   ```bash
   pip install PyQt5
   ```

2. **Download/Clone the Repository**:
   ```bash
   git clone https://github.com/grandolf14/FamilyTreeGenerator
   ```

3. **Run the Application**:
   ```bash
   python main.py
   ```
## Usage
- Search for a specific family in the searchbar (try "Dinkelkorn" as example) to display thair current family tree.
- select one person either in the unassigned area or the assigned dropdown menu.
- select a person to be their closest relative in bottomn dropdown menu.
- specify the relative generation (i.e. -1 for the parents generation) and their relationship (i.e. 1 for siblings, 2 for cousins, 3 for second cousins ...).
- press calculate to initialize generation.

## Project Structure

```
- main.py: Main application logic and GUI components.
- Executable.py: Database helper functions.
- DSA Daten.db: Required SQLite database with individuals and families .
- Graphic_Library/: Directory containing graphical assets like banners or backgrounds.
```


## Author

Created by Fiete Jantsch

## License

Apache License
