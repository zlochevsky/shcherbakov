import InterfaceComponent from './interface.vue';

// Полный список булевых полей perfs (сверено с живой базой 2026-08-17,
// см. docs/directus.md) — отсюда админ в Settings → Data Model выбирает,
// какие показывать чекбоксами прямо в строке сетлиста.
const PARAM_CHOICES = [
	{ text: 'Премьера', value: 'is_premiere' },
	{ text: 'Первая песня концерта', value: 'is_first' },
	{ text: 'Последняя песня концерта', value: 'is_last' },
	{ text: 'Бис', value: 'is_bis' },
	{ text: 'Первая после антракта', value: 'is_first_after_break' },
	{ text: 'Последняя перед антрактом', value: 'is_last_before_break' },
	{ text: 'Дубль/повтор попытки', value: 'take' },
	{ text: 'Стихи', value: 'is_poem' },
	{ text: 'Ансамбль', value: 'is_ensemble' },
	{ text: 'Псевдодуэт', value: 'is_pseudo_duet' },
	{ text: 'С MLS', value: 'with_mls' },
	{ text: 'MLS на гитаре', value: 'plays_mls_guitar' },
	{ text: 'MLS на клавишных', value: 'plays_mls_keyboards' },
	{ text: 'Голос MLS', value: 'has_mls_voice' },
	{ text: 'Синтезатор', value: 'has_synth' },
	{ text: 'MKS без гитары', value: 'mks_no_guitar' },
	{ text: 'MKS без голоса', value: 'mks_no_voice' },
	{ text: 'Поёт под минус', value: 'sings_with_minus' },
	{ text: 'Спето не полностью', value: 'sings_incomplete' },
	{ text: 'Поёт только MLS', value: 'sings_mls_only' },
];

// Регистрация кастомного O2M-интерфейса для Directus 11.x.
// Вешается на alias-поле связи "исполнения" в коллекции концертов.
export default {
	id: 'setlist-editor',
	name: 'Редактор сетлиста',
	icon: 'queue_music',
	description:
		'Инлайн-ввод исполнений с автокомплитом песни по названию. Пишет FK на песню (id), не открывая модалку.',
	component: InterfaceComponent,
	types: ['alias'],
	localTypes: ['o2m'],
	group: 'relational',
	relational: true,
	options: [
		{
			field: 'paramFields',
			name: 'Чекбоксы в строке',
			type: 'json',
			meta: {
				width: 'full',
				interface: 'select-multiple-checkbox',
				note: 'Какие булевы поля perfs показывать галочками прямо в строке исполнения. По умолчанию — Премьера/Бис/Стихи. Остальное быстрее дозаполнить через табличный layout (spreadsheet-layout/super-table) на коллекции perfs.',
				options: { choices: PARAM_CHOICES },
			},
			schema: {
				default_value: ['is_premiere', 'is_bis', 'is_poem'],
			},
		},
	],
};
