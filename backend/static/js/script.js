// Конфигурация
const CONFIG = {
    BACKEND_URL: 'http://localhost:5000/api/process-query'
};

// DOM элементы
let textarea, charCount, searchButton, resultsSection, resultsContainer;
let articlesContainer, articlesResult, processingIndicator;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Инициализация приложения ГИДРОПОИСК (режим заглушек)');
    initializeElements();
    setupEventListeners();
});

function initializeElements() {
    textarea = document.getElementById('componentSearch');
    charCount = document.getElementById('charCount');
    searchButton = document.getElementById('searchButton');
    resultsSection = document.getElementById('resultsSection');
    resultsContainer = document.getElementById('resultsContainer');
    articlesContainer = document.getElementById('articlesContainer');
    articlesResult = document.getElementById('articlesResult');
    processingIndicator = document.querySelector('.processing-indicator');
}

function setupEventListeners() {
    textarea.addEventListener('input', handleTextareaInput);
    searchButton.addEventListener('click', handleSearch);
}

function handleTextareaInput() {
    const count = this.value.length;
    charCount.textContent = count;

    if (count > 1000) {
        charCount.style.color = '#dc3545';
    } else if (count > 800) {
        charCount.style.color = '#ffc107';
    } else {
        charCount.style.color = '#6c757d';
    }
}

async function handleSearch() {
    const query = textarea.value.trim();

    if (!query) {
        alert('Пожалуйста, введите запрос для поиска');
        textarea.focus();
        return;
    }

    processingIndicator.classList.remove('hidden');
    searchButton.disabled = true;
    document.getElementById('loading').style.display = 'block';
    document.getElementById('status').textContent = '';

    try {
        // Отправляем текст в бэкенд
        const backendResponse = await sendToBackend(query);
        console.log('Заглушка от бэкенда:', backendResponse);

        // Отображаем результаты
        displayResults(backendResponse);

    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('status').textContent = 'Ошибка при получении данных.';
        document.getElementById('status').style.color = 'red';
    } finally {
        processingIndicator.classList.add('hidden');
        searchButton.disabled = false;
        document.getElementById('loading').style.display = 'none';
    }
}


async function sendToBackend(query) {
    const payload = { message: query };

    const response = await fetch(CONFIG.BACKEND_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        throw new Error(`Ошибка бэкенда: ${response.status}`);
    }

    return await response.json();
}

function displayResults(data) {
    console.log('Отображение данных:', data);

    resultsContainer.innerHTML = '';
    articlesContainer.classList.add('hidden');

    if (!data || !data.results || !Array.isArray(data.results)) {
        showNoResults('Бэкенд вернул некорректные данные.');
        return;
    }

    const articles = data.results.map(item => item.text).join('\n\n');
    if (articles) {
        articlesResult.textContent = articles;
        articlesContainer.classList.remove('hidden');
    }

    data.results.forEach(item => {
        const card = document.createElement('div');
        card.className = 'result-card';

        const typeLabel = item.type || 'component';
        const badge = document.createElement('span');
        badge.className = `type-badge ${typeLabel}`;
        badge.textContent = typeLabel.toUpperCase();

        const header = document.createElement('div');
        header.className = 'result-header';
        header.appendChild(badge);

        const body = document.createElement('div');
        body.className = 'result-body';
        body.innerHTML = `
            <p><strong>Артикул:</strong> ${item.text || '—'}</p>
            <p><strong>Описание:</strong> ${item.description || 'Информация отсутствует'}</p>
        `;

        card.appendChild(header);
        card.appendChild(body);
        resultsContainer.appendChild(card);
    });

    showResultsSection();
}

function showNoResults(message = 'По вашему запросу не найдено подходящих артикулов.') {
    resultsContainer.innerHTML = `
        <div class="result-card">
            <div class="result-header">
                <span class="type-badge plug">РЕЗУЛЬТАТЫ НЕ НАЙДЕНЫ</span>
            </div>
            <div class="result-body">
                <p>${message}</p>
            </div>
        </div>
    `;
    articlesContainer.classList.add('hidden');
    showResultsSection();
}

function showResultsSection() {
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}


window.debugApp = () => console.log('Debug info ready');