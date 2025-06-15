import matplotlib.pyplot as plt
import io, base64
from collections import defaultdict
from datetime import datetime
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib
import os


matplotlib.use('Agg')
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(__file__), '.matplotlib')


def get_pie_chart(category_data):
    fig, ax = plt.subplots()
    ax.pie(category_data.values(), labels=category_data.keys(), autopct='%1.1f%%')
    ax.set_title("Expenses by Category")
    return save_chart_to_base64(fig)


def get_monthly_expense_chart(transactions):
    df = pd.DataFrame(transactions)
    if df.empty or 'amount' not in df.columns:
        return None

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['amount', 'date'])

    df['month'] = df['date'].dt.to_period('M')
    monthly = df[df['type'] == 'Expense'].groupby('month')['amount'].sum()

    if monthly.empty:
        return None

    fig, ax = plt.subplots()
    monthly.plot(ax=ax, marker='o')
    ax.set_title("Monthly Expense Trend")
    ax.set_ylabel("Amount (₹)")
    return save_chart_to_base64(fig)



def forecast_expense(transactions):
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler

    df = pd.DataFrame(transactions)
    if df.empty:
        return None

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date', 'amount'])
    df = df[df['type'] == 'Expense']

    if df.empty:
        return None

    df['month'] = df['date'].dt.to_period('M').astype(str)
    df['weekday'] = df['date'].dt.weekday
    df['day'] = df['date'].dt.day

    grouped = df.groupby('month')['amount'].sum().reset_index()
    if len(grouped) < 2:
        return None

    grouped['month_num'] = range(1, len(grouped)+1)
    X = grouped[['month_num']]
    y = grouped['amount']

    model = LinearRegression()
    model.fit(X, y)
    next_month = [[len(grouped)+1]]
    predicted = model.predict(next_month)

    return round(predicted[0], 2)

def detect_spending_anomaly(transactions):
    df = pd.DataFrame(transactions)
    if df.empty or 'amount' not in df.columns:
        return None

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date', 'amount'])
    df = df[df['type'] == 'Expense']
    df['month'] = df['date'].dt.to_period('M')
    monthly = df.groupby('month')['amount'].sum()

    if len(monthly) < 2:
        return None

    mean = monthly.mean()
    std = monthly.std()
    threshold = mean + 2 * std

    spikes = monthly[monthly > threshold]
    return spikes.to_dict()



def save_chart_to_base64(fig):
    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')
