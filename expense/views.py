from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import *

# Create your views here.

#Sign up api
@csrf_exempt
def signup(request):
    if request.method=='POST':
        data=json.loads(request.body)
        fullname=data.get('FullName')
        email=data.get('Email')
        password=data.get('Password')
        

    if UserDetail.objects.filter(Email=email).exists():
        return JsonResponse({'message':'Email already exists'},status=400)
    
    UserDetail.objects.create(FullName=fullname,Email=email,Password=password)
    return JsonResponse({"message":"user registered successfuly"},status=201)


# Login api
@csrf_exempt
def login(request):
    if request.method=='POST':
        data=json.loads(request.body)
        print(f"data captured {data}")
        email=data.get('Email')
        password=data.get('Password')

        try:
            user=UserDetail.objects.get(Email=email,Password=password)
            return JsonResponse({'message':'Login Successful','userId':user.id,'username':user.FullName},status=200)
        except:
            return JsonResponse({'message':'Invalid Credentials'},status=400)


@csrf_exempt
def add_expense(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Expense data captured: {data}")

            # Extract data from the request
            # Note: 'userId' should be sent from the frontend after login
            user_id = data.get('UserId')
            print(f"User ID captured: {user_id}")
            expense_date = data.get('ExpenseDate')
            expense_item = data.get('ExpenseItem')
            expense_cost = data.get('ExpenseCost')
            print(f"Expense details - Date: {expense_date}, Item: {expense_item}, Cost: {expense_cost}")

        #     # Validate basic data presence
            if not all([user_id, expense_date, expense_item, expense_cost]):
                return JsonResponse({'message': 'Missing required fields'}, status=400)

        #     # Get the user instance
            user = UserDetail.objects.get(id=user_id)
            print(f"User found: {user.FullName}")

        #     # Create the expense record
            Expense.objects.create(
                UserId=user,
                ExpenseDate=expense_date,
                ExpenseItem=expense_item,
                ExpenseCost=expense_cost
            )

            return JsonResponse({'message': 'Expense added successfully!'}, status=201)

        except UserDetail.DoesNotExist:
            return JsonResponse({'message': 'User not found'}, status=404)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'message': 'An error occurred', 'error': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method'}, status=405)

@csrf_exempt
def manage_expense(request,user_id):
    if request.method == 'GET':
        try:
            user = UserDetail.objects.get(id=user_id)
            expenses = Expense.objects.filter(UserId=user).values('id', 'ExpenseDate', 'ExpenseItem', 'ExpenseCost')
            expenses_list = list(expenses)
            print(f"Expenses retrieved: {expenses_list}")
            return JsonResponse({'expenses': expenses_list}, status=200)

        except UserDetail.DoesNotExist:
            return JsonResponse({'message': 'User not found'}, status=404)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'message': 'An error occurred', 'error': str(e)}, status=500)

@csrf_exempt
def expense_detail(request, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        return JsonResponse({'message': 'Expense not found'}, status=404)

    # UPDATE Logic (For the Modal "Save changes")
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            expense.ExpenseDate = data.get('ExpenseDate', expense.ExpenseDate)
            expense.ExpenseItem = data.get('ExpenseItem', expense.ExpenseItem)
            expense.ExpenseCost = data.get('ExpenseCost', expense.ExpenseCost)
            expense.save()
            return JsonResponse({'message': 'Expense updated successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Update failed', 'error': str(e)}, status=400)

    # DELETE Logic (For the Trash button)
    elif request.method == 'DELETE':
        try:
            expense.delete()
            return JsonResponse({'message': 'Expense deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Delete failed', 'error': str(e)}, status=400)

    return JsonResponse({'message': 'Invalid request method'}, status=405)


@csrf_exempt
def delete_expense(request, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        return JsonResponse({'message': 'Expense not found'}, status=404)

    # UPDATE Logic (For the Modal "Save changes")
    if request.method == 'DELETE':
        try:
            expense.delete()
            return JsonResponse({'message': 'Expense deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Delete failed', 'error': str(e)}, status=400)
