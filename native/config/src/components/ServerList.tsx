import axios from 'axios';
import { useState, useEffect } from 'react';
import { FlatList, View, Text, StyleSheet } from 'react-native';
import RamCard from './RamCard';
import { Ram } from '@/types/Ram';

const API_URL = 'http://127.0.0.1:8000/api/cpu/';
const API_KEY = '31fae73538bd56225e08417f62d7c874c8c2c578f8afb24651dacb5b691cb442';

interface ServerResponse {
    success: boolean;
    id: number;
    server_uuid: string;
    cpu: {
        name: string;
        max_cores: string;
        max_threads: string;
    };
}


const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/',
    headers: {
        'Authorization': `Api-Key ${API_KEY}`,
        'Content-Type': 'application/json',
    }
});

const ServerList = () => {
    const [serverData, setServerData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const getServerData = async () => {
        try {
            setLoading(true);
            const response = await apiClient.get<ServerResponse>('cpu/');
            // console.log('CPU data:', response.data.cpu);
            setServerData(response.data.cpu);
        } catch (err) {
            setError('Ошибка загрузки данных');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        getServerData();
    }, []);

    if (loading) {
        return (
            <View style={styles.container}>
                <Text>Загрузка информации о CPU ...</Text>
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

    if (!serverData) {
        return (
            <View style={styles.container}>
                <Text>Нет данных о CPU</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Информация о CPU</Text>
            <View style={styles.card}>
                <Text style={styles.value}>{serverData.name}</Text>
            </View>
            <View style={styles.card}>
                <Text style={styles.label}>Количество ядер:</Text>
                <Text style={styles.value}>{serverData.max_cores}</Text>
                <Text style={styles.label}>Количество потоков:</Text>
                <Text style={styles.value}>{serverData.max_threads}</Text>
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

export default ServerList;