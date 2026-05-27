export type TemperatureData = {
    id: number;
    server_uuid: string;
    temperature:{
        current_temp: number;
        status_critical: boolean;
    }

}

// "name": NAME_SERVER,
// "INSTALL_TOKEN": API_KEY,
// "sensor_name": sensor_name,
// "status_critical": status_critical,
// "current_temp": entry.current