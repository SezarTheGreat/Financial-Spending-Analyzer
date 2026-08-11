from flask import Flask, request, jsonify, render_template, session
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
import math
import traceback
import io
import uuid
from supabase import create_client, Client

def make_json_safe(obj):
    """
    Recursively converts Pandas/NumPy objects into
    normal Python types so Flask can jsonify them.
    """

    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}

    elif isinstance(obj, list):
        return [make_json_safe(i) for i in obj]

    elif isinstance(obj, tuple):
        return tuple(make_json_safe(i) for i in obj)

    elif isinstance(obj, np.integer):
        return int(obj)

    elif isinstance(obj, np.floating):
        if math.isnan(obj):
            return None
        return float(obj)

    elif isinstance(obj, np.bool_):
        return bool(obj)

    elif isinstance(obj, pd.Timestamp):
        return obj.strftime("%Y-%m-%d")

    elif isinstance(obj, pd.Period):
        return str(obj)

    elif pd.isna(obj):
        return None

    return obj

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

# Backend-only Supabase client. SUPABASE_SERVICE_ROLE_KEY must NEVER be
# sent to the browser or committed to git — set it as a Render env var only.
# It bypasses Row Level Security, which is exactly why the frontend must
# never see it: the frontend never talks to Supabase directly, only
# through this Flask backend.
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

UPLOAD_BUCKET = "finwise-uploads"
UPLOADS_TABLE = "uploads"

CATEGORY_MAP = {
    'zomato': 'Food & Dining', 'swiggy': 'Food & Dining', 'restaurant': 'Food & Dining',
    'cafe': 'Food & Dining', 'food': 'Food & Dining', 'pizza': 'Food & Dining',
    'amazon': 'Shopping', 'flipkart': 'Shopping', 'myntra': 'Shopping',
    'meesho': 'Shopping', 'shop': 'Shopping',
    'uber': 'Transportation', 'ola': 'Transportation', 'metro': 'Transportation',
    'petrol': 'Transportation', 'fuel': 'Transportation',
    'netflix': 'Entertainment', 'spotify': 'Entertainment', 'movie': 'Entertainment',
    'game': 'Entertainment', 'prime': 'Entertainment',
    'electricity': 'Utilities', 'water': 'Utilities', 'wifi': 'Utilities',
    'internet': 'Utilities', 'mobile': 'Utilities', 'airtel': 'Utilities', 'jio': 'Utilities',
    'hospital': 'Healthcare', 'pharmacy': 'Healthcare', 'doctor': 'Healthcare',
    'medicine': 'Healthcare', 'apollo': 'Healthcare',
    'salary': 'Income', 'freelance': 'Income', 'interest': 'Income',
    'rent': 'Housing', 'maintenance': 'Housing',
    'college': 'Education', 'course': 'Education', 'books': 'Education', 'udemy': 'Education',
}

CATEGORY_COLORS = {
    'Food & Dining': '#F4A7B9', 'Shopping': '#F5E642',
    'Transportation': '#B8D4A8', 'Entertainment': '#C9B8E8',
    'Utilities': '#FFD9A0', 'Healthcare': '#A8D4D4',
    'Education': '#D4A8C9', 'Housing': '#F4C7A7',
    'Income': '#B8E8C9', 'Other': '#E8E8E8',
}

def map_category(desc):
    d = str(desc).lower()
    for k, v in CATEGORY_MAP.items():
        if k in d:
            return v
    return 'Other'

def preprocess(df):
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    date_col = next((c for c in df.columns if 'date' in c), None)
    if date_col:
        df['date'] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=['date'])
    amt_col = next(
    (c for c in df.columns if any(x in c for x in ['amount', 'amt', 'debit', 'credit', 'value'])),
    None)
    if amt_col:
        df["amount"] = (
        pd.to_numeric(
            df[amt_col]
            .astype(str)
            .str.replace(r"[₹,\s]", "", regex=True),
            errors="coerce"
        )
        .abs()
        .astype(float)
    )
    df = df.dropna(subset=['amount'])
    df = df[df['amount'] > 0]
    desc_col = next((c for c in df.columns if any(x in c for x in ['desc','narr','particular','detail','remark'])), None)
    if desc_col:
        df['description'] = df[desc_col].astype(str)
    elif 'description' not in df.columns:
        df['description'] = 'Transaction'
    if "category" not in df.columns:
        df["category"] = df["description"].apply(map_category)
    if "type" not in df.columns:
        df["type"] = df["category"].apply(
        lambda c: "income" if c == "Income" else "expense"
    )
           # Normalize transaction type
    df["type"] = (df["type"] .astype(str).str.strip().str.lower())
    print("Normalized Types:")
    print(df["type"].unique())
    df["category"] = (df["category"].fillna("Other").astype(str).str.strip())

    df['month'] = df['date'].dt.to_period('M').astype(str)
    df['weekday'] = df['date'].dt.day_name()
    print("\n========== DEBUG ==========")
    print(df.head())
    print("\nTypes:")
    print(df["type"].value_counts())
    print("\nCategories:")
    print(df["category"].value_counts())
    print("\nMonths:")
    print(df["month"].value_counts())
    print("===========================\n")
    print("\n====== FINAL TYPE VALUES ======")
    print(df["type"].value_counts())
    print("===============================\n")
    return df

def get_summary(df):
    income = df[df['type']=='income']['amount'].sum()
    expenses = df[df['type']=='expense']['amount'].sum()
    savings = income - expenses
    sr = round(savings / income * 100, 1) if income > 0 else 0
    return {
        'total_income': round(income, 2),
        'total_expenses': round(expenses, 2),
        'net_savings': round(savings, 2),
        'savings_rate': sr,
        'total_transactions': len(df),
        'date_range': {'start': df['date'].min().strftime('%d %b %Y'), 'end': df['date'].max().strftime('%d %b %Y')}
    }

def get_categories(df):
    df["category"] = (
    df["category"]
    .astype(str)
    .str.strip()
)
    exp = df[df['type']=='expense']
    cat = exp.groupby('category')['amount'].sum().sort_values(ascending=False).reset_index()
    total = cat['amount'].sum()
    if total == 0:
        return {
        "labels": [],
        "values": [],
        "percentages": [],
        "colors": []
    }
    return {
        'labels': cat['category'].tolist(),
        'values': cat['amount'].round(2).tolist(),
        'percentages': (cat['amount'] / total * 100).round(1).tolist(),
        'colors': [CATEGORY_COLORS.get(c, '#E8E8E8') for c in cat['category']],
    }

def get_income_vs_expense(df):
    m = df.groupby(['month','type'])['amount'].sum().unstack(fill_value=0).reset_index().sort_values('month')
    inc = m.get('income', pd.Series([0]*len(m))).tolist()
    exp = m.get('expense', pd.Series([0]*len(m))).tolist()
    return {
        'months': m['month'].tolist(),
        'income': [round(x,2) for x in inc],
        'expense': [round(x,2) for x in exp],
        'savings': [round(i-e,2) for i,e in zip(inc,exp)],
    }

def get_monthly_overview(df):
    exp = df[df['type']=='expense']
    m = exp.groupby(['month','category'])['amount'].sum().unstack(fill_value=0).reset_index().sort_values('month')
    cats = [c for c in m.columns if c != 'month']
    return {
        'months': m['month'].tolist(),
        'series': [{'name': c, 'data': m[c].round(2).tolist(), 'color': CATEGORY_COLORS.get(c,'#E8E8E8')} for c in cats]
    }

def get_weekly_breakdown(df):
    exp = df[df['type']=='expense']
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    w = exp.groupby('weekday')['amount'].sum().reindex(days, fill_value=0)
    return {'days': days, 'amounts': w.round(2).tolist(), 'peak_day': w.idxmax()}

def get_trends(df):
    exp = df[df['type']=='expense'].sort_values('date')
    daily = exp.groupby('date')['amount'].sum().reset_index()
    return {
        'dates': [d.strftime('%Y-%m-%d') for d in daily['date']],
        'daily': daily['amount'].round(2).tolist(),
    }

def detect_anomalies(df):
    exp = df[df['type']=='expense']
    stats = exp.groupby('category')['amount'].agg(['mean','std']).reset_index()
    merged = exp.merge(stats, on='category')
    merged['z'] = (merged['amount'] - merged['mean']) / (merged['std'] + 1e-9)
    top = merged[merged['z'] > 2.0].sort_values('z', ascending=False).head(10)
    return {'anomalies': [{'date': r['date'].strftime('%d %b %Y'), 'description': r['description'],
        'amount': round(r['amount'],2), 'category': r['category'], 'z_score': round(r['z'],2)} for _,r in top.iterrows()]}

def get_calendar_heatmap(df):
    exp = df[df['type']=='expense']
    daily = exp.groupby('date')['amount'].sum().reset_index()
    return {
        'dates': [d.strftime('%Y-%m-%d') for d in daily['date']],
        'amounts': daily['amount'].round(2).tolist(),
        'max': round(daily['amount'].max(), 2) if len(daily) > 0 else 0,
    }

def get_health_score(df):
    s = get_summary(df)
    sr = s['savings_rate']
    savings_score = min(sr * 2, 100)
    exp = df[df['type']=='expense']
    cat = exp.groupby('category')['amount'].sum()
    if len(cat)==0:
        return {
            "score":0,
            "grade":"N/A",
            "savings_rate":0,
            "spending_rate":0,
            "top_category":"N/A",
            "top_category_pct":0
        }
    total_exp = s['total_expenses']
    food_pct = (cat.get('Food & Dining', 0) / total_exp * 100) if total_exp > 0 else 0
    ent_pct = (cat.get('Entertainment', 0) / total_exp * 100) if total_exp > 0 else 0
    necessity_score = max(0, 100 - max(0, food_pct - 30) * 1.5 - max(0, ent_pct - 10) * 2)
    anom = detect_anomalies(df)
    anomaly_score = max(0, 100 - len(anom['anomalies']) * 10)
    score = max(0, min(100, round(savings_score * 0.5 + necessity_score * 0.3 + anomaly_score * 0.2)))
    grade = 'A+' if score>=90 else 'A' if score>=80 else 'B' if score>=70 else 'C' if score>=60 else 'D'
    return {
        'score': score, 'grade': grade,
        'savings_rate': sr, 'spending_rate': round(100-sr, 1),
        'top_category': cat.idxmax() if len(cat) > 0 else 'N/A',
        'top_category_pct': round(cat.max() / total_exp * 100, 1) if total_exp > 0 else 0,
    }

def generate_ai_insights(df):
    s = get_summary(df)
    h = get_health_score(df)
    w = get_weekly_breakdown(df)
    cat_data = get_categories(df)
    sr = s['savings_rate']
    insights = []
    if sr >= 30:
        insights.append({'type':'positive','icon':'🌿','text':f"Saving {sr}% of income — excellent financial health!"})
    elif sr >= 15:
        insights.append({'type':'neutral','icon':'📊','text':f"{sr}% savings rate is decent. Aim for 30%+ for a stronger cushion."})
    else:
        insights.append({'type':'warning','icon':'⚠️','text':f"Only {sr}% savings rate. Try cutting discretionary spend by 10%."})
    if cat_data['labels']:
        insights.append({'type':'info','icon':'🔍','text':f"'{cat_data['labels'][0]}' is your top expense at {cat_data['percentages'][0]}% of spending."})
    insights.append({'type':'info','icon':'📅','text':f"{w['peak_day']}s are your peak spending days — schedule big purchases earlier in the week."})
    tips = [
        {'icon':'💰','title':'Emergency Fund','text':f"Target ₹{round(s['total_expenses']/12*6):,} — 6 months of expenses — as your safety net."},
        {'icon':'🎯','title':'50/30/20 Rule','text':'Split income: 50% needs, 30% wants, 20% savings/investments.'},
        {'icon':'📈','title':'Invest Surplus','text':f"Your ₹{round(s['net_savings']):,} savings could compound in index funds or SIPs."},
    ]
    return {'insights': insights, 'tips': tips, 'health': h}

def generate_sample_data():
    np.random.seed(42)
    configs = [
        ('Food & Dining',4500,800,'expense'), ('Shopping',3200,1200,'expense'),
        ('Transportation',1800,400,'expense'), ('Entertainment',1500,600,'expense'),
        ('Utilities',2200,300,'expense'), ('Healthcare',600,400,'expense'),
        ('Education',1200,400,'expense'), ('Housing',8000,500,'expense'),
        ('Income',45000,2000,'income'),
    ]
    descs = {
        'Food & Dining':['Zomato order','Swiggy dinner','Restaurant lunch','Cafe coffee','Groceries'],
        'Shopping':['Amazon purchase','Flipkart order','Myntra clothes','Mall shopping','Meesho'],
        'Transportation':['Uber ride','Ola cab','Metro card','Petrol fill','Rapido'],
        'Entertainment':['Netflix subscription','Spotify premium','Movie tickets','BookMyShow','Gaming'],
        'Utilities':['Electricity bill','Water bill','Airtel broadband','Mobile recharge','Gas'],
        'Healthcare':['Apollo pharmacy','Doctor visit','Lab test','Medicine'],
        'Education':['Coursera course','Books','College fee','Udemy'],
        'Housing':['Rent','Society maintenance','Home repair'],
        'Income':['Salary credit','Freelance payment','Interest credit'],
    }
    recs = []
    start = datetime.now() - timedelta(days=365)
    for cat, mean, std, typ in configs:
        n = 12 if cat == 'Income' else np.random.randint(20, 55)
        for _ in range(n):
            amt = max(50, np.random.normal(mean if cat=='Income' else mean/15, std/8 if cat!='Income' else std/5))
            date = start + timedelta(days=np.random.randint(0, 365))
            recs.append({'date': date.strftime('%Y-%m-%d'), 'description': np.random.choice(descs[cat]),
                         'amount': round(amt, 2), 'category': cat, 'type': typ})
    df = pd.DataFrame(recs)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)
    df['weekday'] = df['date'].dt.day_name()
    return df

def save_df(dataframe):
    """
    Persist the uploaded/sample DataFrame to a private Supabase Storage
    bucket (as Parquet — smaller and more portable than pickle) and log
    it in the `uploads` table. The session cookie only ever carries the
    storage path, never the data itself, so any worker process handling
    a later request can fetch the same file straight from Supabase.
    """
    # Each browser session gets a stable id so its files are grouped
    # together in storage, e.g. finwise-uploads/<session_id>/<upload_id>.parquet
    session_id = session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id

    upload_id = str(uuid.uuid4())
    storage_path = f"{session_id}/{upload_id}.parquet"

    buf = io.BytesIO()
    dataframe.to_parquet(buf, index=False)
    buf.seek(0)

    supabase.storage.from_(UPLOAD_BUCKET).upload(
        storage_path,
        buf.getvalue(),
        {"content-type": "application/octet-stream"},
    )

    supabase.table(UPLOADS_TABLE).insert({
        "session_id": session_id,
        "storage_path": storage_path,
    }).execute()

    session["storage_path"] = storage_path

def load_df():
    """
    Returns (dataframe, error_message). On any failure, error_message
    explains exactly what went wrong (no session yet, Supabase download
    failed, or the stored file couldn't be read) so it can be surfaced
    directly in the API response instead of a generic 'No data'.
    """
    storage_path = session.get("storage_path")
    if not storage_path:
        return None, "No upload found in this session — upload a file or load sample data first."
    try:
        raw = supabase.storage.from_(UPLOAD_BUCKET).download(storage_path)
    except Exception as e:
        traceback.print_exc()
        return None, f"Supabase download failed: {type(e).__name__}: {e}"
    try:
        return pd.read_parquet(io.BytesIO(raw)), None
    except Exception as e:
        traceback.print_exc()
        return None, f"Couldn't read stored file: {type(e).__name__}: {e}"

def api_response(builder_fn):
    """Runs builder_fn(dataframe) and wraps it as JSON, or returns the real error."""
    d, err = load_df()
    if d is None:
        return jsonify({'error': err or 'No data'}), 400
    return jsonify(make_json_safe(builder_fn(d)))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/api/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    f = request.files['file']
    if not f.filename.endswith('.csv'):
        return jsonify({'error': 'Please upload a .csv file'}), 400
    try:
        uploaded_df = preprocess(pd.read_csv(f))
        save_df(uploaded_df)
        return jsonify(make_json_safe({'success': True, 'summary': get_summary(uploaded_df)}))
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
            }),500

@app.route('/api/sample')
def load_sample():
    sample_df = generate_sample_data()
    save_df(sample_df)
    return jsonify(make_json_safe({'success': True, 'summary': get_summary(sample_df)}))

@app.route('/api/overview')
def api_overview():
    return api_response(get_summary)
@app.route('/api/categories')
def api_categories():
    return api_response(get_categories)
@app.route('/api/income-expense')
def api_ie():
    return api_response(get_income_vs_expense)
@app.route('/api/monthly')
def api_monthly():
    return api_response(get_monthly_overview)
@app.route('/api/weekly')
def api_weekly():
    return api_response(get_weekly_breakdown)
@app.route('/api/trends')
def api_trends():
    return api_response(get_trends)
@app.route('/api/anomalies')
def api_anomalies():
    return api_response(detect_anomalies)
@app.route('/api/calendar')
def api_calendar():
    return api_response(get_calendar_heatmap)
@app.route('/api/health')
def api_health():
    return api_response(get_health_score)
@app.route('/api/insights')
def api_insights():
    return api_response(generate_ai_insights)
@app.route('/api/transactions')
def api_transactions():
    d, err = load_df()
    if d is None: return jsonify({'error': err or 'No data'}), 400
    page = int(request.args.get('page',1)); per = 20
    s = d.sort_values('date', ascending=False)
    chunk = s.iloc[(page-1)*per:page*per]
    return jsonify(make_json_safe({'transactions': [{'date':r['date'].strftime('%d %b %Y'),'description':r['description'],
        'amount':round(r['amount'],2),'category':r['category'],'type':r['type']} for _,r in chunk.iterrows()],
        'total': len(d), 'page': page}))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
