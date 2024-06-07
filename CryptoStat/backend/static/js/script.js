let socket = new WebSocket('ws://127.0.0.1:8000/ws/crypto/');

socket.onmessage = async function (event) {
    let data = JSON.parse(event.data);
    if (data['type'] === 'top3') {
        let symbol = data.content.symbol;
        let priceData = await getPriceData(symbol);
        let canvasId = symbol + 'Chart';
        let chartElement = `
            <div class="col-md-4 feature">
                <h3>${symbol}</h3>
                <canvas id="${canvasId}" width="400" height="400"></canvas>
                <p>Description of ${symbol}.</p>
            </div>
        `;

        const top_coins = document.getElementById('top-coins');
        top_coins.insertAdjacentHTML('beforeend', chartElement);

        buildChart(canvasId, priceData);
    } else if (data['method'] === 'rearrange') {
        const coins = document.getElementById('coins');
        coins.innerHTML = '';
        for (let coin of data['content']) {
            write_coin(coin);
        }
    } else if (data['type'] === 'coin') {
        write_coin(data['content']);
    }
};

async function getPriceData(symbol) {
    try {
        const response = await fetch(`/get_currency_data/${symbol}/`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Ошибка при загрузке данных о цене криптовалюты:', error);
        return [];
    }
}

function buildChart(canvasId, priceData) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    let labels, prices;
    try {
        labels = priceData.map(entry => new Date(entry.timestamp).toLocaleDateString());
        prices = priceData.map(entry => entry.price);
    } catch (error) {
        labels = ['No data available'];
        prices = [0];
    }

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Price($)",
                    backgroundColor: "#3498DB",
                    borderColor: "#1F618D",
                    data: prices,
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'category',
                    ticks: {
                        color: '#FFFFFF'
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#FFFFFF'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: `Price data for ${canvasId.replace('Chart', '')}`,
                    color: '#FFFFFF',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    labels: {
                        color: '#FFFFFF'
                    }
                }
            }
        }
    });
}
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.split('=')[1];
        }
    }
    return null;
}
function write_coin(data) {
    const coins = document.getElementById('coins');
    const csrfToken = getCSRFToken();

    coins.insertAdjacentHTML('beforeend', `
    <a href="coin/${data.coin.symbol}">
        <div class="card">
            <div class="card-body">
                <h2 class="coin-symbol">${data.coin.symbol}</h2>
                <div class="coin-info">
                    <div class="info-item">
                        <span class="info-label">Price:</span>
                        <span class="info-value">${data.price.price}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Volume:</span>
                        <span class="info-value">${data.status.volume}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Last price:</span>
                        <span class="info-value">${data.status.lastPrice}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Change:</span>
                        <span class="info-value">${data.status.priceChangePercent}%</span>
                    </div>
                </div>
            </div>

        </div>
    </a>
    <form method="post" action="http://localhost:8000/add_to_favs/">
        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
        <input type="hidden" name="symbol" value="${data.coin.symbol}">
        <button type="submit" class="btn btn-primary">Add to Favorites</button>
    </form>
    `);
}

function changeSort(method) {
    socket.send(JSON.stringify({
        'command': 'change_sort',
        'method': method
    }));
}

window.addEventListener('DOMContentLoaded', (event) => {
    const coinsContainer = document.getElementById('coins');
    const loadMoreButton = document.createElement('button');
    loadMoreButton.textContent = 'Load More';
    loadMoreButton.classList.add('btn', 'btn-primary');
    loadMoreButton.addEventListener('click', async () => {
        socket.send(JSON.stringify({
            'command': 'load_more',
            'method': 'load_more'
        }));
    });

    coinsContainer.parentElement.insertBefore(loadMoreButton, coinsContainer.nextSibling);
});
