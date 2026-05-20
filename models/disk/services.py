# models/disk/services.py
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Disk
from server.models import Server
import logging
import re

logger = logging.getLogger(__name__)


class ServerAuthenticationService:
    
    @staticmethod
    def authenticate_server(api_key):
        if not api_key:
            return None, "API key required"
        
        try:
            server = Server.objects.get(api_key=api_key)
            return server, None
        except Server.DoesNotExist:
            return None, "Invalid API key"
    
    @staticmethod
    def extract_api_key_from_request(request):
        api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
        if not api_key:
            api_key = request.headers.get('X-API-Key', '')
        return api_key


class DiskDataValidationService:
    
    @staticmethod
    def validate_size_value(value, field_name):
        if value is None:
            return None, None
        
        value_str = str(value).strip().upper()
        
        if not value_str:
            return None, None
        
        patterns = [
            (r'^(\d+(?:\.\d+)?)\s*(?:GB|GIB?)$', 1024**3),     
            (r'^(\d+(?:\.\d+)?)\s*(?:MB|MIB?)$', 1024**2),      
            (r'^(\d+(?:\.\d+)?)\s*(?:TB|TIB?)$', 1024**4),      
            (r'^(\d+(?:\.\d+)?)\s*(?:KB|KIB?)$', 1024),         
            (r'^(\d+(?:\.\d+)?)\s*$', 1),                       
            (r'^(\d+(?:\.\d+)?)\s*B$', 1),                      
        ]
        
        for pattern, multiplier in patterns:
            match = re.match(pattern, value_str)
            if match:
                try:
                    numeric_value = float(match.group(1))
                    bytes_value = int(numeric_value * multiplier)
                    return bytes_value, value_str
                except (ValueError, TypeError):
                    return None, None
        
        return None, None
    
    @staticmethod
    def validate_disk_data(data):
        errors = {}
        cleaned_data = {}
        
        max_swap = data.get('MAX_SWAP')
        if max_swap is not None:
            bytes_value, original_value = DiskDataValidationService.validate_size_value(max_swap, 'MAX_SWAP')
            if bytes_value is None and original_value is None:
                errors['MAX_SWAP'] = f"Invalid swap size format: {max_swap}. Use format like '8GB', '4096MB', '1TB'"
            else:
                cleaned_data['MAX_SWAP'] = original_value if original_value else str(max_swap)
                if bytes_value and bytes_value > 1024**5: 
                    errors['MAX_SWAP'] = f"Swap size too large: {max_swap}"
                elif bytes_value and bytes_value < 0:
                    errors['MAX_SWAP'] = "Swap size cannot be negative"
        
        max_disk = data.get('MAX_DISK')
        if max_disk is not None:
            bytes_value, original_value = DiskDataValidationService.validate_size_value(max_disk, 'MAX_DISK')
            if bytes_value is None and original_value is None:
                errors['MAX_DISK'] = f"Invalid disk size format: {max_disk}. Use format like '500GB', '1TB', '100MB'"
            else:
                cleaned_data['MAX_DISK'] = original_value if original_value else str(max_disk)
                if bytes_value and bytes_value > 1024**6: 
                    errors['MAX_DISK'] = f"Disk size too large: {max_disk}"
                elif bytes_value and bytes_value < 0:
                    errors['MAX_DISK'] = "Disk size cannot be negative"
        
        free_disk = data.get('Free_DISK')
        if free_disk is not None:
            bytes_value, original_value = DiskDataValidationService.validate_size_value(free_disk, 'Free_DISK')
            if bytes_value is None and original_value is None:
                errors['Free_DISK'] = f"Invalid free space format: {free_disk}"
            else:
                cleaned_data['Free_DISK'] = original_value if original_value else str(free_disk)
                if bytes_value and max_disk:
                    max_bytes, _ = DiskDataValidationService.validate_size_value(max_disk, 'MAX_DISK')
                    if max_bytes and bytes_value > max_bytes:
                        errors['Free_DISK'] = f"Free space ({free_disk}) cannot exceed total disk size ({max_disk})"
        
        disk_name = data.get('DISK_NAME')
        if disk_name is not None:
            disk_name_str = str(disk_name).strip()
            if len(disk_name_str) > 255:
                errors['DISK_NAME'] = "Disk name is too long (max 255 chars)"
            elif disk_name_str:
                cleaned_data['DISK_NAME'] = disk_name_str
        
        return len(errors) == 0, errors, cleaned_data


class DiskMetricsService:
    @staticmethod
    def save_or_update_disk_metrics(server, disk_data):
        is_valid, errors, cleaned_data = DiskDataValidationService.validate_disk_data(disk_data)
        
        if not is_valid:
            raise ValidationError(f"Invalid disk data: {errors}")
        
        try:
            existing_disk = Disk.objects.get(UuidServer=server.uuid)
            
            has_changes = False
            for field, value in cleaned_data.items():
                if getattr(existing_disk, field) != value:
                    has_changes = True
                    break
            
            if not has_changes:
                logger.info(f"No changes in disk metrics for server {server.uuid}")
                return existing_disk, False
            
            for field, value in cleaned_data.items():
                setattr(existing_disk, field, value)
            existing_disk.save()
            
            logger.info(f"Updated disk metrics for server {server.uuid}")
            return existing_disk, False
            
        except Disk.DoesNotExist:
            disk_instance = Disk.objects.create(
                UuidServer=server.uuid,
                **cleaned_data
            )
            logger.info(f"Created new disk metrics for server {server.uuid}")
            return disk_instance, True
    
    @staticmethod
    def get_disk_metrics_for_server(server):
        try:
            disk = Disk.objects.get(UuidServer=server.uuid)
            return {
                "disk_name": disk.DISK_NAME,
                "max_swap": disk.MAX_SWAP,
                "max_disk": disk.MAX_DISK,
                "free_disk": disk.Free_DISK,
                "server_uuid": disk.UuidServer,
                "created_at": getattr(disk, 'created_at', None),
                "updated_at": getattr(disk, 'updated_at', None)
            }
        except Disk.DoesNotExist:
            return None
    
    @staticmethod
    def get_all_disks_with_servers():
        disks = Disk.objects.all()
        result = []
        
        for disk in disks:
            result.append({
                "id": disk.id,
                "server_uuid": disk.UuidServer,
                "disk_name": disk.DISK_NAME,
                "max_swap": disk.MAX_SWAP,
                "max_disk": disk.MAX_DISK,
                "free_disk": disk.Free_DISK,
                "created_at": getattr(disk, 'created_at', None),
                "updated_at": getattr(disk, 'updated_at', None)
            })
        
        return result
    
    @staticmethod
    def get_disk_usage_percentage(server):
        metrics = DiskMetricsService.get_disk_metrics_for_server(server)
        if not metrics or not metrics['max_disk'] or not metrics['free_disk']:
            return None
        
        import re
        def parse_size(size_str):
            if not size_str:
                return 0
            match = re.search(r'(\d+(?:\.\d+)?)', str(size_str))
            if match:
                return float(match.group(1))
            return 0
        
        total = parse_size(metrics['max_disk'])
        free = parse_size(metrics['free_disk'])
        
        if total > 0:
            used_percent = ((total - free) / total) * 100
            return round(used_percent, 2)
        return None


class DiskAlertService:
    
    @staticmethod
    def check_disk_anomalies(disk_data, server):
        warnings = []
        free_disk = disk_data.get('Free_DISK')
        max_disk = disk_data.get('MAX_DISK')
        
        if free_disk and max_disk:
            import re
            def parse_size(size_str):
                if not size_str:
                    return 0
                match = re.search(r'(\d+(?:\.\d+)?)', str(size_str))
                if match:
                    return float(match.group(1))
                return 0
            
            free_val = parse_size(free_disk)
            total_val = parse_size(max_disk)
            
            if total_val > 0:
                free_percent = (free_val / total_val) * 100
                
                if free_percent < 10:
                    warnings.append({
                        "type": "low_disk_space",
                        "message": f"Critical low disk space! Only {free_percent:.1f}% free ({free_disk} of {max_disk})",
                        "severity": "critical"
                    })
                elif free_percent < 20:
                    warnings.append({
                        "type": "low_disk_space",
                        "message": f"Low disk space warning: {free_percent:.1f}% free ({free_disk} of {max_disk})",
                        "severity": "warning"
                    })
        
        max_swap = disk_data.get('MAX_SWAP')
        if max_swap:
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', str(max_swap))
            if match:
                swap_gb = float(match.group(1))
                if 'TB' in str(max_swap).upper():
                    swap_gb *= 1024
                elif 'MB' in str(max_swap).upper():
                    swap_gb /= 1024
                
                if swap_gb > 64:
                    warnings.append({
                        "type": "large_swap",
                        "message": f"Unusually large SWAP size: {max_swap} ({swap_gb:.1f} GB)",
                        "severity": "info"
                    })
        
        if warnings:
            logger.warning(f"Disk anomalies detected for server {server.uuid}: {warnings}")
        
        return warnings
    
    @staticmethod
    def check_all_servers_disk_space():
        all_alerts = []
        disks = Disk.objects.all()
        
        for disk in disks:
            try:
                server = Server.objects.get(uuid=disk.UuidServer)
                disk_data = {
                    'MAX_DISK': disk.MAX_DISK,
                    'Free_DISK': disk.Free_DISK,
                    'MAX_SWAP': disk.MAX_SWAP
                }
                alerts = DiskAlertService.check_disk_anomalies(disk_data, server)
                if alerts:
                    all_alerts.extend(alerts)
            except Server.DoesNotExist:
                continue
        
        return all_alerts


class DiskAnalyticsService:
    
    @staticmethod
    def get_disk_statistics():
        total_disks = Disk.objects.count()
        disks_with_data = Disk.objects.exclude(MAX_DISK__isnull=True).exclude(MAX_DISK='')
        
        total_size = 0
        for disk in disks_with_data:
            if disk.MAX_DISK:
                import re
                match = re.search(r'(\d+(?:\.\d+)?)', str(disk.MAX_DISK))
                if match:
                    size = float(match.group(1))
                    if 'TB' in str(disk.MAX_DISK).upper():
                        size *= 1024
                    elif 'MB' in str(disk.MAX_DISK).upper():
                        size /= 1024
                    total_size += size
        
        avg_size = total_size / disks_with_data.count() if disks_with_data.count() > 0 else 0
        
        return {
            'total_servers_with_disk': total_disks,
            'average_disk_size_gb': round(avg_size, 2),
            'total_disk_space_gb': round(total_size, 2),
            'disks_with_swap': Disk.objects.exclude(MAX_SWAP__isnull=True).exclude(MAX_SWAP='').count()
        }