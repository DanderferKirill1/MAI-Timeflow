document.addEventListener('DOMContentLoaded', () => {
    let activeTooltip = null;

    // Функция для закрытия активного тултипа
    const closeActiveTooltip = () => {
        if (activeTooltip) {
            activeTooltip.classList.remove('tooltip-visible');
            activeTooltip = null;
        }
    };

    // Обработчик клика на предмете
    document.addEventListener('click', (event) => {
        const target = event.target;
        
        // Если клик был на названии предмета
        if (target.classList.contains('lesson-subject')) {
            // Переключаем класс expanded
            target.classList.toggle('expanded');
        } else {
            // Если клик был не на предмете, сворачиваем все развернутые названия
            document.querySelectorAll('.lesson-subject.expanded').forEach(subject => {
                subject.classList.remove('expanded');
            });
        }
    });

    // Закрываем тултип при скролле
    document.addEventListener('scroll', () => {
        closeActiveTooltip();
    }, true);

    // Закрываем тултип при нажатии клавиши Escape
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeActiveTooltip();
        }
    });
}); 