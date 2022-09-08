# -*- coding: utf-8 -*-
import pytest

from alchy import Manager
from copy import copy
import sqlalchemy as sa
from sqlalchemy.engine.url import make_url

from cgstats.db.api import connect


@pytest.fixture
def x_run_dir():
    return "tests/fixtures/170202_ST-E00269_0169_AHC7H2ALXX"


@pytest.fixture
def x_pooled_run_dir():
    return "tests/fixtures/161125_ST-E00269_0150_AH37GVALXX"


@pytest.fixture
def x_pooled_missing_logs_run_dir():
    return "tests/fixtures/missing/all/161125_ST-E00269_0150_AH37GVALXX"


@pytest.fixture
def x_pooled_missing_unaligned_run_dir():
    return "tests/fixtures/missing/Unaligned/161125_ST-E00269_0150_AH37GVALXX"


@pytest.fixture
def rapid_run_dir():
    return "tests/fixtures/150114_D00134_0168_AHB07NADXX"


@pytest.fixture
def mixed_rapid_run_dir():
    return "tests/fixtures/170406_D00410_0399_BHHKV5BCXY"


@pytest.fixture
def miseq_run_dir():
    return "tests/fixtures/170609_M03284_0061_000000000-B59L9"


@pytest.fixture(name="sql_manager")
def fixture_sql_manager() -> Manager:
    """Fixture with a CG store"""
    _sql_manager = connect(uri="sqlite:///")
    _sql_manager.create_all()
    yield _sql_manager
    _sql_manager.drop_all()

# @pytest.fixture(scope="function")
# def sql_manager(request):
#     config_url = request.config.getoption("--sqlalchemy-connect-url")

#     # get the databse from the URL
#     sa_url = copy(make_url(config_url))
#     database = sa_url.database
#     sa_url.database = None

#     engine = sa.create_engine(sa_url)
#     engine.execute("CREATE DATABASE IF NOT EXISTS {}".format(database))

#     manager = connect(config_url)
#     manager.create_all()

#     def fin():
#         print("Removing database")
#         manager.rollback()
#         engine.execute("DROP DATABASE {}".format(database))

#     request.addfinalizer(fin)
#     return manager


def pytest_addoption(parser):
    parser.addoption(
        "--sqlalchemy-connect-url",
        action="store",
        default=None,
        help="Name of the database to connect to",
    )
