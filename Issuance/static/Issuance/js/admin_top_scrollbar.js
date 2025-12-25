document.addEventListener('DOMContentLoaded', function() {
    // Находим основной контейнер таблицы, который имеет горизонтальную прокрутку.
    // Обычно это div с классом 'results' внутри 'changelist-content'.
    const mainScroller = document.querySelector('.changelist-content .results');

    if (!mainScroller) {
        // Если не нашли, значит мы не на странице changelist или структура HTML изменилась.
        return;
    }

    const table = mainScroller.querySelector('table.changelist');
    if (!table) {
        return;
    }

    // Создаем контейнер для верхнего ползунка
    const topScrollerContainer = document.createElement('div');
    topScrollerContainer.className = 'changelist-top-scrollbar-container';

    // Создаем внутренний div, который будет шире контейнера, чтобы вызвать ползунок
    const innerDiv = document.createElement('div');
    topScrollerContainer.appendChild(innerDiv);

    // Вставляем наш новый контейнер перед основным прокручиваемым элементом
    mainScroller.parentNode.insertBefore(topScrollerContainer, mainScroller);

    // Функция для обновления ширины внутреннего div и синхронизации ширины контейнеров
    function updateScrollbarWidths() {
        const tableWidth = table.scrollWidth; // Фактическая ширина таблицы
        innerDiv.style.width = `${tableWidth}px`;
        // Убедимся, что ширина topScrollerContainer соответствует mainScroller
        topScrollerContainer.style.width = `${mainScroller.clientWidth}px`;
    }

    // Синхронизация прокрутки:
    // Когда верхний ползунок прокручивается, прокручиваем основной
    topScrollerContainer.addEventListener('scroll', function() {
        mainScroller.scrollLeft = this.scrollLeft;
    });

    // Когда основной ползунок прокручивается, прокручиваем верхний
    mainScroller.addEventListener('scroll', function() {
        topScrollerContainer.scrollLeft = this.scrollLeft;
    });

    // Инициализируем ширину при загрузке страницы
    updateScrollbarWidths();

    // Обновляем ширину при изменении размера окна (например, пользователь изменяет размер браузера)
    window.addEventListener('resize', updateScrollbarWidths);

    // Используем ResizeObserver для отслеживания изменений размера таблицы
    // Это важно, если столбцы таблицы могут динамически изменяться (например, через JS)
    const tableResizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
            if (entry.target === table) {
                updateScrollbarWidths();
            }
        }
    });
    tableResizeObserver.observe(table);
});
