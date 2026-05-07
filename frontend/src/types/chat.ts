export interface ChartData {
  name: string;
  [key: string]: string | number;
}

export interface Message {
  id: string;
  text: string;
  isUser: boolean;
  isSystem?: boolean;
  hasChart?: boolean;
  chartType?: 'bar' | 'line';
  chartData?: ChartData[];
  isError?: boolean;
}
