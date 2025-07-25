from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from app.forms import RegisterForm, RoomForm
from app.models import PokerRoom, Player


# Create your views here.

def index(request):
    return render(request, 'app/index.html')

def registerUser(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    context = {"form": form, "type": "register"}
    return render(request, 'app/login_register.html', context)

def loginUser(request):
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
                messages.error(request, 'Nieprawidłowe hasło')
        else:
            messages.error(request, "Nieprawidłowa nazwa użytkownika lub e-mail")
    context = {"type": "login"}
    return render(request, 'app/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('index')

def rooms(request):
    if request.method == "POST": # User is trying to join a private room with password
        room_id = request.GET.get('id')
        password = request.POST.get('password')
        room = get_object_or_404(PokerRoom, id=room_id, is_private=True)

        if room.password == password:
            return redirect('join_room', room_id=room.id)
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
            return redirect('join_room', room_id=room.id)
        else:
            messages.error(request, "Błąd podczas tworzenia pokoju. Sprawdź poprawność danych.")
    else:
        form = RoomForm()
    return render(request, 'app/room_form.html', {"form": form})

def joinRoom(request, room_id):
    pass
