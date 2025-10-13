from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    # clear the poker games cache when the app is ready and
    # PokerGames database is cleared
    def ready(self):
        import app.signals
        # from .PokerGame import poker_games
        # from .models import PokerRoom
        #
        # poker_games.clear()
        # PokerRoom.objects.all().delete()
