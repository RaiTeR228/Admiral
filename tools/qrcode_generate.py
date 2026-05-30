import io
import qrcode
from dotenv import load_dotenv
import os

load_dotenv()

def generate_qr_code():
    
    API_KEY = os.getenv("API_TOKEN")
    qr = qrcode.QRCode(box_size=10, border=4, version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(API_KEY)
    f = io.StringIO()
    qr.print_ascii(out=f)
    f.seek(0)
    print(f.read())
    # print(f"\n\n Ваш Api-ключ: {API_KEY}\n\n")
    print ("QR код для подключение через мобильное приложение\n\n")