from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Team(models.Model):
    name = models.CharField(max_length=100)
    country_name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100, null=True, blank=True)
    jersey_number = models.IntegerField(null=True)
    country_name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ScoutingReport(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    scout_name = models.CharField(max_length=100)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    notes = models.TextField()

    def __str__(self):
        return f"Report for {self.player.name} by {self.scout_name}"