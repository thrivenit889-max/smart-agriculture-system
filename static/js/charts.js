// Smart Agriculture and Rural Tech - Analytics & Charts Orchestrator

document.addEventListener('DOMContentLoaded', function() {
    
    // Helper: Generate common chart colors
    const colors = {
        emerald: '#10b981',
        emeraldDark: '#047857',
        emeraldLight: '#d1fae5',
        blue: '#3b82f6',
        orange: '#f59e0b',
        red: '#ef4444',
        slate: '#64748b'
    };

    // 1. Dashboard Financial Summary Mini Chart (Donut)
    const dbCanvas = document.getElementById('dashboardChart');
    if (dbCanvas) {
        const income = parseFloat(dbCanvas.dataset.income) || 0;
        const expense = parseFloat(dbCanvas.dataset.expense) || 0;
        
        new Chart(dbCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Income (₹)', 'Expense (₹)'],
                datasets: [{
                    data: [income, expense],
                    backgroundColor: [colors.emerald, colors.orange],
                    borderWidth: 2,
                    borderColor: 'transparent'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: getComputedStyle(document.body).getPropertyValue('--text-primary') || '#1e293b'
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // 2. Smart Irrigation Soil Moisture History Chart (Line)
    const moistureCanvas = document.getElementById('moistureChart');
    if (moistureCanvas) {
        // Retrieve moisture data array injected on HTML attributes
        const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const values = JSON.parse(moistureCanvas.dataset.values || '[55, 58, 62, 48, 50, 68, 61]');
        
        new Chart(moistureCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Moisture Level (%)',
                    data: values,
                    borderColor: colors.blue,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        ticks: { color: colors.slate }
                    },
                    x: {
                        ticks: { color: colors.slate }
                    }
                }
            }
        });
    }

    // 3. Market Price Comparison Trends Chart (Bar/Line Combo)
    const marketCanvas = document.getElementById('marketChart');
    if (marketCanvas) {
        new Chart(marketCanvas, {
            type: 'bar',
            data: {
                labels: ['Paddy', 'Ragi', 'Maize', 'Cotton', 'Onion', 'Tomato'],
                datasets: [
                    {
                        label: 'Min Price (₹/Quintal)',
                        data: [1800, 3050, 1600, 6000, 1200, 800],
                        backgroundColor: 'rgba(245, 158, 11, 0.7)'
                    },
                    {
                        label: 'Avg Price (₹/Quintal)',
                        data: [2075, 3350, 1820, 6900, 1500, 1150],
                        backgroundColor: 'rgba(16, 185, 129, 0.8)'
                    },
                    {
                        label: 'Max Price (₹/Quintal)',
                        data: [2250, 3600, 1950, 7500, 1800, 1500],
                        backgroundColor: 'rgba(59, 130, 246, 0.7)'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        ticks: { color: colors.slate }
                    },
                    x: {
                        ticks: { color: colors.slate }
                    }
                }
            }
        });
    }

    // 4. Finance Ledger Ledger Category Distribution (Pie)
    const financeCanvas = document.getElementById('financeChart');
    if (financeCanvas) {
        // Collect amounts from template elements
        const labels = ['Seeds', 'Fertilizers', 'Labor', 'Equipment/Fuel', 'Sales Income', 'Other'];
        const values = [1200, 4500, 3200, 2500, 15000, 800];
        
        new Chart(financeCanvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        colors.emerald,
                        colors.orange,
                        colors.blue,
                        colors.red,
                        colors.emeraldDark,
                        colors.slate
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: colors.slate }
                    }
                }
            }
        });
    }

    // 5. Admin Feedback Sentiment Trend Chart (Donut)
    const sentimentCanvas = document.getElementById('sentimentChart');
    if (sentimentCanvas) {
        const positive = parseFloat(sentimentCanvas.dataset.positive) || 50;
        const negative = parseFloat(sentimentCanvas.dataset.negative) || 20;
        const neutral = 100 - (positive + negative);
        
        new Chart(sentimentCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Positive (%)', 'Negative (%)', 'Neutral (%)'],
                datasets: [{
                    data: [positive, negative, neutral],
                    backgroundColor: [colors.emerald, colors.red, colors.orange],
                    borderWidth: 2,
                    borderColor: 'transparent'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: colors.slate }
                    }
                }
            }
        });
    }
});
