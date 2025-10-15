from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Player, PokerRoom
from .PokerGame import poker_games

@receiver(post_delete, sender=Player)
def delete_empty_room(sender, instance, **kwargs):
    """Delete empty PokerRoom after Player is deleted"""
    try:
        room = instance.room
        if room:
            remaining_players = room.players.count()
            if remaining_players == 0:
                poker_games.pop(room.id, None)
                room.delete()
    except PokerRoom.DoesNotExist:
        pass
