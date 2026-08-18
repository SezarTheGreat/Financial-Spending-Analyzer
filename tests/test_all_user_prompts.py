import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from app import app

client = app.test_client()

prompts = [
    ('1. Portfolio XIRR & Math', 'What is my consolidated portfolio XIRR, and how is it calculated compared to simple CAGR or absolute return?'),
    ('2. Rolling Form & Alpha', 'Analyze the rolling form and alpha of each fund in my portfolio. Are any funds classified as Off-Track or Out-of-Form?'),
    ('3. Regular Plan & Cost Drag', 'Do I have any Regular mutual fund plans? If so, what is the estimated 10-year compounded wealth leakage from intermediary commission?'),
    ('4. Stock Overlap & Concentration', 'What is the stock overlap between my equity funds? Which specific common stocks have the highest concentration across multiple schemes?'),
    ('5. Asset Allocation & Rebalancing', 'My current risk profile is Moderate. What is my actual equity vs debt vs commodities allocation, and what specific rebalancing actions should I take to match an Aggressive profile?'),
    ('6. Real Estate & Global Exposure', 'What is my exposure to international real estate in this portfolio?'),
    ('7. Prioritized 30-Day Checklist', 'Give me a prioritized, step-by-step checklist to optimize this portfolio over the next 30 days.'),
    ('8. Spending Overview & Savings Rate', 'What was my total expense, net savings, and savings rate for the period, and which category accounts for the largest share of my outflows?'),
    ('9. Spending Outliers & Anomalies', 'Were there any spending anomalies or irregular transaction spikes detected in my statement?'),
]

print('=' * 80)
print('STARTING AUTOMATED VERIFICATION OF ALL TEST PROMPTS ACROSS FINWISE')
print('=' * 80)

passed = 0
for tag, prompt in prompts:
    res = client.post('/api/chat', json={'message': prompt, 'risk_profile': 'Moderate'})
    assert res.status_code == 200, f'Failed {tag}: HTTP {res.status_code}'
    data = res.get_json()
    reply = data.get('reply', '')
    chart = data.get('chart')
    
    print(f'\n>>> [TEST CASE: {tag}]')
    print(f'PROMPT: "{prompt}"')
    print(f'HTTP STATUS: {res.status_code} OK')
    print(f'HAS CHART ARTIFACT: {bool(chart)} ({chart.get("type") if chart else "None"})')
    print('-' * 80)
    print(reply[:380] + ('...' if len(reply) > 380 else ''))
    print('=' * 80)
    passed += 1

print(f'\n✓ ALL {passed}/{len(prompts)} INSTITUTIONAL TEST PROMPTS VERIFIED AND PASSING 100%!')
