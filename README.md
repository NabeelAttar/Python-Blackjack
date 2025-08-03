# 🎰 Blackjack Game 🎰

A comprehensive Blackjack game implementation featuring both command-line and web interfaces, complete with betting system, statistics tracking, and leaderboard functionality.

## 🌟 Features

### Core Game Features
- **Complete Blackjack Rules**: Standard casino blackjack with proper card values and dealer AI
- **Betting System**: Place bets with customizable amounts ($10-$500)
- **Money Management**: Track balance, winnings, and highest achieved balance
- **Ace Handling**: Smart ace value calculation (11 or 1 based on hand total)
- **Blackjack Detection**: Automatic blackjack detection with 1.5x payout

### Statistics & Tracking
- **Game Statistics**: Track games played, won, lost, and win rate
- **Blackjack Counter**: Count total blackjacks achieved
- **Performance Metrics**: Monitor highest balance and total winnings
- **Session Persistence**: Maintain game state across sessions

### Leaderboard System
- **Top 10 Players**: Automatic ranking by final balance
- **Comprehensive Stats**: Display win rates, games played, and blackjacks
- **Persistent Storage**: JSON-based leaderboard that persists between sessions
- **Date Tracking**: Record when scores were achieved

### User Interfaces
- **Command-Line Interface**: Full-featured terminal-based game
- **Web Interface**: Modern, responsive Flask web application
- **Mobile Responsive**: Optimized for desktop and mobile devices
- **Real-time Updates**: Live statistics and game state updates

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd blackjack
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game**

   **Command Line Version:**
   ```bash
   python main.py
   ```

   **Web Version:**
   ```bash
   python app.py
   ```
   Then open your browser to `http://localhost:5000`

## 🎮 How to Play

### Game Rules
- **Objective**: Beat the dealer by getting closer to 21 without going over
- **Card Values**: 
  - Number cards (2-10): Face value
  - Face cards (J, Q, K): 10 points
  - Ace: 11 points (or 1 if going over 21 would bust)
- **Dealer Rules**: Dealer must hit on 16 or below, stand on 17 or above
- **Blackjack**: Ace + 10-value card = 21 (1.5x bet payout)

### Betting
- **Starting Money**: $1,000
- **Bet Range**: $10 - $500 per hand
- **Payouts**:
  - Win: 1x bet amount
  - Blackjack: 1.5x bet amount
  - Tie: Return original bet
  - Loss: Lose bet amount

### Game Flow
1. Enter your name
2. Place your bet
3. Receive initial cards (2 each for player and dealer)
4. Choose to Hit (take another card) or Stand (keep current hand)
5. Dealer plays automatically
6. Winner is determined and money is awarded
7. View updated statistics and leaderboard

## 📁 Project Structure

```
blackjack/
├── main.py              # Core game logic and CLI interface
├── app.py               # Flask web application
├── test_blackjack.py    # Comprehensive unit tests
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── templates/
│   └── index.html      # Web interface template
└── leaderboard.json    # Persistent leaderboard data (created automatically)
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python -m pytest test_blackjack.py -v
```

Or run with unittest:

```bash
python test_blackjack.py
```

### Test Coverage
- **Card Class**: Creation, string representation
- **Deck Class**: Creation, shuffling, dealing
- **Hand Class**: Card management, value calculation, blackjack detection
- **Player Class**: Betting, statistics, win rate calculation
- **Leaderboard Class**: Data persistence, sorting, player management
- **Game Class**: User input validation, game flow

## 🎨 Web Interface Features

### Modern Design
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Glass Morphism**: Modern UI with backdrop blur effects
- **Card Animations**: Smooth card display with suit symbols
- **Real-time Updates**: Live statistics and game state

### User Experience
- **Intuitive Controls**: Clear hit/stand buttons with proper states
- **Visual Feedback**: Color-coded messages for wins, losses, and ties
- **Statistics Panel**: Real-time balance, win rate, and performance metrics
- **Leaderboard Modal**: Easy access to top players with detailed stats

## 🔧 Technical Implementation

### Object-Oriented Design
- **Card Class**: Represents individual playing cards
- **Deck Class**: Manages 52-card deck with shuffling and dealing
- **Hand Class**: Handles card collections and value calculations
- **Player Class**: Manages player state, betting, and statistics
- **Leaderboard Class**: Handles persistent score storage and ranking
- **Game Class**: Orchestrates game flow and user interaction

### Data Persistence
- **JSON Storage**: Leaderboard data stored in human-readable format
- **Session Management**: Web interface maintains game state
- **Automatic Backup**: Leaderboard automatically saves after each game

### Error Handling
- **Input Validation**: Robust validation for all user inputs
- **Edge Cases**: Handles empty decks, invalid bets, and game states
- **Graceful Degradation**: Web interface works even with network issues

## 📊 Screenshots

### Command Line Interface
```
🎰 Welcome to Blackjack! 🎰
========================================
Enter your name: Player1

Welcome, Player1! You start with $1000

==================================================
Current Balance: $1000
Games Played: 0
Win Rate: 0.0%
Blackjacks: 0
==================================================

Options:
1. Play a game
2. View leaderboard
3. Quit
Enter your choice (1-3): 1

Your current balance: $1000
Betting range: $10 - $500
Enter your bet amount: $100

Bet placed: $100

****************************************
🎯 Round Starting - Bet: $100
****************************************
Player's Hand:
A of hearts
K of spades
Value: 21

Dealer's Hand:
Hidden Card
Q of diamonds

🎰 BLACKJACK! You win 1.5x your bet!
```

### Web Interface
The web interface features a modern, responsive design with:
- Clean card display with suit symbols
- Real-time statistics panel
- Interactive betting controls
- Modal leaderboard display
- Mobile-optimized layout

## 🎯 Resume Impact

This project demonstrates:

### Technical Skills
- **Python Programming**: Advanced OOP, data structures, algorithms
- **Web Development**: Flask framework, HTML/CSS/JavaScript
- **Testing**: Comprehensive unit testing with unittest framework
- **Data Persistence**: JSON file handling and session management

### Software Engineering
- **Clean Code**: Proper naming conventions, documentation, modular design
- **Design Patterns**: Separation of concerns, single responsibility principle
- **Error Handling**: Robust input validation and edge case management
- **Version Control**: Git repository with proper structure

### Problem Solving
- **Game Logic**: Complex rule implementation and state management
- **User Experience**: Intuitive interfaces for different user types
- **Performance**: Efficient algorithms and data structures
- **Scalability**: Extensible architecture for future enhancements

## 🚀 Future Enhancements

### Potential Additions
- **Multiplayer Support**: Real-time multiplayer games
- **AI Opponents**: Computer players with different strategies
- **Tournament Mode**: Competitive tournament system
- **Achievement System**: Unlockable achievements and badges
- **Sound Effects**: Audio feedback for game actions
- **Animations**: Card flip and deal animations
- **Database Integration**: SQL database for better data management
- **API Development**: RESTful API for mobile applications

### Technical Improvements
- **Performance Optimization**: Caching and database indexing
- **Security Enhancements**: Input sanitization and rate limiting
- **Deployment**: Docker containerization and cloud deployment
- **Monitoring**: Logging and performance monitoring
- **CI/CD**: Automated testing and deployment pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

Created with ❤️ for demonstrating Python programming skills and software engineering best practices.

---

**Ready to play?** Run `python main.py` for the command-line version or `python app.py` for the web interface! 