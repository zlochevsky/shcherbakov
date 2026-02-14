/**
 * транспозер аккордов на JavaScript
 * (H=Си, B=Си-бемоль)
 * без оборачивания аккордов в span.c
 */

class ChordTransposer {
    constructor(options = {}) {
        // Немецко-русская нотация: H=Си, B=Си-бемоль
        this.notes = [
            { name: 'C',  value: 0 },
            { name: 'C#', value: 1 },
            { name: 'Db', value: 1 },
            { name: 'D',  value: 2 },
            { name: 'D#', value: 3 },
            { name: 'Eb', value: 3 },
            { name: 'E',  value: 4 },
            { name: 'F',  value: 5 },
            { name: 'F#', value: 6 },
            { name: 'Gb', value: 6 },
            { name: 'G',  value: 7 },
            { name: 'G#', value: 8 },
            { name: 'Ab', value: 8 },
            { name: 'A',  value: 9 },
            { name: 'A#', value: 10 },
            { name: 'Bb', value: 10 },
            { name: 'B',  value: 10 },
            { name: 'H',  value: 11 }
        ];

        // Токены-исключения (не аккорды)
        this.excludeTokens = new Set([
            'intro', 'verse', 'chorus', 'bridge', 'outro',
            'куплет', 'припев', 'проигрыш', 'вступление',
            'bis', 'bass', 'пр.', 'вст.', 'отыгрыш','отыгр.',
            'Пр.','Вст.',
            ...(options.excludeTokens || [])
        ]);

        // Регулярное выражение для поиска аккордов
        // Поддержка: H, B, A-G, с модификаторами (#, b, m, maj, dim, aug, sus, add, цифры)
        // И слэш-аккорды (C/G, Dm/A)
        // Убираем \b в конце, чтобы правильно захватывать F# (иначе граница слова между F и # мешает)
        this.chordRegex = /\b([A-H][#b]?(?:m|maj|dim|aug|sus|add)?[0-9]*(?:\/[A-H][#b]?)?)(?=\s|$|[^\w#b])/g;

        // Сохраняем оригинальный текст для каждого элемента
        this.originalTexts = new WeakMap();

        this.initialKey = null;  // Исходная тональность (никогда не меняется)
        this.currentKey = null;  // Текущая отображаемая тональность
    }

    /**
     * Получить ноту по имени
     */
    getNoteByName(noteName) {
        // Убираем модификаторы (m, 7 и т.д.), оставляем только корень
        const root = noteName.match(/^[A-H][#b]?/)?.[0];
        if (!root) return null;

        return this.notes.find(n => n.name === root);
    }

    /**
     * Получить новую ноту после транспозиции
     */
    transposeNote(noteName, semitones) {
        const note = this.getNoteByName(noteName);
        if (!note) return noteName;

        let newValue = (note.value + semitones) % 12;
        if (newValue < 0) newValue += 12;

        // Выбираем предпочтительную энгармонику
        // Приоритет: диез для #, бемоль для b
        const useSharp = noteName.includes('#');
        const useFlat = noteName.includes('b');

        const candidates = this.notes.filter(n => n.value === newValue);

        let selected;
        if (useSharp) {
            selected = candidates.find(n => n.name.includes('#')) || candidates[0];
        } else if (useFlat) {
            selected = candidates.find(n => n.name.includes('b')) || candidates[0];
        } else {
            // Выбираем натуральную ноту или первую доступную
            selected = candidates.find(n => n.name.length === 1) || candidates[0];
        }

        return selected.name;
    }

    /**
     * Транспонировать аккорд
     */
    transposeChord(chord, semitones) {
        // Разбираем слэш-аккорд (если есть)
        const parts = chord.split('/');
        const mainChord = parts[0];
        const bass = parts[1];

        // Извлекаем корень аккорда и модификаторы
        const match = mainChord.match(/^([A-H][#b]?)(.*)$/);
        if (!match) return chord;

        const [, root, modifiers] = match;
        const newRoot = this.transposeNote(root, semitones);
        let result = newRoot + modifiers;

        // Транспонируем бас (если есть)
        if (bass) {
            const newBass = this.transposeNote(bass, semitones);
            result += '/' + newBass;
        }

        return result;
    }

    /**
     * Проверить, является ли токен аккордом
     */
    isChord(token) {
        // Исключаем токены из списка
        if (this.excludeTokens.has(token.toLowerCase())) {
            return false;
        }

        // Исключаем числа (годы)
        if (/^\d+$/.test(token)) {
            return false;
        }

        // Проверяем по регулярному выражению (полное совпадение с токеном)
        const fullMatch = token.match(/^[A-H][#b]?(?:m|maj|dim|aug|sus|add)?[0-9]*(?:\/[A-H][#b]?)?$/);
        return fullMatch !== null;
    }

    /**
     * Транспонировать текст в элементе
     */
    transposeElement(element, fromKey, toKey) {
        // Сохраняем оригинальный текст при первой транспозиции
        if (!this.originalTexts.has(element)) {
            this.originalTexts.set(element, element.textContent);
        }

        const originalText = this.originalTexts.get(element);
        const semitones = this.calculateSemitones(fromKey, toKey);

        if (semitones === 0) {
            element.textContent = originalText;
            return;
        }

        // Заменяем аккорды в тексте
        const newText = originalText.replace(this.chordRegex, (match) => {
            if (this.isChord(match)) {
                return this.transposeChord(match, semitones);
            }
            return match;
        });

        element.textContent = newText;
    }

    /**
     * Вычислить количество полутонов между тональностями
     */
    calculateSemitones(fromKey, toKey) {
        const from = this.getNoteByName(fromKey);
        const to = this.getNoteByName(toKey);

        if (!from || !to) return 0;

        let delta = to.value - from.value;

        // Выбираем минимальное смещение (по модулю)
        // Например: D(2) -> C(0) = -2 или +10, выбираем -2
        if (delta > 6) {
            delta = delta - 12;  // Преобразуем в отрицательное
        } else if (delta < -6) {
            delta = delta + 12;  // Преобразуем в положительное
        }

        return delta;
    }

    /**
     * Транспонировать все элементы с классом .ch
     */
    transposeAll(container, toKey) {
        const elements = container.querySelectorAll('.ch');

        // ВАЖНО: Всегда транспонируем от ИСХОДНОЙ тональности, а не от текущей!
        elements.forEach(element => {
            this.transposeElement(element, this.initialKey, toKey);
        });

        this.currentKey = toKey;
    }

    /**
     * Создать UI для выбора тональности
     */
    createUI(container, initialKey) {
        this.currentKey = initialKey;

        const wrapper = document.createElement('div');
        wrapper.className = 'transpose-keys';

        // Отображаем только основные тональности (без дублей)
        const displayKeys = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'B', 'H'];

        // Извлекаем корень исходной тональности (без модификаторов m, 7 и т.д.)
        const initialRoot = initialKey.match(/^[A-H][#b]?/)?.[0];

        displayKeys.forEach(keyName => {
            const link = document.createElement('a');
            link.href = '#';
            link.textContent = keyName;
            link.dataset.key = keyName;

            // Выделяем кнопку, соответствующую корню исходной тональности
            if (keyName === initialRoot) {
                link.classList.add('selected');
            }

            link.addEventListener('click', (e) => {
                e.preventDefault();

                // Убираем выделение со всех
                wrapper.querySelectorAll('a').forEach(a => a.classList.remove('selected'));

                // Выделяем текущий
                link.classList.add('selected');

                // Транспонируем
                this.transposeAll(container.closest('.song'), keyName);
            });

            wrapper.appendChild(link);
        });

        return wrapper;
    }

    /**
     * Инициализировать транспозер для элемента
     */
    init(songElement) {
        const initialKey = songElement.dataset.key;
        if (!initialKey) {
            console.warn('No data-key attribute found on song element');
            return;
        }

        this.initialKey = initialKey;  // Сохраняем исходную тональность
        this.currentKey = initialKey;

        // Найти контейнер для UI
        const uiContainer = songElement.closest('.wrapper')?.querySelector('.transpose-wrapper');
        if (uiContainer) {
            const ui = this.createUI(songElement, initialKey);
            uiContainer.appendChild(ui);
        }
    }
}

// Функция для скрытия/показа аккордов
function toggleChords() {
    const chords = document.querySelectorAll('.ch');
    const transposeKeys = document.querySelectorAll('.transpose-keys');

    chords.forEach(el => {
        el.style.display = el.style.display === 'none' ? '' : 'none';
    });

    transposeKeys.forEach(el => {
        el.style.display = el.style.display === 'none' ? '' : 'none';
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    const transposer = new ChordTransposer();

    // Инициализируем все песни на странице
    const songs = document.querySelectorAll('.song[data-key]');
    songs.forEach(song => {
        transposer.init(song);
    });

    // Привязываем кнопку переключения аккордов
    const toggleButton = document.getElementById('toggleChords');
    if (toggleButton) {
        toggleButton.addEventListener('click', () => {
            toggleButton.classList.toggle('note1');
            toggleButton.classList.toggle('note2');
            toggleChords();
        });
    }
});