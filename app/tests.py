from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages

from app.models import PokerRoom, Player


class LoginUserTest(TestCase):
    def setUp(self):
        """Przygotowanie danych testowych przed każdym testem"""
        self.client = Client()
        self.login_url = reverse('login')
        self.index_url = reverse('index')
        
        # Tworzenie testowego użytkownika
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
    def test_login_page_GET(self):
        """Test dostępu do strony logowania metodą GET"""
        response = self.client.get(self.login_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_register.html')
        self.assertEqual(response.context['type'], 'login')
        
    def test_login_with_username_success(self):
        """Test poprawnego logowania przy użyciu nazwy użytkownika"""
        response = self.client.post(self.login_url, {
            'username_or_email': 'testuser',
            'password': 'testpassword123'
        }, follow=True)
        
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, self.index_url)
        
    def test_login_with_email_success(self):
        """Test poprawnego logowania przy użyciu adresu email"""
        response = self.client.post(self.login_url, {
            'username_or_email': 'test@example.com',
            'password': 'testpassword123'
        }, follow=True)
        
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, self.index_url)
        
    def test_login_with_invalid_username(self):
        """Test nieudanego logowania przy użyciu błędnej nazwy użytkownika"""
        response = self.client.post(self.login_url, {
            'username_or_email': 'nonexistentuser',
            'password': 'testpassword123'
        })
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nieprawidłowa nazwa użytkownika lub e-mail')
        self.assertFalse(response.context['user'].is_authenticated)
        
    def test_login_with_invalid_email(self):
        """Test nieudanego logowania przy użyciu błędnego adresu email"""
        response = self.client.post(self.login_url, {
            'username_or_email': 'nonexistent@example.com',
            'password': 'testpassword123'
        })
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nieprawidłowa nazwa użytkownika lub e-mail')
        self.assertFalse(response.context['user'].is_authenticated)
        
    def test_login_with_incorrect_password(self):
        """Test nieudanego logowania przy użyciu błędnego hasła"""
        response = self.client.post(self.login_url, {
            'username_or_email': 'testuser',
            'password': 'wrongpassword'
        })
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nieprawidłowe hasło')
        self.assertFalse(response.context['user'].is_authenticated)


class RegisterUserTest(TestCase):
    def setUp(self):
        """Przygotowanie danych testowych przed każdym testem"""
        self.client = Client()
        self.register_url = reverse('register')
        self.index_url = reverse('index')

        # Tworzenie testowego użytkownika, aby sprawdzić zduplikowany email
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

    def test_register_page_GET(self):
        """Test dostępu do strony rejestracji metodą GET"""
        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_register.html')
        self.assertEqual(response.context['type'], 'register')
        self.assertTrue('form' in response.context)

    def test_register_user_success(self):
        """Test poprawnej rejestracji użytkownika"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123'
        }, follow=True)

        # Sprawdzenie, czy użytkownik został utworzony
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # Sprawdzenie, czy użytkownik jest zalogowany
        self.assertTrue(response.context['user'].is_authenticated)
        # Sprawdzenie przekierowania na stronę główną
        self.assertRedirects(response, self.index_url)

    def test_register_with_duplicate_username(self):
        """Test rejestracji z istniejącą nazwą użytkownika"""
        response = self.client.post(self.register_url, {
            'username': 'testuser',  # już istniejący użytkownik
            'email': 'different@example.com',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123'
        })

        # Sprawdzenie, czy formularz ma błędy
        self.assertTrue(response.context['form'].errors)
        # Sprawdzenie, czy użytkownik nie jest zalogowany
        self.assertFalse(response.context['user'].is_authenticated)

    def test_register_with_duplicate_email(self):
        """Test rejestracji z istniejącym adresem email"""
        response = self.client.post(self.register_url, {
            'username': 'newuser2',
            'email': 'test@example.com',  # już istniejący email
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123'
        })

        # Sprawdzenie, czy formularz ma błędy
        self.assertTrue(response.context['form'].errors)
        # Sprawdzenie, czy użytkownik nie jest zalogowany
        self.assertFalse(response.context['user'].is_authenticated)

    def test_register_with_password_mismatch(self):
        """Test rejestracji z różnymi hasłami"""
        response = self.client.post(self.register_url, {
            'username': 'newuser3',
            'email': 'newuser3@example.com',
            'password1': 'ComplexPass123',
            'password2': 'DifferentPass123'
        })

        # Sprawdzenie, czy formularz ma błędy
        self.assertTrue(response.context['form'].errors)
        # Sprawdzenie, czy użytkownik nie jest zalogowany
        self.assertFalse(response.context['user'].is_authenticated)

    def test_register_with_weak_password(self):
        """Test rejestracji ze słabym hasłem"""
        response = self.client.post(self.register_url, {
            'username': 'newuser4',
            'email': 'newuser4@example.com',
            'password1': 'password',  # zbyt proste hasło
            'password2': 'password'
        })

        # Sprawdzenie, czy formularz ma błędy
        self.assertTrue(response.context['form'].errors)
        # Sprawdzenie, czy użytkownik nie jest zalogowany
        self.assertFalse(response.context['user'].is_authenticated)


class RoomsViewTest(TestCase):
    def setUp(self):
        """Przygotowanie danych testowych przed każdym testem"""
        self.client = Client()
        self.rooms_url = reverse('rooms')

        # Tworzenie testowych użytkowników
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123'
        )

        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123'
        )

        # Tworzenie testowych pokojów
        self.room1 = PokerRoom.objects.create(
            name='Poker Room 1',
            host=self.user1,
            max_players=8,
            is_private=False
        )

        self.room2 = PokerRoom.objects.create(
            name='Poker Room 2',
            host=self.user2,
            max_players=6,
            is_private=True
        )

        # Tworzenie relacji gracz-pokój
        Player.objects.create(
            user=self.user1,
            room=self.room1,
            is_participant=True
        )

        Player.objects.create(
            user=self.user2,
            room=self.room1,
            is_participant=False
        )

    def test_rooms_page_GET(self):
        """Test dostępu do strony pokojów metodą GET"""
        response = self.client.get(self.rooms_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/rooms.html')
        self.assertQuerySetEqual(
            response.context['rooms'],
            PokerRoom.objects.all(),
            transform=lambda x: x,
            ordered=False
        )
        self.assertIsNone(response.context['selected_room'])

    def test_rooms_with_query_filter(self):
        """Test filtrowania pokojów za pomocą parametru query"""
        response = self.client.get(f'{self.rooms_url}?query=Room 1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rooms']), 1)
        self.assertEqual(response.context['rooms'][0], self.room1)
        self.assertEqual(response.context['query'], 'Room 1')

    def test_rooms_filter_by_host(self):
        """Test filtrowania pokojów po nazwie hosta"""
        response = self.client.get(f'{self.rooms_url}?query=user1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rooms']), 1)
        self.assertEqual(response.context['rooms'][0], self.room1)

    def test_rooms_with_selected_room(self):
        """Test wyświetlania szczegółów wybranego pokoju"""
        response = self.client.get(f'{self.rooms_url}?id={self.room1.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_room'], self.room1)
        self.assertFalse(response.context['is_participant'])

    def test_rooms_with_participant_status(self):
        """Test sprawdzania statusu uczestnika dla zalogowanego użytkownika"""
        # Logowanie użytkownika
        self.client.login(username='user1', password='password123')

        response = self.client.get(f'{self.rooms_url}?id={self.room1.id}')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_participant'])

    def test_rooms_with_spectator_status(self):
        """Test sprawdzania statusu widza (nie uczestnika) dla zalogowanego użytkownika"""
        # Logowanie użytkownika
        self.client.login(username='user2', password='password123')

        response = self.client.get(f'{self.rooms_url}?id={self.room1.id}')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_participant'])

    def test_rooms_with_invalid_room_id(self):
        """Test obsługi nieprawidłowego ID pokoju"""
        response = self.client.get(f'{self.rooms_url}?id=999')

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['selected_room'])
        self.assertIsNone(response.context['is_participant'])

    def test_rooms_with_query_and_selected_room(self):
        """Test połączenia filtrowania i wybranego pokoju"""
        response = self.client.get(f'{self.rooms_url}?query=Room&id={self.room2.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rooms']), 2)  # Oba pokoje zawierają 'Room'
        self.assertEqual(response.context['selected_room'], self.room2)

    def test_anonymous_user_participant_status(self):
        """Test statusu uczestnika dla niezalogowanego użytkownika"""
        response = self.client.get(f'{self.rooms_url}?id={self.room1.id}')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_participant'])

    def test_anonymous_user_can_view_public_rooms(self):
        """Test dostępu do publicznych pokojów dla niezalogowanego użytkownika"""
        response = self.client.get(self.rooms_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Poker Room 1')  # publiczny pokój powinien być widoczny

    def test_anonymous_user_can_view_private_rooms(self):
        """Test dostępu do prywatnych pokojów dla niezalogowanego użytkownika"""
        response = self.client.get(self.rooms_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Poker Room 2')  # prywatny pokój też powinien być widoczny w liście

    def test_anonymous_user_room_details(self):
        """Test wyświetlania szczegółów pokoju dla niezalogowanego użytkownika"""
        response = self.client.get(f'{self.rooms_url}?id={self.room1.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_room'], self.room1)
        self.assertIsNotNone(response.context['selected_room'])
        self.assertFalse(response.context['is_participant'])

    def test_anonymous_user_private_room_details(self):
        """Test wyświetlania szczegółów prywatnego pokoju dla niezalogowanego użytkownika"""
        response = self.client.get(f'{self.rooms_url}?id={self.room2.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_room'], self.room2)
        self.assertTrue(response.context['selected_room'].is_private)  # Sprawdzenie czy pokój jest prywatny
        self.assertFalse(response.context['is_participant'])


class CreateRoomTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.create_room_url = reverse('create_room')

    def test_create_room_page_GET(self):
        # Uzyskujemy dostęp do strony tworzenia pokoju bez zalogowania - powinno przekierować do logowania
        response = self.client.get(self.create_room_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

        # Logujemy się i sprawdzamy dostęp do formularza
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.create_room_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')  # Sprawdzamy, czy jest formularz

    def test_create_room_success(self):
        self.client.login(username='testuser', password='testpass')
        form_data = {
            'name': 'Test Room',
            'max_players': 4,
            'is_private': False,
            'password': '',
            'blinds_level': 100,
        }
        response = self.client.post(self.create_room_url, data=form_data)
        # Po poprawnym utworzeniu powinniśmy być przekierowani do pokoju
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PokerRoom.objects.filter(name='Test Room').exists())

    def test_create_room_invalid_data(self):
        self.client.login(username='testuser', password='testpass')
        # Brak nazwy — formularz powinien być niepoprawny
        form_data = {
            'name': '',
            'max_players': 4,
            'is_private': False,
            'password': '',
            'blinds_level': 100,
        }
        response = self.client.post(self.create_room_url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    def test_create_room_without_login(self):
        response = self.client.get(self.create_room_url)
        # Nie zalogowany użytkownik jest przekierowywany do logowania
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)



