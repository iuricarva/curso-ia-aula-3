import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Configura o logger (pode ser ajustado para arquivo, nível, formato etc.)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()  # ou FileHandler('process_users.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# --- Funções auxiliares puras ----------------------------------------------

def is_active(user: Dict[str, Any]) -> bool:
    """Retorna True se o usuário estiver com status 'active'."""
    return user.get('status') == 'active'


def normalize_email(email: Any) -> str:
    """Normaliza um endereço de e-mail para minúsculas; default ''."""
    if not isinstance(email, str):
        return ''
    return email.strip().lower()


def parse_date(date_str: Any) -> Optional[datetime]:
    """
    Tenta converter 'YYYY-MM-DD' em datetime;
    retorna None se falhar.
    """
    if not isinstance(date_str, str):
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None


# --- Função principal com validação ----------------------------------------

def process_user_data(user_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Processa uma lista de usuários:
      1. Filtra apenas ativos.
      2. Normaliza o e-mail (default '').
      3. Converte a data de login (YYYY-MM-DD) em datetime.
      4. Marca login recente (últimos 30 dias).
      5. Se e-mail inválido: normaliza para '' + log warning.
      6. Se data inválida: pula o registro + log warning.
    """
    processed: List[Dict[str, Any]] = []
    threshold = datetime.now() - timedelta(days=30)

    for user in user_list:
        if not is_active(user):
            continue

        # 1) Normaliza e-mail
        raw_email = user.get('email')
        email = normalize_email(raw_email)
        if email == '' and raw_email not in ('', None):
            logger.warning(
                "User %r: email malformado (%r), usando '' como default.",
                user.get('id'),
                raw_email
            )

        # 2) Converte last_login_date
        raw_date = user.get('last_login_date')
        last_dt = parse_date(raw_date)
        if last_dt is None:
            logger.warning(
                "User %r: last_login_date malformado ou ausente (%r); registro ignorado.",
                user.get('id'),
                raw_date
            )
            continue

        # 3) Verifica recência e adiciona ao resultado
        processed.append({
            **user,
            'email': email,
            'last_login_date': last_dt,
            'is_recent_login': last_dt >= threshold
        })

    return processed

users = [
    {"id": 1, "name": "Alice", "email": "Alice@Exemplo.COM", "status": "active", "last_login_date": "2025-05-20"},
    {"id": 2, "name": "Bob",   "email": "Bob@Exemplo.COM",   "status": "inactive", "last_login_date": "2025-06-10"},
    {"id": 3, "name": "Carol", "email": "CAROL@exemplo.com",  "status": "active", "last_login_date": "2025-04-15"},
]

processed = process_user_data(users)
for u in processed:
    print(u)