from django.shortcuts import render, get_object_or_404, redirect
from .models import Article
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import User, UserInfo, Question, Event
import json
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .bot_functions import *

def home(request):
    articles = get_info()
    stat = get_statistics()
    return render(request, 'home.html', {'articles': articles, 'stat': stat})

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'article_detail.html', {'article': article})

def questions(request):
    q = get_all_questions()
    q2 = list_unsolved_questions()
    return render(request, 'questions.html', {'questions': q, "unsolved_questions": q2})

def events(request):
    ev = get_all_events()
    return render(request,'events.html',  {'events': ev})

@ensure_csrf_cookie  # Гарантирует, что куки csrftoken будет установлена
@require_http_methods(["GET"])
def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})
    
def create_user_info(request):
    """
    Создать новую запись UserInfo
    POST /api/userinfo/
    {
        "user_id": 1,
        "disorder": "Тревожное расстройство"
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('tg')
            disorder = data.get('disorder')

            if not user_id or not disorder:
                return JsonResponse({'error': 'Поля user_id и disorder обязательны'}, status=400)

            user = User.objects.get(tg=user_id)
            info = UserInfo.objects.create(
                user=user,
                disorder=disorder
                # date автоматически ставится по умолчанию
            )

            return JsonResponse({
                'id': info.id,
                'user_id': info.user.id,
                'disorder': info.disorder,
                'date': info.date
            }, status=201)

        except User.DoesNotExist:
            return JsonResponse({'error': 'Пользователь с таким ID не найден'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректный JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

def get_statistics():
    stat = {}
    info = UserInfo.objects.all()
    for i in info:
        stat[i.disorder] = stat.get(i.disorder, 0) + 1
    data = []
    for key in stat:
        data.append({'disorder': key, 'n': stat[key]})
    return data

def get_info():
    infos = UserInfo.objects.select_related('user').all()  # Оптимизация: избежать N+1
    result = []
    for info in infos:
        result.append({
            'id': info.id,
            'user_id': info.user.tg,
            'name': info.user.Name,
            'username': info.user.UserName,
            'disorder': info.disorder,
            'date': info.date,
            'events': info.user.EventsSubscriber,
            'advice': info.user.DayAdviceSubscriber
        })
    return result

def update_day_advice_subscriber(request):
    try:
        # Парсим JSON из тела запроса
        data = json.loads(request.body)
        tg_id = data.get("tg")
        is_subscribed = data.get("is_subscribed")
        what_to_update = data.get("category")

        # Проверяем обязательные поля
        if tg_id is None or is_subscribed is None:
            return JsonResponse(
                {"error": "Поля 'tg' и 'is_subscribed' обязательны"}, 
                status=400
            )

        # Пробуем найти и обновить пользователя
        user, created = User.objects.update_or_create(
            tg=tg_id,
            defaults={what_to_update: is_subscribed}
        )

        # Если нужно — можно логировать создание
        if created:
            return JsonResponse(
                {"message": "Пользователь создан и подписан", "tg": tg_id, "subscribed": is_subscribed},
                status=201
            )
        else:
            return JsonResponse(
                {"message": "Статус DayAdviceSubscriber обновлён", "tg": tg_id, "subscribed": is_subscribed},
                status=200
            )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Некорректный JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

def get_all_user_info(request):
    """
    Получить все записи UserInfo
    GET /api/userinfo/
    """
    if request.method == 'GET':
        result = get_info()
        return JsonResponse(result, safe=False, status=200)

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)


def get_user_info_by_id(request, info_id):
    """
    Получить одну запись UserInfo по ID
    GET /api/userinfo/1/
    """
    if request.method == 'GET':
        try:
            info = UserInfo.objects.select_related('user').get(id=info_id)
            return JsonResponse({
                'id': info.id,
                'user_id': info.user.id,
                'username': info.user.username,
                'disorder': info.disorder,
                'date': info.date
            }, status=200)
        except UserInfo.DoesNotExist:
            return JsonResponse({'error': 'Запись не найдена'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)


def create_user(request):
    print("here")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tg = data.get('tg')
            name = data.get('name')
            username = data.get("username")

            if not tg or not name:
                return JsonResponse({'error': 'Поля tg и name обязательны'}, status=400)
            if not username: username = 'unknown'

            # Проверяем, существует ли уже пользователь с таким tg
            if User.objects.filter(tg=tg).exists():
                return JsonResponse({
                    'error': 'Пользователь с таким Telegram ID уже существует',
                    'user': {
                        'id': User.objects.get(tg=tg).id,
                        'tg': tg,
                        'name': User.objects.get(tg=tg).Name,
                        'username': User.objects.get(tg=tg).UserName
                    }
                }, status=200)  # HTTP 409 Conflict

            # Создаём нового пользователя
            user = User.objects.create(tg=tg, Name=name, UserName=username)
            return JsonResponse({
                'id': user.id,
                'tg': user.tg,
                'name': user.Name,
                'username': User.objects.get(tg=tg).UserName
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': f'Ошибка сервера: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Метод не разрешён'}, status=405)


def get_users(request):
    if request.method == 'GET':
        users = User.objects.all()
        data = [
            {'id': u.id, 'tg': u.tg, 'name': u.Name, 'username': u.UserName}
            for u in users
        ]
        return JsonResponse({'users': data}, status=200)
    return JsonResponse({'error': 'Метод не разрешён'}, status=405)

def get_user(request, user_id):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=user_id)
            return JsonResponse({
                'id': user.id,
                'tg': user.tg,
                'name': user.Name
            }, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Пользователь не найден'}, status=404)
    return JsonResponse({'error': 'Метод не разрешён'}, status=405)

def add_question(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            tg_id = data.get("tg")  # Telegram ID пользователя
            question_text = data.get("text")

            if not tg_id or not question_text:
                return JsonResponse({"error": "Missing 'tg' or 'text'"}, status=400)

            # Находим пользователя или создаём нового (по желанию можно создавать)
            user = get_object_or_404(User, tg=tg_id)

            # Создаём вопрос
            question = Question.objects.create(
                from_user=user,
                text=question_text,
                solved=False
            )

            return JsonResponse({
                "id": question.id,
                "from_user": user.Name,
                "text": question.text,
                "solved": question.solved,
                "created_at": question.id  # Используем id как приближение ко времени (или добавьте DateTimeField)
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({'error': 'Метод не разрешён'}, status=405)

def update_question_solved(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            solved = data.get("solved")
            question_id = data.get("question_id")

            if solved is None:
                return JsonResponse({"error": "Missing 'solved' field"}, status=400)

            question = get_object_or_404(Question, id=question_id)
            question.solved = bool(solved)
            question.save()

            return JsonResponse({
                "id": question.id,
                "solved": question.solved,
                "message": "Status updated"
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({'error': 'Метод не разрешён'}, status=405)

def get_all_questions():
    questions = Question.objects.select_related('from_user').all()
    data = [
        {
            "id": q.id,
            "username": q.from_user.UserName,
            "text": q.text,
            "solved": q.solved,
            "answer": q.answer,
        }
        for q in questions
    ]
    return data

def list_all_questions(request):
    return JsonResponse(get_all_questions(), safe=False)

def list_unsolved_questions():
    unsolved = Question.objects.select_related('from_user').filter(solved=False)
    data = [
        {
            "id": q.id,
            "username": q.from_user.UserName,
            "text": q.text,
            "solved": q.solved,
        }
        for q in unsolved
    ]
    return data

def answer_question(request):
    if request.method == "POST":
        category_id = request.POST.get('category')
        answer_text = request.POST.get('answer')

        question = Question.objects.get(id=category_id)
        question.answer = answer_text
        question.solved = True
        question.save()
        
        text = f'Пришел ответ на твой вопрос:\n{question.text}.\nОтвет:\n{answer_text}'
        send_telegram_message(question.from_user.tg, text)
        return  redirect('/about')
    return JsonResponse({'error': 'Метод не разрешён'}, status=405)

def send_invitations(event):
    date_str = event.event_date if event.event_date else "не указана"
    time_str = event.start_time if event.start_time else "не указано"
    name = event.name or "Без названия"
    location = event.location or "Место не указано"
    organizer = event.organizer or "Организатор не указан"
    description = event.description or "Описание отсутствует."

    announcement = f"""
🎉 Анонс мероприятия: {name}

📅 Дата: {date_str}
⏰ Время: {time_str}
📍 Место: {location}

📌 Описание:
{description}

👤 Организатор: {organizer}

Не пропустите! Ждём вас! 🙌
"""
    for user in User.objects.filter(EventsSubscriber=True):
        send_telegram_message(user.tg, announcement)

def create_event(request):
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name')
        organizer = request.POST.get('organizer')
        description = request.POST.get('description')
        event_date = request.POST.get('event_date')
        start_time = request.POST.get('start_time')
        location = request.POST.get('location')
        max_participants = request.POST.get('max_participants')

        # Валидация обязательных полей
        if not all([name, description, event_date, start_time, location]):
            return HttpResponseBadRequest("Заполните все обязательные поля.")

        try:
            max_participants = int(max_participants) if max_participants else 20
            if max_participants < 1:
                max_participants = 20
        except (ValueError, TypeError):
            max_participants = 20

        # Создаём и сохраняем событие
        try:
            event = Event.objects.create(
                name=name,
                organizer=organizer or "Не указано",
                description=description,
                event_date=event_date,
                start_time=start_time,
                location=location,
                max_participants=max_participants
            )
            send_invitations(event)
            # Можно добавить сообщение об успехе
            return redirect('/events')  # или на нужную страницу, например: redirect('event_detail', pk=event.id)
        except Exception as e:
            return HttpResponseBadRequest(f"Ошибка при сохранении: {str(e)}")

    # Если GET-запрос — просто рендерим форму
    return render(request, 'events/create.html')  # замени на имя твоего шаблона

def get_all_events():
    """
    Возвращает все мероприятия в формате JSON.
    """
    events = Event.objects.all().order_by('event_date', 'start_time')
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'name': event.name,
            'organizer': event.organizer,
            'description': event.description,
            'event_date': event.event_date,
            'start_time': event.start_time,
            'location': event.location,
            'max_participants': event.max_participants,
            # Пример с количеством участников (если есть related_name)
            # 'registered_count': event.participants.count(),
        })
    return events_data

def delete_event(request, event_id):
    """
    Удаляет мероприятие по ID.
    Доступно только через POST (для безопасности).
    """
    event = get_object_or_404(Event, id=event_id)

    # Опционально: проверка, может ли пользователь удалять (например, только организатор)
    # if event.organizer != request.user.get_full_name():
    #     return HttpResponseForbidden("У вас нет прав на удаление этого мероприятия.")

    if request.method == 'POST':
        event_name = event.name
        event.delete()
        return redirect('/events')  # Замени на нужный URL, например: 'event_list', 'home', etc.

    # Если GET — можно запретить или перенаправить
    return HttpResponseForbidden("Удаление разрешено только через POST-запрос.")