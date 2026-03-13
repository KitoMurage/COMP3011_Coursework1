from django.shortcuts import render
import json
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.db.models import Avg, Count
from .models import Player, ScoutingReport
import base64
from django.contrib.auth import authenticate



# REQUIREMENT: AUTHENTICATION
def basic_auth_required(view_func):
    """
    Custom decorator to enforce HTTP Basic Authentication on API endpoints.
    """
    def _wrapped_view(request, *args, **kwargs):
        # Check if the Authorization header is present
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Basic '):
            # Decode the base64 encoded username:password
            encoded_credentials = auth_header.split(' ')[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)
            
            # Verify against Django's built-in user database
            user = authenticate(request, username=username, password=password)
            if user is not None:
                request.user = user  # Attach the user to the request
                return view_func(request, *args, **kwargs)
        
        # If auth fails, reject the request with a 401 Unauthorized status
        response = JsonResponse({'error': 'Unauthorized. Please provide valid Basic Auth credentials.'}, status=401)
        response['WWW-Authenticate'] = 'Basic realm="Pro-Scout API"'
        return response
        
    return _wrapped_view

# REQUIREMENT: READ & HATEOAS
def get_player(request, player_id):
    if request.method == 'GET':
        try:
            player = Player.objects.get(id=player_id)
            return JsonResponse({
                "id": player.id,
                "name": player.nickname or player.name,
                "team": player.team.name,
                "jersey": player.jersey_number,
                "_links": {
                    "self": {"href": f"/api/players/{player.id}/", "method": "GET"},
                    "create_report": {"href": "/api/scouting-reports/", "method": "POST"}
                }
            })
        except Player.DoesNotExist:
            return HttpResponseNotFound(json.dumps({"error": "Player not found"}), content_type="application/json")


# REQUIREMENT: CREATE (CRUD) & VALIDATION
@basic_auth_required
def create_report(request):
    # READ: List all reports (This fixes your GET error!)
    if request.method == 'GET':
        reports = ScoutingReport.objects.all()
        reports_data = []
        for report in reports:
            reports_data.append({
                "id": report.id,
                "player": report.player.name,
                "scout_name": report.scout_name,
                "rating": report.rating
            })
        return JsonResponse({"reports": reports_data}, safe=False)

    # CREATE: Make a new report
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            player = Player.objects.get(id=data['player_id'])
            
            # View-level validation
            if not (1 <= data['rating'] <= 100):
                return HttpResponseBadRequest(json.dumps({"error": "Rating must be 1-100"}), content_type="application/json")

            report = ScoutingReport.objects.create(
                player=player,
                scout_name=data['scout_name'],
                rating=data['rating'],
                notes=data['notes']
            )
            
            return JsonResponse({
                "message": "Report Created",
                "report_id": report.id,
                "_links": {
                    "view_report": {"href": f"/api/scouting-reports/{report.id}/", "method": "GET"}
                }
            }, status=201)

        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest(json.dumps({"error": "Invalid JSON"}), content_type="application/json")
        except Player.DoesNotExist:
            return HttpResponseNotFound(json.dumps({"error": "Player does not exist"}), content_type="application/json")
            
    # Catch-all for any other methods (PUT, DELETE) sent to this route
    return JsonResponse({"error": "Method not allowed"}, status=405)

# REQUIREMENT: READ, UPDATE, DELETE (CRUD)
@basic_auth_required
def manage_report(request, report_id):
    try:
        report = ScoutingReport.objects.get(id=report_id)
    except ScoutingReport.DoesNotExist:
        return HttpResponseNotFound(json.dumps({"error": "Report not found"}), content_type="application/json")

    # READ
    if request.method == 'GET':
        return JsonResponse({
            "id": report.id,
            "player": report.player.name,
            "scout_name": report.scout_name,
            "rating": report.rating,
            "notes": report.notes,
            "_links": {
                "update": {"href": f"/api/scouting-reports/{report.id}/", "method": "PUT"},
                "delete": {"href": f"/api/scouting-reports/{report.id}/", "method": "DELETE"}
            }
        })

    # UPDATE
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            if 'rating' in data:
                if not (1 <= data['rating'] <= 100):
                    return HttpResponseBadRequest(json.dumps({"error": "Rating must be 1-100"}), content_type="application/json")
                report.rating = data['rating']
            if 'notes' in data:
                report.notes = data['notes']
                
            report.save()
            return JsonResponse({"message": "Report updated successfully"})
        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({"error": "Invalid JSON"}), content_type="application/json")

    # DELETE
    elif request.method == 'DELETE':
        report.delete()
        return JsonResponse({"message": "Report deleted"}, status=204)


# REQUIREMENT: ANALYTICAL ENDPOINT (Lecture 7)
def get_leaderboard(request):
    if request.method == 'GET':
        top_players = Player.objects.annotate(
            average_rating=Avg('scoutingreport__rating'),
            report_count=Count('scoutingreport')
        ).filter(
            report_count__gt=0
        ).order_by('-average_rating')[:10]

        leaderboard_data = []
        for rank, player in enumerate(top_players, start=1):
            leaderboard_data.append({
                "rank": rank,
                "player_name": player.name,
                "team": player.team.name,
                "average_rating": round(player.average_rating, 1),
                "total_reports": player.report_count,
            })

        return JsonResponse({"leaderboard": leaderboard_data})

# ==========================================
# REQUIREMENT: PERFORMANCE SUMMARY (Analytics)
# ==========================================
def get_team_summary(request):
    if request.method == 'GET':
        # This is a complex query: it goes from Team -> Player -> ScoutingReport
        teams = Team.objects.annotate(
            team_avg_rating=Avg('player__scoutingreport__rating'),
            total_scouted_players=Count('player__scoutingreport', distinct=True)
        ).filter(
            total_scouted_players__gt=0 # Only show teams with scouted players
        ).order_by('-team_avg_rating')

        summary_data = []
        for team in teams:
            summary_data.append({
                "country": team.country_name,
                "squad_average_rating": round(team.team_avg_rating, 1),
                "players_scouted": team.total_scouted_players
            })

        return JsonResponse({"team_performance_summary": summary_data})