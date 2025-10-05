import unittest
from main import evaluate_hand
from pydealer import Stack, Card

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
        self.assertEqual(result[1].value, '5')
    
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
        self.assertEqual(result[1].value, '5')  # W wheel, 5 jest najwyższa
    
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
