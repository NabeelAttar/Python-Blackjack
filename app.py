from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
from main import Card, Deck, Hand, Player, Leaderboard, Game, BLACKJACK, DEALER_STAND

app = Flask(__name__)
app.secret_key = 'blackjack_secret_key_2024'

# Global game state
game_state = {}

@app.route('/')
def index():
    """Main game page"""
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    """Start a new game"""
    data = request.get_json()
    player_name = data.get('player_name', 'Player')
    
    # Initialize game state
    session['player_name'] = player_name
    session['player_money'] = 1000
    session['games_played'] = 0
    session['games_won'] = 0
    session['blackjacks'] = 0
    session['current_bet'] = 0
    session['game_active'] = False
    
    return jsonify({
        'status': 'success',
        'message': f'Welcome, {player_name}!',
        'player_money': session['player_money']
    })

@app.route('/place_bet', methods=['POST'])
def place_bet():
    """Place a bet"""
    data = request.get_json()
    bet_amount = int(data.get('bet_amount', 0))
    
    if bet_amount > session['player_money'] or bet_amount < 10 or bet_amount > 500:
        return jsonify({
            'status': 'error',
            'message': 'Invalid bet amount. Must be between $10 and $500, and not exceed your balance.'
        })
    
    session['current_bet'] = bet_amount
    session['player_money'] -= bet_amount
    session['game_active'] = True
    
    # Initialize game
    deck = Deck()
    deck.shuffle()
    
    player_hand = Hand()
    dealer_hand = Hand(dealer=True)
    
    # Deal initial cards
    for _ in range(2):
        player_hand.add_card(deck.deal(1))
        dealer_hand.add_card(deck.deal(1))
    
    # Check for initial blackjack
    game_message = _check_initial_blackjack(player_hand, dealer_hand)
    
    # Handle blackjack wins immediately
    if game_message and "BLACKJACK" in game_message and "tie" not in game_message:
        if player_hand.is_blackjack():
            # Player wins with blackjack
            session['games_played'] += 1
            session['games_won'] += 1
            session['blackjacks'] += 1
            # Return bet + 1.5x winnings (total = bet + 1.5*bet = 2.5*bet)
            session['player_money'] += session['current_bet'] + int(session['current_bet'] * 1.5)
            session['game_active'] = False
            session['current_bet'] = 0
        elif dealer_hand.is_blackjack():
            # Dealer wins with blackjack
            session['games_played'] += 1
            session['game_active'] = False
            session['current_bet'] = 0
        elif "tie" in game_message:
            # Both have blackjack - tie
            session['games_played'] += 1
            session['player_money'] += session['current_bet']  # Return bet
            session['game_active'] = False
            session['current_bet'] = 0
    
    # Store game state
    session['deck'] = _serialize_deck(deck)
    session['player_hand'] = _serialize_hand(player_hand)
    session['dealer_hand'] = _serialize_hand(dealer_hand)
    
    return jsonify({
        'status': 'success',
        'player_hand': _format_hand_for_display(player_hand),
        'dealer_hand': _format_hand_for_display(dealer_hand, hide_first=True),
        'player_value': player_hand.get_value(),
        'dealer_value': dealer_hand.get_value() if len(dealer_hand.cards) == 2 and dealer_hand.is_blackjack() else '?',
        'game_message': game_message
    })

@app.route('/hit', methods=['POST'])
def hit():
    """Player hits"""
    if not session.get('game_active', False):
        return jsonify({'status': 'error', 'message': 'No active game'})
    
    # Reconstruct game state
    deck = _deserialize_deck(session['deck'])
    player_hand = _deserialize_hand(session['player_hand'])
    dealer_hand = _deserialize_hand(session['dealer_hand'])
    
    # Deal card to player
    player_hand.add_card(deck.deal(1))
    
    # Update session
    session['deck'] = _serialize_deck(deck)
    session['player_hand'] = _serialize_hand(player_hand)
    
    player_value = player_hand.get_value()
    
    if player_value > BLACKJACK:
        # Player busted
        session['games_played'] += 1
        session['game_active'] = False
        return jsonify({
            'status': 'game_over',
            'player_hand': _format_hand_for_display(player_hand),
            'dealer_hand': _format_hand_for_display(dealer_hand, show_all=True),
            'player_value': player_value,
            'dealer_value': dealer_hand.get_value(),
            'message': '💥 You busted! Dealer wins.',
            'result': 'lose'
        })
    
    return jsonify({
        'status': 'continue',
        'player_hand': _format_hand_for_display(player_hand),
        'player_value': player_value,
        'can_hit': player_value < BLACKJACK
    })

@app.route('/stand', methods=['POST'])
def stand():
    """Player stands"""
    if not session.get('game_active', False):
        return jsonify({'status': 'error', 'message': 'No active game'})
    
    # Reconstruct game state
    deck = _deserialize_deck(session['deck'])
    player_hand = _deserialize_hand(session['player_hand'])
    dealer_hand = _deserialize_hand(session['dealer_hand'])
    
    # Dealer's turn
    while dealer_hand.get_value() < DEALER_STAND:
        dealer_hand.add_card(deck.deal(1))
    
    player_value = player_hand.get_value()
    dealer_value = dealer_hand.get_value()
    
    # Determine winner
    result, message = _determine_winner(player_hand, dealer_hand)
    
    # Update session
    session['games_played'] += 1
    if result == 'win':
        session['games_won'] += 1
        if player_hand.is_blackjack():
            session['blackjacks'] += 1
            # Return bet + 1.5x winnings (total = bet + 1.5*bet = 2.5*bet)
            session['player_money'] += session['current_bet'] + int(session['current_bet'] * 1.5)
        else:
            session['player_money'] += session['current_bet'] * 2
    elif result == 'tie':
        session['player_money'] += session['current_bet']
    
    session['current_bet'] = 0
    session['game_active'] = False
    
    return jsonify({
        'status': 'game_over',
        'player_hand': _format_hand_for_display(player_hand),
        'dealer_hand': _format_hand_for_display(dealer_hand, show_all=True),
        'player_value': player_value,
        'dealer_value': dealer_value,
        'message': message,
        'result': result,
        'player_money': session['player_money']
    })

@app.route('/get_stats')
def get_stats():
    """Get player statistics"""
    return jsonify({
        'player_name': session.get('player_name', 'Player'),
        'player_money': session.get('player_money', 0),
        'games_played': session.get('games_played', 0),
        'games_won': session.get('games_won', 0),
        'blackjacks': session.get('blackjacks', 0),
        'win_rate': round((session.get('games_won', 0) / max(session.get('games_played', 1), 1)) * 100, 1)
    })

@app.route('/leaderboard')
def get_leaderboard():
    """Get leaderboard data"""
    leaderboard = Leaderboard()
    # Add cache control headers to prevent caching
    response = jsonify(leaderboard.leaderboard)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/save_to_leaderboard', methods=['POST'])
def save_to_leaderboard():
    """Save current player to leaderboard"""
    if session.get('games_played', 0) == 0:
        return jsonify({'status': 'error', 'message': 'No games played yet'})
    
    # Create player object
    player = Player(session.get('player_name', 'Player'))
    player.money = session.get('player_money', 0)
    player.games_played = session.get('games_played', 0)
    player.games_won = session.get('games_won', 0)
    player.blackjacks = session.get('blackjacks', 0)
    
    # Add to leaderboard
    leaderboard = Leaderboard()
    leaderboard.add_player(player)
    
    return jsonify({'status': 'success', 'message': 'Score saved to leaderboard!'})

# Helper methods
def _serialize_deck(deck):
    """Serialize deck for session storage"""
    return [{'suit': card.suit, 'rank': card.rank, 'value': card.value} for card in deck.cards]

def _deserialize_deck(deck_data):
    """Deserialize deck from session storage"""
    deck = Deck()
    deck.cards = []
    for card_data in deck_data:
        rank_data = {'rank': card_data['rank'], 'value': card_data['value']}
        deck.cards.append(Card(card_data['suit'], rank_data))
    return deck

def _serialize_hand(hand):
    """Serialize hand for session storage"""
    return {
        'cards': [{'suit': card.suit, 'rank': card.rank, 'value': card.value} for card in hand.cards],
        'dealer': hand.dealer
    }

def _deserialize_hand(hand_data):
    """Deserialize hand from session storage"""
    hand = Hand(dealer=hand_data['dealer'])
    for card_data in hand_data['cards']:
        rank_data = {'rank': card_data['rank'], 'value': card_data['value']}
        hand.cards.append(Card(card_data['suit'], rank_data))
    return hand

def _format_hand_for_display(hand, hide_first=False, show_all=False):
    """Format hand for display"""
    cards = []
    for i, card in enumerate(hand.cards):
        if hide_first and i == 0 and not show_all and not hand.is_blackjack():
            cards.append({'display': '🂠 Hidden', 'suit': 'hidden', 'rank': 'hidden'})
        else:
            suit_symbol = _get_suit_symbol(card.suit)
            cards.append({
                'display': f'{suit_symbol}{card.rank}',
                'suit': card.suit,
                'rank': card.rank
            })
    return cards

def _get_suit_symbol(suit):
    """Get Unicode suit symbol"""
    symbols = {
        'hearts': '♥',
        'diamonds': '♦',
        'clubs': '♣',
        'spades': '♠'
    }
    return symbols.get(suit, suit)

def _check_initial_blackjack(player_hand, dealer_hand):
    """Check for initial blackjack"""
    if player_hand.is_blackjack() and dealer_hand.is_blackjack():
        return "🤝 Both have blackjack! It's a tie."
    elif player_hand.is_blackjack():
        return "🎰 BLACKJACK! You win 1.5x your bet!"
    elif dealer_hand.is_blackjack():
        return "😱 Dealer has blackjack! Dealer wins."
    return ""

def _determine_winner(player_hand, dealer_hand):
    """Determine game winner"""
    player_value = player_hand.get_value()
    dealer_value = dealer_hand.get_value()
    
    if dealer_value > BLACKJACK:
        return 'win', '🎉 Dealer busted! You win!'
    elif player_value > dealer_value:
        return 'win', '🎉 You win!'
    elif player_value < dealer_value:
        return 'lose', '😔 Dealer wins!'
    else:
        return 'tie', '🤝 It\'s a tie!'

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 