export interface TickerData {
  ticker: string;
}

export interface Prediction {
  date: string;
  prediction: number;
}

export interface Actual {
  date: string;
  close: number;
}

export interface TickerDetail {
  ticker: string;
  predictions: Prediction[];
  actuals: Actual[];
  mae?: number;
  dailyMae?: number;
}
