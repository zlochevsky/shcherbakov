<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import { useApi } from '@directus/extensions-sdk';

/* ─────────────────────────────────────────────────────────────
   Треклист альбома (sets) поверх sets_entries. Сестра setlist-editor
   и perf-picker: как и они, пишет через api.* напрямую (кнопка Save формы
   при этом не нужна), но не создаёт исполнения, а выбирает существующие.
   id записи и её номер (если не передан) проставляет Flow
   «Auto set entry id». Номер в строке можно править, id при этом не меняется
   (id «раз и навсегда»).
   ───────────────────────────────────────────────────────────── */
const ENTRY_COLLECTION = 'sets_entries';
const SET_FK = 'sets_id';
const PERF_FK = 'perfs_id';
const PERF_COLLECTION = 'perfs';
const WORK_FK = 'works_id';
const EVENT_FK = 'events_id';
const EVENT_COLLECTION = 'events';
const WORK_COLLECTION = 'works';
const NUMBER_FIELD = 'num';
const SIDE_FIELD = 'side';
const SIDES = ['A', 'B'];
const WORK_TITLE_FIELDS = ['name', 'qualifier', 'incipit', 'fincipit', 'sort'];
const EVENT_FIELDS = ['id', 'date', 'year', 'town'];
/* ───────────────────────────────────────────────────────────── */

const props = defineProps({
	value: { type: [Array, Object], default: null },
	collection: { type: String, default: null },
	field: { type: String, default: null },
	primaryKey: { type: [String, Number], default: null },
});
// См. комментарий в setlist-editor: без декларации Directus-овский @input
// прилипает к корневому <div> как DOM-листенер.
defineEmits(['input']);

const api = useApi();

const rows = ref([]);
const loading = ref(false);
const error = ref('');
const query = ref('');
const activeIndex = ref(0);
const listOpen = ref(false);
const searchInput = ref(null);

// Режим 1 (событие не закреплено): песня → её исполнения.
const allWorks = ref([]);         // справочник песен, грузится один раз
const chosenWork = ref(null);     // выбранная песня; null — шаг «песня»
const workPerfs = ref([]);        // исполнения выбранной песни, свежие сверху
// Режим 2 (событие закреплено): песни из сет-листа этого события.
const pinned = ref(null);         // { id, date, year, town }
const eventPerfs = ref([]);       // исполнения закреплённого события по num
const pinning = ref(false);       // открыт поиск события для закрепления
const eventQuery = ref('');
const eventResults = ref([]);
const eventActive = ref(0);
const eventInput = ref(null);
let eventTimer = null;

const saved = computed(() => props.primaryKey != null && props.primaryKey !== '+');
const addedPerfIds = computed(() => new Set(rows.value.map((r) => r[PERF_FK]?.id)));

const entryFields = [
	'id',
	NUMBER_FIELD,
	SIDE_FIELD,
	`${PERF_FK}.id`,
	...WORK_TITLE_FIELDS.map((f) => `${PERF_FK}.${WORK_FK}.${f}`),
	...EVENT_FIELDS.map((f) => `${PERF_FK}.${EVENT_FK}.${f}`),
];

function describeError(e, fallback) {
	const apiError = e?.response?.data?.errors?.[0];
	if (apiError?.extensions?.code === 'RECORD_NOT_UNIQUE') return 'Такая запись уже есть в альбоме.';
	return apiError?.message || fallback;
}

function capitalize(s) {
	return s ? s.replace(/^([^\p{L}\p{N}]*)(.)/u, (m, pre, ch) => pre + ch.toUpperCase()) : s;
}
function workTitle(work) {
	if (!work) return '—';
	if (work.name) {
		// Как workTitle() в setlist-editor и partials/work-title.html: *курсив* снят,
		// qualifier (": вчера") различает одноимённые песни. Поля fname больше нет.
		const t = capitalize(work.name.trim().replace(/\*([^*]+)\*/g, '$1'));
		return work.qualifier ? `${t}: ${work.qualifier}` : t;
	}
	return work.fincipit || work.incipit || '—';
}
function eventLabel(ev) {
	if (!ev) return '';
	return [ev.id, ev.town].filter(Boolean).join(' · ');
}

watch(
	() => props.primaryKey,
	(pk) => {
		if (pk != null && pk !== '+') loadRows();
		else rows.value = [];
	},
	{ immediate: true }
);

function sortRows() {
	rows.value.sort((a, b) => (a[NUMBER_FIELD] ?? 0) - (b[NUMBER_FIELD] ?? 0));
}

async function loadRows() {
	if (!saved.value) return;
	loading.value = true;
	error.value = '';
	try {
		const res = await api.get(`/items/${ENTRY_COLLECTION}`, {
			params: {
				filter: { [SET_FK]: { _eq: props.primaryKey } },
				sort: [NUMBER_FIELD],
				fields: entryFields,
				limit: -1,
			},
		});
		rows.value = res.data.data;
	} catch (e) {
		error.value = describeError(e, 'Не удалось загрузить треклист.');
	} finally {
		loading.value = false;
	}
}

/* Добавление (переделано 2026-11-03: поиск сразу по всем исполнениям давал
   слишком много лишнего). Одно поле ввода, два режима:
   1) событие не закреплено — ввод названия песни (только name и sort, как в
      setlist-editor), выбор песни → список её исполнений, свежие сверху; ввод
      «2003», «бостон», «L2003-04» сужает его по году, городу, id события.
      Подходит для сборников из разных событий.
   2) событие закреплено — список его сет-листа по номерам; пустой ввод — весь,
      ввод сужает по названию. Концерт добавляется подряд Enter'ами.
   Закрепить можно событие последнего трека (кнопка) или найти любое.
   Поиск события — явный _icontains, не ?search= (баг с кириллицей). */

// Как в setlist-editor и catalogue.html: регистр, диакритика, ё→е, без *разметки*.
function normalize(text) {
	return (text || '')
		.toLowerCase()
		.trim()
		.normalize('NFD')
		.replace(/\p{Diacritic}/gu, '')
		.replace(/ё/g, 'е')
		.replace(/\*/g, '');
}

async function loadAllWorks() {
	if (allWorks.value.length) return;
	try {
		const res = await api.get(`/items/${WORK_COLLECTION}`, {
			params: { fields: ['id', ...WORK_TITLE_FIELDS], sort: ['sort'], limit: -1 },
		});
		allWorks.value = res.data.data;
	} catch (e) {
		error.value = describeError(e, 'Справочник песен не загрузился.');
	}
}
loadAllWorks();

function perfFields() {
	return [
		'id',
		NUMBER_FIELD,
		...WORK_TITLE_FIELDS.map((f) => `${WORK_FK}.${f}`),
		...EVENT_FIELDS.map((f) => `${EVENT_FK}.${f}`),
	];
}

// Что сейчас в выпадающем списке: { kind: 'work' | 'perf', item }.
const items = computed(() => {
	const q = normalize(query.value);
	if (pinned.value) {
		return eventPerfs.value
			.filter((p) => !q || [p[WORK_FK]?.name, p[WORK_FK]?.sort, p[WORK_FK]?.fincipit]
				.some((t) => normalize(t).includes(q)))
			.map((p) => ({ kind: 'perf', item: p }));
	}
	if (chosenWork.value) {
		const tokens = q.split(/\s+/).filter(Boolean);
		return workPerfs.value
			.filter((p) => tokens.every((t) => {
				const ev = p[EVENT_FK] || {};
				return [p.id, ev.id, ev.town, ev.year].some((v) => normalize(String(v ?? '')).includes(t));
			}))
			.map((p) => ({ kind: 'perf', item: p }));
	}
	if (q.length < 2) return [];
	const scored = [];
	for (const w of allWorks.value) {
		const name = normalize(w.name), sort = normalize(w.sort);
		const score = name.startsWith(q) || sort.startsWith(q) ? 0
			: name.includes(q) || sort.includes(q) ? 1 : -1;
		if (score >= 0) scored.push({ score, w });
	}
	scored.sort((x, y) => x.score - y.score);
	return scored.slice(0, 12).map(({ w }) => ({ kind: 'work', item: w }));
});
watch(query, () => {
	activeIndex.value = 0;
	listOpen.value = true;
});

const placeholder = computed(() =>
	pinned.value ? 'Песня из этого события (пусто — весь сет-лист)…'
	: chosenWork.value ? 'Исполнение: год / город / id события (пусто — все)…'
	: 'Название песни…');

// Событие последнего трека — кандидат на закрепление.
const lastEvent = computed(() => rows.value[rows.value.length - 1]?.[PERF_FK]?.[EVENT_FK] || null);

function focusInput() {
	nextTick(() => searchInput.value?.focus?.());
}

async function chooseWork(work) {
	chosenWork.value = work;
	query.value = '';
	workPerfs.value = [];
	try {
		const res = await api.get(`/items/${PERF_COLLECTION}`, {
			params: {
				filter: { [WORK_FK]: { _eq: work.id } },
				fields: perfFields(),
				sort: [`-${EVENT_FK}.date`, NUMBER_FIELD],
				limit: -1,
			},
		});
		workPerfs.value = res.data.data;
	} catch (e) {
		error.value = describeError(e, 'Не удалось загрузить исполнения песни.');
	}
	activeIndex.value = 0;
	listOpen.value = true;
	focusInput();
}

function backToSongs() {
	chosenWork.value = null;
	workPerfs.value = [];
	query.value = '';
	focusInput();
}

async function pinEvent(ev) {
	if (!ev) return;
	pinned.value = ev;
	pinning.value = false;
	eventQuery.value = '';
	eventResults.value = [];
	chosenWork.value = null;
	query.value = '';
	eventPerfs.value = [];
	try {
		const res = await api.get(`/items/${PERF_COLLECTION}`, {
			params: { filter: { [EVENT_FK]: { _eq: ev.id } }, fields: perfFields(), sort: [NUMBER_FIELD], limit: -1 },
		});
		eventPerfs.value = res.data.data;
	} catch (e) {
		error.value = describeError(e, 'Не удалось загрузить сет-лист события.');
	}
	activeIndex.value = 0;
	listOpen.value = true;
	focusInput();
}

function unpin() {
	pinned.value = null;
	eventPerfs.value = [];
	query.value = '';
	focusInput();
}

function startPinning() {
	pinning.value = true;
	nextTick(() => eventInput.value?.focus?.());
}

function onEventInput() {
	clearTimeout(eventTimer);
	if (eventQuery.value.trim().length < 2) {
		eventResults.value = [];
		return;
	}
	eventTimer = setTimeout(searchEvents, 200);
}

async function searchEvents() {
	const tokens = eventQuery.value.trim().split(/\s+/).filter(Boolean);
	if (!tokens.length) return;
	try {
		const res = await api.get(`/items/${EVENT_COLLECTION}`, {
			params: {
				// каждое слово — в id, городе или году: «2003 бостон», «L2003-04», «s1985»
				filter: {
					_and: tokens.map((t) => ({
						_or: [
							{ id: { _icontains: t } },
							{ town: { _icontains: t } },
							...(/^\d{4}$/.test(t) ? [{ year: { _eq: Number(t) } }] : []),
						],
					})),
				},
				fields: EVENT_FIELDS,
				sort: ['-date'],
				limit: 20,
			},
		});
		eventResults.value = res.data.data;
		eventActive.value = 0;
	} catch (e) {
		error.value = describeError(e, 'Не удалось найти события.');
	}
}

function moveEvent(delta) {
	if (!eventResults.value.length) return;
	eventActive.value = (eventActive.value + delta + eventResults.value.length) % eventResults.value.length;
}

function move(delta) {
	if (!items.value.length) return;
	listOpen.value = true;
	activeIndex.value = (activeIndex.value + delta + items.value.length) % items.value.length;
}

function onEsc() {
	if (listOpen.value && items.value.length) listOpen.value = false;
	else if (chosenWork.value) backToSongs();
}

function onBackspace(ev) {
	// пустое поле + Backspace на шаге «исполнение» — назад к выбору песни
	if (!query.value && chosenWork.value && !pinned.value) {
		ev.preventDefault();
		backToSongs();
	}
}

function pick(entry) {
	const e = entry ?? items.value[activeIndex.value];
	if (!e) return;
	if (e.kind === 'work') chooseWork(e.item);
	else addPerf(e.item);
}

// Добавление: id и (без num) номер проставляет Flow. Сторону наследуем от
// последней строки. В режиме события список остаётся открытым и курсор идёт
// дальше; в режиме песни — назад к вводу следующей песни. Уже добавленные помечены.
async function addPerf(chosen) {
	if (!chosen || !saved.value) return;
	error.value = '';
	if (addedPerfIds.value.has(chosen.id)) {
		error.value = `«${workTitle(chosen[WORK_FK])}» (${chosen[EVENT_FK]?.id ?? chosen.id}) уже в альбоме.`;
		return;
	}
	const last = rows.value[rows.value.length - 1];
	const payload = { [SET_FK]: props.primaryKey, [PERF_FK]: chosen.id };
	if (last?.[SIDE_FIELD]) payload[SIDE_FIELD] = last[SIDE_FIELD];
	try {
		const res = await api.post(`/items/${ENTRY_COLLECTION}`, payload, { params: { fields: entryFields } });
		rows.value.push(res.data.data);
		sortRows();
		if (pinned.value) {
			if (activeIndex.value < items.value.length - 1) activeIndex.value += 1;
		} else {
			backToSongs();
		}
	} catch (e) {
		error.value = describeError(e, 'Не удалось добавить исполнение.');
	} finally {
		focusInput();
	}
}

async function saveNum(row, ev) {
	const n = parseInt(ev.target.value, 10);
	if (!Number.isInteger(n) || n < 1) {
		ev.target.value = row[NUMBER_FIELD];
		return;
	}
	if (n === row[NUMBER_FIELD]) return;
	error.value = '';
	try {
		await api.patch(`/items/${ENTRY_COLLECTION}/${row.id}`, { [NUMBER_FIELD]: n });
		row[NUMBER_FIELD] = n;
		sortRows();
	} catch (e) {
		ev.target.value = row[NUMBER_FIELD];
		error.value = describeError(e, 'Не удалось изменить номер.');
	}
}

async function saveSide(row, ev) {
	const v = ev.target.value || null;
	error.value = '';
	try {
		await api.patch(`/items/${ENTRY_COLLECTION}/${row.id}`, { [SIDE_FIELD]: v });
		row[SIDE_FIELD] = v;
	} catch (e) {
		ev.target.value = row[SIDE_FIELD] ?? '';
		error.value = describeError(e, 'Не удалось изменить сторону.');
	}
}

async function removeRow(row) {
	error.value = '';
	try {
		await api.delete(`/items/${ENTRY_COLLECTION}/${row.id}`);
		rows.value = rows.value.filter((r) => r.id !== row.id);
	} catch (e) {
		error.value = describeError(e, 'Не удалось убрать исполнение.');
	}
}
</script>

<template>
	<div class="album-tracklist">
		<v-notice v-if="!saved" type="info">Сначала сохрани альбом — потом добавляй исполнения.</v-notice>

		<template v-else>
			<v-notice v-if="error" type="warning" class="error-notice" closable @close="error = ''">
				{{ error }}
			</v-notice>

			<div v-for="row in rows" :key="row.id" class="entry-row">
				<input
					class="num"
					type="number"
					min="1"
					:value="row[NUMBER_FIELD]"
					title="Номер в альбоме"
					@change="saveNum(row, $event)"
					@keydown.enter.prevent="$event.target.blur()"
				/>
				<select class="side" :value="row[SIDE_FIELD] ?? ''" title="Сторона" @change="saveSide(row, $event)">
					<option value="">—</option>
					<option v-for="s in SIDES" :key="s" :value="s">{{ s }}</option>
				</select>
				<span class="title">{{ workTitle(row[PERF_FK]?.[WORK_FK]) }}</span>
				<span class="hint">{{ eventLabel(row[PERF_FK]?.[EVENT_FK]) || row[PERF_FK]?.id }}</span>
				<v-icon name="close" clickable class="remove" @click="removeRow(row)" />
			</div>

			<div class="add-row">
				<!-- Закрепление события -->
				<div class="pin-row">
					<template v-if="pinned">
						Событие закреплено: <b>{{ eventLabel(pinned) }}</b>
						<span class="hint">{{ eventPerfs.length }} исп.</span>
						<v-button x-small secondary @click="unpin">Открепить</v-button>
					</template>
					<template v-else-if="pinning">
						<div class="event-box">
							<input
								ref="eventInput"
								v-model="eventQuery"
								class="event-input"
								placeholder="Событие: id / год / город…"
								@input="onEventInput"
								@blur="pinning = false"
								@keydown.down.prevent="moveEvent(1)"
								@keydown.up.prevent="moveEvent(-1)"
								@keydown.enter.prevent="pinEvent(eventResults[eventActive])"
								@keydown.esc.prevent="pinning = false"
							/>
							<ul v-if="eventResults.length" class="dropdown">
								<li
									v-for="(ev, i) in eventResults"
									:key="ev.id"
									:class="{ active: i === eventActive }"
									@mousedown.prevent="pinEvent(ev)"
								>
									{{ ev.id }} <span class="hint">{{ ev.town }}</span>
								</li>
							</ul>
						</div>
					</template>
					<template v-else>
						<v-button v-if="lastEvent" x-small secondary @click="pinEvent(lastEvent)">
							Закрепить {{ eventLabel(lastEvent) }}
						</v-button>
						<v-button x-small secondary @click="startPinning">
							{{ lastEvent ? 'Другое событие…' : 'Закрепить событие…' }}
						</v-button>
					</template>
				</div>

				<!-- Шаг «исполнение» в режиме песни: какая песня выбрана -->
				<div v-if="chosenWork && !pinned" class="chosen-work">
					Песня: <b>{{ workTitle(chosenWork) }}</b>
					<span class="hint">{{ workPerfs.length }} исп.</span>
					<v-icon name="close" small clickable title="Другая песня" @click="backToSongs" />
				</div>

				<div class="song-box">
					<input
						ref="searchInput"
						v-model="query"
						class="song-input"
						:placeholder="placeholder"
						@focus="listOpen = true"
						@blur="listOpen = false"
						@keydown.down.prevent="move(1)"
						@keydown.up.prevent="move(-1)"
						@keydown.enter.prevent="pick()"
						@keydown.esc.prevent="onEsc"
						@keydown.backspace="onBackspace"
					/>
					<ul v-if="listOpen && items.length" class="dropdown">
						<li
							v-for="(e, i) in items"
							:key="e.kind + e.item.id"
							:class="{ active: i === activeIndex, added: e.kind === 'perf' && addedPerfIds.has(e.item.id) }"
							@mousedown.prevent="pick(e)"
						>
							<template v-if="e.kind === 'work'">
								{{ workTitle(e.item) }}
								<span v-if="e.item.name && e.item.fincipit" class="hint">({{ e.item.fincipit }})</span>
							</template>
							<template v-else-if="pinned">
								<span v-if="addedPerfIds.has(e.item.id)" class="mark">✓</span>
								<span class="hint">{{ e.item[NUMBER_FIELD] }}.</span>
								{{ workTitle(e.item[WORK_FK]) }}
							</template>
							<template v-else>
								<span v-if="addedPerfIds.has(e.item.id)" class="mark">✓</span>
								{{ eventLabel(e.item[EVENT_FK]) || e.item.id }}
								<span class="hint">№ {{ e.item[NUMBER_FIELD] }}</span>
							</template>
						</li>
					</ul>
				</div>
			</div>

			<v-progress-circular v-if="loading" indeterminate small />
		</template>
	</div>
</template>

<style scoped>
.error-notice { margin-bottom: 8px; }
.entry-row {
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 4px 0;
	border-bottom: 1px solid var(--theme--border-color-subdued, #e4e4e4);
}
.num, .side {
	padding: 4px 6px;
	border: 1px solid var(--theme--border-color);
	border-radius: var(--theme--border-radius, 6px);
	background: var(--theme--background);
	color: var(--theme--foreground);
}
.num { width: 64px; }
.side { width: 60px; }
.title { flex: 1; }
.hint { color: var(--theme--foreground-subdued); font-size: 0.9em; margin-left: 4px; }
.remove { color: var(--theme--danger); }
.add-row { position: relative; margin-top: 8px; }
.song-input {
	width: 100%;
	padding: 8px 10px;
	border: 2px solid var(--theme--border-color);
	border-radius: var(--theme--border-radius, 6px);
	background: var(--theme--background);
	color: var(--theme--foreground);
}
.pin-row, .chosen-work { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 6px; }
.event-box, .song-box { position: relative; flex: 1; }
.event-input {
	width: 100%;
	padding: 4px 8px;
	border: 1px solid var(--theme--border-color);
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
	max-height: 320px;
	overflow-y: auto;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}
.dropdown li { padding: 8px 10px; cursor: pointer; }
.dropdown li.active, .dropdown li:hover { background: var(--theme--background-subdued); }
.dropdown li.added { color: var(--theme--foreground-subdued); }
.mark { color: var(--theme--success, green); margin-right: 4px; }
</style>
