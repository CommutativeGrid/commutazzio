from classia.filtration import CLFiltration,CLFiltrationDB
import json
import pytest


@pytest.fixture(scope='module')
def clf_db():
    db = CLFiltrationDB(':memory:')  # use an in-memory database for testing
    cc1 = CLFiltration()
    cc1.ladder_length = 3
    cc1.upper.insert([1, 2], 1)
    cc1.upper.insert([1, 2], 2)
    cc1.upper.insert([2, 3], 2)
    cc1.upper.insert([3, 1], 2)
    cc1.upper.insert([1, 2, 3], 3)
    cc1.lower.insert([1], 1)
    cc1.lower.insert([1, 3], 2)
    cc1.lower.insert([1, 2], 3)
    cc1.lower.insert([2, 3], 3)
    cc1.metadata = {'test': [[1, 2, 3]]}
    db.add_filtration(cc1)

    cc2 = CLFiltration()
    cc2.ladder_length = 4
    cc2.upper.insert([1, 2], 1)
    cc2.upper.insert([1, 2], 2)
    cc2.upper.insert([2, 3], 2)
    cc2.upper.insert([3, 1], 2)
    cc2.upper.insert([1, 2, 3], 3)
    cc2.upper.insert([2, 3, 4], 3)
    cc2.upper.insert([3, 4, 1], 3)
    cc2.upper.insert([4, 1, 2], 3)
    cc2.upper.insert([1, 2, 3, 4], 4)
    cc2.lower.insert([1], 1)
    cc2.lower.insert([1, 3], 2)
    cc2.lower.insert([1, 2], 3)
    cc2.lower.insert([2, 3], 3)
    cc2.metadata = {'test': [[1, 2, 3, 4]]}
    db.add_filtration(cc2)

    yield db  # return the database object

    # teardown code, called after the tests have run
    db.conn.close()


def test_read_filtration(clf_db):
    # create a new filtration object and add it to the database
    filtrations = clf_db.read_all()
    assert len(filtrations) == 2
    assert filtrations[0].ladder_length == 3
    assert filtrations[1].ladder_length == 4
    assert filtrations[0].metadata == {'test': [[1, 2, 3]]}
    assert filtrations[1].h_params == [1,2,3,4]
    assert filtrations[0].get_simplicial_complex(*(2,2)).simplices == [(1,), (2,), (3,), (1, 2), (1, 3), (2, 3)]