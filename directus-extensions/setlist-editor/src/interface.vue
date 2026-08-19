<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useApi } from '@directus/extensions-sdk';

/* ─────────────────────────────────────────────────────────────
   Схема (см. docs/directus.md в репозитории) — уточнено запросом
   к живой базе 2026-08-17, при расхождениях доверять этому месту,
   а не памяти.
   ───────────────────────────────────────────────────────────── */
const PERF_COLLECTION = 'perfs';   // коллекция исполнений
const WORK_COLLECTION = 'works';   // справочник песен
const EVENT_FK         = 'events_id'; // FK исполнения -> концерт (events)
const WORK_FK          = 'works_id';  // FK исполнения -> песня (works)
const NUMBER_FIELD     = 'number';    // порядок в программе — НЕ отправляем при
                                       // создании: Flow «Auto perf id» сам
                                       // проставляет id и number (max+1), если
                                       // они не пришли в payload. Если слать
                                       // number вручную отсюда, есть риск
                                       // разъехаться с чужими одновременными
                                       // правками того же концерта.

// Заголовок песни строим так же, как это делает layouts/miscellaneous/catalogue.html:
// name (с fname, если есть) — а если name пусто, то fincipit. incipit/fincipit
// тянем только для подсказки в выпадашке, в поиск их не пускаем — см. SEARCH_FIELDS.
const WORK_TITLE_FIELDS = ['name', 'fname', 'incipit', 'fincipit', 'sort'];
// Поля, по которым реально матчим ввод. Сознательно БЕЗ incipit/fincipit —
// поиск по всей первой строке тянет много лишнего (совпадение где-то в середине
// фразы). sort почти всегда содержит короткую "витрину" песни: имя, если оно
// задано, иначе fincipit (см. пример rusalka — name пуст, sort == fincipit) —
// так что name+fname+sort фактически покрывают все случаи и остаются узкими.
const SEARCH_FIELDS = ['name', 'fname', 'sort'];
const EXCLUDE_HIDDEN = true; // не предлагать works.hidden = true в автокомплите

// Русские подписи для всех булевых полей perfs — набор чекбоксов, которые
// реально показываются в строке, настраивается по месту, в Settings →
// Data Model → events → songs_performed → Options (см. PARAM_CHOICES
// в index.js — это единственное место, где надо добавить новое поле,
// если в perfs появится ещё один булевый столбец).
const PARAM_LABELS = {
	is_premiere: 'Премьера',
	is_first: 'Первая песня концерта',
	is_last: 'Последняя песня концерта',
	is_bis: 'Бис',
	is_first_after_break: 'Первая после антракта',
	is_last_before_break: 'Последняя перед антрактом',
	take: 'Дубль/повтор попытки',
	is_poem: 'Стихи',
	is_ensemble: 'Ансамбль',
	is_pseudo_duet: 'Псевдодуэт',
	with_mls: 'С MLS',
	plays_mls_guitar: 'MLS на гитаре',
	plays_mls_keyboards: 'MLS на клавишных',
	has_mls_voice: 'Голос MLS',
	has_synth: 'Синтезатор',
	mks_no_guitar: 'MKS без гитары',
	mks_no_voice: 'MKS без голоса',
	sings_with_minus: 'Поёт под минус',
	sings_incomplete: 'Спето не полностью',
	sings_mls_only: 'Поёт только MLS',
};
// Короткие подписи для бирок в строке (при большом числе настроенных
// чекбоксов полные названия с чекбоксами перестают влезать — см. фикс
// 2026-08-17). Полные названия остаются в меню «+».
const PARAM_SHORT_LABELS = {
	is_premiere: 'Прем.',
	is_first: '1-я',
	is_last: 'Посл.',
	is_bis: 'Бис',
	is_first_after_break: 'После антр.',
	is_last_before_break: 'До антр.',
	take: 'Дубль',
	is_poem: 'Стихи',
	is_ensemble: 'Ансамбль',
	is_pseudo_duet: 'Дуэт',
	with_mls: 'MLS',
	plays_mls_guitar: 'MLS гит.',
	plays_mls_keyboards: 'MLS клав.',
	has_mls_voice: 'MLS голос',
	has_synth: 'Синт.',
	mks_no_guitar: 'MKS без гит.',
	mks_no_voice: 'MKS без гол.',
	sings_with_minus: 'Минус',
	sings_incomplete: 'Не полн.',
	sings_mls_only: 'Только MLS',
};
const DEFAULT_PARAM_KEYS = ['is_premiere', 'is_bis', 'is_poem'];
/* ───────────────────────────────────────────────────────────── */

const props = defineProps({
	value: { type: [Array, Object], default: null },
	collection: { type: String, default: null },
	field: { type: String, default: null },
	primaryKey: { type: [String, Number], default: null },
	// Directus передаёт каждое объявленное в index.js options[] поле отдельным
	// пропом с тем же именем (field: 'paramFields' -> props.paramFields), а
	// НЕ единым объектом props.options — так и не работало до этого фикса.
	paramFields: { type: Array, default: null },
});

// Чекбоксы, реально показываемые в строке — берём из настроек интерфейса
// (Data Model → Options → «Чекбоксы в строке»), иначе — дефолт.
const PARAM_FIELDS = computed(() => {
	const keys = props.paramFields?.length ? props.paramFields : DEFAULT_PARAM_KEYS;
	return keys.map((key) => ({
		key,
		label: PARAM_LABELS[key] || key,
		short: PARAM_SHORT_LABELS[key] || PARAM_LABELS[key] || key,
	}));
});

// Какие из настроенных флагов у строки реально включены — их и показываем
// бирками. Остальное скрыто за кнопкой "+", чтобы строка не разъезжалась
// вширь/ввысь при большом количестве настроенных чекбоксов.
function activeParams(row) {
	return PARAM_FIELDS.value.filter((p) => row[p.key]);
}

const menuRowId = ref(null); // id строки, у которой сейчас открыто меню "+"
function toggleMenu(row) {
	menuRowId.value = menuRowId.value === row.id ? null : row.id;
}
function closeMenu() {
	menuRowId.value = null;
}

const api = useApi();

const rows = ref([]);          // уже созданные исполнения этого концерта
const loading = ref(false);
const rowsError = ref(null);   // текст ошибки загрузки списка, если запрос упал
const query = ref('');         // строка поиска песни
const results = ref([]);       // результаты автокомплита
const activeIndex = ref(0);    // подсветка в выпадашке
const searchInput = ref(null); // ref на инпут для рефокуса
const dropdown = ref(null);    // ref на <ul>, чтобы скроллить активный пункт в вид

const allWorks = ref([]);      // весь справочник песен, тянем один раз при монтировании

// Пока концерт не сохранён — нет id, писать исполнения некуда.
const concertSaved = computed(
	() => props.primaryKey != null && props.primaryKey !== '+'
);

const rowFields = computed(() => [
	'id',
	NUMBER_FIELD,
	`${WORK_FK}.id`,
	...WORK_TITLE_FIELDS.map((f) => `${WORK_FK}.${f}`),
	...PARAM_FIELDS.value.map((p) => p.key),
]);

onMounted(() => {
	loadAllWorks();
	document.addEventListener('click', closeMenu);
});
onUnmounted(() => {
	document.removeEventListener('click', closeMenu);
});

// primaryKey у alias-полей вроде songs_performed не всегда готов к моменту
// onMounted — форма события может смонтировать поля раньше, чем до них
// доходит реальный id (или Directus переиспользует инстанс компонента между
// разными событиями без ремонта). onMounted(loadRows) в такой гонке иногда
// вызывался, когда concertSaved.value ещё был false, тихо выходил из
// loadRows() по раннему return и больше никогда не перезапускался — список
// оставался пустым навсегда, хотя сами perfs в базе были. watch с
// immediate:true перезапускает загрузку при любой смене primaryKey, включая
// момент, когда он наконец появляется.
watch(() => props.primaryKey, loadRows, { immediate: true });

// Справочник песен — несколько сотен штук, тянем целиком один раз и дальше
// фильтруем на клиенте (см. onQueryInput). Раньше здесь был запрос к API с
// filter[...][_icontains] на каждую букву, но в этой базе (sqlite) LOWER()
// ломает регистронезависимое сравнение на кириллице — это тот же баг, что и
// у штатного ?search= (см. docs/directus.md, «Открытые вопросы»), но задевает
// вообще все операторы _icontains/_istarts_with на нелатинских полях, не
// только штатный поиск. Проверено вживую: даже точное по регистру совпадение
// через _icontains возвращало 0 строк на "rusalka". Фильтрация в JS (как уже
// сделано в catalogue.html) этой проблемы не имеет — .toLowerCase() в JS
// корректно работает с юникодом.
async function loadAllWorks() {
	try {
		const res = await api.get(`/items/${WORK_COLLECTION}`, {
			params: {
				filter: EXCLUDE_HIDDEN ? { hidden: { _neq: true } } : {},
				fields: ['id', ...WORK_TITLE_FIELDS],
				sort: ['sort'],
				limit: -1,
			},
		});
		allWorks.value = res.data.data;
	} catch (e) {
		rowsError.value = `Справочник песен не загрузился: ${e?.response?.data?.errors?.[0]?.message || e?.message || e}`;
	}
}

async function loadRows() {
	if (!concertSaved.value) return;
	loading.value = true;
	rowsError.value = null;
	try {
		const res = await api.get(`/items/${PERF_COLLECTION}`, {
			params: {
				filter: { [EVENT_FK]: { _eq: props.primaryKey } },
				sort: [NUMBER_FIELD],
				fields: rowFields.value,
				limit: -1,
			},
		});
		rows.value = res.data.data;
	} catch (e) {
		rowsError.value = e?.response?.data?.errors?.[0]?.message || e?.message || String(e);
	} finally {
		loading.value = false;
	}
}

// Заголовок песни — та же логика, что в catalogue.html.
function capitalize(s) {
	return s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
}
function workTitle(work) {
	if (!work) return '—';
	if (work.name) return capitalize(work.fname || work.name);
	return work.fincipit || work.incipit || '—';
}
// Подсказка вторым планом (как "(fincipit)" на сайте) — помогает отличить
// одноимённые/похожие вещи в выпадашке.
function workHint(work) {
	if (!work) return '';
	return work.name ? work.fincipit || '' : '';
}

// Как в catalogue.html: нижний регистр + снятие диакритики + ё->е. Свой,
// а не общий с сайтом код, но намеренно та же логика — уже проверенная.
function normalize(text) {
	return (text || '')
		.toLowerCase()
		.trim()
		.normalize('NFD')
		.replace(/\p{Diacritic}/gu, '')
		.replace(/ё/g, 'е');
}

// Автокомплит: 2+ буквы -> фильтр по уже загруженному справочнику (см.
// loadAllWorks). Совпадения с начала поля — выше совпадений в середине.
function onQueryInput() {
	const q = normalize(query.value);
	if (q.length < 2) {
		results.value = [];
		return;
	}
	const scored = [];
	for (const work of allWorks.value) {
		let best = -1; // -1 = нет совпадения, 0 = с начала поля, 1 = внутри поля
		for (const f of SEARCH_FIELDS) {
			const v = normalize(work[f]);
			const idx = v.indexOf(q);
			if (idx === 0) { best = 0; break; }
			if (idx > 0 && best !== 0) best = 1;
		}
		if (best >= 0) scored.push({ work, best });
	}
	scored.sort((a, b) => a.best - b.best); // сначала совпадения с начала слова/строки
	results.value = scored.slice(0, 10).map((s) => s.work);
	activeIndex.value = 0;
}

function move(delta) {
	if (!results.value.length) return;
	activeIndex.value =
		(activeIndex.value + delta + results.value.length) % results.value.length;
	dropdown.value
		?.querySelector('li.active')
		?.scrollIntoView({ block: 'nearest' });
}

// Enter/выбор: создаём исполнение с FK на песню, чистим строку, фокус остаётся.
// id и number сюда не передаём — их проставляет Flow «Auto perf id».
async function pick(song) {
	const chosen = song ?? results.value[activeIndex.value];
	if (!chosen || !concertSaved.value) return;

	const payload = {
		[EVENT_FK]: props.primaryKey,
		[WORK_FK]: chosen.id,
	};

	const res = await api.post(`/items/${PERF_COLLECTION}`, payload, {
		params: { fields: rowFields.value },
	});
	rows.value.push(res.data.data);

	query.value = '';
	results.value = [];
	searchInput.value?.focus?.();
}

async function toggleParam(row, key) {
	const next = !row[key];
	await api.patch(`/items/${PERF_COLLECTION}/${row.id}`, { [key]: next });
	row[key] = next;
}

async function removeRow(row) {
	await api.delete(`/items/${PERF_COLLECTION}/${row.id}`);
	rows.value = rows.value.filter((r) => r.id !== row.id);
}
</script>

<template>
	<div class="setlist-editor">
		<v-notice v-if="!concertSaved" type="info">
			Сначала сохрани концерт — потом добавляй песни.
		</v-notice>

		<template v-else>
			<v-notice v-if="rowsError" type="danger">
				{{ rowsError }}
			</v-notice>
			<v-notice v-else-if="!loading && !rows.length" type="info">
				Пока ни одной песни не занесено через этот редактор.
			</v-notice>

			<!-- Уже введённые исполнения -->
			<div v-for="row in rows" :key="row.id" class="perf-row">
				<span class="idx">{{ row[NUMBER_FIELD] }}.</span>
				<span class="title">{{ workTitle(row[WORK_FK]) }}</span>
				<span class="flags">
					<button
						v-for="p in activeParams(row)"
						:key="p.key"
						type="button"
						class="flag-chip"
						:title="p.label + ' — клик, чтобы снять'"
						@click.stop="toggleParam(row, p.key)"
					>{{ p.short }}</button>

					<button
						type="button"
						class="flag-add"
						title="Добавить параметр"
						@click.stop="toggleMenu(row)"
					>+</button>

					<div v-if="menuRowId === row.id" class="flag-menu" @click.stop>
						<label v-for="p in PARAM_FIELDS" :key="p.key" class="flag-menu-item">
							<v-checkbox
								:model-value="!!row[p.key]"
								@update:model-value="toggleParam(row, p.key)"
							/>
							<span>{{ p.label }}</span>
						</label>
					</div>
				</span>
				<a
					:href="`/admin/content/${PERF_COLLECTION}/${encodeURIComponent(row.id)}`"
					target="_blank"
					rel="noopener"
					class="open-perf"
					title="Открыть исполнение (остальные поля, ревизии...)"
				>
					<v-icon name="launch" small />
				</a>
				<v-icon
					name="close"
					clickable
					class="remove"
					@click="removeRow(row)"
				/>
			</div>

			<!-- Строка ввода новой песни -->
			<div class="add-row">
				<input
					ref="searchInput"
					v-model="query"
					class="song-input"
					placeholder="Название песни…"
					@input="onQueryInput"
					@keydown.down.prevent="move(1)"
					@keydown.up.prevent="move(-1)"
					@keydown.enter.prevent="pick()"
					@keydown.esc.prevent="results = []"
				/>
				<ul v-if="results.length" ref="dropdown" class="dropdown">
					<li
						v-for="(s, i) in results"
						:key="s.id"
						:class="{ active: i === activeIndex }"
						@mousedown.prevent="pick(s)"
					>
						{{ workTitle(s) }}
						<span v-if="workHint(s)" class="hint">({{ workHint(s) }})</span>
					</li>
				</ul>
			</div>

			<v-progress-circular v-if="loading" indeterminate small />
		</template>
	</div>
</template>

<style scoped>
.perf-row {
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 4px 0;
	border-bottom: 1px solid var(--theme--border-color-subdued, #e4e4e4);
}
.idx { width: 28px; text-align: right; color: var(--theme--foreground-subdued); }
.title { flex: 1; }
.remove { color: var(--theme--danger); }

.flags {
	position: relative;
	display: inline-flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 4px;
}
.flag-chip {
	border: none;
	border-radius: 999px;
	padding: 2px 8px;
	font-size: 0.8em;
	white-space: nowrap;
	cursor: pointer;
	background: var(--theme--primary-background, var(--theme--background-subdued));
	color: var(--theme--primary, var(--theme--foreground));
}
.flag-chip:hover { opacity: 0.75; }
.flag-add {
	border: 1px dashed var(--theme--border-color);
	border-radius: 999px;
	width: 22px;
	height: 22px;
	line-height: 1;
	cursor: pointer;
	background: transparent;
	color: var(--theme--foreground-subdued);
}
.flag-add:hover {
	border-color: var(--theme--primary);
	color: var(--theme--primary);
}
.flag-menu {
	position: absolute;
	top: 100%;
	left: 0;
	z-index: 20;
	margin-top: 4px;
	padding: 6px;
	display: flex;
	flex-direction: column;
	white-space: nowrap;
	background: var(--theme--background);
	border: 1px solid var(--theme--border-color);
	border-radius: var(--theme--border-radius, 6px);
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}
.flag-menu-item { display: flex; align-items: center; gap: 4px; padding: 2px 4px; }
.open-perf { display: inline-flex; color: var(--theme--foreground-subdued); }
.open-perf:hover { color: var(--theme--primary); }
.add-row { position: relative; margin-top: 8px; }
.song-input {
	width: 100%;
	padding: 8px 10px;
	border: 2px solid var(--theme--border-color);
	border-radius: var(--theme--border-radius, 6px);
	background: var(--theme--background);
	color: var(--theme--foreground);
}
.dropdown {
	position: absolute;
	z-index: 10;
	left: 0; right: 0;
	margin: 2px 0 0;
	padding: 0;
	list-style: none;
	background: var(--theme--background);
	border: 1px solid var(--theme--border-color);
	border-radius: var(--theme--border-radius, 6px);
	max-height: 260px;
	overflow-y: auto;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}
.dropdown li { padding: 8px 10px; cursor: pointer; }
.dropdown li:hover { background: var(--theme--background-subdued); }
.dropdown li.active {
	background: var(--theme--primary-background, var(--theme--background-subdued));
	outline: 2px solid var(--theme--primary, transparent);
	outline-offset: -2px;
}
.hint { color: var(--theme--foreground-subdued); font-size: 0.9em; margin-left: 4px; }
</style>
