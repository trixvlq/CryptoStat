let socket = new WebSocket('ws://127.0.0.1:8000/ws/crypto/');
socket.onmessage = async function (event) {
    let data = JSON.parse(event.data);
    if(data['type'] == 'top3'){
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
    }
    else if (data['method'] == 'rearrange'){
        const coins = document.getElementById('coins');
        coins.innerHTML = '';
        for (let coin of data['content']) {
            write_coin(coin);
        }
    }
    else if (data['type'] == 'coin'){
        write_coin(data['content'])
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

    let labels,prices;
    try{
        labels = priceData.map(entry => new Date(entry.timestamp).toLocaleDateString());
        prices = priceData.map(entry => entry.price);
    }catch (error){
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['No data available'],
                datasets: [{

                    label: 'Price',
                    data: [0],
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'category'
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Price($)",
                    backgroundColor: "#79AEC8",
                    borderColor: "#417690",
                    data: prices
                }
            ]
        },
        options: {
            title: {
                text: "Gross Volume in 2020",
                display: true
            }
        }
    });
}
function write_coin(data){
    const coins = document.getElementById('coins');
    console.log(data);
    coins.insertAdjacentHTML('beforeend', `
    <a href="coin/${data.coin.symbol}">
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
    </a>
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
        }))
    });

    coinsContainer.parentElement.insertBefore(loadMoreButton, coinsContainer.nextSibling);
});
