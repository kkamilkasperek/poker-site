import unittest
from pydealer import Stack, Card

from pydealer import Stack, POKER_RANKS

RANKS = POKER_RANKS['values']


def evaluate_hand(cards):  # input is a Stack class of cards
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
                    return True, hand[1:] + [hand[0]]
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
                return True, hand[1:] + [hand[0]]
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
        '''
        rank_counter = {}
        for card in cards:
            rank_counter[card.value] = rank_counter.get(card.value, 0) + 1

        # Find all pairs
        pairs = []
        for rank, count in rank_counter.items():
            if count >= 2:
                pairs.append(rank)

        if len(pairs) >= 2:
            # Sort pairs by rank (highest first)
            pairs_sorted = sorted(pairs, key=lambda x: RANKS[x], reverse=True)

            # Get the two highest pairs
            high_pair_rank = pairs_sorted[0]
            low_pair_rank = pairs_sorted[1]

            # Get card objects for each pair
            high_pair_card = next(card for card in cards if card.value == high_pair_rank)
            low_pair_card = next(card for card in cards if card.value == low_pair_rank)

            # Find the highest kicker (card that's not part of the two pairs)
            kickers = sorted([card for card in cards if card.value not in [high_pair_rank, low_pair_rank]], reverse=True)
            kicker = kickers[0] if kickers else None

            return True, (high_pair_card, low_pair_card, kicker)
        return False, (None, None, None)
        '''

        one_pair = pair(cards)
        if (one_pair[0]):
            high_pair = one_pair[1][0]
            hand_without_first_pair = [card for card in cards if card.value != high_pair.value]
            second_pair = pair(hand_without_first_pair)  # check pair in remaining cards
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

class TestEvaluateHand(unittest.TestCase):
    
    def test_high_card(self):
        """Test dla wysokiej karty"""
        cards = Stack()
        cards.add([
            Card('2', 'Hearts'),
            Card('7', 'Diamonds'), 
            Card('9', 'Clubs'),
            Card('Jack', 'Spades'),
            Card('King', 'Hearts')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "high_card")
        # Sprawdź, czy najwyższą kartą jest król
        self.assertEqual(result[1][0].value, 'King')
    
    def test_pair(self):
        """Test dla pary"""
        cards = Stack()
        cards.add([
            Card('8', 'Hearts'),
            Card('8', 'Diamonds'),
            Card('3', 'Clubs'),
            Card('Jack', 'Spades'),
            Card('King', 'Hearts')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "pair")
        self.assertEqual(result[1][0].value, '8')
    
    def test_two_pair(self):
        """Test dla dwóch par"""
        cards = Stack()
        cards.add([
            Card('8', 'Hearts'),
            Card('8', 'Diamonds'),
            Card('3', 'Clubs'),
            Card('3', 'Spades'),
            Card('King', 'Hearts')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "two_pair")
        # Sprawdź wyższą parę
        self.assertEqual(result[1][0].value, '8')

    def test_two_pair_low_pairs_second(self):
        """Test dla dwóch par z niskimi kartami"""
        cards = Stack()
        cards.add([
            Card("5", "Hearts"),
            Card("5", "Diamonds"),
            Card("Ace", "Clubs"),
            Card("3", "Clubs"),
            Card("3", "Spades"),
            Card("7", "Hearts"),
            Card("Jack", "Hearts")
        ])

        result = evaluate_hand(cards)
        self.assertEqual(result[0], "two_pair")
        self.assertEqual(result[1][0].value, '5')  # wyższa para
        self.assertEqual(result[1][1].value, '3')  # niższa para
        self.assertEqual(result[1][2].value, 'Ace')  # kicker
    
    def test_two_pair_with_ace_high(self):
        """Test dla dwóch par z asem jako wyższą parą"""
        cards = Stack()
        cards.add([
            Card('Ace', 'Hearts'),
            Card('Ace', 'Diamonds'),
            Card('King', 'Clubs'),
            Card('King', 'Spades'),
            Card('Queen', 'Hearts')
        ])

        result = evaluate_hand(cards)
        self.assertEqual(result[0], "two_pair")
        self.assertEqual(result[1][0].value, 'Ace')  # wyższa para
        self.assertEqual(result[1][1].value, 'King')  # niższa para
        self.assertEqual(result[1][2].value, 'Queen')  # kicker

    def test_two_pair_with_low_kicker(self):
        """Test dla dwóch par z niskim kickerem"""
        cards = Stack()
        cards.add([
            Card('Jack', 'Hearts'),
            Card('Jack', 'Diamonds'),
            Card('9', 'Clubs'),
            Card('9', 'Spades'),
            Card('2', 'Hearts')
        ])

        result = evaluate_hand(cards)
        self.assertEqual(result[0], "two_pair")
        self.assertEqual(result[1][0].value, 'Jack')  # wyższa para
        self.assertEqual(result[1][1].value, '9')  # niższa para
        self.assertEqual(result[1][2].value, '2')  # kicker

    def test_two_pair_from_seven_cards(self):
        """Test dla dwóch par z 7 kart (Texas Hold'em scenario)"""
        cards = Stack()
        cards.add([
            Card('Ace', 'Hearts'),
            Card('Ace', 'Diamonds'),
            Card('King', 'Clubs'),
            Card('King', 'Spades'),
            Card('Queen', 'Hearts'),
            Card('7', 'Diamonds'),
            Card('2', 'Clubs')
        ])

        result = evaluate_hand(cards)
        self.assertEqual(result[0], "two_pair")
        self.assertEqual(result[1][0].value, 'Ace')  # wyższa para
        self.assertEqual(result[1][1].value, 'King')  # niższa para
        self.assertEqual(result[1][2].value, 'Queen')  # najwyższy kicker

    def test_two_pair_with_three_pairs(self):
        """Test dla trzech par - powinno wybrać dwie najwyższe"""
        cards = Stack()
        cards.add([
            Card('Ace', 'Hearts'),
            Card('Ace', 'Diamonds'),
            Card('King', 'Clubs'),
            Card('King', 'Spades'),
            Card('Queen', 'Hearts'),
            Card('Queen', 'Diamonds'),
            Card('5', 'Clubs')
        ])

        result = evaluate_hand(cards)
        self.assertEqual(result[0], "two_pair")
        self.assertEqual(result[1][0].value, 'Ace')  # wyższa para
        self.assertEqual(result[1][1].value, 'King')  # niższa para (nie Queen!)
        self.assertEqual(result[1][2].value, 'Queen')  # kicker

    def test_two_pair_low_pairs(self):
        """Test dla dwóch niskich par"""
        cards = Stack()
        cards.add([
            Card('5', 'Hearts'),
            Card('5', 'Diamonds'),
            Card('3', 'Clubs'),
            Card('3', 'Spades'),
            Card('Ace', 'Hearts')
        ])

        result = evaluate_hand(cards)
        self.assertEqual(result[0], "two_pair")
        self.assertEqual(result[1][0].value, '5')  # wyższa para
        self.assertEqual(result[1][1].value, '3')  # niższa para
        self.assertEqual(result[1][2].value, 'Ace')  # kicker

    def test_two_pair_vs_three_of_kind(self):
        """Test że trójka jest lepsze niż dwie pary"""
        cards = Stack()
        cards.add([
            Card('8', 'Hearts'),
            Card('8', 'Diamonds'),
            Card('8', 'Clubs'),
            Card('3', 'Spades'),
            Card('King', 'Hearts')
        ])

        result = evaluate_hand(cards)
        # Powinno wykryć trójkę, nie dwie pary
        self.assertEqual(result[0], "three_of_kind")
        self.assertEqual(result[1][0].value, '8')

    def test_three_of_kind(self):
        """Test dla trójki"""
        cards = Stack()
        cards.add([
            Card('Queen', 'Hearts'),
            Card('Queen', 'Diamonds'),
            Card('Queen', 'Clubs'),
            Card('5', 'Spades'),
            Card('King', 'Hearts')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "three_of_kind")
        self.assertEqual(result[1][0].value, 'Queen')
    
    def test_straight(self):
        """Test dla strita"""
        cards = Stack()
        cards.add([
            Card('5', 'Hearts'),
            Card('6', 'Diamonds'),
            Card('7', 'Clubs'),
            Card('8', 'Spades'),
            Card('9', 'Hearts')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "straight")
        # Sprawdź najwyższą kartę w stricie
        self.assertEqual(result[1][0].value, '9')
    
    def test_straight_ace_low(self):
        """Test dla strita Ace-2-3-4-5 (wheel)"""
        cards = Stack()
        cards.add([
            Card('Ace', 'Hearts'),
            Card('2', 'Diamonds'),
            Card('3', 'Clubs'),
            Card('4', 'Spades'),
            Card('5', 'Hearts')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "straight")
        # W przypadku wheel, najwyższą kartą jest 5
        self.assertEqual(result[1][0].value, '5')
        self.assertEqual(result[1][-1].value, 'Ace')
    
    def test_flush(self):
        """Test dla koloru"""
        cards = Stack()
        cards.add([
            Card('2', 'Hearts'),
            Card('7', 'Hearts'),
            Card('9', 'Hearts'),
            Card('Jack', 'Hearts'),
            Card('King', 'Hearts')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "flush")
        # Sprawdź, czy wszystkie karty mają ten sam kolor
        self.assertTrue(all(card.suit == 'Hearts' for card in result[1]))
    
    def test_full_house(self):
        """Test dla full house"""
        cards = Stack()
        cards.add([
            Card('Queen', 'Hearts'),
            Card('Queen', 'Diamonds'),
            Card('Queen', 'Clubs'),
            Card('5', 'Spades'),
            Card('5', 'Hearts')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "full_house")
        self.assertEqual(result[1][0].value, 'Queen')  # trójka
        self.assertEqual(result[1][1].value, '5')  # para
    
    def test_four_of_kind(self):
        """Test dla kareta"""
        cards = Stack()
        cards.add([
            Card('Ace', 'Hearts'),
            Card('Ace', 'Diamonds'),
            Card('Ace', 'Clubs'),
            Card('Ace', 'Spades'),
            Card('King', 'Hearts')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "four_of_kind")
        self.assertEqual(result[1][0].value, 'Ace')
    
    def test_straight_flush(self):
        """Test dla poker (straight flush)"""
        cards = Stack()
        cards.add([
            Card('5', 'Hearts'),
            Card('6', 'Hearts'),
            Card('7', 'Hearts'),
            Card('8', 'Hearts'),
            Card('9', 'Hearts')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "straight_flush")
        # Sprawdź najwyższą kartę
        self.assertEqual(result[1][0].value, '9')
    
    def test_royal_flush(self):
        """Test dla pokera królewskiego (royal flush)"""
        cards = Stack()
        cards.add([
            Card('10', 'Spades'),
            Card('Jack', 'Spades'),
            Card('Queen', 'Spades'),
            Card('King', 'Spades'),
            Card('Ace', 'Spades')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "straight_flush")
        self.assertEqual(result[1][0].value, 'Ace')
    
    def test_wheel_straight_flush(self):
        """Test dla straight flush Ace-2-3-4-5"""
        cards = Stack()
        cards.add([
            Card('Ace', 'Hearts'),
            Card('2', 'Hearts'),
            Card('3', 'Hearts'),
            Card('4', 'Hearts'),
            Card('5', 'Hearts')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "straight_flush")
        self.assertEqual(result[1][0].value, '5')  # W wheel, 5 jest najwyższa
        self.assertEqual(result[1][-1].value, 'Ace')
    
    def test_too_few_cards(self):
        """Test dla zbyt małej liczby kart (mniej niż 5)"""
        cards = Stack()
        cards.add([
            Card('Ace', 'Hearts'),
            Card('King', 'Diamonds'),
            Card('Queen', 'Clubs'),
            Card('Jack', 'Spades')
        ])
        
        result = evaluate_hand(cards)
        self.assertIsNone(result)
    
    def test_more_than_five_cards(self):
        """Test dla więcej niż 5 kart - powinien wybrać najlepsze 5"""
        cards = Stack()
        cards.add([
            Card('Ace', 'Hearts'),
            Card('Ace', 'Diamonds'),
            Card('2', 'Clubs'),
            Card('3', 'Spades'),
            Card('4', 'Hearts'),
            Card('5', 'Clubs'),
            Card('6', 'Diamonds')
        ])
        
        result = evaluate_hand(cards)
        self.assertEqual(result[0], "straight")
        self.assertEqual(result[1][0].value, '6')

if __name__ == '__main__':
    unittest.main()
