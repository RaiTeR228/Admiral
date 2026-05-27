// utils/converters.ts
export class DataConverter {
    // Преобразование байт в ГБ
    static bytesToGB(bytes: string | number, decimals: number = 2): string {
        const bytesNum = typeof bytes === 'string' ? parseFloat(bytes) : bytes;
        const gb = bytesNum / (1024 * 1024 * 1024);
        return `${gb.toFixed(decimals)} GB`;
    }
    
    // Преобразование байт в удобный формат (автоматический выбор единиц)
    static formatBytes(bytes: string | number, decimals: number = 2): string {
        const bytesNum = typeof bytes === 'string' ? parseFloat(bytes) : bytes;
        if (bytesNum === 0) return '0 Bytes';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytesNum) / Math.log(k));
        
        return `${parseFloat((bytesNum / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
    }
    
    // Преобразование процентов
    static formatPercent(value: number | string, decimals: number = 1): string {
        const num = typeof value === 'string' ? parseFloat(value) : value;
        return `${num.toFixed(decimals)}%`;
    }
}

// Использование в компоненте:
// <Text>{DataConverter.bytesToGB(diskData.free_disk)}</Text>