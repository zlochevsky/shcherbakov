
const axios = require('axios');

const DIRECTUS_URL = 'https://db.sch.com.ru'; // URL вашего Directus
const API_TOKEN = '9kSTtq6uGSNBtTbrm0pyQ_QrucJdJmgm'; // Вставьте здесь ваш API токен
const COLLECTION_NAME = 'works'; // Название коллекции
const SOURCE_FIELD = 'year'; // Поле-источник
const TARGET_FIELD = 'date'; // Целевое поле
const LIMIT = '-1';

async function updateRecords() {
    try {
        // Получение всех записей из коллекции
        const { data } = await axios.get(`${DIRECTUS_URL}/items/${COLLECTION_NAME}?limit=${LIMIT}`, {
            headers: {
                Authorization: `Bearer ${API_TOKEN}`,
            },
        });

        const records = data.data;

        for (const record of records) {
            const sourceValue = record[SOURCE_FIELD];

            // Преобразование строки в число
            const targetValue = parseInt(sourceValue, 10);

            if (!isNaN(targetValue)) {
                // Обновление записи
                await axios.patch(
                    `${DIRECTUS_URL}/items/${COLLECTION_NAME}/${record.id}`,
                    {
                        [TARGET_FIELD]: targetValue,
                    },
                    {
                        headers: {
                            Authorization: `Bearer ${API_TOKEN}`,
                        },
                    }
                );
                console.log(`Record ${record.id} updated: ${SOURCE_FIELD} -> ${TARGET_FIELD}`);
            } else {
                console.log(`Skipping record ${record.id}: Invalid number in ${SOURCE_FIELD}`);
            }
        }

        console.log('All records updated successfully.');
    } catch (error) {
        console.error('Error updating records:', error.response?.data || error.message);
    }
}

updateRecords();
