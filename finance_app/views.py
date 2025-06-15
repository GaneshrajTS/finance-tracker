from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, TransactionForm
from .models import Transaction
from datetime import datetime
from .ml_utils import get_pie_chart, get_monthly_expense_chart, forecast_expense
from .ml_utils import detect_spending_anomaly
from .forms import TransactionForm, UserRegisterForm, CategoryForm
from .models import Transaction, Category
from django.db.models import Q
import calendar
import pandas as pd
from django.http import HttpResponse

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'finance_app/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'finance_app/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def add_category_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('add_transaction')
    else:
        form = CategoryForm()
    return render(request, 'finance_app/add_category.html', {'form': form})


# Edit transaction
@login_required
def edit_transaction_view(request, pk):
    transaction = Transaction.objects.get(pk=pk, user=request.user)
    form = TransactionForm(request.POST or None, instance=transaction)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'finance_app/edit_transaction.html', {'form': form})


# Delete transaction
@login_required
def delete_transaction_view(request, pk):
    transaction = Transaction.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        return redirect('dashboard')
    return render(request, 'finance_app/delete_transaction.html', {'transaction': transaction})


# Filtered dashboard view
@login_required
def dashboard_view(request):
    transactions = Transaction.objects.filter(user=request.user)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category')

    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    if category and category != 'All':
        transactions = transactions.filter(category__name=category)

    income = sum(t.amount for t in transactions if t.type == 'Income')
    expenses = sum(t.amount for t in transactions if t.type == 'Expense')

    category_data = {}
    for t in transactions:
        if t.type == 'Expense':
            name = t.category.name if t.category else "Uncategorized"
            category_data[name] = category_data.get(name, 0) + float(t.amount)

    from .ml_utils import get_pie_chart, get_monthly_expense_chart, forecast_expense
    pie_chart = get_pie_chart(category_data)
    line_chart = get_monthly_expense_chart(transactions.values())
    forecast = forecast_expense(transactions.values())

    all_categories = Category.objects.filter(user=request.user)
    anomalies = detect_spending_anomaly(transactions.values())

    return render(request, 'finance_app/dashboard.html', {
        'transactions': transactions,
        'income': income,
        'expenses': expenses,
        'category_data': category_data,
        'pie_chart': pie_chart,
        'line_chart': line_chart,
        'forecast': forecast,
        'all_categories': all_categories
    })

@login_required
def export_transactions_excel(request):
    transactions = Transaction.objects.filter(user=request.user).values(
        'date', 'title', 'amount', 'type', 'category__name', 'notes', 'is_recurring'
    )
    df = pd.DataFrame(transactions)
    df.rename(columns={
        'category__name': 'category',
        'is_recurring': 'recurring'
    }, inplace=True)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'
    df.to_excel(response, index=False)
    return response


@login_required
def add_transaction_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()
    return render(request, 'finance_app/add_transaction.html', {'form': form})
