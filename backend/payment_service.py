import requests
import os
from datetime import datetime
import uuid

# Modo de simulación local (sin llamadas a Wompi)
SIMULATION_MODE = True

# Claves de API de Wompi - Se usarán solo cuando SIMULATION_MODE sea False
WOMPI_PUBLIC_KEY = "pub_test_O0CfpGEg1hMlgpWy2RzJLnMIBkVOwqnL"
WOMPI_PRIVATE_KEY = "prv_test_i8MiyYHbcIQDvKS1Dle8h5dEOw1dbwKE"
WOMPI_API_URL = "https://sandbox.wompi.co/v1"  # URL de sandbox

# Almacenamiento local de simulación para pagos
simulated_payments = {}

def create_payment_link(user_id, plan_id, plan_name, amount):
    """
    Crea un enlace de pago en Wompi o simula uno en modo local
    """
    print(f"Creating payment link for user {user_id}, plan {plan_name}, amount {amount}")
    
    # Calcular el valor en centavos (Wompi trabaja con la moneda en centavos)
    # El monto viene en pesos colombianos (por ejemplo 19900 para $19.900)
    amount_in_cents = int(float(amount)) * 100
    
    # Crear una referencia única para el pago
    reference = f"plan_{plan_id}_{user_id}_{int(datetime.now().timestamp())}"
    
    if SIMULATION_MODE:
        print("Running in simulation mode - creating local payment link")
        
        # Generar un ID único para el pago simulado
        payment_id = str(uuid.uuid4())
        
        # Crear URL de pago simulada
        payment_url = f"http://localhost:3000/simulated-payment?reference={reference}&amount={amount}&plan={plan_name}"
        
        # Guardar información del pago simulado
        simulated_payments[reference] = {
            "id": payment_id,
            "status": "PENDING",
            "amount": amount,
            "amount_in_cents": amount_in_cents,
            "plan_id": plan_id,
            "plan_name": plan_name,
            "user_id": user_id,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "payment_url": payment_url,
            "reference": reference,
            "simulated": True
        }
    
    # Datos para crear el enlace de pago en Wompi
    payload = {
        "name": f"Suscripción Plan {plan_name} - Skills Hub",
        "description": f"Suscripción mensual al plan {plan_name}",
        "single_use": True,
        "currency": "COP",
        "amount_in_cents": amount_in_cents,
        "redirect_url": "http://localhost:3000/payment-success",
        "reference": reference
    }
    
    headers = {
        "Authorization": f"Bearer {WOMPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to Wompi: {payload}")
    
    try:
        response = requests.post(
            f"{WOMPI_API_URL}/payment_links",
            json=payload,
            headers=headers
        )
        
        print(f"Wompi response status: {response.status_code}")
        print(f"Wompi response: {response.text}")
        
        if response.status_code in [200, 201]:
            return {
                "success": True,
                "payment_url": response.json()["data"]["url"],
                "reference": reference
            }
        else:
            return {
                "success": False,
                "error": f"Error al crear el enlace de pago: {response.text}"
            }
    except Exception as e:
        print(f"Exception in create_payment_link: {str(e)}")
        return {
            "success": False,
            "error": f"Error de conexión: {str(e)}"
        }

def verify_payment(reference):
    """
    Verifica el estado de un pago por su referencia
    """
    print(f"Verifying payment with reference: {reference}")
    
    if SIMULATION_MODE:
        print("Running in simulation mode - checking local payment status")
        
        # Verificar si existe el pago simulado
        if reference in simulated_payments:
            payment = simulated_payments[reference]
            
            # En modo simulación, asumimos que todos los pagos son exitosos después de verificar
            if payment["status"] == "PENDING":
                payment["status"] = "APPROVED"
                simulated_payments[reference] = payment
            
            return {
                "success": True,
                "status": payment["status"],
                "payment_method_type": "SIMULATED",
                "amount": payment["amount"],
                "reference": reference
            }
        else:
            # Para pruebas, simular un pago exitoso si la referencia tiene un formato específico
            if reference.startswith("plan_"):
                print("Simulating successful payment in simulation mode")
                return {
                    "success": True,
                    "status": "APPROVED",
                    "payment_method_type": "SIMULATED",
                    "amount": 19900,  # Valor por defecto
                    "reference": reference
                }
            
            return {
                "success": False,
                "error": "No se encontró el pago simulado"
            }
    
    headers = {
        "Authorization": f"Bearer {WOMPI_PRIVATE_KEY}"
    }
    
    try:
        response = requests.get(
            f"{WOMPI_API_URL}/transactions?reference={reference}",
            headers=headers
        )
        
        print(f"Wompi verify response status: {response.status_code}")
        print(f"Wompi verify response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()["data"]
            if data and len(data) > 0:
                transaction = data[0]
                return {
                    "success": True,
                    "status": transaction["status"],
                    "payment_method_type": transaction["payment_method_type"],
                    "amount": transaction["amount_in_cents"] / 100,
                    "reference": transaction["reference"]
                }
            
            return {
                "success": False,
                "error": "No se encontró el pago"
            }
        
        return {
            "success": False,
            "error": f"Error al consultar el pago: {response.text}"
        }
    except Exception as e:
        print(f"Exception in verify_payment: {str(e)}")
        return {
            "success": False,
            "error": f"Error de conexión: {str(e)}"
        }

# Función para aprobar manualmente un pago simulado (para pruebas)
def approve_simulated_payment(reference):
    """
    Aprueba manualmente un pago simulado por su referencia
    """
    if not SIMULATION_MODE:
        return {"success": False, "error": "Esta función solo está disponible en modo simulación"}
    
    if reference in simulated_payments:
        payment = simulated_payments[reference]
        payment["status"] = "APPROVED"
        simulated_payments[reference] = payment
        return {"success": True, "payment": payment}
    
    return {"success": False, "error": "No se encontró el pago simulado"}

# Función para pruebas
if __name__ == "__main__":
    # Probar la creación de un enlace de pago
    test_result = create_payment_link(
        user_id="test_user_123",
        plan_id="tier_pro",
        plan_name="Pro",
        amount=19900
    )
    
    print("\nTest result:", test_result)
    
    # Si se creó exitosamente, verificar el pago (simulando)
    if test_result["success"]:
        verify_result = verify_payment(test_result["reference"])
        print("\nVerify result:", verify_result) 