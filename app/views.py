from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.urls import reverse

from app.forms import RegisterForm, RoomForm
from app.models import PokerRoom, Player
from .PokerGame import PokerGame, poker_games


# Create your views here.

def index(request):
    return render(request, 'app/index.html', {"page": "home"})

def handler_404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'app/404.html', {"page": "home"}, status=404)

def errorMessage(request):
    return render(request, 'app/errors.html', status=403)

def registerUser(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    context = {"form": form,
               "type": "register",
               "page": "login"
               }
    return render(request, 'app/login_register.html', context)

def loginUser(request):
    identifier_error = None
    password_error = None
    identifier = ""

    if request.method == "POST":
        identifier = request.POST.get('username_or_email')
        password = request.POST.get('password')

        user_query = User.objects.filter(Q(username=identifier) | Q(email=identifier)).first()

        if user_query:
            user = authenticate(request, username=user_query.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                password_error = 'Nieprawidłowe hasło.'
        else:
            identifier_error = 'Nieprawidłowa nazwa użytkownika lub e-mail.'
    context = {
        "type": "login",
        "identifier": identifier,
        "identifier_error": identifier_error,
        "password_error": password_error,
        "page": "login"
    }
    return render(request, 'app/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('index')

def rooms(request):
    if request.method == "POST": # User is trying to join a private room with password
        if not request.user.is_authenticated:
            messages.error(request, "Musisz być zalogowany, aby dołączyć pokoju.")
            return redirect('login')
        room_id = request.GET.get('id')
        password = request.POST.get('password')
        room = get_object_or_404(PokerRoom, id=room_id, is_private=True)

        if room.password == password:
            return redirect(reverse('join_room', kwargs={'room_id': room.id}) + '?role=participant')
        else:
            messages.error(request, "Błędne hasło do pokoju.")
            # return redirect('rooms')

    room_details_id = request.GET.get('id')
    query = request.GET.get('query', '')
    selected_room = PokerRoom.objects.filter(id=room_details_id).first() \
        if room_details_id else None
    rooms = PokerRoom.objects.filter(Q(name__icontains=query) | Q(host__username__icontains=query)) \
        if query else PokerRoom.objects.all()

    if selected_room:
        is_participant = Player.objects.filter(room=selected_room, user=request.user, is_participant=True).exists() \
            if request.user.is_authenticated else False
    context = {
        "rooms": rooms,
        "query": query,
        "selected_room": selected_room,
        "is_participant": is_participant if selected_room else None,
        "page": "rooms"
    }
    return render(request, 'app/rooms.html', context)

@login_required(login_url='login')
def createRoom(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            poker_games[room.id] = PokerGame(room.id, big_blind=room.blinds_level,max_players=room.max_players)
            return redirect(f"{reverse("join_room", kwargs={'room_id': room.id})}?role=participant")
    else:
        form = RoomForm()
    return render(request, 'app/room_form.html', {"form": form, "page": "create_room"})

@login_required(login_url='login')
def joinRoom(request, room_id):
    room = get_object_or_404(PokerRoom, id=room_id)
    role = request.GET.get('role', 'observer')
    current_players_count = Player.objects.filter(room=room, is_participant=True).count()
    if role == 'participant' and current_players_count >= room.max_players:
        messages.error("Pokój jest pełny. Nie możesz dołączyć jako uczestnik.")
        role = 'observer'

    # if role == 'participant' and not request.user.is_authenticated:
    #     messages.error(request, "Musisz być zalogowany, aby dołączyć jako uczestnik.")
    #     return redirect('login')

    context = {
        "room": room,
        "small_blind": room.blinds_level // 2,
        "role": role,
        "seat_range": range(room.max_players),
        "page": "room"
    }
    return render(request, 'app/room.html', context)

def deleteRoom(request, room_id):
    room = get_object_or_404(PokerRoom, id=room_id)
    if request.user == room.host:
        room.delete()
    else:
        messages.error(request, "Tylko gospodarz pokoju może go usunąć.")
        return redirect('forbidden')
    return redirect('rooms')
