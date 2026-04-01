"""Test filter stacking: vol-only, momentum-only, and vol+momentum combined on fade-long."""
import subprocess, json, pathlib

OUTPUT_FILE = pathlib.Path('reports/backtest_result.json')

combos = [
    ('fade-long baseline', 'C'),
    ('fade-long + vol filter', 'Cvol'),
    ('fade-long + BTC momentum', 'Cmom'),
    ('fade-long + vol + momentum (stacked)', 'Cstack'),
]

results = []
for label, strat in combos:
    cmd = ['python', '-m', 'edge_catcher', 'backtest',
           '--series', 'KXBTCD', '--strategy', strat,
           '--start', '2025-10-01', '--end', '2025-12-31']
    print(f'Running {label} ({strat})...', flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f'  ERROR (exit {r.returncode}): {r.stderr[:200]}', flush=True)
        continue
    try:
        data = json.loads(OUTPUT_FILE.read_text())
        row = {
            'label': label,
            'trades': data.get('total_trades', 0),
            'wins': data.get('wins', 0),
            'losses': data.get('losses', 0),
            'win_rate': round(data.get('win_rate', 0)*100, 1),
            'net_pnl': data.get('net_pnl_cents', 0),
            'sharpe': round(data.get('sharpe', 0), 2),
            'avg_win': round(data.get('avg_win_cents', 0), 1),
            'avg_loss': round(data.get('avg_loss_cents', 0), 1),
        }
        results.append(row)
        pnl = row['net_pnl']
        print(f'  trades={row["trades"]} wr={row["win_rate"]}% net={pnl:+d}¢ sharpe={row["sharpe"]}', flush=True)
    except Exception as e:
        print(f'  ERROR: {e}', flush=True)

print('\n=== COMPARISON TABLE ===')
print(f'{"Label":<42} {"Trades":>7} {"WR":>7} {"Net PnL":>10} {"Sharpe":>8}')
print('-' * 78)
for r in results:
    flag = '✅' if r['net_pnl'] > 0 else '❌'
    print(f'{flag} {r["label"]:<40} {r["trades"]:>7} {r["win_rate"]:>6}% {r["net_pnl"]:>+9d}¢ {r["sharpe"]:>8.2f}')

import subprocess as sp
sp.run(['openclaw', 'system', 'event', '--text',
        'Filter stacking test complete — results ready', '--mode', 'now'], capture_output=True)
