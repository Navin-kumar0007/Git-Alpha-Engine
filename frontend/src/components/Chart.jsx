import React from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

/**
 * Interactive Chart Component
 * Displays price history with gradient fills and hover effects
 */
const Chart = ({
  data = [],
  dataKey = 'price',
  type = 'area', // 'line' or 'area'
  height = 300,
  showGrid = true,
  showAxis = true,
  gradient = true,
  color = '#6366f1',
}) => {
  // Custom Tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-card p-3 text-sm">
          <p className="text-slate-300 mb-1">{label}</p>
          <p className="text-white font-semibold">
            ${Number(payload[0].value).toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </p>
          {payload[0].payload.commits !== undefined && (
            <p className="text-slate-400 text-xs mt-1">
              {payload[0].payload.commits} commits
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  // Calculate min/max for better Y-axis scaling
  const values = data.map(d => d[dataKey] || 0);
  const min = Math.min(...values) * 0.95;
  const max = Math.max(...values) * 1.05;

  const commonProps = {
    data,
    margin: { top: 10, right: 10, left: 0, bottom: 0 },
  };

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        {type === 'area' ? (
          <AreaChart {...commonProps}>
            {gradient && (
              <defs>
                <linearGradient id={`colorGradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={color} stopOpacity={0.8} />
                  <stop offset="95%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
            )}
            {showGrid && (
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255, 255, 255, 0.1)"
                vertical={false}
              />
            )}
            {showAxis && (
              <>
                <XAxis
                  dataKey="day"
                  stroke="rgba(255, 255, 255, 0.3)"
                  tick={{ fill: 'rgba(255, 255, 255, 0.5)', fontSize: 12 }}
                  tickLine={false}
                />
                <YAxis
                  domain={[min, max]}
                  stroke="rgba(255, 255, 255, 0.3)"
                  tick={{ fill: 'rgba(255, 255, 255, 0.5)', fontSize: 12 }}
                  tickLine={false}
                  tickFormatter={(value) =>
                    `$${value >= 1000 ? (value / 1000).toFixed(1) + 'k' : value.toFixed(0)}`
                  }
                />
              </>
            )}
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: color, strokeWidth: 1 }} />
            <Area
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              strokeWidth={2}
              fill={gradient ? `url(#colorGradient-${dataKey})` : color}
              fillOpacity={gradient ? 1 : 0.2}
              animationDuration={800}
              animationEasing="ease-out"
            />
          </AreaChart>
        ) : (
          <LineChart {...commonProps}>
            {showGrid && (
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255, 255, 255, 0.1)"
                vertical={false}
              />
            )}
            {showAxis && (
              <>
                <XAxis
                  dataKey="day"
                  stroke="rgba(255, 255, 255, 0.3)"
                  tick={{ fill: 'rgba(255, 255, 255, 0.5)', fontSize: 12 }}
                  tickLine={false}
                />
                <YAxis
                  domain={[min, max]}
                  stroke="rgba(255, 255, 255, 0.3)"
                  tick={{ fill: 'rgba(255, 255, 255, 0.5)', fontSize: 12 }}
                  tickLine={false}
                  tickFormatter={(value) =>
                    `$${value >= 1000 ? (value / 1000).toFixed(1) + 'k' : value.toFixed(0)}`
                  }
                />
              </>
            )}
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: color, strokeWidth: 1 }} />
            <Line
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: color, stroke: '#fff', strokeWidth: 2 }}
              animationDuration={800}
              animationEasing="ease-out"
            />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
};

export default Chart;
