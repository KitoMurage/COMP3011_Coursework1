import json
import os
from django.core.management.base import BaseCommand
from api.models import Team, Player

class Command(BaseCommand):
    help = 'Imports StatsBomb JSON lineup data into the database'

    def handle(self, *args, **kwargs):
        file_path = 'open-data-master/data/lineups/3869685.json'

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        self.stdout.write("Starting import...")

        for team_data in data:
            team_name = team_data.get('team_name')
            
            team, created = Team.objects.get_or_create(
                name=team_name,
                defaults={'country_name': team_name}
            )

            lineup = team_data.get('lineup', [])
            for player_data in lineup:
                Player.objects.get_or_create(
                    name=player_data.get('player_name'),
                    team=team,
                    defaults={
                        'nickname': player_data.get('player_nickname') or player_data.get('player_name'),
                        'jersey_number': player_data.get('jersey_number'),
                        'country_name': player_data.get('country', {}).get('name', 'Unknown')
                    }
                )
        self.stdout.write(self.style.SUCCESS('✅ Successfully imported all StatsBomb data!'))