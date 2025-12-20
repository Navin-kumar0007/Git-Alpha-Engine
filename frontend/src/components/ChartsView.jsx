import React from 'react';
import MultiChartDashboard from './charts/MultiChartDashboard';
import MarketHeatmap from './charts/MarketHeatmap';

// Generate historical data for charts
const generateHistoricalData = (asset, days = 30) => {
    const data = [];
    const basePrice = asset?.price || 100;
    let price = basePrice;

    for (let i = days; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);

        const change = (Math.random() - 0.5) * (basePrice * 0.05);
        price = Math.max(basePrice * 0.7, Math.min(basePrice * 1.3, price + change));

        const open = price;
        const close = price + (Math.random() - 0.5) * (basePrice * 0.03);
        const high = Math.max(open, close) + Math.random() * (basePrice * 0.02);
        const low = Math.min(open, close) - Math.random() * (basePrice * 0.02);
        const volume = Math.floor(Math.random() * 10000000) + 1000000;

        data.push({
            date: date.toISOString().split('T')[0],
            open: parseFloat(open.toFixed(2)),
            high: parseFloat(high.toFixed(2)),
            low: parseFloat(low.toFixed(2)),
            close: parseFloat(close.toFixed(2)),
            volume,
        });

        price = close;
    }

    return data;
};

const ChartsView = ({ assets, selectedAsset, onAssetSelect }) => {
    return (
        <div className="flex-1 overflow-auto p-4 space-y-4">
            <MarketHeatmap
                assets={assets}
                onAssetSelect={onAssetSelect}
            />

            {selectedAsset && (
                <MultiChartDashboard
                    asset={selectedAsset}
                    historicalData={generateHistoricalData(selectedAsset)}
                />
            )}
        </div>
    );
};

export default ChartsView;
