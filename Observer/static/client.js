let ws = null;
let observerId = null;

const currencyNames = {
    'USD': 'Доллар США',
    'EUR': 'Евро',
    'GBP': 'Фунт стерлингов',
    'CNY': 'Китайский юань',
    'JPY': 'Японская иена',
    'RUB': 'Российский рубль'
};

function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log('Уже подключен');
        return;
    }

    // Создаем WebSocket соединение
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = function() {
        console.log('WebSocket соединение установлено');
        updateConnectionStatus(true);
        document.getElementById('connect-btn').disabled = true;
        document.getElementById('disconnect-btn').disabled = false;
    };

    ws.onclose = function() {
        console.log('WebSocket соединение закрыто');
        updateConnectionStatus(false);
        document.getElementById('connect-btn').disabled = false;
        document.getElementById('disconnect-btn').disabled = true;
        observerId = null;
    };

    ws.onerror = function(error) {
        console.error('WebSocket ошибка:', error);
        updateConnectionStatus(false);
    };

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('Получены данные:', data);

        if (data.type === 'connection_established') {
            observerId = data.observer_id;
            document.getElementById('observer-id').textContent = observerId;
            console.log(`ID наблюдателя: ${observerId}`);
        }
        else if (data.type === 'currency_update') {
            updateCurrencyTable(data.data);
        }
    };
}

function disconnectWebSocket() {
    if (ws) {
        ws.close();
        ws = null;
    }
}

function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    const statusText = document.getElementById('connection-status');

    if (connected) {
        statusText.textContent = 'Подключен';
        statusElement.className = 'status connected';
    } else {
        statusText.textContent = 'Отключен';
        statusElement.className = 'status disconnected';
    }
}

function updateCurrencyTable(data) {
    const tbody = document.getElementById('currency-data');
    const currencies = data.currencies || {};
    const timestamp = data.timestamp || '—';


    document.getElementById('last-update').textContent = timestamp;


    tbody.innerHTML = '';


    const sortedCurrencies = Object.entries(currencies).sort(([codeA], [codeB]) => {
        const order = ['USD', 'EUR', 'GBP', 'CNY', 'JPY', 'RUB'];
        return order.indexOf(codeA) - order.indexOf(codeB);
    });


    sortedCurrencies.forEach(([code, rate]) => {
        const row = document.createElement('tr');

        const codeCell = document.createElement('td');
        codeCell.className = 'currency-code';
        codeCell.textContent = code;

        const rateCell = document.createElement('td');
        rateCell.className = 'currency-rate';
        rateCell.textContent = code === 'RUB' ? '1.00' : rate.toFixed(2);

        const nameCell = document.createElement('td');
        nameCell.textContent = currencyNames[code] || code;

        row.appendChild(codeCell);
        row.appendChild(rateCell);
        row.appendChild(nameCell);

        tbody.appendChild(row);
    });
}

// Автоподключение при загрузке страницы
window.addEventListener('DOMContentLoaded', function() {
    connectWebSocket();

    // Автоматическое переподключение при потере соединения
    setInterval(function() {
        if (ws && ws.readyState === WebSocket.CLOSED) {
            console.log('Попытка переподключения...');
            connectWebSocket();
        }
    }, 5000);
});