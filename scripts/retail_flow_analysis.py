"""
Track A: Retail Flow Score Analysis

For each KXBTCD market, compute a flow score from the first N trades:
- Flow = (YES_taker_volume - NO_taker_volume) / total_volume
- Range: -1.0 (all NO takers) to +1.0 (all YES takers)
- Hypothesis: extreme flow predicts settlement (retail is wrong at extremes)

Also look at:
- Small trades (count <= 10) vs large trades (count > 100) — retail vs institutional
- Flow in first 25% vs last 25% of market lifecycle
"""

import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

DB_PATH = Path("data/kalshi.db")

def analyze_flow(series: str = "KXBTCD", first_n: int = 50, year: str = "2025"):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA cache_size = -262144")  # 256MB cache
    
    print(f"Loading markets for {series} in {year}...")
    
    # Get settled markets with results
    markets = conn.execute(f"""
        SELECT ticker, result, close_time 
        FROM markets 
        WHERE series_ticker = ? 
        AND result IN ('yes', 'no')
        AND close_time LIKE '{year}%'
    """, (series,)).fetchall()
    
    print(f"Found {len(markets)} settled markets")
    
    results = []
    batch_size = 500
    
    for i in range(0, len(markets), batch_size):
        batch = markets[i:i+batch_size]
        tickers = [m[0] for m in batch]
        result_map = {m[0]: m[1] for m in batch}
        
        placeholders = ",".join("?" * len(tickers))
        
        # Get first N trades per market, ordered by time
        trades = conn.execute(f"""
            SELECT ticker, taker_side, count, yes_price, created_time,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY created_time) as rn
            FROM trades 
            WHERE ticker IN ({placeholders})
        """, tickers).fetchall()
        
        # Group by ticker
        ticker_trades = defaultdict(list)
        for t in trades:
            if t[5] <= first_n:  # rn <= first_n
                ticker_trades[t[0]].append(t)
        
        for ticker, mkt_trades in ticker_trades.items():
            if len(mkt_trades) < 10:  # skip thin markets
                continue
                
            yes_vol = sum(t[2] for t in mkt_trades if t[1] == 'yes')
            no_vol = sum(t[2] for t in mkt_trades if t[1] == 'no')
            total_vol = yes_vol + no_vol
            
            if total_vol == 0:
                continue
            
            flow_score = (yes_vol - no_vol) / total_vol  # -1 to +1
            
            # Small trades only (retail proxy: count <= 10)
            small_yes = sum(t[2] for t in mkt_trades if t[1] == 'yes' and t[2] <= 10)
            small_no = sum(t[2] for t in mkt_trades if t[1] == 'no' and t[2] <= 10)
            small_total = small_yes + small_no
            small_flow = (small_yes - small_no) / small_total if small_total > 0 else 0
            
            # Large trades only (institutional proxy: count > 100)
            big_yes = sum(t[2] for t in mkt_trades if t[1] == 'yes' and t[2] > 100)
            big_no = sum(t[2] for t in mkt_trades if t[1] == 'no' and t[2] > 100)
            big_total = big_yes + big_no
            big_flow = (big_yes - big_no) / big_total if big_total > 0 else 0
            
            avg_price = sum(t[3] for t in mkt_trades) / len(mkt_trades)
            
            result = result_map.get(ticker, 'unknown')
            # YES settled = 1, NO settled = 0
            settled_yes = 1 if result == 'yes' else 0
            
            results.append({
                'ticker': ticker,
                'flow_score': flow_score,
                'small_flow': small_flow,
                'big_flow': big_flow,
                'total_vol': total_vol,
                'n_trades': len(mkt_trades),
                'avg_price': avg_price,
                'settled_yes': settled_yes,
            })
        
        if (i + batch_size) % 2000 == 0:
            print(f"  Processed {i + batch_size}/{len(markets)} markets...")
    
    print(f"\nAnalyzed {len(results)} markets with >= 10 trades")
    
    # Bucket by flow score
    buckets = [
        ("Strong YES flow (>0.5)", lambda r: r['flow_score'] > 0.5),
        ("Mild YES flow (0.1-0.5)", lambda r: 0.1 < r['flow_score'] <= 0.5),
        ("Neutral (-0.1 to 0.1)", lambda r: -0.1 <= r['flow_score'] <= 0.1),
        ("Mild NO flow (-0.5 to -0.1)", lambda r: -0.5 <= r['flow_score'] < -0.1),
        ("Strong NO flow (<-0.5)", lambda r: r['flow_score'] < -0.5),
    ]
    
    print("\n=== FLOW SCORE vs SETTLEMENT ===")
    print(f"{'Bucket':40s}  {'N':>6}  {'YES%':>6}  {'NO%':>6}  {'Avg Price':>10}")
    print("-" * 75)
    
    for name, filt in buckets:
        group = [r for r in results if filt(r)]
        if not group:
            continue
        n = len(group)
        yes_pct = sum(r['settled_yes'] for r in group) / n * 100
        no_pct = 100 - yes_pct
        avg_p = sum(r['avg_price'] for r in group) / n
        print(f"{name:40s}  {n:>6}  {yes_pct:>5.1f}%  {no_pct:>5.1f}%  {avg_p:>9.1f}¢")
    
    # Same for SMALL trades only (retail)
    print("\n=== RETAIL FLOW (small trades ≤10) vs SETTLEMENT ===")
    small_buckets = [
        ("Retail strong YES (>0.5)", lambda r: r['small_flow'] > 0.5),
        ("Retail mild YES (0.1-0.5)", lambda r: 0.1 < r['small_flow'] <= 0.5),
        ("Retail neutral (-0.1 to 0.1)", lambda r: -0.1 <= r['small_flow'] <= 0.1),
        ("Retail mild NO (-0.5 to -0.1)", lambda r: -0.5 <= r['small_flow'] < -0.1),
        ("Retail strong NO (<-0.5)", lambda r: r['small_flow'] < -0.5),
    ]
    
    print(f"{'Bucket':40s}  {'N':>6}  {'YES%':>6}  {'NO%':>6}")
    print("-" * 60)
    
    for name, filt in small_buckets:
        group = [r for r in results if filt(r)]
        if not group:
            continue
        n = len(group)
        yes_pct = sum(r['settled_yes'] for r in group) / n * 100
        no_pct = 100 - yes_pct
        print(f"{name:40s}  {n:>6}  {yes_pct:>5.1f}%  {no_pct:>5.1f}%")
    
    # Same for BIG trades (institutional)
    print("\n=== INSTITUTIONAL FLOW (big trades >100) vs SETTLEMENT ===")
    big_buckets = [
        ("Inst strong YES (>0.5)", lambda r: r['big_flow'] > 0.5),
        ("Inst mild YES (0.1-0.5)", lambda r: 0.1 < r['big_flow'] <= 0.5),
        ("Inst neutral (-0.1 to 0.1)", lambda r: -0.1 <= r['big_flow'] <= 0.1),
        ("Inst mild NO (-0.5 to -0.1)", lambda r: -0.5 <= r['big_flow'] < -0.1),
        ("Inst strong NO (<-0.5)", lambda r: r['big_flow'] < -0.5),
    ]
    
    print(f"{'Bucket':40s}  {'N':>6}  {'YES%':>6}  {'NO%':>6}")
    print("-" * 60)
    
    for name, filt in big_buckets:
        group = [r for r in results if filt(r)]
        if not group:
            continue
        n = len(group)
        yes_pct = sum(r['settled_yes'] for r in group) / n * 100
        no_pct = 100 - yes_pct
        print(f"{name:40s}  {n:>6}  {yes_pct:>5.1f}%  {no_pct:>5.1f}%")
    
    # Key question: when retail and institutional flow DISAGREE, who's right?
    print("\n=== FLOW DIVERGENCE: Retail vs Institutional ===")
    divergence = [
        ("Retail YES + Inst NO", lambda r: r['small_flow'] > 0.3 and r['big_flow'] < -0.3),
        ("Retail NO + Inst YES", lambda r: r['small_flow'] < -0.3 and r['big_flow'] > 0.3),
        ("Both agree YES", lambda r: r['small_flow'] > 0.3 and r['big_flow'] > 0.3),
        ("Both agree NO", lambda r: r['small_flow'] < -0.3 and r['big_flow'] < -0.3),
    ]
    
    print(f"{'Pattern':40s}  {'N':>6}  {'YES%':>6}  {'Edge':>8}")
    print("-" * 65)
    
    for name, filt in divergence:
        group = [r for r in results if filt(r)]
        if not group:
            print(f"{name:40s}  {'N/A':>6}")
            continue
        n = len(group)
        yes_pct = sum(r['settled_yes'] for r in group) / n * 100
        avg_p = sum(r['avg_price'] for r in group) / n
        # Edge = actual settlement rate - implied probability (avg_price/100)
        edge = yes_pct - avg_p
        print(f"{name:40s}  {n:>6}  {yes_pct:>5.1f}%  {edge:>+7.1f}pp")
    
    conn.close()

if __name__ == "__main__":
    series = sys.argv[1] if len(sys.argv) > 1 else "KXBTCD"
    first_n = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    analyze_flow(series, first_n)
