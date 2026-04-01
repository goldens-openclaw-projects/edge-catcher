"""Full-range validation: fade-long-vol and stacked on all of 2025."""
import subprocess, json, pathlib

OUTPUT_FILE = pathlib.Path('reports/backtest_result.json')

combos = [
    ('fade-long baseline (2025)', 'C', '2025-01-01', '2025-12-31'),
    ('fade-long + vol filter (2025)', 'Cvol', '2025-01-01', '2025-12-31'),
    ('fade-long + stacked (2025)', 'Cstack', '2025-01-01', '2025-12-31'),
]

FEE_PCT = '1.0'  # 1.0 = full Kalshi taker fee (0.07 * P * (1-P))

results = []
for label, strat, start, end in combos:
    cmd = ['python', '-m', 'edge_catcher', 'backtest',
           '--series', 'KXBTCD', '--strategy', strat,
           '--start', start, '--end', end,
           '--fee-pct', FEE_PCT]
    print(f'Running {label}...', flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f'  ERROR (exit {r.returncode}): {r.stderr[:300]}', flush=True)
        results.append({'label': label, 'error': True})
        continue
    try:
        data = json.loads(OUTPUT_FILE.read_text())
        row = {
            'label': label, 'strategy': strat, 'period': f'{start} to {end}',
            'trades': data.get('total_trades', 0),
            'wins': data.get('wins', 0),
            'losses': data.get('losses', 0),
            'win_rate': round(data.get('win_rate', 0)*100, 1),
            'net_pnl': data.get('net_pnl_cents', 0),
            'fees_paid': data.get('total_fees_paid', 0),
            'sharpe': round(data.get('sharpe', 0), 2),
            'avg_win': round(data.get('avg_win_cents', 0), 1),
            'avg_loss': round(data.get('avg_loss_cents', 0), 1),
        }
        results.append(row)
        pnl = row['net_pnl']
        print(f'  trades={row["trades"]} wr={row["win_rate"]}% net={pnl:+d}¢ sharpe={row["sharpe"]}', flush=True)
    except Exception as e:
        print(f'  PARSE ERROR: {e}', flush=True)
        results.append({'label': label, 'error': str(e)})

pathlib.Path('reports/fullrange_validation.json').write_text(json.dumps(results, indent=2))

print('\n=== FULL-RANGE VALIDATION (2025) ===')
print(f'{"Label":<38} {"Trades":>8} {"WR":>7} {"Net PnL":>11} {"Sharpe":>8}')
print('-' * 75)
for r in results:
    if 'error' in r:
        print(f'  ERROR: {r["label"]}')
        continue
    flag = '✅' if r['net_pnl'] > 0 else '❌'
    print(f'{flag} {r["label"]:<36} {r["trades"]:>8} {r["win_rate"]:>6}% {r["net_pnl"]:>+10d}¢ {r["sharpe"]:>8.2f}')

import subprocess as sp
sp.run(['openclaw', 'system', 'event', '--text',
        'Full-range validation (2025) complete — results in reports/fullrange_validation.json',
        '--mode', 'now'], capture_output=True)
