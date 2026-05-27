export type Disk = {
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
};