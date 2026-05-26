const API_BASE = '';

async function apiFetch(path) {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

function formatDate(d) {
    return new Date(d).toLocaleString('ru-RU');
}

// Home page counters
function animateCounter(el, target) {
    const duration = 1500;
    const start = performance.now();
    function tick(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(eased * target);
        if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
}

// Observer for fade-in/animations
const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
        if (e.isIntersecting) {
            e.target.classList.add('fade-in');
            observer.unobserve(e.target);
        }
    });
}, { threshold: 0.2 });

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.observe').forEach(el => observer.observe(el));
});

// Monitoring page - load consumers and readings
async function loadMonitoring() {
    const container = document.getElementById('monitoring-content');
    if (!container) return;
    container.innerHTML = '<div class="loading">Загрузка данных...</div>';
    try {
        const consumers = await apiFetch('/api/v1/consumers');
        const readings = await apiFetch('/api/v1/readings');
        let html = '<div class="kpi-grid">';
        html += `<div class="kpi"><div class="kpi-value">${consumers.length}</div><div class="kpi-label">Абонентов</div></div>`;
        html += `<div class="kpi"><div class="kpi-value">${readings.length}</div><div class="kpi-label">Показаний</div></div>`;
        html += '</div>';
        html += '<div class="table-wrapper"><table><thead><tr><th>ID</th><th>Абонент</th><th>Адрес</th><th>Договор</th><th>Тип</th></tr></thead><tbody>';
        consumers.forEach(c => {
            const types = {residential: 'Жилой', commercial: 'Коммерческий', industrial: 'Промышленный'};
            html += `<tr><td>${c.id}</td><td>${c.name}</td><td>${c.address || '-'}</td><td>${c.contract_number}</td><td>${types[c.consumer_type] || c.consumer_type}</td></tr>`;
        });
        html += '</tbody></table></div>';
        container.innerHTML = html;
    } catch (e) {
        container.innerHTML = `<div class="loading">Ошибка загрузки: ${e.message}</div>`;
    }
}

// Dashboard
async function loadDashboard() {
    const container = document.getElementById('dashboard-content');
    if (!container) return;
    container.innerHTML = '<div class="loading">Загрузка данных...</div>';
    try {
        const consumers = await apiFetch('/api/v1/consumers');
        const readings = await apiFetch('/api/v1/readings');
        const now = new Date();
        const start = new Date(now.getFullYear(), 0, 1).toISOString().split('T')[0];
        const end = now.toISOString().split('T')[0];
        let balance = {total_supplied_gcal: 0, total_consumed_gcal: 0, loss_gcal: 0, loss_percent: 0};
        try {
            balance = await apiFetch(`/api/v1/reports/balance?period_start=${start}&period_end=${end}`);
        } catch (_) {}

        let html = '<div class="kpi-grid">';
        html += `<div class="kpi"><div class="kpi-value">${consumers.length}</div><div class="kpi-label">Абоненты</div></div>`;
        html += `<div class="kpi"><div class="kpi-value">${readings.length}</div><div class="kpi-label">Показания</div></div>`;
        html += `<div class="kpi"><div class="kpi-value">${balance.total_supplied_gcal.toFixed(1)}</div><div class="kpi-label">Выработано Гкал</div></div>`;
        html += `<div class="kpi"><div class="kpi-value">${balance.total_consumed_gcal.toFixed(1)}</div><div class="kpi-label">Потреблено Гкал</div></div>`;
        html += `<div class="kpi"><div class="kpi-value">${balance.loss_gcal.toFixed(1)}</div><div class="kpi-label">Потери Гкал</div></div>`;
        html += `<div class="kpi"><div class="kpi-value">${balance.loss_percent.toFixed(1)}%</div><div class="kpi-label">Потери %</div></div>`;
        html += '</div>';

        // Bar chart (demo data)
        const months = ['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек'];
        const demoData = [145, 138, 120, 95, 68, 45, 32, 38, 55, 82, 110, 130];
        html += '<div class="chart-container"><h3>Выработка тепла по месяцам (Гкал)</h3><div class="chart-bars">';
        const maxVal = Math.max(...demoData);
        demoData.forEach((val, i) => {
            const pct = (val / maxVal) * 100;
            const color = `hsl(${200 - i * 5}, 65%, 50%)`;
            html += `<div class="chart-bar-wrapper"><div class="chart-bar" style="height:${pct}%;background:${color}"></div><div class="chart-bar-label">${months[i]}<br>${val}</div></div>`;
        });
        html += '</div></div>';

        html += '<div class="chart-container"><h3>Состояние API</h3><div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))">';
        const endpoints = [
            {path: 'GET /consumers', status: 200},
            {path: 'GET /readings', status: 200},
            {path: 'GET /reports/balance', status: 200},
            {path: 'POST /readings', status: '-'},
            {path: 'POST /reports/generate-act', status: '-'},
        ];
        endpoints.forEach(ep => {
            const cls = ep.status === 200 ? 'badge-success' : 'badge-warning';
            html += `<div class="card"><h3>${ep.path}</h3><p>Статус: <span class="badge ${cls}">${ep.status}</span></p></div>`;
        });
        html += '</div></div>';

        container.innerHTML = html;
    } catch (e) {
        container.innerHTML = `<div class="loading">Ошибка загрузки: ${e.message}</div>`;
    }
}

// Header active page
document.addEventListener('DOMContentLoaded', () => {
    const page = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('nav a').forEach(a => {
        if (a.getAttribute('href') === page) a.classList.add('active');
    });
});
