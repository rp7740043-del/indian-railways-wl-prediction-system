/**
 * WL Predictor - Chart.js Visualizations
 * Handles Movement Line Chart, Daily Cancellations Bar Chart, and Outcomes Doughnut Chart
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Movement Chart if canvas exists
    const movementCanvas = document.getElementById('movementChart');
    if (movementCanvas) {
        const ticketId = movementCanvas.dataset.ticketId;
        if (ticketId) {
            loadMovementChart(movementCanvas, ticketId);
        }
    }

    // 2. Initialize Analytics Charts if canvases exist
    const cancellationsCanvas = document.getElementById('cancellationsChart');
    const outcomesCanvas = document.getElementById('outcomesChart');
    if (cancellationsCanvas && outcomesCanvas) {
        loadAnalyticsCharts(cancellationsCanvas, outcomesCanvas);
    }
});

/**
 * Loads and renders the Waiting List Movement progression line chart
 */
async function loadMovementChart(canvas, ticketId) {
    try {
        const response = await fetch(`/api/movement-data/${ticketId}`);
        const data = await response.json();

        if (!data.labels || data.labels.length === 0) {
            const ctx = canvas.getContext('2d');
            ctx.font = '14px Inter, sans-serif';
            ctx.fillStyle = '#64748B';
            ctx.textAlign = 'center';
            ctx.fillText('No historical status points logged yet.', canvas.width / 2, canvas.height / 2);
            return;
        }

        const ctx = canvas.getContext('2d');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Waitlist Number',
                    data: data.values,
                    borderColor: '#0B3C5D',
                    backgroundColor: 'rgba(11, 60, 93, 0.08)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: function(context) {
                        const index = context.dataIndex;
                        const count = context.dataset.data.length;
                        return index === count - 1 ? '#2E7D32' : '#0B3C5D';
                    },
                    pointBorderColor: '#FFFFFF',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 9
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: '#07263A',
                        titleFont: { family: 'Poppins', size: 13 },
                        bodyFont: { family: 'Inter', size: 13 },
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                return `Status: WL ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: '#EDF2F7' },
                        ticks: {
                            font: { family: 'Inter', size: 12 },
                            color: '#475569'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: '#EDF2F7' },
                        ticks: {
                            font: { family: 'Inter', size: 12 },
                            color: '#475569',
                            stepSize: 5,
                            callback: function(value) {
                                return 'WL ' + value;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Failed to load WL movement chart:', error);
    }
}

/**
 * Loads and renders the Analytics Bar Chart and Outcomes Doughnut Chart
 */
async function loadAnalyticsCharts(cancellationsCanvas, outcomesCanvas) {
    try {
        const response = await fetch('/api/analytics-data');
        const data = await response.json();

        // 1. Cancellations Bar Chart
        if (data.cancellations && data.cancellations.dates) {
            new Chart(cancellationsCanvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.cancellations.dates,
                    datasets: [{
                        label: 'Total Cancellations',
                        data: data.cancellations.counts,
                        backgroundColor: '#1D5D8A',
                        hoverBackgroundColor: '#0B3C5D',
                        borderRadius: 6,
                        borderSkipped: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#07263A',
                            titleFont: { family: 'Poppins', size: 13 },
                            bodyFont: { family: 'Inter', size: 13 },
                            padding: 12,
                            cornerRadius: 8,
                            callbacks: {
                                label: function(context) {
                                    return `${context.parsed.y} seats released`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: {
                                font: { family: 'Inter', size: 11 },
                                color: '#475569'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            grid: { color: '#EDF2F7' },
                            ticks: {
                                font: { family: 'Inter', size: 12 },
                                color: '#475569',
                                stepSize: 10
                            }
                        }
                    }
                }
            });
        }

        // 2. Outcomes Doughnut Chart
        if (data.outcomes && data.outcomes.labels) {
            new Chart(outcomesCanvas.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: data.outcomes.labels,
                    datasets: [{
                        data: data.outcomes.counts,
                        backgroundColor: [
                            '#2E7D32', // Confirmed - Signal Green
                            '#E65100', // RAC - Signal Amber
                            '#D32F2F'  // Waiting - Signal Red
                        ],
                        borderWidth: 3,
                        borderColor: '#FFFFFF',
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '68%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                font: { family: 'Inter', size: 13 },
                                color: '#1E293B',
                                padding: 18,
                                usePointStyle: true,
                                pointStyle: 'circle'
                            }
                        },
                        tooltip: {
                            backgroundColor: '#07263A',
                            titleFont: { family: 'Poppins', size: 13 },
                            bodyFont: { family: 'Inter', size: 13 },
                            padding: 12,
                            cornerRadius: 8,
                            callbacks: {
                                label: function(context) {
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const val = context.parsed;
                                    const pct = Math.round((val / total) * 100);
                                    return `${context.label}: ${val} (${pct}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Failed to load analytics charts:', error);
    }
}
