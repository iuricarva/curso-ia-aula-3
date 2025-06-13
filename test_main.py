import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# --- Configuração de logging ------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# --- Funções auxiliares puras ----------------------------------------------

def is_active(user: Dict[str, Any]) -> bool:
    return user.get('status') == 'active'


def normalize_email(email: Any) -> str:
    if not isinstance(email, str):
        return ''
    return email.strip().lower()


def parse_date(date_str: Any) -> Optional[datetime]:
    if not isinstance(date_str, str):
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None


# --- Função principal -------------------------------------------------------

def process_user_data(user_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    processed: List[Dict[str, Any]] = []
    threshold = datetime.now() - timedelta(days=30)

    for user in user_list:
        if not is_active(user):
            continue

        raw_email = user.get('email')
        email = normalize_email(raw_email)
        if email == '' and raw_email not in ('', None):
            logger.warning(
                "User %r: email malformado (%r), usando '' como default.",
                user.get('id'),
                raw_email
            )

        raw_date = user.get('last_login_date')
        last_dt = parse_date(raw_date)
        if last_dt is None:
            logger.warning(
                "User %r: last_login_date malformado ou ausente (%r); registro ignorado.",
                user.get('id'),
                raw_date
            )
            continue

        processed.append({
            **user,
            'email': email,
            'last_login_date': last_dt,
            'is_recent_login': last_dt >= threshold
        })

    return processed


# --- Testes inline ---------------------------------------------------------

if __name__ == "__main__":
    # Gera datas dinâmicas para testes
    now = datetime.now()
    STR_15_DIAS = (now - timedelta(days=15)).strftime('%Y-%m-%d')
    STR_31_DIAS = (now - timedelta(days=31)).strftime('%Y-%m-%d')

    # 1) Testa filtragem de ativos
    users1 = [
        {'id': 1, 'email': 'a@x.com', 'status': 'active',   'last_login_date': STR_15_DIAS},
        {'id': 2, 'email': 'b@x.com', 'status': 'inactive', 'last_login_date': STR_15_DIAS},
    ]
    out1 = process_user_data(users1)
    assert {u['id'] for u in out1} == {1}, "Filtro de ativos falhou"

    # 2) Testa normalização de email e default para valores inválidos
    users2 = [
        {'id': 1, 'email': '  USER@EXAMPLE.COM  ', 'status': 'active', 'last_login_date': STR_15_DIAS},
        {'id': 2, 'email': None,                   'status': 'active', 'last_login_date': STR_15_DIAS},
        {'id': 3,                                   'status': 'active', 'last_login_date': STR_15_DIAS},
    ]
    out2 = process_user_data(users2)
    assert out2[0]['email'] == 'user@example.com', "Email não foi corretamente normalizado"
    assert out2[1]['email'] == '', "Email None não virou ''"
    assert out2[2]['email'] == '', "Email ausente não virou ''"

    # 3) Testa conversão de data e is_recent_login
    users3 = [
        {'id': 1, 'email': 'x@x.com', 'status': 'active', 'last_login_date': STR_15_DIAS},
        {'id': 2, 'email': 'y@y.com', 'status': 'active', 'last_login_date': STR_31_DIAS},
    ]
    out3 = {u['id']: u for u in process_user_data(users3)}
    assert isinstance(out3[1]['last_login_date'], datetime), "Data não foi convertida"
    assert out3[1]['is_recent_login'] is True, "Login recente (15 dias) não marcado como True"
    assert out3[2]['is_recent_login'] is False, "Login antigo (31 dias) não marcado como False"

    # 4) Testa pulo de registros com data inválida
    users4 = [
        {'id': 1, 'email': 'a@a.com', 'status': 'active', 'last_login_date': '2025-02-30'},
        {'id': 2, 'email': 'b@b.com', 'status': 'active', 'last_login_date': None},
        {'id': 3, 'email': 'c@c.com', 'status': 'active', 'last_login_date': STR_15_DIAS},
    ]
    out4 = process_user_data(users4)
    assert [u['id'] for u in out4] == [3], "Registros com data inválida não foram pulados"

    # 5) Testa que inativos são ignorados sem warnings adicionais
    users5 = [
        {'id': 1, 'email': 'a@a.com', 'status': 'inactive', 'last_login_date': STR_15_DIAS},
    ]
    # Limpa o buffer de logs
    logger.handlers[0].flush()
    out5 = process_user_data(users5)
    assert out5 == [], "Usuários inativos não deveriam ser retornados"

    print("Todos os testes inline passaram com sucesso!")
