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

    const viewType = getViewType();
    manageTransposer(viewType);
    applyViewType(viewType);

    // Обработчик для кнопки транспозера
    transposeButton = document.getElementById('transposer');
    transposeWrapper = document.querySelector('.transpose-wrapper');
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
