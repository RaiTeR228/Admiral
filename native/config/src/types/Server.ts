// жесткая типизация для объектов, которые приходят с сервера
export type Server = {
    id: number; 
    server_uuid: string;         
    server_info: {                
        id: number;
        name: string;
        ip_address: string | null;
    };
    cpu_name: string;              
    cores: string;                
    threads: string;              
    created_at: string;
    updated_at: string;
};