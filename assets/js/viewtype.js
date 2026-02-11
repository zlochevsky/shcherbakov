const VALID_VIEW_TYPES = ['text', 'side', 'above', 'source'];
const DEFAULT_VIEW_TYPE = 'side';
const COOKIE_PARAMETERS = 'Path=/; Max-Age=31536000; SameSite=Lax';

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("settings").style.display = "block";
    const currentViewType = getViewType();
    applyViewType(currentViewType)
    const buttonAbove = document.getElementById('above');
    const buttonSide = document.getElementById('side');
    const buttonText = document.getElementById('text');
    const buttonSource = document.getElementById('source');
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

    console.log(getViewType());
});

function applyViewType(viewType) {
    // Скрываем все контейнеры
    const containers = document.querySelectorAll('.view-container');
    containers.forEach(container => {
        container.style.display = 'none';
    });

    // Показываем выбранный
    const activeContainer = document.querySelector('.viewtype-' + viewType);
    if (activeContainer) {
        activeContainer.style.display = 'block';
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


