from datetime import datetime, timedelta
from typing import List, Dict

def process_user_data(user_list: List[Dict]) -> List[Dict]:
    """
    Processa uma lista de dicionários de usuários.

    Passos:
    - Filtra apenas usuários com status 'active'.
    - Normaliza o campo 'email' para minúsculas.
    - Converte 'last_login_date' (string 'YYYY-MM-DD') em objeto datetime.
    - Adiciona campo 'is_recent_login': True se o último login foi nos últimos 30 dias, caso contrário False.

    Retorna:
        Lista de dicionários de usuários processados.
    """
    processed_users = []
    today = datetime.now()
    threshold = today - timedelta(days=30)

    for user in user_list:
        if user.get('status') != 'active':
            continue

        # Normaliza email
        email = user.get('email', '')
        normalized_email = email.lower()

        # Converte last_login_date
        last_login_str = user.get('last_login_date')
        try:
            last_login_dt = datetime.strptime(last_login_str, '%Y-%m-%d')
        except (TypeError, ValueError):
            # Se a data não for válida, pula este usuário
            continue

        # Verifica se é login recente
        is_recent = last_login_dt >= threshold

        # Cria o dicionário processado (copia pra não alterar o original)
        processed_user = {
            **user,
            'email': normalized_email,
            'last_login_date': last_login_dt,
            'is_recent_login': is_recent
        }

        processed_users.append(processed_user)

    return processed_users


users = [
    {"id": 1, "name": "Alice", "email": "Alice@Exemplo.COM", "status": "active", "last_login_date": "2025-05-20"},
    {"id": 2, "name": "Bob",   "email": "Bob@Exemplo.COM",   "status": "inactive", "last_login_date": "2025-06-10"},
    {"id": 3, "name": "Carol", "email": "CAROL@exemplo.com",  "status": "active", "last_login_date": "2025-04-15"},
]

processed = process_user_data(users)
for u in processed:
    print(u)