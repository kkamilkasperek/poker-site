'''
Script realizing logic in single poker room. Uses pydealer module for card deck management.
'''
import asyncio
import itertools

from django.contrib.messages import success
from pydealer import Stack, POKER_RANKS, Deck

RANKS = POKER_RANKS['values']

poker_games = {}

class PokerGame:
    def __init__(self, id, big_blind, max_players=8):
        self.id = id
        self.players = {i: None for i in range(max_players)}
        self.default_chip_count = big_blind * 100
        self.big_blind = big_blind

        # game state
        self.game_state = 'waiting'
        self.deck = None
        self.board_cards = Stack()
        self.pot = 0
        self.current_max_bet = 0
        self.dealer_position = None
        self.current_player_position = None
        self.last_raiser_position = None

        # messsage callbacks
        self.message_callback = None
        self.private_message_callback = None

        # async event for player action
        self.player_action_event = asyncio.Event()
        self.waiting_for_player = False

        self.state_transitions = {
            'waiting': 'pre_flop',
            'pre_flop': 'flop',
            'flop': 'turn',
            'turn': 'river',
            'river': 'showdown',
            'showdown': 'waiting'
        }

        self.state_setup_methods = {
             'waiting': self._setup_waiting,
             'pre_flop': self._setup_pre_flop,
             'flop': self._setup_flop,
             'turn': self._setup_turn,
             'river': self._setup_river,
        #     'showdown': self._setup_showdown
        }

    async def _next_state(self):
        ''' Transition to the next game state. '''
        next_state = self.state_transitions.get(self.game_state)
        self.last_raiser_position = None
        self.current_max_bet = 0
        self.current_player_position = None
        for pos in self.players:
            if self.players[pos]:
                self.players[pos]['current_bet'] = 0
        await self.notify_clear_betting()
        if next_state:
            self._transition_state(next_state)

    def _transition_state(self, new_state):
        ''' Transition to a new game state and set up the state. '''
        self.game_state = new_state
        setup_method = self.state_setup_methods.get(new_state)
        if setup_method:
            asyncio.create_task(setup_method())

    def _setup_waiting(self):
        pass

    async def _setup_pre_flop(self):
        ''' If heads up, dealer is small blind '''
        self.deck = Deck()
        self.board_cards = Stack()
        self.pot = 0
        self.current_max_bet = 0

        self.deck.shuffle()

        active_players = self.get_all_players()
        for pos in active_players:
            player = active_players[pos]
            if player:
                player['active'] = True
        positions = list(active_players.keys())
        dealer_index = positions.index(self.dealer_position)

        if len(positions) == 2:  # heads up
            self.player_bet(self.dealer_position, self.big_blind // 2) # small blind
            next_pos = positions[(dealer_index + 1) % len(positions)]
            self.player_bet(next_pos, self.big_blind) # big blind
            self.current_player_position = self.dealer_position

            # send info to frontend
            await self.notify_bet(self.dealer_position)
            await self.notify_bet(next_pos)
        else: # more than 2 players, standard blinds
            small_blind_pos = positions[(dealer_index + 1) % len(positions)]
            big_blind_pos = positions[(dealer_index + 2) % len(positions)]
            self.player_bet(small_blind_pos, self.big_blind // 2)
            self.player_bet(big_blind_pos, self.big_blind)
            self.current_player_position = positions[(dealer_index + 3) % len(positions)]

            # send info to frontend
            await self.notify_bet(small_blind_pos)
            await self.notify_bet(big_blind_pos)

        dealing_order = positions[dealer_index + 1:] + positions[:dealer_index + 1]
        for pos in dealing_order:
            player = active_players[pos]
            if player:
                player['cards'] = Stack()
                player['cards'].add(self.deck.deal(2))
                await self.notify_dealt_cards(pos, player['cards'], positions)

        state_result = await self._betting_round()
        if state_result == 'next_state':
            await self._next_state()
        elif state_result == 'waiting':
            self._transition_state('waiting')

    async def _setup_flop(self):
        self.board_cards.add(self.deck.deal(3))
        await self.notify_board_cards()
        self.current_player_position = (self.dealer_position + 1) % len(self.players)
        state_result = await self._betting_round()
        if state_result == 'next_state':
            await self._next_state()

    async def _setup_turn(self):
        self.board_cards.add(self.deck.deal(1))
        await self.notify_board_cards()
        self.current_player_position = (self.dealer_position + 1) % len(self.players)
        state_result = await self._betting_round()
        if state_result == 'next_state':
            await self._next_state()

    async def _setup_river(self):
        self.board_cards.add(self.deck.deal(1))
        await self.notify_board_cards()
        self.current_player_position = (self.dealer_position + 1) % len(self.players)
        state_result = await self._betting_round()
        if state_result == 'next_state':
            await self._next_state()


    async def _betting_round(self):
        ''' Conduct a betting round starting from current_player_position '''
        active_players = self.get_all_active_players()
        if len(active_players) <= 1:
            if self.game_state == 'pre_flop':
                return 'waiting'
            else:
                return 'next_state'

        betting_order = self._get_acting_order()
        # TODO: implement betting sequence using generators
        for i, position in enumerate(itertools.cycle(betting_order)):
            if len(self.get_not_folded_players()) <= 1: # remaining player wins
                # TODO: handle win
                return 'next_state'
            if i >= len(betting_order): # completed a full round
                if self.game_state == 'pre_flop' and self.current_max_bet == self.big_blind:
                    break
                if self.last_raiser_position is None or (position == self.last_raiser_position \
                and self.current_max_bet == active_players[position]['current_bet']):
                    break # at least one full round and no new raises
            self.current_player_position = position
            if position in self.get_all_players(): # check if player still in game
                player = active_players.get(position)
                if player and not player['folded'] and not player['all_in']:
                    await self._wait_for_player_action(position)
                else:
                    continue
            else:
                continue
        return 'next_state'



    def _get_acting_order(self):
        ''' In later version should be implemented as generator '''
        active_players = self.get_all_active_players()
        positions = list(active_players.keys())
        if self.current_player_position not in positions:
            next_pos = (self.current_player_position + 1) % len(self.players)
            while next_pos not in positions:
                next_pos = (next_pos + 1) % len(self.players)
            self.current_player_position = next_pos
        return positions[self.current_player_position:] + positions[:self.current_player_position]

    def _evaluate_hand(self, cards):  # input is a Stack class of cards
        def straight_flush(cards):
            suits_counter = {
                "Clubs": 0,
                "Diamonds": 0,
                "Hearts": 0,
                "Spades": 0
            }

            for card in cards:
                suits_counter[card.suit] += 1

            max_suit = max(suits_counter, key=suits_counter.get)
            if suits_counter[max_suit] >= 5:
                suited_cards = sorted([card for card in cards if card.suit == max_suit], reverse=True)
                for i in range(len(suited_cards) - 4):
                    hand = suited_cards[i: i + 5]
                    if hand[0].value == 'Ace' and hand[1].value == '5' and len(hand) == 5:  # wheel
                        return True, hand[1:] + hand[0]
                    if RANKS[hand[0].value] - RANKS[hand[-1].value] == 4 and len(hand) == 5:
                        return True, hand
            return False, None

        def four_of_a_kind(cards):
            rank_counter = {}
            for card in cards:
                rank_counter[card.value] = rank_counter.get(card.value, 0) + 1
            for rank, count in rank_counter.items():
                if count == 4:
                    hand_value = next(card for card in cards if card.value == rank)
                    kicker = max([card for card in cards if card.value != rank])
                    return True, (hand_value, kicker)
            return False, (None, None)

        def full_house(cards):
            three_kind = three_of_a_kind(cards)
            if (three_kind[0]):
                three_card = three_kind[1][0]
                pair_candidates = [card for card in cards if card.value != three_card.value]
                pair_in_rest = pair(pair_candidates)
                if (pair_in_rest[0]):
                    pair_card = pair_in_rest[1][0]
                    return True, (three_card, pair_card)
            return False, (None, None)

        def flush(cards):
            suits_counter = {
                "Clubs": 0,
                "Diamonds": 0,
                "Hearts": 0,
                "Spades": 0
            }

            for card in cards:
                suits_counter[card.suit] += 1

            max_suit = max(suits_counter, key=suits_counter.get)
            if suits_counter[max_suit] >= 5:
                suited_cards = sorted([card for card in cards if card.suit == max_suit], reverse=True)
                return True, suited_cards[:5]
            return False, None

        def straight(cards):
            unique_ranks = Stack()
            for i in range(len(cards)):
                if cards[i].value not in [card.value for card in unique_ranks]:
                    unique_ranks.add(cards[i])
            unique_ranks = sorted(unique_ranks, reverse=True)

            for i in range(len(unique_ranks) - 4):
                hand = unique_ranks[i: i + 5]
                if hand[0].value == 'Ace' and hand[1].value == '5' and len(hand) == 5:
                    return True, hand[1:] + hand[0]
                if RANKS[hand[0].value] - RANKS[hand[-1].value] == 4 and len(hand) == 5:
                    return True, hand
            return False, None

        def three_of_a_kind(cards):
            rank_counter = {
                'Ace': 0,
                'King': 0,
                'Queen': 0,
                'Jack': 0,
                '10': 0,
                '9': 0,
                '8': 0,
                '7': 0,
                '6': 0,
                '5': 0,
                '4': 0,
                '3': 0,
                '2': 0
            }
            for card in cards:
                rank_counter[card.value] = rank_counter.get(card.value, 0) + 1
            for rank, count in rank_counter.items():
                if count == 3:
                    hand_value = next(card for card in cards if card.value == rank)
                    kickers = sorted([card for card in cards if card.value != rank], reverse=True)[:2]
                    return True, (hand_value, kickers)
            return False, (None, None)

        def two_pair(cards):
            one_pair = pair(cards)
            if (one_pair[0]):
                high_pair = one_pair[1][0]
                second_pair = pair(one_pair[1][1])  # check pair in remaining cards
                if (second_pair[0]):
                    low_pair = second_pair[1][0]
                    kicker = second_pair[1][1][0]  # highest remaining card
                    return True, (high_pair, low_pair, kicker)
            return False, (None, None, None)

        def pair(cards):
            rank_counter = {
                'Ace': 0,
                'King': 0,
                'Queen': 0,
                'Jack': 0,
                '10': 0,
                '9': 0,
                '8': 0,
                '7': 0,
                '6': 0,
                '5': 0,
                '4': 0,
                '3': 0,
                '2': 0
            }
            for card in cards:
                rank_counter[card.value] = rank_counter.get(card.value, 0) + 1
            for rank, count in rank_counter.items():
                if count == 2:
                    hand_value = next(card for card in cards if card.value == rank)
                    kickers = sorted([card for card in cards if card.value != rank], reverse=True)[:3]
                    return True, (hand_value, kickers)
            return False, (None, None)

        if len(cards) < 5:
            return None

        is_straight_flush, sf_hand = straight_flush(cards)
        if is_straight_flush:
            return ("straight_flush", sf_hand)

        is_four, four_hand = four_of_a_kind(cards)
        if is_four:
            return ("four_of_kind", four_hand)

        is_full_house, fh_hand = full_house(cards)
        if is_full_house:
            return ("full_house", fh_hand)

        is_flush, flush_hand = flush(cards)
        if is_flush:
            return ("flush", flush_hand)

        is_straight, straight_hand = straight(cards)
        if is_straight:
            return ("straight", straight_hand)

        is_three, three_hand = three_of_a_kind(cards)
        if is_three:
            return ("three_of_kind", three_hand)

        is_two_pair, tp_hand = two_pair(cards)
        if is_two_pair:
            return ("two_pair", tp_hand)

        is_pair, pair_hand = pair(cards)
        if is_pair:
            return ("pair", pair_hand)

        high_cards = sorted(cards, reverse=True)[:5]
        return ("high_card", high_cards)

    def _compare_hands(self, hand1, hand2):
        hand_ranking = {
            "high_card": 1,
            "pair": 2,
            "two_pair": 3,
            "three_of_kind": 4,
            "straight": 5,
            "flush": 6,
            "full_house": 7,
            "four_of_kind": 8,
            "straight_flush": 9
        }

        rank1, cards1 = hand1
        rank2, cards2 = hand2

        if hand_ranking[rank1] > hand_ranking[rank2]:
            return 1
        elif hand_ranking[rank1] < hand_ranking[rank2]:
            return -1
        else:
            # Same rank, compare the cards
            if rank1 in ["straight_flush", "straight", "flush", "high_card"]:  # compare cards in hands
                for i in range(5):
                    if cards1[i].gt(cards2[i], RANKS):
                        return 1
                    elif cards1[i].lt(cards2[i], RANKS):
                        return -1
                return 0  # Tie
            elif rank1 in ["four_of_kind", "full_house"]:  # compare quads first, then kicker
                if cards1[0].gt(cards2[0], RANKS):
                    return 1
                elif cards1[0].lt(cards2[0], RANKS):
                    return -1
                else:
                    if cards1[1].gt(cards2[1], RANKS):
                        return 1
                    elif cards1[1].lt(cards2[1], RANKS):
                        return -1
                    else:
                        return 0
            elif rank1 in ["three_of_kind", "pair"]:  # compare trips/pair first, then kickers
                if cards1[0].gt(cards2[0], RANKS):
                    return 1
                elif cards1[0].lt(cards2[0], RANKS):
                    return -1
                else:
                    for i in range(len(cards1[1])):
                        if cards1[1][i].gt(cards2[1][i], RANKS):
                            return 1
                        elif cards1[1][i].lt(cards2[1][i], RANKS):
                            return -1
                    return 0
            elif rank1 == "two_pair":  # compare high pair, then low pair, then kicker
                if cards1[0].gt(cards2[0], RANKS):
                    return 1
                elif cards1[0].lt(cards2[0], RANKS):
                    return -1
                else:
                    if cards1[1].gt(cards2[1], RANKS):
                        return 1
                    elif cards1[1].lt(cards2[1], RANKS):
                        return -1
                    else:
                        if cards1[2].gt(cards2[2], RANKS):
                            return 1
                        elif cards1[2].lt(cards2[2], RANKS):
                            return -1
                        else:
                            return 0
            return None  # wrong input

    def start_game(self):
        ''' Start a new poker game if there are enough players. Set dealer'''
        active_players = self.get_all_players()
        if len(active_players) >= 2 and self.game_state == 'waiting':
            self.dealer_position = min(active_players) if self.dealer_position is None else \
                (self.dealer_position + 1) % len(self.players)
            self._transition_state("pre_flop")
            return True
        return False

    def add_player(self, player):
        for i in self.players:
            if self.players[i] is None:
                self.players[i] = {
                    'username': player.username,
                    'chip_count': self.default_chip_count,
                    'cards': None,
                    'folded': False,
                    'all_in': False,
                    'current_bet': 0,
                    'active': False, # pending implementation
                }
                return i
        return None  # No available slot

    def remove_player(self, player):
        for i in self.players:
            if self.players[i] is not None and self.players[i]['username'] == player.username:
                if self.current_player_position == i and self.waiting_for_player and not self.player_action_event.is_set():
                    self.waiting_for_player = False
                    self.player_action_event.set()
                self.players[i] = None
                return i
        return None

    def get_player(self, identifier): # get player by username or position
        if isinstance(identifier, str):
            for i in self.players:
                if self.players[i] and self.players[i]['username'] == identifier:
                    return i, self.players[i]
        elif isinstance(identifier, int):
            if identifier in self.players and self.players[identifier]:
                return identifier, self.players[identifier]
        return None, None  # Player not found

    def get_all_players(self):
        return {i: self.players[i] for i in self.players if self.players[i] is not None}

    def get_all_active_players(self):
        return {i: self.players[i] for i in self.players if self.players[i] is not None \
                and not self.players[i]['folded'] and not self.players[i]['all_in'] and self.players[i]['active']}

    def get_not_folded_players(self):
        return {i: self.players[i] for i in self.players if self.players[i] is not None \
                and not self.players[i]['folded'] and self.players[i]['active']}

    def player_bet(self, identifier, amount):
        position, player = self.get_player(identifier)
        if position is not None and not player['folded'] and not player['all_in'] and self.game_state != 'waiting':
            if amount >= player['chip_count']: # all in
                amount = player['chip_count']
                player['all_in'] = True
            if amount + player['current_bet'] >= self.current_max_bet: # call or raise
                diff = amount + player['current_bet'] - self.current_max_bet
                player['chip_count'] -= amount
                player['current_bet'] += amount
                self.pot += amount
                if diff > 0:
                    self.current_max_bet += diff
                    self.last_raiser_position = position
                return amount
            else: # bet is too small
                return False
        return False

    async def _wait_for_player_action(self, position):
        ''' Notify player to act and wait for their action '''
        self.waiting_for_player = True
        self.player_action_event.clear()
        pos, player = self.get_player(position)

        if pos is not None and player:
            await self.notify_player_turn(position)
            await self.broadcast_player_turn(position)
            await self.player_action_event.wait()  # Wait until player acts

    async def player_action(self, identifier, action, amount=0):
        '''check is handled as call with amount 0'''
        position, player = self.get_player(identifier)
        if position is None or player is None:
            return False, "Player not found."
        if position != self.current_player_position:
            return False, "Not your turn."
        if not self.waiting_for_player:
            return False, "Action not expected."
        if player['all_in'] or player['folded']:
            return False, "You cannot act."

        if action == 'fold':
            player['folded'] = True
            await self._send_broadcast_message(
                'player_folded',
                {
                    'position': position,
                }
            )
        elif action == 'call':
            call_amount = self.current_max_bet - player['current_bet']
            bet_am = self.player_bet(identifier, call_amount)
            if bet_am > 0:
                await self.notify_bet(position)
            elif bet_am == 0:
                await self._send_broadcast_message(
                    'player_checked',
                    {
                        'position': position,
                    }
                )
            else:
                return False, "Cannot call."
        elif action == 'raise':
            if amount <= 0:
                return False, "Raise amount must be positive."
            if amount + player['current_bet'] <= self.current_max_bet:
                return False, "Raise must be greater than current max bet."
            bet_am = self.player_bet(identifier, amount)
            if bet_am:
                await self.notify_bet(position)
        else:
            return False, "Invalid action."

        self.waiting_for_player = False
        self.player_action_event.set()
        return True, None
    
    async def notify_clear_betting(self):
        await self._send_broadcast_message(
            'clear_betting',{}
        )

    async def notify_bet(self, identifier):
        position, player = self.get_player(identifier)
        if position is not None:
            await self._send_broadcast_message(
                'player_bet',
                {
                    'position': position,
                    'amount': player['current_bet'],
                    'chip_count': player['chip_count'],
                    'pot': self.pot,
                }
            )

    async def notify_dealt_cards(self, identifier, cards, active_positions):
        position, player = self.get_player(identifier)
        if position is not None:
            await self._send_private_message(
                player['username'],
                'dealt_cards',
                {
                    'cards': [str(card) for card in cards],
                    'active_positions': active_positions,
                }
            )

    async def notify_board_cards(self):
        await self._send_broadcast_message(
            'board_cards',
            {
                'cards': [str(card) for card in self.board_cards],
            }
        )

    async def notify_player_turn(self, identifier):
        position, player = self.get_player(identifier)
        if position is not None:
            await self._send_private_message(
                player['username'],
                'your_turn',
                {
                    'current_bet': self.current_max_bet,
                    'player_bet': player['current_bet'],
                    'chip_count': player['chip_count'],
                    'pot': self.pot,
                }
            )

    async def broadcast_player_turn(self, identifier):
        position, player = self.get_player(identifier)
        if position is not None:
            await self._send_broadcast_message(
                'player_turn',
                {
                    'username': player['username'],
                }
            )


    async def _send_broadcast_message(self, type, message):
        if self.message_callback:
            await self.message_callback(type, message)

    async def _send_private_message(self, username, type, message):
        if self.private_message_callback:
            await self.private_message_callback(username, type, message)