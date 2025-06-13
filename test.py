import logging
from datetime import datetime, timedelta
import pytest
from main_3 import process_user_data  # Ajuste para o nome do módulo onde sua função está

# Configuração de logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# Gera datas dinâmicas para testes
now = datetime.now()
STR_15_DIAS = (now - timedelta(days=15)).strftime('%Y-%m-%d')
STR_31_DIAS = (now - timedelta(days=31)).strftime('%Y-%m-%d')


@pytest.fixture(autouse=True)
def caplog_level(caplog):
    caplog.set_level(logging.WARNING)
    return caplog


def test_filtra_ativos():
    users = [
        {'id': 1, 'email': 'a@x.com', 'status': 'active', 'last_login_date': STR_15_DIAS},
        {'id': 2, 'email': 'b@x.com', 'status': 'inactive', 'last_login_date': STR_15_DIAS},
    ]
    out = process_user_data(users)
    assert {u['id'] for u in out} == {1}, "Filtro de ativos falhou"


def test_normaliza_email():
    users = [
        {'id': 1, 'email': '  USER@EXAMPLE.COM  ', 'status': 'active', 'last_login_date': STR_15_DIAS},
        {'id': 2, 'email': None, 'status': 'active', 'last_login_date': STR_15_DIAS},
        {'id': 3, 'status': 'active', 'last_login_date': STR_15_DIAS},
    ]
    out = process_user_data(users)
    assert out[0]['email'] == 'user@example.com', "Email não foi corretamente normalizado"
    assert out[1]['email'] == '', "Email None não virou ''"
    assert out[2]['email'] == '', "Email ausente não virou ''"


def test_converte_data_e_recencia():
    users = [
        {'id': 1, 'email': 'x@x.com', 'status': 'active', 'last_login_date': STR_15_DIAS},
        {'id': 2, 'email': 'y@y.com', 'status': 'active', 'last_login_date': STR_31_DIAS},
    ]
    out = {u['id']: u for u in process_user_data(users)}
    assert isinstance(out[1]['last_login_date'], datetime), "Data não foi convertida"
    assert out[1]['is_recent_login'] is True, "Login recente (15 dias) não marcado como True"
    assert out[2]['is_recent_login'] is False, "Login antigo (31 dias) não marcado como False"


def test_data_invalida_e_pula_registro(caplog):
    users = [
        {'id': 1, 'email': 'a@a.com', 'status': 'active', 'last_login_date': '2025-02-30'},
        {'id': 2, 'email': 'b@b.com', 'status': 'active', 'last_login_date': None},
        {'id': 3, 'email': 'c@c.com', 'status': 'active', 'last_login_date': STR_15_DIAS},
    ]
    out = process_user_data(users)
    assert [u['id'] for u in out] == [3], "Registros com data inválida não foram pulados"
    msgs = [r.message for r in caplog.records]
    assert any("last_login_date malformado" in str(m) for m in msgs)


def test_inativa_sem_erro(caplog):
    users = [
        {'id': 1, 'email': 'a@a.com', 'status': 'inactive', 'last_login_date': STR_15_DIAS},
    ]
    out = process_user_data(users)
    assert out == [], "Usuários inativos não deveriam ser retornados"
    assert caplog.records == [], "Não deve haver logs de usuários inativos"
