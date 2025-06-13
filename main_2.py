from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# --- Funções auxiliares puras ----------------------------------------------

def is_active(user: Dict[str, Any]) -> bool:
    """Retorna True se o usuário estiver com status 'active'."""
    return user.get('status') == 'active'

def normalize_email(email: str) -> str:
    """Normaliza um endereço de e-mail para minúsculas."""
    return email.lower()

def parse_date(date_str: str) -> Optional[datetime]:
    """Tenta converter 'YYYY-MM-DD' em datetime; retorna None se falhar."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except (TypeError, ValueError):
        return None

def is_recent_login(last_login: datetime, *, days: int = 30) -> bool:
    """Verifica se last_login está dentro dos últimos `days` dias."""
    return last_login >= (datetime.now() - timedelta(days=days))


# --- Função principal otimizada --------------------------------------------

def process_user_data(user_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Processa uma lista de usuários de forma eficiente:
      1. Filtra apenas ativos.
      2. Normaliza o e-mail.
      3. Converte a data de login.
      4. Marca login recente (últimos 30 dias).
    """
    # Um único cálculo de limite de recência
    threshold = datetime.now() - timedelta(days=30)

    processed = [
        {
            **user,
            'email': normalize_email(user['email']),
            'last_login_date': last_dt,
            'is_recent_login': last_dt >= threshold
        }
        for user in user_list
        if is_active(user)
        and (last_dt := parse_date(user.get('last_login_date', ''))) is not None
    ]
    return processed


users = [
    {"id": 1, "name": "Alice", "email": "Alice@Exemplo.COM", "status": "active", "last_login_date": "2025-05-20"},
    {"id": 2, "name": "Bob",   "email": "Bob@Exemplo.COM",   "status": "inactive", "last_login_date": "2025-06-10"},
    {"id": 3, "name": "Carol", "email": "CAROL@exemplo.com",  "status": "active", "last_login_date": "2025-04-15"},
]

processed = process_user_data(users)
for u in processed:
    print(u)