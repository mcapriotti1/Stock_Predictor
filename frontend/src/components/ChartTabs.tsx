'use client';
import { act, useState } from 'react';
import { Chart as ChartJS, LineElement, PointElement, CategoryScale, LinearScale, Title, Legend, Tooltip  } from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Actual, Prediction, TickerData } from '@/types';
import { useRouter } from "next/navigation";
import { FaArrowUp, FaArrowDown } from 'react-icons/fa';
import Link from 'next/link';

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Title, Legend, Tooltip);

interface ChartTabsProps {
  actuals: Actual[];
  predictions: Prediction[];
  pastPredictions?: Prediction[];
  pastActuals?: Actual[];
  mae?: number;
  ticker: String;
  dailyMae?: number;
}

interface ForecastChartProps {
  actuals: Actual[];
  predictions: Prediction[];
}

const ForecastChart = ({ actuals, predictions }: ForecastChartProps) => {
  const todayActual = Number(actuals[actuals.length - 1].close.toFixed(2));
  const todayPrediction = Number(predictions[predictions.length - 1]?.prediction.toFixed(2));

  const changeAmount = todayPrediction && todayActual ? todayPrediction - todayActual : 0;
  const changePercent = todayPrediction && todayActual ? (changeAmount / todayActual) * 100 : 0;
  const isUp = changeAmount > 0;

  return (
    <div>
      <p style={{ fontSize: '2rem', margin: '0.5rem 0', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}>
        {todayPrediction !== undefined && (
          <>
            Current: ${todayActual.toFixed(2)}
            {isUp ? <FaArrowUp color="green" /> : <FaArrowDown color="red" />}
            <span style={{ color: isUp ? 'green' : 'red', fontWeight: 'bold' }}>
              {isUp ? '+' : '-'}${Math.abs(changeAmount).toFixed(2)} ({isUp ? '+' : '-'}{Math.abs(changePercent).toFixed(2)}%)
            </span>
            Predicted: ${todayPrediction?.toFixed(2)}
          </>
        )}
      </p>
    <Line
      data={{
        labels: [
          ...actuals.map(a => a.date),
          predictions.length ? predictions[predictions.length - 1].date : null,
        ].filter(Boolean),
        datasets: [
          {
            label: 'Actual',
            data: actuals.map(a => a.close),
            borderColor: getComputedStyle(document.documentElement).getPropertyValue('--color-actual'),
            pointRadius: Number(getComputedStyle(document.documentElement).getPropertyValue('--point-size')),
            pointBackgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--color-actual'),
            fill: false,
          },
          {
            label: 'Prediction',
            data: [
              ...Array(actuals.length - 1).fill(null),
              actuals[actuals.length - 1].close,
              predictions.length ? predictions[predictions.length - 1].prediction : null,
            ],
            borderColor: getComputedStyle(document.documentElement).getPropertyValue('--color-prediction'),
            pointRadius: Number(getComputedStyle(document.documentElement).getPropertyValue('--point-size')),
            pointBackgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--color-prediction'),
            fill: false,
          },
        ],
      }}
      options={{
        responsive: true,
        plugins: {
          
          title: {
            display: true,
            text: 'Forecast Prediction',
            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text'),
            font: {
              size: Number(getComputedStyle(document.documentElement).getPropertyValue('--chart-title-size')),
              weight: 'bold',
            },
            padding: {
              top: Number(getComputedStyle(document.documentElement).getPropertyValue('--chart-title-padding-top')),
              bottom: Number(getComputedStyle(document.documentElement).getPropertyValue('--chart-title-padding-bottom')),
            },
            align: 'center',
          },
          legend: {
            display: true,
            position: 'top',
            align: 'center',
            labels: {
              usePointStyle: true,   
              pointStyle: 'circ',
              color: getComputedStyle(document.documentElement).getPropertyValue('--color-text'),
            },
          },
          tooltip: {
            enabled: true,
            mode: 'index',
            intersect: false,
            callbacks: {
              label: function(context) {
                const datasetLabel = context.dataset.label;
                const value = context.raw;

                if (datasetLabel === 'Prediction') {
                  const actualDataset = context.chart.data.datasets.find(ds => ds.label === 'Actual');
                  const actualValue = actualDataset?.data[context.dataIndex];
                  if (actualValue != null) return null;
                  return `Prediction: ${Number(value).toFixed(2)}`;
                }
                if (datasetLabel === 'Actual' && value != null) {
                  return `Actual: ${Number(value).toFixed(2)}`;
                }
                return null;
              },
            },
          },

          
        },
        interaction: { mode: 'index', intersect: false },
        scales: {
          x: {
            title: { display: true, text: 'Date', color: getComputedStyle(document.documentElement).getPropertyValue('--color-text'),
              font: {
                size: Number(getComputedStyle(document.documentElement).getPropertyValue('--date-size')),
                weight: 'bold'
              },
             },
            grid: { color: getComputedStyle(document.documentElement).getPropertyValue('--color-grid'), drawOnChartArea: true },
            ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--color-text'), maxTicksLimit: 10 },
          },
          y: {
            title: { display: true, text: 'Price', color: getComputedStyle(document.documentElement).getPropertyValue('--color-text'),
              font: {
                size: Number(getComputedStyle(document.documentElement).getPropertyValue('--date-size')),
                weight: 'bold'
              },
             },
            grid: { color: getComputedStyle(document.documentElement).getPropertyValue('--color-grid') },
            ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--color-text') },
          },
        },
      }}
      
    />
    </div>
  );
};

interface PastChartProps {
  pastActuals: Actual[];
  pastPredictions: Prediction[];
  ticker: String;
  dailyMae: number;
}

const PastChart = ({ pastActuals, pastPredictions, ticker, dailyMae}: PastChartProps) => {

  return (
    <div>
      <h2>
      Mean Absolute Error (MAE) Percent Over Last 10 Trading Days: {dailyMae.toFixed(2)}%
      </h2>
      <Line
        data={{
          labels: pastActuals.map(a => a.date),
          datasets: [
            {
              label: 'Actual',
              data: pastActuals.map(a => a.close),
              borderColor: getComputedStyle(document.documentElement).getPropertyValue('--color-actual'),
              pointRadius: Number(getComputedStyle(document.documentElement).getPropertyValue('--point-size')),
              pointBackgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--color-actual'),
              fill: false,
            },
            ...pastPredictions.map((p, i) => ({
              label: `Prediction ${i + 1}`,
              data: pastActuals.map((_, j) => (j === i ? pastActuals[i].close : j === i + 1? p.prediction : null)),
              borderColor: getComputedStyle(document.documentElement).getPropertyValue('--color-prediction'),
              fill: false,
              spanGaps: true,
              pointRadius: Number(getComputedStyle(document.documentElement).getPropertyValue('--point-size')),
              pointBackgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--color-prediction'),
            })),
          ],
        }}
        options={{
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Past Predictions',
              color: getComputedStyle(document.documentElement).getPropertyValue('--color-text'),
              font: {
                size: Number(getComputedStyle(document.documentElement).getPropertyValue('--chart-title-size')),
                weight: 'bold',
              },
              padding: {
                top: Number(getComputedStyle(document.documentElement).getPropertyValue('--chart-title-padding-top')),
                bottom: Number(getComputedStyle(document.documentElement).getPropertyValue('--chart-title-padding-bottom')),
              },
              align: 'center',
            },
            legend: {
              display: true,
              position: 'top',
              align: 'center',
              labels: {
                pointStyle: 'circ',
                usePointStyle: true, 
                generateLabels: function(chart) {
                  const datasets = chart.data.datasets;
                  const labels: any[] = [];

                  datasets.forEach((ds, i) => {
                    if (ds.label === 'Actual') {
                      labels.push({
                        text: 'Actual',
                        fontColor: "#FFF",
                        fillStyle: ds.borderColor,
                        hidden: !chart.isDatasetVisible(i),
                        datasetIndex: i,
                      });
                    } else if (ds.label?.startsWith('Prediction') && !labels.some(l => l.text === 'Predictions')) {
                      labels.push({
                        text: 'Predictions',
                        fillStyle: ds.borderColor,
                        hidden: !datasets.some((d, idx) => d.label?.startsWith('Prediction') && chart.isDatasetVisible(idx)),
                        datasetIndex: undefined,
                      });
                    }
                  });

                  return labels;
                }
              },
          
            },
            tooltip: {
              enabled: true,
              mode: 'index',
              intersect: false,
              callbacks: {
                label: function(context) {
                  const value = context.raw;
                  const datasetLabel = context.dataset.label;
                  const chart = context.chart;
                  const actualDataset = chart.data.datasets.find(ds => ds.label === 'Actual');
                  const actualValue = actualDataset?.data[context.dataIndex];

                  if (datasetLabel === 'Actual' && value != null) {
                    return `Actual: ${value.toFixed(2)}`;
                  }

                  if (datasetLabel.startsWith('Prediction') && value != null) {
                    let percentError = actualValue != null ? 100 * (Math.abs(value - actualValue) / actualValue) : null;
                    if (actualValue != null && Number(actualValue) === Number(value)) return null;

                    return percentError != null
                      ? `Prediction: ${value.toFixed(2)} (MAE: ${percentError.toFixed(2)}%)`
                      : `Prediction: ${value.toFixed(2)}`;
                  }

                  return null;
                },
              },
            },
          },
          interaction: { mode: 'index', intersect: false },
          scales: {
            x: { title: { display: true, text: 'Date', color: getComputedStyle(document.documentElement).getPropertyValue('--color-text'),
              font: {
                size: Number(getComputedStyle(document.documentElement).getPropertyValue('--date-size')),
                weight: 'bold'
              },
             },
                 grid: { color: getComputedStyle(document.documentElement).getPropertyValue('--color-grid') },
                 ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--color-text') } },
            y: { title: { display: true, text: 'Price', color: getComputedStyle(document.documentElement).getPropertyValue('--color-text'),
              font: {
                size: Number(getComputedStyle(document.documentElement).getPropertyValue('--date-size')),
                weight: 'bold'
              },
             },
                 grid: { color: getComputedStyle(document.documentElement).getPropertyValue('--color-grid') },
                 ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--color-text') } },
          },
        }}
      />
    </div>
  );
};

// ------------------ Main Tabs Component ------------------
export default function ChartTabs({ actuals, predictions, pastPredictions, pastActuals, mae, ticker, dailyMae }: ChartTabsProps) {
  const [tab, setTab] = useState<'forecast' | 'past'>('forecast');
  const router = useRouter();

  return (
    <div>
      <div style={{ marginTop: "2rem" }}>
        <button className={`tab ${tab === 'forecast' ? 'active' : ''}`} onClick={() => setTab('forecast')}>Forecast</button>
        <button className={`tab ${tab === 'past' ? 'active' : ''}`} onClick={() => setTab('past')}>Past</button>
      </div>

      <div style={{
        border: '1px solid #ccc',
        borderRadius: '0 5px 5px 5px',
        padding: '1rem',
        backgroundColor: '#111',
      }}>
      {tab === 'forecast' && <ForecastChart actuals={actuals} predictions={predictions} />}
      {tab === 'past' && pastActuals && pastPredictions && <PastChart pastActuals={pastActuals} pastPredictions={pastPredictions} ticker={ticker} dailyMae={dailyMae} />}

      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          marginTop: '1rem',
        }}
      >
        <Link href="/">
          <h1 style={{ cursor: 'pointer', margin: 0, color: 'white' }}>
            See Other Stocks
          </h1>
        </Link>
      </div>
        </div>
    </div>
  );
}
