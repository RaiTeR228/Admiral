import axios from 'axios';
import { useState, useEffect } from 'react';
import { FlatList, View, Text, StyleSheet } from 'react-native';
// import { DataConverter } from '../types/converters';

const API_URL = 'http://127.0.0.1:8000/api/disk/';
const API_KEY = '31fae73538bd56225e08417f62d7c874c8c2c578f8afb24651dacb5b691cb442';

interface ServerResponse {
    success: boolean;
    id: number;
    server_uuid: string;
    disk: {
        disk_name: string;
        max_swap: string;
        max_disk: string;
        free_disk: string;
        server_uuid: string;
        created_at: null;
        updated_at: null;
        usage_percent: number;
    };
}

// {
//     "success": true,
//     "server_uuid": "829b4efe-908f-416e-bee2-8879bc079dca",
//     "disk": {
//         "disk_name": "C:\\",
//         "max_swap": "3145728000",
//         "max_disk": "255351234560",
//         "free_disk": "31437463552",
//         "server_uuid": "829b4efe-908f-416e-bee2-8879bc079dca",
//         "created_at": null,
//         "updated_at": null,
//         "usage_percent": 87.69
//     }
// }

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/',
    headers: {
        'Authorization': `Api-Key ${API_KEY}`,
        'Content-Type': 'application/json',
    }
});

const DiskList = () => {
    const [Data, setServerData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const getServerData = async () => {
        try {
            setLoading(true);
            const response = await apiClient.get<ServerResponse>('disk/');
            // console.log('Disk data:', response.data.disk);
            setServerData(response.data.disk);
        } catch (err) {
            setError('Ошибка загрузки данных');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }

    const bytesToGB = (bytes: string): string => {
        const gb = parseFloat(bytes) / (1024 * 1024 * 1024);
        return `${gb.toFixed(2)} GB`;
    };

    useEffect(() => {
        getServerData();
    }, []);

    if (loading) {
        return (
            <View style={styles.container}>
                <Text>Загрузка информации о диске ...</Text>
            </View>
        );
    }

    if (error) {
        return (
            <View style={styles.container}>
                <Text style={styles.error}>Ошибка: {error}</Text>
            </View>
        );
    }

    if (!Data) {
        return (
            <View style={styles.container}>
                <Text>Нет данных о диске</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Информация о диске</Text>
            <View style={styles.card}>
                <Text style={styles.value}>{Data.disk_name}</Text>
            </View>
            <View style={styles.card}>
                <Text style={styles.label}>Максимальный объем:</Text>
                {/* <Text style={styles.value}>{Data.max_disk}</Text> */}
                <Text>{bytesToGB(Data.max_disk)}</Text>
                <Text style={styles.label}>Свободный объем:</Text>
                <Text>{bytesToGB(Data.free_disk)}</Text>
                <Text style={styles.label}>Swap:</Text>
                <Text>{bytesToGB(Data.max_swap)}</Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        padding: 15,
    },
    title: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 10,
    },
    card: {
        backgroundColor: '#f0f0f0',
        padding: 15,
        borderRadius: 8,
        marginBottom: 10,
    },
    label: {
        fontSize: 14,
        color: '#666',
        marginBottom: 5,
    },
    value: {
        fontSize: 16,
        fontWeight: '600',
        color: '#333',
    },
    error: {
        color: 'red',
    },
});

export default DiskList;