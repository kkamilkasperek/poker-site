import unittest
from main import compare_hands
from pydealer import Card

class TestCompareHands(unittest.TestCase):
    
    def test_different_ranks_higher_wins(self):
        """Test porównania różnych układów - wyższy wygrywa"""
        # Straight flush vs Four of a kind
        hand1 = ("straight_flush", [Card('9', 'Hearts'), Card('8', 'Hearts'), Card('7', 'Hearts'), Card('6', 'Hearts'), Card('5', 'Hearts')])
        hand2 = ("four_of_kind", (Card('Ace', 'Hearts'), Card('King', 'Spades')))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Full house vs Flush
        hand1 = ("full_house", (Card('Queen', 'Hearts'), Card('5', 'Spades')))
        hand2 = ("flush", [Card('King', 'Hearts'), Card('Jack', 'Hearts'), Card('9', 'Hearts'), Card('7', 'Hearts'), Card('2', 'Hearts')])
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Pair vs High card
        hand1 = ("pair", (Card('8', 'Hearts'), [Card('King', 'Spades'), Card('Jack', 'Diamonds'), Card('3', 'Clubs')]))
        hand2 = ("high_card", [Card('Ace', 'Spades'), Card('Queen', 'Hearts'), Card('Jack', 'Clubs'), Card('9', 'Diamonds'), Card('7', 'Hearts')])
        self.assertEqual(compare_hands(hand1, hand2), 1)
    
    def test_different_ranks_lower_loses(self):
        """Test porównania różnych układów - niższy przegrywa"""
        # High card vs Pair
        hand1 = ("high_card", [Card('Ace', 'Spades'), Card('Queen', 'Hearts'), Card('Jack', 'Clubs'), Card('9', 'Diamonds'), Card('7', 'Hearts')])
        hand2 = ("pair", (Card('2', 'Hearts'), [Card('King', 'Spades'), Card('Jack', 'Diamonds'), Card('3', 'Clubs')]))
        self.assertEqual(compare_hands(hand1, hand2), -1)
        
        # Three of kind vs Straight
        hand1 = ("three_of_kind", (Card('Ace', 'Hearts'), [Card('King', 'Spades'), Card('Queen', 'Diamonds')]))
        hand2 = ("straight", [Card('9', 'Hearts'), Card('8', 'Diamonds'), Card('7', 'Clubs'), Card('6', 'Spades'), Card('5', 'Hearts')])
        self.assertEqual(compare_hands(hand1, hand2), -1)
    
    def test_high_card_comparison(self):
        """Test porównania wysokich kart"""
        # Wyższa najwyższa karta
        hand1 = ("high_card", [Card('Ace', 'Spades'), Card('Queen', 'Hearts'), Card('Jack', 'Clubs'), Card('9', 'Diamonds'), Card('7', 'Hearts')])
        hand2 = ("high_card", [Card('King', 'Spades'), Card('Queen', 'Diamonds'), Card('Jack', 'Hearts'), Card('9', 'Clubs'), Card('7', 'Spades')])
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Ta sama najwyższa, wyższa druga
        hand1 = ("high_card", [Card('Ace', 'Spades'), Card('King', 'Hearts'), Card('Jack', 'Clubs'), Card('9', 'Diamonds'), Card('7', 'Hearts')])
        hand2 = ("high_card", [Card('Ace', 'Diamonds'), Card('Queen', 'Hearts'), Card('Jack', 'Spades'), Card('9', 'Clubs'), Card('7', 'Diamonds')])
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Identyczne karty - remis
        hand1 = ("high_card", [Card('Ace', 'Spades'), Card('King', 'Hearts'), Card('Queen', 'Clubs'), Card('Jack', 'Diamonds'), Card('9', 'Hearts')])
        hand2 = ("high_card", [Card('Ace', 'Diamonds'), Card('King', 'Spades'), Card('Queen', 'Hearts'), Card('Jack', 'Clubs'), Card('9', 'Diamonds')])
        self.assertEqual(compare_hands(hand1, hand2), 0)
    
    def test_pair_comparison(self):
        """Test porównania par"""
        # Wyższa para
        hand1 = ("pair", (Card('King', 'Hearts'), [Card('Queen', 'Spades'), Card('Jack', 'Diamonds'), Card('9', 'Clubs')]))
        hand2 = ("pair", (Card('Queen', 'Hearts'), [Card('King', 'Spades'), Card('Jack', 'Hearts'), Card('9', 'Diamonds')]))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Ta sama para, wyższy kicker
        hand1 = ("pair", (Card('8', 'Hearts'), [Card('Ace', 'Spades'), Card('Jack', 'Diamonds'), Card('9', 'Clubs')]))
        hand2 = ("pair", (Card('8', 'Diamonds'), [Card('King', 'Spades'), Card('Jack', 'Hearts'), Card('9', 'Hearts')]))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Ta sama para i pierwszy kicker, wyższy drugi kicker
        hand1 = ("pair", (Card('8', 'Hearts'), [Card('Ace', 'Spades'), Card('Queen', 'Diamonds'), Card('9', 'Clubs')]))
        hand2 = ("pair", (Card('8', 'Diamonds'), [Card('Ace', 'Hearts'), Card('Jack', 'Hearts'), Card('9', 'Hearts')]))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Identyczne pary i kickery - remis
        hand1 = ("pair", (Card('8', 'Hearts'), [Card('Ace', 'Spades'), Card('King', 'Diamonds'), Card('Queen', 'Clubs')]))
        hand2 = ("pair", (Card('8', 'Diamonds'), [Card('Ace', 'Hearts'), Card('King', 'Hearts'), Card('Queen', 'Hearts')]))
        self.assertEqual(compare_hands(hand1, hand2), 0)
    
    def test_two_pair_comparison(self):
        """Test porównania dwóch par"""
        # Wyższa para
        hand1 = ("two_pair", (Card('King', 'Hearts'), Card('8', 'Diamonds'), Card('5', 'Clubs')))
        hand2 = ("two_pair", (Card('Queen', 'Hearts'), Card('Jack', 'Diamonds'), Card('Ace', 'Clubs')))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Ta sama wysoka para, wyższa niska para
        hand1 = ("two_pair", (Card('King', 'Hearts'), Card('9', 'Diamonds'), Card('5', 'Clubs')))
        hand2 = ("two_pair", (Card('King', 'Diamonds'), Card('8', 'Hearts'), Card('Ace', 'Clubs')))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Te same pary, wyższy kicker
        hand1 = ("two_pair", (Card('King', 'Hearts'), Card('8', 'Diamonds'), Card('Queen', 'Clubs')))
        hand2 = ("two_pair", (Card('King', 'Diamonds'), Card('8', 'Hearts'), Card('Jack', 'Clubs')))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Identyczne dwójki par - remis
        hand1 = ("two_pair", (Card('King', 'Hearts'), Card('8', 'Diamonds'), Card('Queen', 'Clubs')))
        hand2 = ("two_pair", (Card('King', 'Diamonds'), Card('8', 'Hearts'), Card('Queen', 'Hearts')))
        self.assertEqual(compare_hands(hand1, hand2), 0)
    
    def test_three_of_kind_comparison(self):
        """Test porównania trójek"""
        # Wyższa trójka
        hand1 = ("three_of_kind", (Card('Queen', 'Hearts'), [Card('King', 'Spades'), Card('Jack', 'Diamonds')]))
        hand2 = ("three_of_kind", (Card('Jack', 'Hearts'), [Card('Ace', 'Spades'), Card('King', 'Diamonds')]))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Ta sama trójka, wyższy kicker
        hand1 = ("three_of_kind", (Card('8', 'Hearts'), [Card('Ace', 'Spades'), Card('King', 'Diamonds')]))
        hand2 = ("three_of_kind", (Card('8', 'Diamonds'), [Card('Queen', 'Spades'), Card('Jack', 'Hearts')]))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Identyczne trójki i kickery - remis
        hand1 = ("three_of_kind", (Card('8', 'Hearts'), [Card('Ace', 'Spades'), Card('King', 'Diamonds')]))
        hand2 = ("three_of_kind", (Card('8', 'Diamonds'), [Card('Ace', 'Hearts'), Card('King', 'Hearts')]))
        self.assertEqual(compare_hands(hand1, hand2), 0)
    
    def test_straight_comparison(self):
        """Test porównania stritów"""
        # Wyższy strit
        hand1 = ("straight", [Card('10', 'Hearts'), Card('9', 'Diamonds'), Card('8', 'Clubs'), Card('7', 'Spades'), Card('6', 'Hearts')])
        hand2 = ("straight", [Card('9', 'Hearts'), Card('8', 'Diamonds'), Card('7', 'Clubs'), Card('6', 'Spades'), Card('5', 'Hearts')])
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Identyczne strity - remis
        hand1 = ("straight", [Card('9', 'Hearts'), Card('8', 'Diamonds'), Card('7', 'Clubs'), Card('6', 'Spades'), Card('5', 'Hearts')])
        hand2 = ("straight", [Card('9', 'Diamonds'), Card('8', 'Hearts'), Card('7', 'Hearts'), Card('6', 'Clubs'), Card('5', 'Diamonds')])
        self.assertEqual(compare_hands(hand1, hand2), 0)
    
    def test_flush_comparison(self):
        """Test porównania kolorów"""
        # Wyższy kolor
        hand1 = ("flush", [Card('Ace', 'Hearts'), Card('King', 'Hearts'), Card('9', 'Hearts'), Card('7', 'Hearts'), Card('5', 'Hearts')])
        hand2 = ("flush", [Card('King', 'Spades'), Card('Queen', 'Spades'), Card('Jack', 'Spades'), Card('10', 'Spades'), Card('9', 'Spades')])
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Ta sama najwyższa karta, wyższa druga
        hand1 = ("flush", [Card('Ace', 'Hearts'), Card('Queen', 'Hearts'), Card('9', 'Hearts'), Card('7', 'Hearts'), Card('5', 'Hearts')])
        hand2 = ("flush", [Card('Ace', 'Spades'), Card('Jack', 'Spades'), Card('10', 'Spades'), Card('8', 'Spades'), Card('6', 'Spades')])
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Identyczne kolory - remis
        hand1 = ("flush", [Card('Ace', 'Hearts'), Card('King', 'Hearts'), Card('Queen', 'Hearts'), Card('Jack', 'Hearts'), Card('9', 'Hearts')])
        hand2 = ("flush", [Card('Ace', 'Spades'), Card('King', 'Spades'), Card('Queen', 'Spades'), Card('Jack', 'Spades'), Card('9', 'Spades')])
        self.assertEqual(compare_hands(hand1, hand2), 0)
    
    def test_full_house_comparison(self):
        """Test porównania full house"""
        # Wyższa trójka
        hand1 = ("full_house", (Card('King', 'Hearts'), Card('8', 'Spades')))
        hand2 = ("full_house", (Card('Queen', 'Hearts'), Card('Ace', 'Spades')))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Ta sama trójka, wyższa para
        hand1 = ("full_house", (Card('8', 'Hearts'), Card('King', 'Spades')))
        hand2 = ("full_house", (Card('8', 'Diamonds'), Card('Queen', 'Hearts')))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Identyczne full house - remis
        hand1 = ("full_house", (Card('8', 'Hearts'), Card('King', 'Spades')))
        hand2 = ("full_house", (Card('8', 'Diamonds'), Card('King', 'Hearts')))
        self.assertEqual(compare_hands(hand1, hand2), 0)
    
    def test_four_of_kind_comparison(self):
        """Test porównania karetów"""
        # Wyższy karet
        hand1 = ("four_of_kind", (Card('Ace', 'Hearts'), Card('King', 'Spades')))
        hand2 = ("four_of_kind", (Card('King', 'Hearts'), Card('Ace', 'Spades')))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Ten sam karet, wyższy kicker
        hand1 = ("four_of_kind", (Card('8', 'Hearts'), Card('Ace', 'Spades')))
        hand2 = ("four_of_kind", (Card('8', 'Diamonds'), Card('King', 'Hearts')))
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Identyczne karety - remis
        hand1 = ("four_of_kind", (Card('8', 'Hearts'), Card('King', 'Spades')))
        hand2 = ("four_of_kind", (Card('8', 'Diamonds'), Card('King', 'Hearts')))
        self.assertEqual(compare_hands(hand1, hand2), 0)
    
    def test_straight_flush_comparison(self):
        """Test porównania pokerów"""
        # Wyższy poker
        hand1 = ("straight_flush", [Card('10', 'Hearts'), Card('9', 'Hearts'), Card('8', 'Hearts'), Card('7', 'Hearts'), Card('6', 'Hearts')])
        hand2 = ("straight_flush", [Card('9', 'Spades'), Card('8', 'Spades'), Card('7', 'Spades'), Card('6', 'Spades'), Card('5', 'Spades')])
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Identyczne pokery - remis
        hand1 = ("straight_flush", [Card('9', 'Hearts'), Card('8', 'Hearts'), Card('7', 'Hearts'), Card('6', 'Hearts'), Card('5', 'Hearts')])
        hand2 = ("straight_flush", [Card('9', 'Spades'), Card('8', 'Spades'), Card('7', 'Spades'), Card('6', 'Spades'), Card('5', 'Spades')])
        self.assertEqual(compare_hands(hand1, hand2), 0)
        
        # Royal flush vs zwykły straight flush
        hand1 = ("straight_flush", [Card('Ace', 'Hearts'), Card('King', 'Hearts'), Card('Queen', 'Hearts'), Card('Jack', 'Hearts'), Card('10', 'Hearts')])
        hand2 = ("straight_flush", [Card('King', 'Spades'), Card('Queen', 'Spades'), Card('Jack', 'Spades'), Card('10', 'Spades'), Card('9', 'Spades')])
        self.assertEqual(compare_hands(hand1, hand2), 1)
    
    def test_wheel_comparisons(self):
        """Test porównania układów z wheel (A-2-3-4-5)"""
        # Wheel straight vs wyższy straight
        hand1 = ("straight", [Card('9', 'Hearts'), Card('8', 'Diamonds'), Card('7', 'Clubs'), Card('6', 'Spades'), Card('5', 'Hearts')])
        hand2 = ("straight", [Card('5', 'Hearts'), Card('4', 'Diamonds'), Card('3', 'Clubs'), Card('2', 'Spades'), Card('Ace', 'Hearts')])
        self.assertEqual(compare_hands(hand1, hand2), 1)
        
        # Wheel straight flush vs wyższy straight flush
        hand1 = ("straight_flush", [Card('9', 'Hearts'), Card('8', 'Hearts'), Card('7', 'Hearts'), Card('6', 'Hearts'), Card('5', 'Hearts')])
        hand2 = ("straight_flush", [Card('5', 'Spades'), Card('4', 'Spades'), Card('3', 'Spades'), Card('2', 'Spades'), Card('Ace', 'Spades')])
        self.assertEqual(compare_hands(hand1, hand2), 1)
    
    def test_edge_cases(self):
        """Test przypadków brzegowych"""
        # Test z identycznymi układami różnych kolorów
        hand1 = ("pair", (Card('Ace', 'Hearts'), [Card('King', 'Spades'), Card('Queen', 'Diamonds'), Card('Jack', 'Clubs')]))
        hand2 = ("pair", (Card('Ace', 'Diamonds'), [Card('King', 'Hearts'), Card('Queen', 'Clubs'), Card('Jack', 'Hearts')]))
        self.assertEqual(compare_hands(hand1, hand2), 0)

if __name__ == '__main__':
    unittest.main()
