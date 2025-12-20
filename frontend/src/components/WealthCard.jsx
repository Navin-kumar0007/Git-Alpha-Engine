import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

/**
 * Wealth Card Component
 * Displays key metrics with glassmorphic design and trend indicators
 */
const WealthCard = ({
  title = '',
  value = 0,
  change = 0,
  icon: Icon = null,
  prefix = '$',
  suffix = '',
  trend = 'neutral', // 'up', 'down', 'neutral'
  gradient = false,
  className = '',
  onClick = null,
}) => {
  // Format large numbers
  const formatValue = (val) => {
    // Handle null, undefined, or non-numeric values
    const numVal = Number(val) || 0;

    if (numVal >= 1000000) return `${(numVal / 1000000).toFixed(2)}M`;
    if (numVal >= 1000) return `${(numVal / 1000).toFixed(2)}K`;
    return numVal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  // Determine trend icon and color
  const getTrendInfo = () => {
    if (trend === 'up' || change > 0) {
      return {
        icon: TrendingUp,
        color: 'text-green-400',
        bg: 'bg-green-500/10',
      };
    }
    if (trend === 'down' || change < 0) {
      return {
        icon: TrendingDown,
        color: 'text-red-400',
        bg: 'bg-red-500/10',
      };
    }
    return {
      icon: Minus,
      color: 'text-slate-400',
      bg: 'bg-slate-500/10',
    };
  };

  const trendInfo = getTrendInfo();
  const TrendIcon = trendInfo.icon;

  return (
    <div
      className={`${gradient ? 'card-gradient-primary' : 'glass-card'
        } hover-lift cursor-pointer ${className}`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="text-sm text-slate-300 mb-1">{title}</div>
          <div className="text-2xl font-bold">
            {prefix}
            {formatValue(value)}
            {suffix}
          </div>
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl ${gradient ? 'bg-white/20' : 'bg-indigo-500/10'}`}>
            <Icon size={24} className={gradient ? 'text-white' : 'text-indigo-400'} />
          </div>
        )}
      </div>

      {change !== 0 && (
        <div className="flex items-center gap-2">
          <div className={`flex items-center gap-1 px-2 py-1 rounded-lg ${trendInfo.bg}`}>
            <TrendIcon size={14} className={trendInfo.color} />
            <span className={`text-xs font-semibold ${trendInfo.color}`}>
              {Math.abs(change).toFixed(2)}%
            </span>
          </div>
          <span className={`text-xs ${gradient ? 'text-white/70' : 'text-slate-400'}`}>
            24h
          </span>
        </div>
      )}
    </div>
  );
};

export default WealthCard;
