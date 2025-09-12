'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import axios from 'axios';
import { TickerDetail } from '@/types';
import ChartTabs from '@/components/ChartTabs';

export default function TickerPage() {
  const params = useParams();
  const ticker = params.ticker;
  const [data, setData] = useState<TickerDetail | null>(null);

  useEffect(() => {
    axios.get(`/api/predict/${ticker}`)
      .then((res) => setData(res.data))
      .catch(console.error);
  }, [ticker]);

  if (!data) return <p>Loading...</p>;
    console.log(data?.actuals)


  return (
    <div>
      <h1>{data.ticker}</h1>
      <h2>Mean Absolute Error (MAE) Percent from 2024-2025: {data.mae}%</h2>
      <ChartTabs
        actuals={data.actuals}
        predictions={data.predictions}
        pastActuals={data.actuals.slice(-11)}
        pastPredictions={data.predictions.slice(3, 13)}
        mae={data.mae}
        dailyMae={data.dailyMae}
        ticker={data.ticker}
      />
    </div>
  );
}
