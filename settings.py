# settings.py
import os
import secrets

# Токен для установки (сгенерируйте один раз и сохраните)
# INSTALL_TOKEN = os.getenv('INSTALL_TOKEN', 'SUPER_SECRET_123')

# Можно сгенерировать безопасный токен:
if not os.getenv('INSTALL_TOKEN'):
    INSTALL_TOKEN = secrets.token_hex(32)
else:
    INSTALL_TOKEN = os.getenv('INSTALL_TOKEN')