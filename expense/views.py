from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
import logging
from .models import *

logger = logging.getLogger(__name__)

# Create your views here.

# ✅ Sign up api - optimized
@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    try:
        data = json.loads(request.body)
        fullname = data.get('FullName', '').strip()
        email = data.get('Email', '').strip().lower()
        password = data.get('Password', '').strip()
        
        # Validation
        if not all([fullname, email, password]):
            return JsonResponse({'message': 'Missing required fields'}, status=400)
        
        if len(password) < 6:
            return JsonResponse({'message': 'Password must be at least 6 characters'}, status=400)

        # ✅ Check with index lookup
        if UserDetail.objects.filter(Email=email).exists():
            return JsonResponse({'message': 'Email already exists'}, status=400)
        
        user = UserDetail.objects.create(FullName=fullname, Email=email, Password=password)
        logger.info(f"New user registered: {email}")
        
        return JsonResponse({"message": "user registered successfully"}, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return JsonResponse({'message': 'An error occurred'}, status=500)


# ✅ Login api - optimized with indexing
@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    try:
        data = json.loads(request.body)
        email = data.get('Email', '').strip().lower()
        password = data.get('Password', '').strip()

        # ✅ Single query with index lookup
        user = UserDetail.objects.get(Email=email, Password=password)
        logger.info(f"Login successful: {email}")
        
        return JsonResponse({
            'message': 'Login Successful',
            'userId': user.id,
            'username': user.FullName
        }, status=200)
    
    except UserDetail.DoesNotExist:
        return JsonResponse({'message': 'Invalid Credentials'}, status=400)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return JsonResponse({'message': 'An error occurred'}, status=500)


# ✅ Add expense - optimized
@csrf_exempt
@require_http_methods(["POST"])
def add_expense(request):
    try:
        data = json.loads(request.body)
        
        user_id = data.get('UserId')
        expense_date = data.get('ExpenseDate')
        expense_item = data.get('ExpenseItem', '').strip()
        expense_cost = data.get('ExpenseCost')
        
        # Validate
        if not all([user_id, expense_date, expense_item, expense_cost]):
            return JsonResponse({'message': 'Missing required fields'}, status=400)

        # ✅ Get user by ID (fast with index on PK)
        user = UserDetail.objects.get(id=user_id)

        Expense.objects.create(
            UserId=user,
            ExpenseDate=expense_date,
            ExpenseItem=expense_item,
            ExpenseCost=expense_cost
        )

        logger.info(f"Expense added for user {user_id}")
        return JsonResponse({'message': 'Expense added successfully!'}, status=201)

    except UserDetail.DoesNotExist:
        return JsonResponse({'message': 'User not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Add expense error: {str(e)}")
        return JsonResponse({'message': 'An error occurred', 'error': str(e)}, status=500)

# ✅ Manage expense - OPTIMIZED WITH PAGINATION & QUERY OPTIMIZATION
@csrf_exempt
@require_http_methods(["GET"])
def manage_expense(request, user_id):
    try:
        # ✅ Verify user exists
        user = UserDetail.objects.get(id=user_id)
        
        # ✅ Optimized query with only needed fields
        expenses_queryset = Expense.objects.filter(
            UserId=user
        ).values('id', 'ExpenseDate', 'ExpenseItem', 'ExpenseCost', 'NoteDate').order_by('-NoteDate')
        
        # ✅ Add pagination to prevent loading huge datasets
        page_num = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 20)
        
        paginator = Paginator(expenses_queryset, page_size)
        page = paginator.get_page(page_num)
        
        logger.info(f"Retrieved {len(page.object_list)} expenses for user {user_id}")
        
        return JsonResponse({
            'expenses': list(page.object_list),
            'total_count': paginator.count,
            'page': int(page_num),
            'page_size': int(page_size)
        }, status=200)

    except UserDetail.DoesNotExist:
        return JsonResponse({'message': 'User not found'}, status=404)
    except Exception as e:
        logger.error(f"Manage expense error: {str(e)}")
        return JsonResponse({'message': 'An error occurred', 'error': str(e)}, status=500)

# ✅ Get/Update/Delete single expense
@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def expense_detail(request, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        return JsonResponse({'message': 'Expense not found'}, status=404)

    # UPDATE Logic
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            expense.ExpenseDate = data.get('ExpenseDate', expense.ExpenseDate)
            expense.ExpenseItem = data.get('ExpenseItem', expense.ExpenseItem)
            expense.ExpenseCost = data.get('ExpenseCost', expense.ExpenseCost)
            expense.save()
            logger.info(f"Expense {expense_id} updated")
            return JsonResponse({'message': 'Expense updated successfully'}, status=200)
        except Exception as e:
            logger.error(f"Update error: {str(e)}")
            return JsonResponse({'message': 'Update failed', 'error': str(e)}, status=400)

    # DELETE Logic
    elif request.method == 'DELETE':
        try:
            expense.delete()
            logger.info(f"Expense {expense_id} deleted")
            return JsonResponse({'message': 'Expense deleted successfully'}, status=200)
        except Exception as e:
            logger.error(f"Delete error: {str(e)}")
            return JsonResponse({'message': 'Delete failed', 'error': str(e)}, status=400)

    # GET Logic
    elif request.method == 'GET':
        return JsonResponse({
            'id': expense.id,
            'ExpenseDate': expense.ExpenseDate,
            'ExpenseItem': expense.ExpenseItem,
            'ExpenseCost': expense.ExpenseCost
        }, status=200)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_expense(request, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id)
        expense.delete()
        logger.info(f"Expense {expense_id} deleted")
        return JsonResponse({'message': 'Expense deleted successfully'}, status=200)
    except Expense.DoesNotExist:
        return JsonResponse({'message': 'Expense not found'}, status=404)
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        return JsonResponse({'message': 'Delete failed', 'error': str(e)}, status=400)
