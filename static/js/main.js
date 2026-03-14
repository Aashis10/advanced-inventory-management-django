window.addEventListener('load', () => {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => overlay.style.display = 'none', 320);
    }
});

window.__chartRegistry = window.__chartRegistry || [];

function getChartPalette() {
    const isDark = document.body.classList.contains('dark-mode');
    return {
        legend: isDark ? '#cbd5e1' : '#64748b',
        grid: isDark ? 'rgba(148, 163, 184, 0.24)' : 'rgba(148, 163, 184, 0.12)',
    };
}

function registerChart(chart) {
    window.__chartRegistry.push(chart);
    return chart;
}

function applyThemeToCharts() {
    const palette = getChartPalette();
    (window.__chartRegistry || []).forEach((chart) => {
        if (chart.options?.plugins?.legend?.labels) {
            chart.options.plugins.legend.labels.color = palette.legend;
        }
        if (chart.options?.scales?.x?.grid) {
            chart.options.scales.x.grid.color = palette.grid;
        }
        if (chart.options?.scales?.y?.grid) {
            chart.options.scales.y.grid.color = palette.grid;
        }
        chart.update('none');
    });
}

(function themeMode() {
    const body = document.body;
    const storageKey = 'ats-theme';
    const toggle = document.getElementById('theme-toggle');
    const toggleIcon = toggle ? toggle.querySelector('i') : null;

    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        if (body) {
            body.classList.toggle('dark-mode', theme === 'dark');
        }
        if (toggle && toggleIcon) {
            toggleIcon.className = theme === 'dark' ? 'fa-regular fa-sun' : 'fa-regular fa-moon';
            toggle.setAttribute('title', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
        }
        applyThemeToCharts();
    };

    const savedTheme = localStorage.getItem(storageKey) || 'light';
    applyTheme(savedTheme);

    if (toggle) {
        toggle.addEventListener('click', () => {
            const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            localStorage.setItem(storageKey, next);
            applyTheme(next);
        });
    }
})();

(function sidebarMobile() {
    const trigger = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    if (trigger && sidebar) {
        trigger.addEventListener('click', () => sidebar.classList.toggle('open'));
    }
})();

(function counters() {
    const counters = document.querySelectorAll('.counter');
    counters.forEach((counter) => {
        const target = parseFloat(counter.dataset.target || '0');
        let current = 0;
        const increment = Math.max(1, target / 45);
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                counter.textContent = Math.round(target).toLocaleString();
                clearInterval(timer);
            } else {
                counter.textContent = Math.round(current).toLocaleString();
            }
        }, 24);
    });
})();

(function dashboardCharts() {
    const node = document.getElementById('chart-data');
    if (!node) return;

    const data = JSON.parse(node.textContent);
    const palette = getChartPalette();
    const common = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: palette.legend, usePointStyle: true } } },
        animation: { duration: 1100 },
    };

    const categoryEl = document.getElementById('categoryChart');
    if (categoryEl) {
        registerChart(new Chart(categoryEl, {
        type: 'doughnut',
        data: {
            labels: data.category_labels,
            datasets: [{ data: data.category_values, backgroundColor: ['#2563eb', '#0ea663', '#ef8e11', '#dd4a48', '#4f46e5', '#14b8a6', '#0ea5e9'], borderWidth: 0 }],
        },
        options: { ...common, cutout: '58%' },
    }));
    }

    const trendEl = document.getElementById('salesTrendChart');
    if (trendEl) {
        registerChart(new Chart(trendEl, {
        type: 'line',
        data: {
            labels: data.monthly_labels,
            datasets: [{ label: 'Sales', data: data.monthly_values, borderColor: '#2563eb', backgroundColor: 'rgba(37, 99, 235, .18)', tension: .4, fill: true }],
        },
        options: {
            ...common,
            scales: {
                x: { grid: { color: palette.grid } },
                y: { grid: { color: palette.grid } },
            },
        },
    }));
    }

    const topSellingEl = document.getElementById('topSellingChart');
    if (topSellingEl) {
        registerChart(new Chart(topSellingEl, {
        type: 'bar',
        data: {
            labels: data.top_labels,
            datasets: [{ label: 'Units Sold', data: data.top_values, backgroundColor: '#2563eb', borderRadius: 10 }],
        },
        options: {
            ...common,
            indexAxis: 'y',
            scales: {
                x: { grid: { color: palette.grid } },
                y: { grid: { display: false } },
            },
        },
    }));
    }
})();

(function analyticsCharts() {
    const node = document.getElementById('analytics-data');
    if (!node) return;

    const data = JSON.parse(node.textContent);
    const palette = getChartPalette();
    const common = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: palette.legend, usePointStyle: true } } },
        animation: { duration: 1100 },
    };

    registerChart(new Chart(document.getElementById('revenueProfitChart'), {
        type: 'line',
        data: {
            labels: data.revenue_labels,
            datasets: [
                { label: 'Revenue', data: data.revenue_values, borderColor: '#1f5eff', backgroundColor: 'rgba(31, 94, 255, .14)', tension: 0.35, fill: true },
                { label: 'Profit', data: data.profit_values, borderColor: '#0ea663', backgroundColor: 'rgba(14, 166, 99, .12)', tension: 0.35, fill: true },
            ],
        },
        options: {
            ...common,
            scales: {
                x: { grid: { color: palette.grid } },
                y: { grid: { color: palette.grid } },
            },
        },
    }));

    registerChart(new Chart(document.getElementById('salesByCategoryChart'), {
        type: 'bar',
        data: {
            labels: data.sales_category_labels,
            datasets: [{ label: 'Sales Value', data: data.sales_category_values, backgroundColor: '#2563eb', borderRadius: 10 }],
        },
        options: {
            ...common,
            scales: {
                x: { grid: { display: false } },
                y: { grid: { color: palette.grid } },
            },
        },
    }));

    registerChart(new Chart(document.getElementById('profitMarginChart'), {
        type: 'line',
        data: {
            labels: data.margin_labels,
            datasets: [{ label: 'Profit Margin %', data: data.margin_values, borderColor: '#ef8e11', backgroundColor: 'rgba(239, 142, 17, .16)', tension: 0.3, fill: true }],
        },
        options: {
            ...common,
            scales: {
                x: { grid: { display: false } },
                y: { grid: { color: palette.grid } },
            },
        },
    }));

    registerChart(new Chart(document.getElementById('stockTrendChart'), {
        type: 'bar',
        data: {
            labels: data.movement_labels,
            datasets: [
                { label: 'Incoming Stock', data: data.movement_incoming, backgroundColor: '#0ea663', borderRadius: 10 },
                { label: 'Outgoing Stock', data: data.movement_outgoing, backgroundColor: '#dd4a48', borderRadius: 10 },
            ],
        },
        options: {
            ...common,
            scales: {
                x: { grid: { display: false } },
                y: { grid: { color: palette.grid } },
            },
        },
    }));

    registerChart(new Chart(document.getElementById('stockSnapshotChart'), {
        type: 'doughnut',
        data: {
            labels: data.stock_snapshot_labels,
            datasets: [{ data: data.stock_snapshot_values, backgroundColor: ['#0ea663', '#ef8e11', '#dd4a48'], borderWidth: 0 }],
        },
        options: { ...common, cutout: '60%' },
    }));
})();

(function saleReceiptPreview() {
    const buttons = document.querySelectorAll('.receipt-btn');
    const modalEl = document.getElementById('receiptModal');
    const body = document.getElementById('receiptBody');
    if (!buttons.length || !modalEl || !body || !window.bootstrap) return;

    const modal = new bootstrap.Modal(modalEl);
    buttons.forEach((btn) => {
        btn.addEventListener('click', () => {
            body.innerHTML = `
                <div class="receipt-preview">
                    <p><strong>Buyer:</strong> ${btn.dataset.buyer}</p>
                    <p><strong>Product:</strong> ${btn.dataset.product}</p>
                    <p><strong>Quantity:</strong> ${btn.dataset.qty}</p>
                    <p><strong>Total Amount:</strong> $${btn.dataset.total}</p>
                    <p><strong>Amount Paid:</strong> $${btn.dataset.paid}</p>
                    <p><strong>Balance Due:</strong> $${btn.dataset.balance}</p>
                    <p><strong>Date:</strong> ${btn.dataset.date}</p>
                </div>
            `;
            modal.show();
        });
    });
})();
