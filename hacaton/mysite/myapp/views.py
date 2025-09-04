from django.shortcuts import render, get_object_or_404
from .models import Article
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, UserInfo
import json
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

def home(request):
    articles = get_info()
    return render(request, 'home.html', {'articles': articles})

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'article_detail.html', {'article': article})

def questions(request):
    return render(request, 'questions.html')

def events(request):
    return render(request,'events.html')

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

def get_info():
    infos = UserInfo.objects.select_related('user').all()  # Оптимизация: избежать N+1
    result = []
    for info in infos:
        result.append({
            'id': info.id,
            'user_id': info.user.tg,
            'username': info.user.Name,
            'disorder': info.disorder,
            'date': info.date
        })
    return result
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

            if not tg or not name:
                return JsonResponse({'error': 'Поля tg и name обязательны'}, status=400)

            # Проверяем, существует ли уже пользователь с таким tg
            if User.objects.filter(tg=tg).exists():
                return JsonResponse({
                    'error': 'Пользователь с таким Telegram ID уже существует',
                    'user': {
                        'id': User.objects.get(tg=tg).id,
                        'tg': tg,
                        'name': User.objects.get(tg=tg).Name
                    }
                }, status=200)  # HTTP 409 Conflict

            # Создаём нового пользователя
            user = User.objects.create(tg=tg, Name=name)
            return JsonResponse({
                'id': user.id,
                'tg': user.tg,
                'name': user.Name
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': f'Ошибка сервера: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Метод не разрешён'}, status=405)


def get_users(request):
    if request.method == 'GET':
        users = User.objects.all()
        data = [
            {'id': u.id, 'tg': u.tg, 'name': u.Name}
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