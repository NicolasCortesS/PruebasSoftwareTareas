import logging
import os
from datetime import datetime

def setup_logger():
    """
    Configura y retorna el logger principal del sistema.
    
    Returns:
        logging.Logger: Logger configurado con handlers para archivo y consola.
    """
    # Crear directorio de logs si no existe
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar el logger principal
    logger = logging.getLogger('event_system')
    logger.setLevel(logging.INFO)
    
    # Evitar duplicar handlers si ya existen
    if not logger.handlers:
        # Handler para archivo
        file_handler = logging.FileHandler(
            os.path.join(log_dir, 'operations.log'), 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato de los logs
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Logger global
logger = setup_logger()

def log_operation(operation, details):
    """
    Registra una operación genérica en el log.
    
    Args:
        operation (str): Tipo de operación a registrar.
        details (str): Detalles específicos de la operación.
    """
    logger.info(f"{operation}: {details}")

def log_user_operation(user_id, username, operation, details=""):
    """
    Registra operaciones relacionadas con usuarios.
    
    Args:
        user_id (int): ID del usuario.
        username (str): Nombre de usuario.
        operation (str): Tipo de operación (CREATE, AUTH_SUCCESS, etc.).
        details (str, optional): Detalles adicionales de la operación.
    """
    log_operation(f"USER_{operation}", f"user_id={user_id}, username={username}, {details}")

def log_event_operation(event_id, operation, details=""):
    """
    Registra operaciones relacionadas con eventos.
    
    Args:
        event_id (int): ID del evento.
        operation (str): Tipo de operación (CREATE, UPDATE, DELETE).
        details (str, optional): Detalles adicionales de la operación.
    """
    log_operation(f"EVENT_{operation}", f"event_id={event_id}, {details}")

def log_sale_operation(event_id, user_id, qty, operation_type):
    """
    Registra operaciones de venta y devolución de entradas.
    
    Args:
        event_id (int): ID del evento.
        user_id (int): ID del usuario que realiza la operación.
        qty (int): Cantidad de entradas.
        operation_type (str): Tipo de operación (SALE o REFUND).
    """
    log_operation(f"SALE_{operation_type}", f"event_id={event_id}, user_id={user_id}, qty={qty}")
