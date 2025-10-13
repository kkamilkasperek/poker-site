import asyncio

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404

from .models import PokerRoom, Player
from .PokerGame import poker_games


class PokerConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.user = self.scope['user']
        self.room_group_name = f"poker_room_{self.room_id}"
        self.user_group_name = f"poker_user_{self.user.username}"
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        self.role = query_params.get('role', [None])[0]


        if self.role not in ['participant', 'observer']:
            await self.close(code=4000)
            return

        # Check if room exists in database
        room_exists = await self.check_room_exists()
        if not room_exists:
            await self.close(code=4004)
            return

        # add user to room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        # add user to personal group
        await self.channel_layer.group_add(self.user_group_name,self.channel_name)

        self.poker_room = poker_games.get(int(self.room_id))

        if self.poker_room is None:
            await self.close(code=4005)
            return

        if self.poker_room.message_callback is None:
            self.poker_room.message_callback = self.broadcast_game_message
            self.poker_room.private_message_callback = self.private_game_message

        await self.accept()

        await self.update_or_create_player_db()
        await self.create_player_game()

    async def disconnect(self, code):
        # Check if poker_room still exists
        if hasattr(self, 'poker_room') and self.poker_room is not None and self.role == 'participant':
            player_info = self.poker_room.get_player(self.user.username)
            if player_info:
                player_pos = player_info[0]
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'player_left',
                        'position': player_pos,
                        'sender_channel': self.channel_name,
                    }
                )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

        await self.remove_player_db()
        await self.remove_player_game()

        await self.close()

    async def receive_json(self, content):
        msg_type = content.get('type')
        if msg_type == 'init_new_player': # new player joined the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': content['type'],
                    'role': self.role,
                    'username': self.user.username,
                    'sender_channel': self.channel_name,
                }
            )
        # elif msg_type == 'start_game' and self.role == 'participant':
        #     asyncio.create_task(self.poker_room.start_game())
        elif msg_type == 'player_action' and self.role == 'participant':
            print("Received action:", self.user.username, content)
            action = content.get('action')
            amount = content.get('amount', 0)
            success, message = await self.poker_room.player_action(self.user.username, action, amount)
            if not success:
                await self.send_json({
                    'type': 'action_error',
                    'message': message,
                })

    async def init_new_player(self, event):
        request_role = event['role']
        request_player = self.poker_room.get_player(event['username'])
        room_players = self.poker_room.get_all_players()

        for player_pos in room_players: # remove cards info before sending to others
            if room_players[player_pos]['username'] != event['username'] and \
                room_players[player_pos]['cards'] is not None:
                room_players[player_pos] = room_players[player_pos].copy()
                room_players[player_pos]['cards'] = ['XX', 'XX']


        if request_role == 'participant':
            if event['sender_channel'] != self.channel_name:
                # send to others info about new player
                await self.send_json({
                    'type': 'new_player',
                    'position': request_player[0],
                    'username': event['username'],
                    'chip_count': request_player[1]['chip_count'],
                })
            else:
                # send to new player info about all players in the room
                await self.send_json({
                    'type': 'init_participant',
                    'players': room_players,
                    'your_position': request_player[0],
                })
                # start game if all players are ready
                if self.poker_room.can_start_game():
                    asyncio.create_task(self.poker_room.start_game())
        elif event['sender_channel'] == self.channel_name:
            # send to observer info about all players in the room
            await self.send_json({
                'type': 'init_observer',
                'players': room_players,
            })

    async def player_left(self, event):
        if event['sender_channel'] != self.channel_name:
            await self.send_json({
                'type': 'player_left',
                'position': event['position'],
            })

    # function responsible for sending game_messages, called by PokerGame instance
    async def broadcast_game_message(self, message_type, data):
        print("Broadcasting message:", message_type, data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_message',
                'message_type': message_type,
                'data': data,
            }
        )

    async def private_game_message(self, username, message_type, data):
        print("Sending private message:", username, message_type, data)
        user_group_name = f"poker_user_{username}"
        await self.channel_layer.group_send(
            user_group_name,
            {
                'type': 'game_message',
                'message_type': message_type,
                'data': data,
            }
        )

    async def game_message(self, event):
        await self.send_json({
            'type': event['message_type'],
            **event['data'], # unpack data dictionary into the message
        })


    async def create_player_game(self):
        if self.role == 'participant':
            position = self.poker_room.add_player(self.user)
            if position is None:
                raise ValueError("No available slot in the game.")


    async def remove_player_game(self):
        if self.role == 'participant':
            game = poker_games.get(int(self.room_id))
            if game is not None:
                position = game.remove_player(self.user.username)
            # if position is None: player can be already removed
            #     raise ValueError("Player not found in the game.")

    @database_sync_to_async
    def check_room_exists(self):
        return PokerRoom.objects.filter(pk=self.room_id).exists()

    @database_sync_to_async
    def update_or_create_player_db(self):
        room = get_object_or_404(PokerRoom, pk=self.room_id)
        player, created = Player.objects.update_or_create(
            user = self.user,
            room = room,
            defaults={'is_participant': self.role == 'participant'}
        )
        # done in separate function
        '''if self.role == 'participant':
            position = poker_games[room.id].add_player(player)
            if position is None:
                raise ValueError("No available slot in the game.")'''

    @database_sync_to_async
    def remove_player_db(self):
        try:
            room = PokerRoom.objects.get(pk=self.room_id)
        except PokerRoom.DoesNotExist:
            return
        player = Player.objects.filter(pk=(self.user.id , self.room_id)).first()

        if player:
            player.delete()

        # done in separate function
        '''if self.role == 'participant':
            position = poker_games[room.id].remove_player(player)
            if position is None:
                raise ValueError("Player not found in the game.")'''
