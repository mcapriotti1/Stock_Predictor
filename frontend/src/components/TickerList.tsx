'use client';
import Link from 'next/link';
import { TickerData } from '@/types';

interface TickerListProps {
  tickers: TickerData[];
}

export default function TickerList({ tickers }: TickerListProps) {
  const Top = 14
  const topAmount = tickers.slice(0, Top);
  const rest = tickers.slice(Top);

  return (
    <div
      style={{
        maxHeight: '400px',
        overflowY: 'auto',
        display: 'flex',
        gap: '0.5rem',
        padding: '0 1rem',
        flexDirection: 'column',
      }}
    >
      {/* Hot Stocks */}
      {topAmount.length > 0 && (
        <div style={{ marginBottom: '1rem' }}>
          <h3 style={{ color: 'orange', margin: '0 0 0.5rem 0' }}>Hot Stocks (Lowest Error Over Last 10 Days)</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {topAmount.map((t) => (
              <Link
                key={t.ticker}
                href={`/ticker/${t.ticker}`}
                className='hotTickers'
              >
                {t.ticker}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Other Stocks */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
        {rest.map((t) => (
          <Link
            key={t.ticker}
            href={`/ticker/${t.ticker}`}
            className="tickers"
          >
            {t.ticker}
          </Link>
        ))}
      </div>
    </div>
  );
}
