const VALID_VIEW_TYPES = ['text', 'side', 'above', 'source'];
const DEFAULT_VIEW_TYPE = 'side';
const COOKIE_PARAMETERS = 'Path=/; Max-Age=31536000; SameSite=Lax';

// Глобальные переменные для кнопок (инициализируются в DOMContentLoaded)
let buttonAbove, buttonSide, buttonText, buttonSource;
let transposeButton, transposeWrapper;

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("settings").style.display = "block";

    // Инициализируем кнопки
    buttonAbove = document.getElementById('above');
    buttonSide = document.getElementById('side');
    buttonText = document.getElementById('text');
    buttonSource = document.getElementById('source');
    buttonStress = document.getElementById('stress');

    // Инициализируем транспозер ДО вызова функций, которые его используют
    transposeButton = document.getElementById('transposer');
    transposeWrapper = document.querySelector('.transpose-wrapper');

    const viewType = getViewType();
    manageTransposer(viewType);
    applyViewType(viewType);
    if (transposeButton && transposeWrapper) {
        transposeButton.addEventListener('click', function() {
            transposeWrapper.classList.toggle('active');
        });
    }

    buttonSide.addEventListener('click', function() {
        setViewType('side');  // устанавливаем новый режим
    });
    buttonAbove.addEventListener('click', function() {
        setViewType('above');  // устанавливаем новый режим
    });
    buttonText.addEventListener('click', function() {
        setViewType('text');  // устанавливаем новый режим
    });
    buttonSource.addEventListener('click', function() {
        setViewType('source');  // устанавливаем новый режим
    });
    buttonStress.addEventListener('click', toggleStress);
    
    console.log(getViewType());
});
function manageTransposer(viewType){
    // Скрываем транспозер в видах text и source
    if (viewType === 'text' || viewType === 'source') {
        if (transposeButton) transposeButton.style.display = "none";
        if (transposeWrapper) transposeWrapper.classList.remove('active');
    } else {
        if (transposeButton) transposeButton.style.display = "inline-block";
    }
}

function manageStressButton(viewType){
    // Показываем кнопку stress только для вида side И если в песне есть ударения
    if (viewType === 'side') {
        const sideContainer = document.querySelector('.viewtype-side');
        const hasStress = sideContainer && sideContainer.dataset.hasStress === 'true';
        if (buttonStress) {
            buttonStress.style.display = hasStress ? "inline-block" : "none";
        }
    } else {
        if (buttonStress) buttonStress.style.display = "none";
    }
}

function applyViewType(viewType) {
    const containers = document.querySelectorAll('.view-container');
    containers.forEach(container => {
        container.classList.remove('active');
        container.style.display = '';  // убираем inline-стиль
    });

    // Убираем active у всех кнопок
    [buttonAbove, buttonSide, buttonSource, buttonText].forEach(btn => btn.classList.remove('active'));

    manageTransposer(viewType);
    manageStressButton(viewType);

    const activeContainer = document.querySelector('.viewtype-' + viewType);
    if (activeContainer) {
        activeContainer.classList.add('active');
    }

    // Позиционируем аккорды для вида above
    if (viewType === 'above') {
        positionChordsAbove();
    }

    // Добавляем active к текущей кнопке
    const activeButton = {
        'above': buttonAbove,
        'side': buttonSide,
        'source': buttonSource,
        'text': buttonText,
    }[viewType];
    if (activeButton) {
        activeButton.classList.add('active');
    }
}

function getViewType(){
    const cookies = document.cookie.split("; ");
    const found = cookies.find(row => row.startsWith('viewType='));
    if (found) 
        return found.split('=')[1];
    return DEFAULT_VIEW_TYPE;
}

function setViewType(viewType){
    const validatedViewType = VALID_VIEW_TYPES.includes(viewType)
        ? viewType
        : DEFAULT_VIEW_TYPE;
    document.cookie = `viewType=${validatedViewType}; ${COOKIE_PARAMETERS}`;
    applyViewType(validatedViewType);
}

function toggleStress(){
    document.querySelectorAll('.strss').forEach(el => {
        const isHidden = window.getComputedStyle(el).visibility === 'hidden';
        el.style.visibility = isHidden ? 'visible' : 'hidden';
    });
    document.querySelector('#stress').classList.toggle('active');
}

function positionChordsAbove() {
    const viewtypeAbove = document.querySelector('.viewtype-above');
    if (!viewtypeAbove) return;

    // Находим все span.ch с data-positions в viewtype-above
    const chordSpans = viewtypeAbove.querySelectorAll('.ch[data-positions]');

    chordSpans.forEach(span => {
        // Проверяем, не были ли уже позиционированы аккорды
        if (span.hasAttribute('data-positioned')) return;

        const positionsStr = span.getAttribute('data-positions');
        if (!positionsStr || positionsStr.trim() === '') return;

        // 1. Парсим позиции в массив чисел (1-based из Hugo)
        const positions = positionsStr.split(',').map(p => parseInt(p.trim(), 10));

        // 2. Разбираем аккорды по пробелам
        const chordText = span.textContent.trim().replace(/[|0-9]/g, '');
        const chords = chordText.split(/\s+/).filter(c => c.length > 0);

        // Проверяем совпадение количества
        if (chords.length !== positions.length) {
            span.classList.add('chord-position-error');
            return;
        }

        // Массив для хранения информации об аккордах
        const chordInfos = [];

        chords.forEach((chord, index) => {
            const originalPos = positions[index]; // 1-based
            const chordLen = chord.length;

            // 3. Вычисляем смещение для центрирования
            const offset = Math.ceil(chordLen / 2);
            let desiredPos = originalPos - offset + 2; // 1-based, сдвиг на 1 вправо

            // 4. Проверка выхода за левую границу
            if (index === 0) {
                if (desiredPos < 1) {
                    desiredPos = 1;
                }
            }

            // 5. Проверка коллизии с предыдущим аккордом
            if (index > 0) {
                const prevChord = chordInfos[index - 1];
                const prevEnd = prevChord.endPos;
                if (desiredPos <= prevEnd + 1) {
                    desiredPos = prevEnd + 2;
                }
            }

            // 6. Вычисляем позицию конца аккорда
            const endPos = desiredPos + chordLen - 1;

            chordInfos.push({
                chord: chord,
                pos: desiredPos,
                endPos: endPos
            });
        });

        // 7. Формируем строку с правильными пробелами
        let result = '';
        let currentPos = 1; // 1-based

        chordInfos.forEach(info => {
            // Добавляем пробелы до позиции аккорда
            const spacesNeeded = info.pos - currentPos;
            if (spacesNeeded > 0) {
                result += ' '.repeat(spacesNeeded);
            }
            result += info.chord;
            currentPos = info.endPos + 1;
        });

        // Обновляем содержимое span и помечаем как позиционированный
        span.textContent = result;
        span.setAttribute('data-positioned', 'true');
    });
}
