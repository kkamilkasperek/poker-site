from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class PokerRoom(models.Model):
    BLINDS_CHOICES = [
        (2, '1/2' ),
        (6, '3/6' ),
        (12, '6/12'),
        (24, '12/24'),
        (50, '25/50'),
        (100, '50/100'),
    ]

    PLAYERS_CHOICES = [
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
    ]

    name = models.CharField(max_length=100, unique=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    max_players = models.IntegerField(default=8, validators=[MinValueValidator(2), MaxValueValidator(8)], choices=PLAYERS_CHOICES)
    is_private = models.BooleanField(default=False)
    password = models.CharField(max_length=100, null=True, blank=True)
    blinds_level = models.PositiveIntegerField(default=100, choices=BLINDS_CHOICES)
    players = models.ManyToManyField(User, through="Player", related_name="player_rooms")

    def __str__(self):
        return self.name

class Player(models.Model):
    pk = models.CompositePrimaryKey("user_id", "room_id")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(PokerRoom, on_delete=models.CASCADE)
    is_participant = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "room")

    def __str__(self):
        return f"{self.user.username} in {self.room.name}"


