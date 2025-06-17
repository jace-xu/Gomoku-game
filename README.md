<<<<<<< HEAD
6.9
完成1.0版本，ai很弱智
=======
# 🎯 Gomoku Game - AI-Powered Five-in-a-Row

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)
![License](https://img.shields.io/badge/License-GPL--3.0-red.svg)

*An intelligent Gomoku game featuring AI opponents and real-time commentary*

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Screenshots](#screenshots) • [Contributing](#contributing)

</div>

---

## 🌟 Features

### 🎮 **Core Gameplay**
- **Classic Gomoku Rules**: Traditional 15×15 board with five-in-a-row victory condition
- **Intelligent AI Opponent**: Advanced algorithm with strategic thinking
- **Interactive UI**: Clean and intuitive graphical interface
- **Move History**: Complete game replay and analysis

### 🤖 **AI-Powered Commentary**
- **Real-time Analysis**: AI-generated commentary using OpenAI GPT
- **Strategic Insights**: Detailed explanation of moves and tactics
- **Multilingual Support**: Commentary available in multiple languages

### 📊 **Game Management**
- **Match History**: Complete record of all games played
- **Detailed Statistics**: Win/loss ratios and performance tracking
- **Game Snapshots**: Visual board state preservation
- **Export Functionality**: Save and share game records

### 🎨 **User Experience**
- **Smooth Animations**: Fluid piece placement and transitions
- **Audio Feedback**: Sound effects for enhanced immersion
- **Responsive Controls**: Mouse and keyboard input support
- **Customizable Settings**: Adjustable difficulty and display options

---

## 🚀 Installation

### Prerequisites
- **Python 3.8+** installed on your system
- **pip** package manager

### Quick Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/Gomoku-game.git
   cd Gomoku-game
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenAI API** (Optional for AI commentary)
   ```bash
   # Create a .env file in the project root
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

4. **Run the Game**
   ```bash
   python main.py
   ```

### Alternative Installation Methods

<details>
<summary>Using Virtual Environment (Recommended)</summary>

```bash
# Create virtual environment
python -m venv gomoku_env

# Activate virtual environment
# On Windows:
gomoku_env\Scripts\activate
# On macOS/Linux:
source gomoku_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

</details>

<details>
<summary>Using Conda</summary>

```bash
# Create conda environment
conda create -n gomoku python=3.8
conda activate gomoku

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

</details>

---

## 🎯 Usage

### Basic Gameplay

1. **Start a New Game**
   - Launch the application with `python main.py`
   - Click "Start Game" from the main menu
   - Black pieces move first (human player)

2. **Making Moves**
   - Click on any intersection to place your piece
   - The AI will automatically respond
   - First to get five in a row wins!

3. **Game Controls**
   - **Undo**: Take back your last move
   - **Settings**: Adjust game preferences
   - **History**: View past games

### Advanced Features

#### 📈 **Viewing Game History**
Access historical games through: Menu → History → Select Game → View Details

#### 🤖 **AI Commentary System**
The game features an intelligent commentary system that provides:
- **Move Analysis**: Evaluation of strategic decisions
- **Pattern Recognition**: Identification of tactical formations
- **Game Flow Commentary**: Real-time narrative of the match

#### 🔧 **Customization Options**
- **Board Size**: Adjustable grid dimensions
- **AI Difficulty**: Multiple skill levels
- **Visual Themes**: Different board and piece styles
- **Audio Settings**: Sound effects and background music

---

## 📁 Project Structure

```
Gomoku-game/
├── assets/                 # Game assets and resources
│   ├── board_bgm.mp3      # Background music
│   ├── loadbackground.jpg  # Menu background
│   └── piece_sound.mp3    # Sound effects
├── game_database/          # Game data storage
│   ├── history.json       # Match history
│   └── results.json       # Game results
├── logic/                  # Core game logic
│   ├── board_state.py     # Board management
│   ├── comment.py         # AI commentary
│   └── move_logic.py      # AI decision making
├── ui/                     # User interface
│   ├── board_ui.py        # Game board display
│   ├── menu_ui.py         # Menu systems
│   └── past_ui.py         # History viewer
├── main.py                # Application entry point
├── requirements.txt       # Dependencies
├── .gitignore            # Git ignore rules
├── LICENSE               # License information
└── README.md             # This file
```

---

## ⚙️ Configuration

### OpenAI API Setup
To enable AI commentary features:

1. **Get OpenAI API Key**
   - Visit [OpenAI Platform](https://platform.openai.com/)
   - Create an account and generate an API key

2. **Configure Environment**
   ```bash
   # Method 1: Environment variable
   export OPENAI_API_KEY="your-api-key"
   
   # Method 2: .env file
   echo "OPENAI_API_KEY=your-api-key" > .env
   ```

### Game Settings
Customize your experience by modifying `config.json`:

```json
{
    "board_size": 15,
    "ai_difficulty": "medium",
    "enable_sound": true,
    "enable_commentary": true,
    "language": "en"
}
```

---

## 🧠 AI Algorithm

The game features a sophisticated AI opponent with:

### **Strategic Evaluation**
- **Position Scoring**: Advanced heuristic evaluation
- **Pattern Recognition**: Detection of winning formations
- **Threat Assessment**: Defensive and offensive prioritization

### **Search Algorithm**
- **Minimax with Alpha-Beta Pruning**: Efficient game tree exploration
- **Iterative Deepening**: Dynamic search depth adjustment
- **Transposition Tables**: Position caching for performance

### **Learning Capabilities**
- **Opening Book**: Pre-computed optimal opening moves
- **Endgame Database**: Perfect play in simplified positions
- **Adaptive Difficulty**: Dynamic skill adjustment

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### **How to Contribute**

1. **Fork the Repository**
   ```bash
   git fork https://github.com/your-username/Gomoku-game.git
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Your Changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed

4. **Commit Your Changes**
   ```bash
   git commit -m "Add amazing feature"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/amazing-feature
   ```

### **Development Guidelines**

- **Code Style**: Follow PEP 8 conventions
- **Testing**: Ensure all tests pass
- **Documentation**: Update docstrings and comments
- **Performance**: Consider computational efficiency

### **Areas for Contribution**
- 🎨 UI/UX improvements
- 🤖 AI algorithm enhancements
- 🌍 Internationalization
- 🐛 Bug fixes and optimizations
- 📚 Documentation improvements

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

### **License Summary**
- ✅ **Use**: Free for personal and commercial use
- ✅ **Modify**: Can be modified and distributed
- ✅ **Distribute**: Can be freely shared
- ⚠️ **Copyleft**: Derivative works must also be GPL-licensed
- ⚠️ **No Warranty**: Software provided "as-is"

---

## 🙏 Acknowledgments

### **Technology Stack**
- **[Pygame](https://www.pygame.org/)**: Game development framework
- **[OpenAI](https://openai.com/)**: AI commentary generation
- **[Python](https://python.org/)**: Core programming language

### **Special Thanks**
- The open-source community for continuous inspiration
- Beta testers for valuable feedback and bug reports
- Contributors who helped improve the codebase

### **Inspiration**
This project draws inspiration from:
- Traditional Gomoku/Five-in-a-Row games
- Modern AI chess engines
- Educational programming resources

---

## 📞 Support & Contact

### **Getting Help**
- 📖 Check the Documentation
- 🐛 Report bugs via Issues
- 💬 Join discussions

### **Maintainers**
- **Primary Developer**: [@your-username](https://github.com/your-username)

---

<div align="center">

**⭐ Star this repository if you found it helpful!**

*Made with ❤️ for the gaming and AI community*

</div>
>>>>>>> develop
