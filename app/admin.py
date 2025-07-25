from django.contrib import admin
from .models import PokerRoom, Player

# Register your models here.
admin.site.register(PokerRoom)

# Composite primary keys are not supported in the Django admin
# admin.site.register(Player)


