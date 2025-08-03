import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from main import Card, Deck, Hand, Player, Leaderboard, Game, BLACKJACK, DEALER_STAND

class TestCard(unittest.TestCase):
    def test_card_creation(self):
        """Test card creation with suit and rank"""
        rank_data = {"rank": "A", "value": 11}
        card = Card("hearts", rank_data)
        self.assertEqual(card.suit, "hearts")
        self.assertEqual(card.rank, "A")
        self.assertEqual(card.value, 11)

    def test_card_string_representation(self):
        """Test card string representation"""
        rank_data = {"rank": "K", "value": 10}
        card = Card("spades", rank_data)
        self.assertEqual(str(card), "K of spades")

class TestDeck(unittest.TestCase):
    def test_deck_creation(self):
        """Test deck creation with all 52 cards"""
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)

    def test_deck_shuffle(self):
        """Test deck shuffling"""
        deck = Deck()
        original_order = [str(card) for card in deck.cards[:5]]
        deck.shuffle()
        new_order = [str(card) for card in deck.cards[:5]]
        # Note: There's a small chance this could fail if shuffle returns same order
        # In practice, this is extremely unlikely with 52 cards
        self.assertNotEqual(original_order, new_order)

    def test_deck_deal(self):
        """Test dealing cards from deck"""
        deck = Deck()
        initial_count = len(deck.cards)
        dealt_cards = deck.deal(3)
        
        self.assertEqual(len(dealt_cards), 3)
        self.assertEqual(len(deck.cards), initial_count - 3)

    def test_deck_deal_empty(self):
        """Test dealing from empty deck"""
        deck = Deck()
        deck.cards = []  # Empty the deck
        dealt_cards = deck.deal(5)
        self.assertEqual(len(dealt_cards), 0)

class TestHand(unittest.TestCase):
    def test_hand_creation(self):
        """Test hand creation"""
        hand = Hand()
        self.assertEqual(len(hand.cards), 0)
        self.assertEqual(hand.value, 0)
        self.assertFalse(hand.dealer)

    def test_dealer_hand_creation(self):
        """Test dealer hand creation"""
        hand = Hand(dealer=True)
        self.assertTrue(hand.dealer)

    def test_add_card(self):
        """Test adding cards to hand"""
        hand = Hand()
        card1 = Card("hearts", {"rank": "A", "value": 11})
        card2 = Card("spades", {"rank": "K", "value": 10})
        
        hand.add_card([card1])
        self.assertEqual(len(hand.cards), 1)
        
        hand.add_card([card2])
        self.assertEqual(len(hand.cards), 2)

    def test_calculate_value_no_ace(self):
        """Test hand value calculation without ace"""
        hand = Hand()
        card1 = Card("hearts", {"rank": "K", "value": 10})
        card2 = Card("spades", {"rank": "Q", "value": 10})
        
        hand.add_card([card1, card2])
        hand.calculate_value()
        self.assertEqual(hand.value, 20)

    def test_calculate_value_with_ace_high(self):
        """Test hand value calculation with ace as 11"""
        hand = Hand()
        card1 = Card("hearts", {"rank": "A", "value": 11})
        card2 = Card("spades", {"rank": "K", "value": 10})
        
        hand.add_card([card1, card2])
        hand.calculate_value()
        self.assertEqual(hand.value, 21)

    def test_calculate_value_with_ace_low(self):
        """Test hand value calculation with ace as 1"""
        hand = Hand()
        card1 = Card("hearts", {"rank": "A", "value": 11})
        card2 = Card("spades", {"rank": "K", "value": 10})
        card3 = Card("diamonds", {"rank": "Q", "value": 10})
        
        hand.add_card([card1, card2, card3])
        hand.calculate_value()
        self.assertEqual(hand.value, 21)  # Ace becomes 1

    def test_is_blackjack(self):
        """Test blackjack detection"""
        hand = Hand()
        card1 = Card("hearts", {"rank": "A", "value": 11})
        card2 = Card("spades", {"rank": "K", "value": 10})
        
        hand.add_card([card1, card2])
        hand.calculate_value()
        self.assertTrue(hand.is_blackjack())

    def test_is_not_blackjack(self):
        """Test non-blackjack hand"""
        hand = Hand()
        card1 = Card("hearts", {"rank": "K", "value": 10})
        card2 = Card("spades", {"rank": "Q", "value": 10})
        
        hand.add_card([card1, card2])
        hand.calculate_value()
        self.assertFalse(hand.is_blackjack())

class TestPlayer(unittest.TestCase):
    def test_player_creation(self):
        """Test player creation"""
        player = Player("TestPlayer")
        self.assertEqual(player.name, "TestPlayer")
        self.assertEqual(player.money, 1000)
        self.assertEqual(player.current_bet, 0)
        self.assertEqual(player.games_played, 0)
        self.assertEqual(player.games_won, 0)
        self.assertEqual(player.games_lost, 0)
        self.assertEqual(player.blackjacks, 0)

    def test_place_bet_valid(self):
        """Test placing a valid bet"""
        player = Player("TestPlayer")
        self.assertTrue(player.place_bet(100))
        self.assertEqual(player.money, 900)
        self.assertEqual(player.current_bet, 100)

    def test_place_bet_invalid_amount(self):
        """Test placing an invalid bet amount"""
        player = Player("TestPlayer")
        self.assertFalse(player.place_bet(5))  # Below minimum
        self.assertFalse(player.place_bet(600))  # Above maximum
        self.assertFalse(player.place_bet(2000))  # Above available money

    def test_win_bet(self):
        """Test winning a bet"""
        player = Player("TestPlayer")
        player.place_bet(100)
        player.win_bet()
        self.assertEqual(player.money, 1000)  # Back to starting amount
        self.assertEqual(player.current_bet, 0)
        self.assertEqual(player.total_winnings, 100)

    def test_win_bet_with_multiplier(self):
        """Test winning a bet with multiplier"""
        player = Player("TestPlayer")
        player.place_bet(100)
        player.win_bet(1.5)  # Blackjack payout
        self.assertEqual(player.money, 1050)
        self.assertEqual(player.total_winnings, 150)

    def test_lose_bet(self):
        """Test losing a bet"""
        player = Player("TestPlayer")
        player.place_bet(100)
        player.lose_bet()
        self.assertEqual(player.money, 900)
        self.assertEqual(player.current_bet, 0)

    def test_get_win_rate_no_games(self):
        """Test win rate calculation with no games played"""
        player = Player("TestPlayer")
        self.assertEqual(player.get_win_rate(), 0)

    def test_get_win_rate_with_games(self):
        """Test win rate calculation with games played"""
        player = Player("TestPlayer")
        player.games_played = 10
        player.games_won = 6
        self.assertEqual(player.get_win_rate(), 60.0)

    def test_highest_balance_tracking(self):
        """Test highest balance tracking"""
        player = Player("TestPlayer")
        player.place_bet(100)
        player.win_bet(2)  # Win 200
        self.assertEqual(player.highest_balance, 1100)

class TestLeaderboard(unittest.TestCase):
    def setUp(self):
        """Set up temporary file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()

    def tearDown(self):
        """Clean up temporary file"""
        os.unlink(self.temp_file.name)

    def test_leaderboard_creation(self):
        """Test leaderboard creation"""
        leaderboard = Leaderboard(self.temp_file.name)
        self.assertEqual(len(leaderboard.leaderboard), 0)

    def test_load_leaderboard_empty_file(self):
        """Test loading empty leaderboard"""
        leaderboard = Leaderboard(self.temp_file.name)
        self.assertEqual(len(leaderboard.leaderboard), 0)

    def test_load_leaderboard_with_data(self):
        """Test loading leaderboard with existing data"""
        test_data = [
            {"name": "Player1", "final_balance": 1500, "highest_balance": 1500,
             "games_played": 10, "games_won": 6, "win_rate": 60.0,
             "blackjacks": 2, "total_winnings": 500, "date": "2024-01-01"}
        ]
        with open(self.temp_file.name, 'w') as f:
            json.dump(test_data, f)

        leaderboard = Leaderboard(self.temp_file.name)
        self.assertEqual(len(leaderboard.leaderboard), 1)
        self.assertEqual(leaderboard.leaderboard[0]["name"], "Player1")

    def test_add_player(self):
        """Test adding a player to leaderboard"""
        leaderboard = Leaderboard(self.temp_file.name)
        player = Player("TestPlayer")
        player.money = 1200
        player.games_played = 5
        player.games_won = 3
        player.blackjacks = 1
        player.total_winnings = 200

        leaderboard.add_player(player)
        self.assertEqual(len(leaderboard.leaderboard), 1)
        self.assertEqual(leaderboard.leaderboard[0]["name"], "TestPlayer")
        self.assertEqual(leaderboard.leaderboard[0]["final_balance"], 1200)

    def test_leaderboard_sorting(self):
        """Test leaderboard sorting by final balance"""
        leaderboard = Leaderboard(self.temp_file.name)
        
        # Add players in random order
        player1 = Player("Player1")
        player1.money = 800
        
        player2 = Player("Player2")
        player2.money = 1500
        
        player3 = Player("Player3")
        player3.money = 1200

        leaderboard.add_player(player1)
        leaderboard.add_player(player2)
        leaderboard.add_player(player3)

        # Should be sorted by final balance (descending)
        self.assertEqual(leaderboard.leaderboard[0]["name"], "Player2")
        self.assertEqual(leaderboard.leaderboard[1]["name"], "Player3")
        self.assertEqual(leaderboard.leaderboard[2]["name"], "Player1")

    def test_leaderboard_limit(self):
        """Test leaderboard keeps only top 10 players"""
        leaderboard = Leaderboard(self.temp_file.name)
        
        # Add 12 players
        for i in range(12):
            player = Player(f"Player{i}")
            player.money = 1000 - i * 10  # Decreasing balances
            leaderboard.add_player(player)

        self.assertEqual(len(leaderboard.leaderboard), 10)
        self.assertEqual(leaderboard.leaderboard[0]["name"], "Player0")  # Highest balance

class TestGame(unittest.TestCase):
    def test_game_creation(self):
        """Test game creation"""
        game = Game()
        self.assertIsInstance(game.leaderboard, Leaderboard)

    @patch('builtins.input')
    def test_get_player_name(self, mock_input):
        """Test getting player name"""
        mock_input.return_value = "TestPlayer"
        game = Game()
        name = game.get_player_name()
        self.assertEqual(name, "TestPlayer")

    @patch('builtins.input')
    def test_get_bet_amount_valid(self, mock_input):
        """Test getting valid bet amount"""
        mock_input.return_value = "100"
        game = Game()
        player = Player("TestPlayer")
        bet = game.get_bet_amount(player)
        self.assertEqual(bet, 100)

    @patch('builtins.input')
    def test_get_bet_amount_invalid_then_valid(self, mock_input):
        """Test getting invalid then valid bet amount"""
        mock_input.side_effect = ["invalid", "50"]
        game = Game()
        player = Player("TestPlayer")
        bet = game.get_bet_amount(player)
        self.assertEqual(bet, 50)

if __name__ == '__main__':
    unittest.main() 