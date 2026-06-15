import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

import {Bar, Line} from "react-chartjs-2";
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Tooltip, Legend, Filler);

export default function TrafficCharts({ data }) {
  const lineDataset = {
    labels: data.labels,
    datasets: [
      {
        label: 'Average Speed (km/h)',
        data: data.speeds,
        borderColor: '#2f80ed',
        backgroundColor: 'rgba(47, 128, 237, 0.2)',
        fill: true,
        tension: 0.3
      }
    ]
  };

  const barDataset = {
    labels: data.labels,
    datasets: [
      {
        label: 'Vehicle Count',
        data: data.vehicleCounts,
        backgroundColor: '#27ae60'
      },
      {
        label: 'Pollution Index',
        data: data.pollution,
        backgroundColor: '#eb5757'
      }
    ]
  };

  return (
    <div className="charts-grid">
      <div className="chart-card">
        <h3>Traffic flow</h3>
        <Bar data={barDataset} options={{ responsive: true, plugins: { legend: { position: 'top' } } }} />
      </div>
      <div className="chart-card">
        <h3>Average speed trend</h3>
        <Line data={lineDataset} options={{ responsive: true, plugins: { legend: { position: 'top' } } }} />
      </div>
    </div>
  );
}
