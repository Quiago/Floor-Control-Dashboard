# test_notifications.py
import asyncio
import os
from dotenv import load_dotenv
from app.services.notification_service import notification_service

# Cargar variables del .env manualmente para la prueba
load_dotenv()

async def main():
    print("--- 🧪 PRUEBA DE NOTIFICACIONES NEXUS ---")
    
    # 1. Verificar Configuración
    print(f"Modo Mock: {notification_service.config.mock_mode}")
    print(f"Email Configurado: {notification_service.config.email_configured}")
    print(f"WhatsApp Configurado: {notification_service.config.whatsapp_configured}")
    
    # Datos de prueba (CAMBIA ESTO POR TUS DATOS REALES)
    TEST_EMAIL = "cquiala12work@gmail.com" 
    TEST_PHONE = "+971581524067" # Tu número con código de país (sin +)

    # 2. Prueba de Email
    if notification_service.config.email_configured:
        print(f"\n📧 Enviando correo de prueba a {TEST_EMAIL}...")
        result = await notification_service.send_email(
            to_email=TEST_EMAIL,
            subject="🚀 Prueba Nexus: Sistema Operativo",
            body="Si lees esto, el servicio SMTP funciona correctamente.",
            html_body="<h1>🚀 Nexus Online</h1><p>El sistema de notificaciones está activo.</p>"
        )
        print(f"Resultado Email: {'✅ Éxito' if result.success else '❌ Error'}")
        if not result.success:
            print(f"Error: {result.error}")
    else:
        print("\n⚠️ Email no configurado en .env (Saltando prueba)")

    # 3. Prueba de WhatsApp
    if notification_service.config.whatsapp_configured:
        print(f"\n💬 Enviando WhatsApp de prueba a {TEST_PHONE}...")
        result = await notification_service.send_whatsapp(
            phone_number=TEST_PHONE,
            message="🤖 Nexus: Esta es una prueba de conectividad de la API de WhatsApp.",
            #template_name="hello_world"  # Asegúrate de que este template exista en tu configuración de WhatsApp Business
        )
        print(f"Resultado WhatsApp: {'✅ Éxito' if result.success else '❌ Error'}")
        if not result.success:
            print(f"Error: {result.error}")
    else:
        print("\n⚠️ WhatsApp no configurado en .env (Saltando prueba)")

    await notification_service.close()

if __name__ == "__main__":
    asyncio.run(main())