'use client';
import { useEffect, useState } from 'react';
import axios from 'axios';
import SearchBar from '@/components/SearchBar';
import TickerList from '@/components/TickerList';
import { TickerData } from '@/types';

export default function Home() {
  const [tickers, setTickers] = useState<TickerData[]>([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    axios.get('/api/')
      .then((res) => setTickers(res.data.tickers))
      .catch(console.error);
  }, []);

  const filtered = tickers.filter((t) => t.ticker.toLowerCase().includes(search.toLowerCase()));
  console.log(filtered)

  return (
    <>
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '2rem', padding: '2rem', justifyContent: "center"}}>
      <div style={{ flex: 1 }}>
        <h2 style={{ marginBottom: '1rem', fontSize: '2rem' }}>Welcome to Stock Forecast</h2>
        <p style={{ fontSize: '1.2rem', marginTop: '3rem', marginBottom: '3rem' }}>
          Forecast one day ahead for popular stocks using AI trained on data from 2020-2024 (~400 top companies).
          <a 
            href="https://github.com/" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            Learn More
          </a>
        </p>

        <h2 style={{ fontSize: '2rem', marginTop: '1rem' }}>
          Select a Ticker to Start Forecasting
        </h2>
      </div>

      <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <img 
          src="/ForecastChart.png" 
          alt="Ticker forecast example" 
          style={{ maxWidth: '100%', borderRadius: '1rem', boxShadow: '0 4px 10px rgba(0,0,0,0.3)' }} 
        />
      </div>

    
    
    </div>
        <SearchBar value={search} onChange={setSearch} />
        <TickerList tickers={filtered}/>
        </>

  );
}
