"""
Tests for PokerGame class logic
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydealer import Stack, Card
from app.PokerGame import PokerGame


class MockUser:
    """Mock user object for testing"""
    def __init__(self, username):
        self.username = username


@pytest.fixture
def poker_game():
    """Create a fresh PokerGame instance for each test"""
    game = PokerGame(id=1, big_blind=10, max_players=8)
    return game


@pytest.fixture
def mock_callbacks():
    """Create mock callback functions"""
    return {
        'message_callback': AsyncMock(),
        'private_message_callback': AsyncMock()
    }


class TestPokerGameBasics:
    """Test basic PokerGame functionality"""
    
    def test_initialization(self, poker_game):
        """Test that PokerGame initializes correctly"""
        assert poker_game.id == 1
        assert poker_game.big_blind == 10
        assert poker_game.default_chip_count == 1000
        assert poker_game.game_state == 'waiting'
        assert len(poker_game.players) == 8
        assert all(v is None for v in poker_game.players.values())
        assert poker_game.pot == 0
        assert poker_game.dealer_position is None

    def test_add_player(self, poker_game):
        """Test adding players to the game"""
        user1 = MockUser("player1")
        user2 = MockUser("player2")
        
        pos1 = poker_game.add_player(user1)
        assert pos1 == 0
        assert poker_game.players[pos1]['username'] == "player1"
        assert poker_game.players[pos1]['chip_count'] == 1000
        assert poker_game.players[pos1]['cards'] is None
        assert poker_game.players[pos1]['folded'] is False
        
        pos2 = poker_game.add_player(user2)
        assert pos2 == 1
        assert poker_game.players[pos2]['username'] == "player2"

    def test_add_player_full_table(self, poker_game):
        """Test adding players when table is full"""
        for i in range(8):
            user = MockUser(f"player{i}")
            pos = poker_game.add_player(user)
            assert pos == i
        
        # Try to add 9th player
        user9 = MockUser("player9")
        pos = poker_game.add_player(user9)
        assert pos is None

    def test_remove_player(self, poker_game):
        """Test removing a player from the game"""
        user = MockUser("player1")
        pos = poker_game.add_player(user)
        assert poker_game.players[pos] is not None
        
        removed_pos = poker_game.remove_player("player1")
        assert removed_pos == pos
        assert poker_game.players[pos] is None

    def test_get_player_by_username(self, poker_game):
        """Test retrieving a player by username"""
        user = MockUser("player1")
        added_pos = poker_game.add_player(user)
        
        pos, player = poker_game.get_player("player1")
        assert pos == added_pos
        assert player['username'] == "player1"

    def test_get_player_by_position(self, poker_game):
        """Test retrieving a player by position"""
        user = MockUser("player1")
        added_pos = poker_game.add_player(user)
        
        pos, player = poker_game.get_player(added_pos)
        assert pos == added_pos
        assert player['username'] == "player1"

    def test_get_all_players(self, poker_game):
        """Test getting all players"""
        user1 = MockUser("player1")
        user2 = MockUser("player2")
        
        poker_game.add_player(user1)
        poker_game.add_player(user2)
        
        all_players = poker_game.get_all_players()
        assert len(all_players) == 2
        assert 0 in all_players
        assert 1 in all_players

    def test_can_start_game(self, poker_game):
        """Test game start conditions"""
        assert not poker_game.can_start_game()  # Not enough players
        
        user1 = MockUser("player1")
        poker_game.add_player(user1)
        assert not poker_game.can_start_game()  # Still not enough
        
        user2 = MockUser("player2")
        poker_game.add_player(user2)
        assert poker_game.can_start_game()  # Now we can start


class TestPokerGameBetting:
    """Test betting functionality"""
    
    def test_player_bet_valid(self, poker_game):
        """Test a valid bet"""
        user = MockUser("player1")
        pos = poker_game.add_player(user)
        
        # Set game state to pre_flop to allow betting
        poker_game.game_state = 'pre_flop'
        poker_game.players[pos]['active'] = True
        
        result = poker_game.player_bet(pos, 100)
        assert result == 100
        assert poker_game.players[pos]['chip_count'] == 900
        assert poker_game.players[pos]['current_bet'] == 100
        assert poker_game.pot == 100

    def test_player_bet_all_in(self, poker_game):
        """Test all-in bet"""
        user = MockUser("player1")
        pos = poker_game.add_player(user)
        
        poker_game.game_state = 'pre_flop'
        poker_game.players[pos]['active'] = True
        
        # Bet more than chip count
        result = poker_game.player_bet(pos, 1500)
        assert result == 1000  # Should bet all chips
        assert poker_game.players[pos]['chip_count'] == 0
        assert poker_game.players[pos]['all_in'] is True

    def test_player_bet_raises_max_bet(self, poker_game):
        """Test that raising updates current_max_bet"""
        user1 = MockUser("player1")
        user2 = MockUser("player2")
        
        pos1 = poker_game.add_player(user1)
        pos2 = poker_game.add_player(user2)
        
        poker_game.game_state = 'pre_flop'
        poker_game.players[pos1]['active'] = True
        poker_game.players[pos2]['active'] = True
        
        poker_game.player_bet(pos1, 50)
        assert poker_game.current_max_bet == 50
        assert poker_game.last_raiser_position == pos1
        
        poker_game.player_bet(pos2, 100)
        assert poker_game.current_max_bet == 100
        assert poker_game.last_raiser_position == pos2

    def test_player_bet_folded_player(self, poker_game):
        """Test that folded players cannot bet"""
        user = MockUser("player1")
        pos = poker_game.add_player(user)
        
        poker_game.game_state = 'pre_flop'
        poker_game.players[pos]['folded'] = True
        
        result = poker_game.player_bet(pos, 100)
        assert result is False

    def test_get_all_active_players(self, poker_game):
        """Test getting only active players"""
        user1 = MockUser("player1")
        user2 = MockUser("player2")
        user3 = MockUser("player3")
        
        pos1 = poker_game.add_player(user1)
        pos2 = poker_game.add_player(user2)
        pos3 = poker_game.add_player(user3)
        
        poker_game.players[pos1]['active'] = True
        poker_game.players[pos2]['active'] = True
        poker_game.players[pos2]['folded'] = True
        poker_game.players[pos3]['active'] = True
        poker_game.players[pos3]['all_in'] = True
        
        active_players = poker_game.get_all_active_players()
        assert len(active_players) == 1  # Only player1
        assert pos1 in active_players

    def test_get_not_folded_players(self, poker_game):
        """Test getting players who haven't folded"""
        user1 = MockUser("player1")
        user2 = MockUser("player2")
        
        pos1 = poker_game.add_player(user1)
        pos2 = poker_game.add_player(user2)
        
        poker_game.players[pos1]['active'] = True
        poker_game.players[pos2]['active'] = True
        poker_game.players[pos1]['folded'] = True
        
        not_folded = poker_game.get_not_folded_players()
        assert len(not_folded) == 1
        assert pos2 in not_folded


class TestPokerGameAsync:
    """Test async functionality of PokerGame"""
    
    @pytest.mark.asyncio
    async def test_start_game_dealer_initialization(self, poker_game, mock_callbacks):
        """Test that starting a game initializes dealer position"""
        poker_game.message_callback = mock_callbacks['message_callback']
        poker_game.private_message_callback = mock_callbacks['private_message_callback']
        
        user1 = MockUser("player1")
        user2 = MockUser("player2")
        
        poker_game.add_player(user1)
        poker_game.add_player(user2)
        
        assert poker_game.dealer_position is None
        assert poker_game.can_start_game()
        
        # Mock _transition_state to prevent full game start
        async def mock_transition(state):
            poker_game.game_state = state
            poker_game.dealer_position = 0  # Set dealer without running full game
        
        original_transition = poker_game._transition_state
        poker_game._transition_state = mock_transition
        
        result = await poker_game.start_game()
        
        poker_game._transition_state = original_transition
        
        assert result is True
        assert poker_game.dealer_position is not None
        assert poker_game.game_state == 'pre_flop'

    @pytest.mark.asyncio
    async def test_player_action_fold(self, poker_game, mock_callbacks):
        """Test player fold action"""
        poker_game.message_callback = mock_callbacks['message_callback']
        poker_game.private_message_callback = mock_callbacks['private_message_callback']
        
        user = MockUser("player1")
        pos = poker_game.add_player(user)
        
        poker_game.game_state = 'pre_flop'
        poker_game.current_player_position = pos
        poker_game.waiting_for_player = True
        
        success, msg = await poker_game.player_action("player1", "fold")
        
        assert success is True
        assert poker_game.players[pos]['folded'] is True
        assert not poker_game.waiting_for_player

    @pytest.mark.asyncio
    async def test_player_action_call(self, poker_game, mock_callbacks):
        """Test player call action"""
        poker_game.message_callback = mock_callbacks['message_callback']
        poker_game.private_message_callback = mock_callbacks['private_message_callback']
        
        user = MockUser("player1")
        pos = poker_game.add_player(user)
        
        poker_game.game_state = 'pre_flop'
        poker_game.current_player_position = pos
        poker_game.waiting_for_player = True
        poker_game.current_max_bet = 50
        poker_game.players[pos]['active'] = True
        
        success, msg = await poker_game.player_action("player1", "call")
        
        assert success is True
        assert poker_game.players[pos]['current_bet'] == 50
        assert poker_game.players[pos]['chip_count'] == 950

    @pytest.mark.asyncio
    async def test_player_action_raise(self, poker_game, mock_callbacks):
        """Test player raise action"""
        poker_game.message_callback = mock_callbacks['message_callback']
        poker_game.private_message_callback = mock_callbacks['private_message_callback']
        
        user = MockUser("player1")
        pos = poker_game.add_player(user)
        
        poker_game.game_state = 'pre_flop'
        poker_game.current_player_position = pos
        poker_game.waiting_for_player = True
        poker_game.current_max_bet = 50
        poker_game.players[pos]['active'] = True
        
        success, msg = await poker_game.player_action("player1", "raise", 100)
        
        assert success is True
        assert poker_game.players[pos]['current_bet'] == 100
        assert poker_game.current_max_bet == 100

    @pytest.mark.asyncio
    async def test_player_action_not_your_turn(self, poker_game):
        """Test that players can't act out of turn"""
        user1 = MockUser("player1")
        user2 = MockUser("player2")
        
        pos1 = poker_game.add_player(user1)
        pos2 = poker_game.add_player(user2)
        
        poker_game.game_state = 'pre_flop'
        poker_game.current_player_position = pos1
        poker_game.waiting_for_player = True
        
        # Player2 tries to act when it's player1's turn
        success, msg = await poker_game.player_action("player2", "fold")
        
        assert success is False
        assert msg == "Not your turn."

    @pytest.mark.asyncio
    async def test_player_action_invalid_action(self, poker_game):
        """Test invalid action type"""
        user = MockUser("player1")
        pos = poker_game.add_player(user)
        
        poker_game.game_state = 'pre_flop'
        poker_game.current_player_position = pos
        poker_game.waiting_for_player = True
        
        success, msg = await poker_game.player_action("player1", "invalid_action")
        
        assert success is False
        assert msg == "Invalid action."

    @pytest.mark.asyncio
    async def test_notify_callbacks(self, poker_game, mock_callbacks):
        """Test that notification callbacks are called"""
        poker_game.message_callback = mock_callbacks['message_callback']
        poker_game.private_message_callback = mock_callbacks['private_message_callback']
        
        user = MockUser("player1")
        pos = poker_game.add_player(user)
        poker_game.players[pos]['active'] = True
        
        await poker_game.notify_bet(pos)
        mock_callbacks['message_callback'].assert_called_once()
        
        cards = Stack()
        await poker_game.notify_dealt_cards(pos, cards, [0, 1])
        mock_callbacks['private_message_callback'].assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_game(self, poker_game, mock_callbacks):
        """Test game reset functionality"""
        poker_game.message_callback = mock_callbacks['message_callback']
        poker_game.private_message_callback = mock_callbacks['private_message_callback']
        
        user = MockUser("player1")
        pos = poker_game.add_player(user)
        
        # Simulate game state
        poker_game.pot = 100
        poker_game.current_max_bet = 50
        poker_game.players[pos]['folded'] = True
        poker_game.players[pos]['current_bet'] = 50
        poker_game.players[pos]['active'] = True
        
        await poker_game._reset_game()
        
        assert poker_game.pot == 0
        assert poker_game.current_max_bet == 0
        assert poker_game.players[pos]['folded'] is False
        assert poker_game.players[pos]['current_bet'] == 0
        assert poker_game.ready_for_new_round is True


class TestPokerGameHandEvaluation:
    """Test hand evaluation (basic tests, you have separate files for comprehensive tests)"""
    
    def test_evaluate_hand_high_card(self, poker_game):
        """Test high card evaluation"""
        cards = Stack()
        cards.add(Card('Ace', 'Spades'))
        cards.add(Card('King', 'Hearts'))
        cards.add(Card('Queen', 'Diamonds'))
        cards.add(Card('Jack', 'Clubs'))
        cards.add(Card('9', 'Spades'))
        
        hand_type, hand_cards = poker_game._evaluate_hand(cards)
        assert hand_type == "high_card"

    def test_evaluate_hand_pair(self, poker_game):
        """Test pair evaluation"""
        cards = Stack()
        cards.add(Card('Ace', 'Spades'))
        cards.add(Card('Ace', 'Hearts'))
        cards.add(Card('King', 'Diamonds'))
        cards.add(Card('Queen', 'Clubs'))
        cards.add(Card('Jack', 'Spades'))
        
        hand_type, hand_cards = poker_game._evaluate_hand(cards)
        assert hand_type == "pair"

    def test_evaluate_hand_insufficient_cards(self, poker_game):
        """Test hand evaluation with less than 5 cards"""
        cards = Stack()
        cards.add(Card('Ace', 'Spades'))
        cards.add(Card('King', 'Hearts'))
        
        result = poker_game._evaluate_hand(cards)
        assert result is None

    def test_compare_hands_same_rank(self, poker_game):
        """Test comparing hands of the same rank"""
        # Create two pairs, first should win
        cards1 = Stack()
        cards1.add(Card('Ace', 'Spades'))
        cards1.add(Card('Ace', 'Hearts'))
        cards1.add(Card('King', 'Diamonds'))
        cards1.add(Card('Queen', 'Clubs'))
        cards1.add(Card('Jack', 'Spades'))
        
        cards2 = Stack()
        cards2.add(Card('King', 'Spades'))
        cards2.add(Card('King', 'Hearts'))
        cards2.add(Card('Queen', 'Diamonds'))
        cards2.add(Card('Jack', 'Clubs'))
        cards2.add(Card('10', 'Spades'))
        
        hand1 = poker_game._evaluate_hand(cards1)
        hand2 = poker_game._evaluate_hand(cards2)
        
        result = poker_game._compare_hands(hand1, hand2)
        assert result == 1  # hand1 wins

    def test_compare_hands_different_rank(self, poker_game):
        """Test comparing hands of different ranks"""
        # Pair vs straight
        cards1 = Stack()
        cards1.add(Card('Ace', 'Spades'))
        cards1.add(Card('Ace', 'Hearts'))
        cards1.add(Card('King', 'Diamonds'))
        cards1.add(Card('Queen', 'Clubs'))
        cards1.add(Card('Jack', 'Spades'))
        
        cards2 = Stack()
        cards2.add(Card('King', 'Spades'))
        cards2.add(Card('Queen', 'Hearts'))
        cards2.add(Card('Jack', 'Diamonds'))
        cards2.add(Card('10', 'Clubs'))
        cards2.add(Card('9', 'Spades'))
        
        hand1 = poker_game._evaluate_hand(cards1)
        hand2 = poker_game._evaluate_hand(cards2)
        
        result = poker_game._compare_hands(hand1, hand2)
        assert result == -1  # straight wins over pair