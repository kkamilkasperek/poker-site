"""
Tests for WebSocket consumer and integration with PokerGame
"""
import pytest
import asyncio
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from app.consumers import PokerConsumer
from app.models import PokerRoom, Player
from app.PokerGame import poker_games, PokerGame

User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestWebSocketConnection:
    """Test WebSocket connection and disconnection"""

    async def test_connect_as_participant(self, create_room, create_users):
        """Test connecting as a participant"""
        room = await create_room()
        user1, user2, user3 = await create_users()

        communicator = WebsocketCommunicator(
            PokerConsumer.as_asgi(),
            f"/ws/poker/{room.id}/?role=participant"
        )
        communicator.scope['user'] = user1
        communicator.scope['url_route'] = {'kwargs': {'room_id': room.id}}

        connected, subprotocol = await communicator.connect()
        assert connected

        # Should receive init message with timeout
        try:
            response = await asyncio.wait_for(
                communicator.receive_json_from(),
                timeout=2.0
            )
            assert response['type'] == 'init_participant'
        except asyncio.TimeoutError:
            pytest.fail("Did not receive init_participant message within timeout")
        finally:
            await communicator.disconnect()

    async def test_connect_as_observer(self, create_room, create_users):
        """Test connecting as an observer"""
        room = await create_room()
        user1, user2, user3 = await create_users()

        communicator = WebsocketCommunicator(
            PokerConsumer.as_asgi(),
            f"/ws/poker/{room.id}/?role=observer"
        )
        communicator.scope['user'] = user3
        communicator.scope['url_route'] = {'kwargs': {'room_id': room.id}}

        connected, subprotocol = await communicator.connect()
        assert connected

        # Should receive init message with timeout
        try:
            response = await asyncio.wait_for(
                communicator.receive_json_from(),
                timeout=2.0
            )
            assert response['type'] == 'init_observer'
        except asyncio.TimeoutError:
            pytest.fail("Did not receive init_observer message within timeout")
        finally:
            await communicator.disconnect()

    async def test_connect_invalid_role(self, create_room, create_users):
        """Test that invalid roles are rejected"""
        room = await create_room()
        user1, user2, user3 = await create_users()

        communicator = WebsocketCommunicator(
            PokerConsumer.as_asgi(),
            f"/ws/poker/{room.id}/?role=invalid"
        )
        communicator.scope['user'] = user1
        communicator.scope['url_route'] = {'kwargs': {'room_id': room.id}}

        connected, subprotocol = await communicator.connect()
        assert not connected

    async def test_disconnect_removes_player(self, create_room, create_users):
        """Test that disconnecting removes player from game"""
        room = await create_room()
        user1, user2, user3 = await create_users()

        communicator = WebsocketCommunicator(
            PokerConsumer.as_asgi(),
            f"/ws/poker/{room.id}/?role=participant"
        )
        communicator.scope['user'] = user1
        communicator.scope['url_route'] = {'kwargs': {'room_id': room.id}}

        await communicator.connect()
        
        # Consume init message with timeout
        try:
            await asyncio.wait_for(
                communicator.receive_json_from(),
                timeout=2.0
            )
        except asyncio.TimeoutError:
            pytest.fail("Did not receive init message")

        # Check player was added
        poker_game = poker_games[room.id]
        pos, player = poker_game.get_player(user1.username)
        assert player is not None

        await communicator.disconnect()
        
        # Give a moment for cleanup to process
        await asyncio.sleep(0.1)

        # Check player was removed
        pos, player = poker_game.get_player(user1.username)
        assert player is None


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestWebSocketMessages:
    """Test WebSocket message handling"""

    async def test_player_receives_new_player_notification(self, create_room, create_users):
        """Test that existing players are notified of new players"""
        room = await create_room()
        user1, user2, user3 = await create_users()

        # Connect first player
        comm1 = WebsocketCommunicator(
            PokerConsumer.as_asgi(),
            f"/ws/poker/{room.id}/?role=participant"
        )
        comm1.scope['user'] = user1
        comm1.scope['url_route'] = {'kwargs': {'room_id': room.id}}
        await comm1.connect()
        
        try:
            await asyncio.wait_for(comm1.receive_json_from(), timeout=2.0)  # Consume init message

            # Connect second player
            comm2 = WebsocketCommunicator(
                PokerConsumer.as_asgi(),
                f"/ws/poker/{room.id}/?role=participant"
            )
            comm2.scope['user'] = user2
            comm2.scope['url_route'] = {'kwargs': {'room_id': room.id}}
            await comm2.connect()
            await asyncio.wait_for(comm2.receive_json_from(), timeout=2.0)  # Consume init message

            # First player should receive notification about second player
            response = await asyncio.wait_for(comm1.receive_json_from(), timeout=2.0)
            assert response['type'] == 'new_player'
            assert user2.username in response['username']

            await comm2.disconnect()
        except asyncio.TimeoutError:
            pytest.fail("Timeout waiting for WebSocket messages")
        finally:
            await comm1.disconnect()

    async def test_player_action_fold(self, create_room, create_users):
        """Test sending fold action through WebSocket"""
        room = await create_room()
        user1, user2, user3 = await create_users()

        # Setup game with player
        poker_game = poker_games[room.id]

        communicator = WebsocketCommunicator(
            PokerConsumer.as_asgi(),
            f"/ws/poker/{room.id}/?role=participant"
        )
        communicator.scope['user'] = user1
        communicator.scope['url_route'] = {'kwargs': {'room_id': room.id}}

        await communicator.connect()
        
        try:
            await asyncio.wait_for(
                communicator.receive_json_from(),
                timeout=2.0
            )  # Consume init message

            # Setup game state for player action
            pos, player = poker_game.get_player(user1.username)
            poker_game.game_state = 'pre_flop'
            poker_game.current_player_position = pos
            poker_game.waiting_for_player = True

            # Send fold action
            await communicator.send_json_to({
                'type': 'player_action',
                'action': 'fold',
            })

            # Wait a moment for processing
            await asyncio.sleep(0.2)

            # Check that player folded
            assert poker_game.players[pos]['folded'] is True
        except asyncio.TimeoutError:
            pytest.fail("Timeout in test")
        finally:
            await communicator.disconnect()

    async def test_observer_receives_game_updates(self, create_room, create_users):
        """Test that observers receive game update messages"""
        room = await create_room()
        user1, user2, user3 = await create_users()

        # Connect observer
        comm_observer = WebsocketCommunicator(
            PokerConsumer.as_asgi(),
            f"/ws/poker/{room.id}/?role=observer"
        )
        comm_observer.scope['user'] = user3
        comm_observer.scope['url_route'] = {'kwargs': {'room_id': room.id}}
        await comm_observer.connect()
        
        try:
            await asyncio.wait_for(
                comm_observer.receive_json_from(),
                timeout=2.0
            )  # Consume init message

            # Connect participant
            comm_participant = WebsocketCommunicator(
                PokerConsumer.as_asgi(),
                f"/ws/poker/{room.id}/?role=participant"
            )
            comm_participant.scope['user'] = user1
            comm_participant.scope['url_route'] = {'kwargs': {'room_id': room.id}}
            await comm_participant.connect()
            await asyncio.wait_for(
                comm_participant.receive_json_from(),
                timeout=2.0
            )  # Consume init message

            # Observer should be notified about new participant
            response = await asyncio.wait_for(
                comm_observer.receive_json_from(),
                timeout=2.0
            )
            assert response['type'] == 'new_player'

            await comm_participant.disconnect()
        except asyncio.TimeoutError:
            pytest.fail("Timeout waiting for observer update")
        finally:
            await comm_observer.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestGameFlow:
    """Test basic game flow through WebSocket"""

    async def test_game_starts_with_two_players(self, create_room, create_users):
        """Test that game can handle two players joining"""
        room = await create_room()
        user1, user2, user3 = await create_users()

        poker_game = poker_games[room.id]

        # Connect first player
        comm1 = WebsocketCommunicator(
            PokerConsumer.as_asgi(),
            f"/ws/poker/{room.id}/?role=participant"
        )
        comm1.scope['user'] = user1
        comm1.scope['url_route'] = {'kwargs': {'room_id': room.id}}
        await comm1.connect()
        
        try:
            await asyncio.wait_for(comm1.receive_json_from(), timeout=2.0)  # init

            # Game should still be waiting
            assert poker_game.game_state == 'waiting'

            # Connect second player
            comm2 = WebsocketCommunicator(
                PokerConsumer.as_asgi(),
                f"/ws/poker/{room.id}/?role=participant"
            )
            comm2.scope['user'] = user2
            comm2.scope['url_route'] = {'kwargs': {'room_id': room.id}}
            await comm2.connect()
            await asyncio.wait_for(comm2.receive_json_from(), timeout=2.0)  # init

            # Allow time for game to potentially start
            await asyncio.sleep(0.3)

            # Both players should be in the game
            all_players = poker_game.get_all_players()
            assert len(all_players) == 2

            await comm2.disconnect()
        except asyncio.TimeoutError:
            pytest.fail("Timeout in game flow test")
        finally:
            await comm1.disconnect()

    async def test_betting_round_messages(self, create_room, create_users):
        """Test that players can exchange messages"""
        room = await create_room()
        user1, user2, user3 = await create_users()

        poker_game = poker_games[room.id]

        # Add players directly to game
        comm1 = WebsocketCommunicator(
            PokerConsumer.as_asgi(),
            f"/ws/poker/{room.id}/?role=participant"
        )
        comm1.scope['user'] = user1
        comm1.scope['url_route'] = {'kwargs': {'room_id': room.id}}
        await comm1.connect()
        
        try:
            await asyncio.wait_for(comm1.receive_json_from(), timeout=2.0)

            comm2 = WebsocketCommunicator(
                PokerConsumer.as_asgi(),
                f"/ws/poker/{room.id}/?role=participant"
            )
            comm2.scope['user'] = user2
            comm2.scope['url_route'] = {'kwargs': {'room_id': room.id}}
            await comm2.connect()
            await asyncio.wait_for(comm2.receive_json_from(), timeout=2.0)

            # Wait for any game messages
            await asyncio.sleep(0.3)

            # Verify both players are connected
            assert len(poker_game.get_all_players()) == 2

            await comm2.disconnect()
        except asyncio.TimeoutError:
            pytest.fail("Timeout in betting round test")
        finally:
            await comm1.disconnect()