import random
import json
import os
from datetime import datetime

# Constants
BLACKJACK = 21
DEALER_STAND = 17
STARTING_MONEY = 1000
MIN_BET = 10
MAX_BET = 500

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank["rank"]
        self.value = rank["value"]

    def __str__(self):
        return f"{self.rank} of {self.suit}"

class Deck:
    def __init__(self):
        self.cards = []
        suits = ["hearts", "diamonds", "clubs", "spades"]
        ranks = [
            {"rank": "A", "value": 11},
            {"rank": "2", "value": 2},
            {"rank": "3", "value": 3},
            {"rank": "4", "value": 4},
            {"rank": "5", "value": 5},
            {"rank": "6", "value": 6},
            {"rank": "7", "value": 7},
            {"rank": "8", "value": 8},
            {"rank": "9", "value": 9},
            {"rank": "10", "value": 10},
            {"rank": "J", "value": 10},
            {"rank": "Q", "value": 10},
            {"rank": "K", "value": 10}
        ]

        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))

    def shuffle(self):
        if len(self.cards) > 1:
            random.shuffle(self.cards)

    def deal(self, number):
        cards_dealt = []
        for _ in range(number):
            if len(self.cards) > 0:
                card = self.cards.pop()
                cards_dealt.append(card)
        return cards_dealt

class Hand:
    def __init__(self, dealer=False):
        self.cards = []
        self.value = 0
        self.dealer = dealer

    def add_card(self, card_list):
        self.cards.extend(card_list)
    
    def calculate_value(self):
        self.value = 0
        has_ace = False
        
        for card in self.cards:
            self.value += card.value
            if card.rank == "A":
                has_ace = True
        
        if has_ace and self.value > BLACKJACK:
            self.value -= 10

    def get_value(self):
        self.calculate_value()
        return self.value
    
    def is_blackjack(self):
        return self.value == BLACKJACK
    
    def display(self, show_all_dealer_cards=False):
        print("Dealer's Hand:" if self.dealer else "Player's Hand:")
        for index, card in enumerate(self.cards):
            if index == 0 and self.dealer and not show_all_dealer_cards and not self.is_blackjack():
                print("Hidden Card") 
            else:
                print(card)

        if not self.dealer:
            print("Value:", self.get_value())
        print()

class Player:
    def __init__(self, name):
        self.name = name
        self.money = STARTING_MONEY
        self.current_bet = 0
        self.games_played = 0
        self.games_won = 0
        self.games_lost = 0
        self.blackjacks = 0
        self.total_winnings = 0
        self.highest_balance = STARTING_MONEY

    def place_bet(self, amount):
        if amount <= self.money and MIN_BET <= amount <= MAX_BET:
            self.money -= amount
            self.current_bet = amount
            return True
        return False

    def win_bet(self, multiplier=1):
        # For blackjack (multiplier=1.5), we want: bet + 1.5*bet = 2.5*bet
        # For regular win (multiplier=1), we want: bet + 1*bet = 2*bet
        winnings = self.current_bet + (self.current_bet * multiplier)
        self.money += winnings
        self.total_winnings += winnings
        self.current_bet = 0
        if self.money > self.highest_balance:
            self.highest_balance = self.money

    def lose_bet(self):
        self.current_bet = 0

    def get_win_rate(self):
        if self.games_played == 0:
            return 0
        return (self.games_won / self.games_played) * 100

class Leaderboard:
    def __init__(self, filename="leaderboard.json"):
        self.filename = filename
        self.leaderboard = self.load_leaderboard()

    def load_leaderboard(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_leaderboard(self):
        with open(self.filename, 'w') as f:
            json.dump(self.leaderboard, f, indent=2)

    def add_player(self, player):
        player_data = {
            "name": player.name,
            "final_balance": player.money,
            "highest_balance": player.highest_balance,
            "games_played": player.games_played,
            "games_won": player.games_won,
            "win_rate": round(player.get_win_rate(), 2),
            "blackjacks": player.blackjacks,
            "total_winnings": player.total_winnings,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Check if player already exists in leaderboard
        existing_player_index = None
        for i, existing_player in enumerate(self.leaderboard):
            if existing_player["name"] == player.name:
                existing_player_index = i
                break
        
        if existing_player_index is not None:
            # Keep the entry with the BEST win rate (not the latest)
            existing_player = self.leaderboard[existing_player_index]
            if player_data["win_rate"] > existing_player["win_rate"]:
                # New player has better win rate, update the entry
                self.leaderboard[existing_player_index] = player_data
            elif player_data["win_rate"] == existing_player["win_rate"]:
                # Same win rate, keep the one with higher final balance
                if player_data["final_balance"] > existing_player["final_balance"]:
                    self.leaderboard[existing_player_index] = player_data
            # If existing player has better win rate, don't update
        else:
            # Add new player
            self.leaderboard.append(player_data)
        
        # Sort by win rate (highest first), then by final balance as tiebreaker
        self.leaderboard.sort(key=lambda x: (x["win_rate"], x["final_balance"]), reverse=True)
        
        # Keep only top 10 players
        self.leaderboard = self.leaderboard[:10]
        self.save_leaderboard()

    def display_leaderboard(self):
        print("\n" + "="*60)
        print("🏆 LEADERBOARD 🏆")
        print("="*60)
        print(f"{'Rank':<4} {'Name':<15} {'Final Balance':<15} {'Win Rate':<10} {'Games':<8} {'Blackjacks':<12}")
        print("-"*60)
        
        for i, player in enumerate(self.leaderboard, 1):
            print(f"{i:<4} {player['name']:<15} ${player['final_balance']:<14} {player['win_rate']}%{'':<6} {player['games_played']:<8} {player['blackjacks']:<12}")
        print("="*60)

class Game:
    def __init__(self):
        self.leaderboard = Leaderboard()

    def get_player_name(self):
        while True:
            name = input("Enter your name: ").strip()
            if name:
                return name
            print("Please enter a valid name.")

    def get_bet_amount(self, player):
        while True:
            try:
                print(f"\nYour current balance: ${player.money}")
                print(f"Betting range: ${MIN_BET} - ${min(MAX_BET, player.money)}")
                bet = int(input("Enter your bet amount: $"))
                
                if player.place_bet(bet):
                    return bet
                else:
                    print("Invalid bet amount. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def play(self):
        print("🎰 Welcome to Blackjack! 🎰")
        print("="*40)
        
        player_name = self.get_player_name()
        player = Player(player_name)
        
        print(f"\nWelcome, {player.name}! You start with ${player.money}")
        
        while player.money >= MIN_BET:
            print(f"\n{'='*50}")
            print(f"Current Balance: ${player.money}")
            print(f"Games Played: {player.games_played}")
            print(f"Win Rate: {player.get_win_rate():.1f}%")
            print(f"Blackjacks: {player.blackjacks}")
            print(f"{'='*50}")
            
            choice = input("\nOptions:\n1. Play a game\n2. View leaderboard\n3. Quit\nEnter your choice (1-3): ")
            
            if choice == "1":
                self.play_single_game(player)
            elif choice == "2":
                self.leaderboard.display_leaderboard()
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please try again.")

        # Game over - add to leaderboard
        print(f"\n🎮 Game Over! 🎮")
        print(f"Final Balance: ${player.money}")
        print(f"Total Games: {player.games_played}")
        print(f"Win Rate: {player.get_win_rate():.1f}%")
        print(f"Blackjacks: {player.blackjacks}")
        
        self.leaderboard.add_player(player)
        self.leaderboard.display_leaderboard()

    def play_single_game(self, player):
        bet = self.get_bet_amount(player)
        print(f"\nBet placed: ${bet}")
        
        deck_of_cards = Deck()
        deck_of_cards.shuffle()
        player_hand = Hand()
        dealer_hand = Hand(dealer=True)

        # Deal initial cards
        for _ in range(2):
            player_hand.add_card(deck_of_cards.deal(1))
            dealer_hand.add_card(deck_of_cards.deal(1))
        
        print(f"\n{'*' * 40}")
        print(f"🎯 Round Starting - Bet: ${bet}")
        print(f"{'*' * 40}")
        player_hand.display()
        dealer_hand.display()

        # Check for immediate blackjack
        if self.check_winner(player_hand, dealer_hand, player):
            return
                
        # Player's turn
        choice = ""
        while player_hand.get_value() < BLACKJACK and choice not in ['s', 'stand']:
            choice = input("Do you want to hit (h) or stand (s)? ").lower()
            print()
            while choice not in ['h', 's', 'hit', 'stand']:
                choice = input("Invalid choice. Please enter 'h' to hit or 's' to stand: ").lower()
                print()
            if choice in ['h', 'hit']:
                player_hand.add_card(deck_of_cards.deal(1))
                player_hand.display() 

        if self.check_winner(player_hand, dealer_hand, player):
            return

        # Dealer's turn
        player_hand_value = player_hand.get_value()
        dealer_hand_value = dealer_hand.get_value()

        while dealer_hand_value < DEALER_STAND:
            dealer_hand.add_card(deck_of_cards.deal(1))
            dealer_hand_value = dealer_hand.get_value()

        dealer_hand.display(show_all_dealer_cards=True)

        if self.check_winner(player_hand, dealer_hand, player):
            return

        print("Final Results:")
        print(f"Your hand: {player_hand_value}")
        print(f"Dealer hand: {dealer_hand_value}")

        self.check_winner(player_hand, dealer_hand, player, game_over=True)

    def check_winner(self, player_hand, dealer_hand, player, game_over=False):
        player.games_played += 1
        
        if not game_over:
            if player_hand.get_value() > BLACKJACK:
                print("💥 You busted! Dealer wins.")
                player.games_lost += 1
                player.lose_bet()
                return True
            elif dealer_hand.get_value() > BLACKJACK:
                print("🎉 Dealer busted! You win!")
                player.games_won += 1
                player.win_bet()
                return True
            elif player_hand.is_blackjack() and dealer_hand.is_blackjack():
                print("🤝 Both have blackjack! It's a tie.")
                player.current_bet = 0  # Return bet
                return True
            elif player_hand.is_blackjack():
                print("🎰 BLACKJACK! You win 1.5x your bet!")
                player.games_won += 1
                player.blackjacks += 1
                player.win_bet(1.5)
                return True
            elif dealer_hand.is_blackjack():
                print("😱 Dealer has blackjack! Dealer wins.")
                player.games_lost += 1
                player.lose_bet()
                return True
        else:
            if player_hand.get_value() > dealer_hand.get_value():
                print("🎉 You win!")
                player.games_won += 1
                player.win_bet()
            elif player_hand.get_value() < dealer_hand.get_value():
                print("😔 Dealer wins!")
                player.games_lost += 1
                player.lose_bet()
            else:
                print("🤝 It's a tie!")
                player.current_bet = 0  # Return bet
            return True

        return False

if __name__ == "__main__":
    game = Game()
    game.play()