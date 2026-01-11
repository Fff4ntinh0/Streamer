from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseForbidden
from .models import *
from datetime import date,datetime
from django.shortcuts import get_object_or_404

def register(request):
    if request.method == "GET":
        return render(request,"register.html")
    elif request.method == "POST":
        name = request.POST.get('name')
        years = request.POST.get('event_date')
        email = request.POST.get('email')

        password_notconfirmed = request.POST.get('password')
        password_confirmed = request.POST.get('confirm_password')
        password_notconfirmed = request.POST.get('password')
        password_confirmed = request.POST.get('confirm_password')

        if password_notconfirmed != password_confirmed:
            return render(request, "register.html", {
                'error': "Passwords do not match!"
            })

        password = password_confirmed

        new_user = User(
            name=name,
            email=email,
            password_hash=password,
            date_created=date.today(),
            plain_id=1,
            years=years            
        )

        new_user.save()

        request.session['name'] = name
        return render(request,"home.html", {'name': name})

def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    elif request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "login.html", {
                'error': "Email not found"
            })

        if user.password_hash != password:
            return render(request, "login.html", {
                'error': "Password is wrong"
            })

        request.session["user_id"] = user.plain_id
        request.session["name"] = user.name

        return render(request, "home.html", {"name": user.name})

    
def create(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return HttpResponseForbidden("You don't sing in")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseForbidden("Invalued User")
    print("PLANO DO USUÁRIO:", user.plain_id)
    if user.plain_id != 1:
        return HttpResponseForbidden("You aren't a super user")
    
    genres = Genres.objects.all()
    error = None

    if request.method == "POST":
        name = request.POST.get("name")
        genre = request.POST.getlist("genre[]")
        release_date = request.POST.get("event_date")
        trailer = request.POST.get("trailer")
        poster = request.FILES.get("poster")
        description = request.POST.get("description")
        age = request.POST.get("age")
        is_film = request.POST.get("type") == "on"
        duration = request.POST.get("duration")
        link = request.POST.get("link")

        title = Titles.objects.create(
            name=name,
            release_year=release_date,
            trailer_url=trailer,
            poster_url=poster,
            description=description,
            age_rating=age,
            type=is_film,
            duration=duration,
            link=link,
            created_by=user
        )

        if genre:
            genre_ids = [int(g) for g in genre]
            genres = Genres.objects.filter(id__in=genre_ids)
            title.genres.set(genres)

        print("TÍTULO:", name)
        print("GÊNEROS:", genre)

        return redirect("create")

    return render(request, "create.html", {
        "name": user.name,
        "genres": genres,
        "error": error
    })

def logout(request):
    request.session.flush()
    return redirect("login")

def config(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return HttpResponseForbidden("You don't sing in")
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseForbidden("Invalued User")
    username = request.POST.get("username")

    profile, created = Profile.objects.get_or_create(
        user_id=user.id,
        defaults={
            "name": user.name,   
            "age_rating": ""
        }
    )

    birth = user.years
    if isinstance(birth, int):
        age_rating = date.today().year - birth
    elif isinstance(birth, date):
        today = date.today()
        age_rating = today.year - birth.year
        if (today.month, today.day) < (birth.month, birth.day):
            age_rating -= 1
    elif isinstance(birth, str):
        birth = datetime.strptime(birth, "%Y-%m-%d").date()
        today = date.today()
        age_rating = today.year - birth.year
        if (today.month, today.day) < (birth.month, birth.day):
            age_rating -= 1
    else:
        age_rating = ""    

    if request.method == "POST":
        username = request.POST.get("username")
        file = request.FILES.get("file")
        
        if file:
            if profile.arq:
                profile.arq.delete(save=False)
            profile.arq = file

        if username:
            profile.name = username

        profile.age_rating = age_rating
        profile.save()
        return redirect("config")

    return render(request, "config.html", {         
        "profile":profile    
    })

def configout(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return HttpResponseForbidden("You don't sing in")
    try:
        user = User.objects.get(id=user_id)
        return render(request, "home.html", {"name": user.name})
    except User.DoesNotExist:
        return HttpResponseForbidden("Invalued User")

def catalog(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return HttpResponseForbidden("You don't sing in")

    try:
        profile = Profile.objects.get(id=user_id)
        movie = Titles.objects.all()

        return render(request, "catalog.html", {
            "name": profile.name,
            "movie": movie
        })

    except Profile.DoesNotExist:
        return HttpResponseForbidden("Invalued User")
    
def film_detail(request,id):
    user_id = request.session.get("user_id")
    if not user_id:
        return HttpResponseForbidden("You don't sing in")
    
    movie = get_object_or_404(Titles, id=id)
    comments = Coment.objects.filter(title=movie).select_related('profile')

    return render(request, "film_detail.html", {
        "movie": movie,
        "comments": comments
    })
            
def comment(request, title_id):
    title = get_object_or_404(Titles, id=title_id)
    if request.method == "POST":
        session_user_id = request.session.get("user_id")
        if not session_user_id:
            return HttpResponseForbidden("You must be logged in to comment.")
        
        profile = get_object_or_404(Profile, user_id=session_user_id)
        
        text = request.POST.get("comment", "").strip()
        
        if text:
            Coment.objects.create(
                text_coment=text,
                title=title,  
                profile=profile  
            )
            return redirect("film_detail", id=title.id) 

    return redirect("film_detail", id=title.id)