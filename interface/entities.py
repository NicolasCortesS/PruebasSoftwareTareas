from typing import Optional
from pydantic import BaseModel

class ResponseLogin(BaseModel):
    """
    Respuesta de autenticación de usuario.
    
    Attributes:
        success (bool): Indica si la autenticación fue exitosa.
        userData (Optional[UserData]): Datos del usuario si la autenticación fue exitosa.
    """
    success: bool
    userData: Optional['UserData'] = None

class UserData(BaseModel):
    """
    Datos de un usuario del sistema.
    
    Attributes:
        id (int): Identificador único del usuario.
        username (str): Nombre de usuario.
        role (str): Rol del usuario (admin o user).
    """
    id: int
    username: str
    role: str