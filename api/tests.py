import base64
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Team, Player, ScoutingReport

class ProScoutAPITests(TestCase):
    def setUp(self):
        """Set up the mock database and authentication headers for testing."""
        self.client = Client()
        self.user = User.objects.create_superuser(username='testadmin', password='testpassword')
        
        # Updated to perfectly match your Team model
        self.team = Team.objects.create(name="Test Team", country_name="Test Country")
        
        # Updated to perfectly match your Player model
        self.player = Player.objects.create(name="Test Player", country_name="Test Country", team=self.team)
        
        # Updated to perfectly match your ScoutingReport model (added scout_name)
        self.report = ScoutingReport.objects.create(
            player=self.player, scout_name="Admin Scout", rating=80, notes="Initial scout"
        )
        
        # Setup basic auth headers
        auth_string = 'testadmin:testpassword'
        self.encoded_auth = base64.b64encode(auth_string.encode()).decode()
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Basic {self.encoded_auth}'}

    # --- 1. AUTHENTICATION & ACCESS TESTS ---
    
    def test_public_endpoints_allow_unauthenticated_access(self):
        """Test that GET endpoints do not require login."""
        response = self.client.get('/api/analytics/leaderboard/') 
        self.assertEqual(response.status_code, 200)

    def test_protected_endpoints_block_unauthenticated_access(self):
        """Test that POST/PUT/DELETE require authentication."""
        response = self.client.delete(f'/api/scouting-reports/{self.report.id}/')
        self.assertEqual(response.status_code, 401)

    # --- 2. BOUNDARY & ERROR HANDLING TESTS ---

    def test_create_report_invalid_rating_too_high(self):
        """Test that ratings over 100 return a 400 Bad Request."""
        # Added scout_name and used player.id
        payload = {'player_id': self.player.id, 'scout_name': 'Tester', 'rating': 150, 'notes': 'Impossible rating'}
        response = self.client.post(
            '/api/scouting-reports/', 
            data=json.dumps(payload), content_type='application/json', **self.auth_headers
        )
        self.assertEqual(response.status_code, 400)

    def test_get_nonexistent_player_returns_404(self):
        """Test that requesting a missing ID returns a proper 404, not a 500 crash."""
        response = self.client.get('/api/players/99999/')
        self.assertEqual(response.status_code, 404)

    # --- 3. CRUD & ARCHITECTURE TESTS ---

    def test_successful_report_creation(self):
        """Test the CREATE (POST) operation with valid data."""
        payload = {'player_id': self.player.id, 'scout_name': 'Tester', 'rating': 95, 'notes': 'Excellent'}
        response = self.client.post(
            '/api/scouting-reports/', 
            data=json.dumps(payload), content_type='application/json', **self.auth_headers
        )
        self.assertIn(response.status_code, [200, 201])
        # Verify it actually saved to the database (Initial + this new one = 2)
        self.assertEqual(ScoutingReport.objects.count(), 2) 

    def test_successful_report_update(self):
        """Test the UPDATE (PUT) operation."""
        payload = {'scout_name': 'Tester', 'rating': 85, 'notes': 'Updated notes'}
        response = self.client.put(
            f'/api/scouting-reports/{self.report.id}/', 
            data=json.dumps(payload), content_type='application/json', **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        self.report.refresh_from_db()
        self.assertEqual(self.report.rating, 85)

    def test_successful_report_deletion(self):
        """Test the DELETE operation."""
        response = self.client.delete(
            f'/api/scouting-reports/{self.report.id}/', **self.auth_headers
        )
        self.assertIn(response.status_code, [200, 204])
        self.assertEqual(ScoutingReport.objects.count(), 0)

    def test_hateoas_links_present_in_response(self):
        """Test that the API correctly returns HATEOAS _links in the JSON payload."""
        response = self.client.get(f'/api/players/{self.player.id}/')
        data = response.json()
        self.assertIn('_links', data)