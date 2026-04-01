"""Test volume filter on KXBTC15M (debut-fade strategy)."""
import subprocess, json, pathlib

OUTPUT_FILE = pathlib.Path('reports/backtest_result.json')

combos = [
    ('debut-fade baseline (KXBTC15M)', 'D', 'KXBTC15M'),
    ('debut-fade + vol filter (KXBTC15M)', 'Dvol', 'KXBTC15M'),
    # Also test on KXBTCD for comparison
    ('debut-fade baseline (KXBTCD)', 'D', 'KXBTCD'),
    ('debut-fade + vol filter (KXBTCD)', 'Dvol', 'KXBTCD'),
]

results = []
for label, strat, series in combos:
    cmd = ['python', '-m', 'edge_catcher', 'backtest',
           '--series', series, '--strategy', strat,
           '--start', '2025-10-01', '--end', '2025-12-31']
    print(f'Running {label}...', flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f'  ERROR (exit {r.returncode}): {r.stderr[:200]}', flush=True)
        continue
    try:
        data = json.loads(OUTPUT_FILE.read_text())
        row = {
            'label': label, 'series': series,
            'trades': data.get('total_trades', 0),
            'wins': data.get('wins', 0),
            'losses': data.get('losses', 0),
            'win_rate': round(data.get('win_rate', 0)*100, 1),
            'net_pnl': data.get('net_pnl_cents', 0),
            'sharpe': round(data.get('sharpe', 0), 2),
        }
        results.append(row)
        print(f'  trades={row["trades"]} wr={row["win_rate"]}% net={row["net_pnl"]:+d}¢ sharpe={row["sharpe"]}', flush=True)
    except Exception as e:
        print(f'  ERROR: {e}', flush=True)

print('\n=== RESULTS ===')
print(f'{"Label":<45} {"Trades":>7} {"WR":>7} {"Net PnL":>10} {"Sharpe":>8}')
print('-' * 80)
for r in results:
    flag = '✅' if r['net_pnl'] > 0 else '❌'
    print(f'{flag} {r["label"]:<43} {r["trades"]:>7} {r["win_rate"]:>6}% {r["net_pnl"]:>+9d}¢ {r["sharpe"]:>8.2f}')

import subprocess as sp
sp.run(['openclaw', 'system', 'event', '--text',
        'KXBTC15M volume filter test complete', '--mode', 'now'], capture_output=True)
