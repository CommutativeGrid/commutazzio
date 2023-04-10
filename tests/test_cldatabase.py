from commutazzio.filtration import CLFiltration,CLFiltrationDB
import json
import pytest

# create a fixture that creates a database with two filtrations
@pytest.fixture(scope='module')
def clf_db():
    # create a new in-memory database
    db = CLFiltrationDB(':memory:') 
    # create a new filtration object
    cc1 = CLFiltration()
    cc1.ladder_length = 3
    # add simplices to the upper complex
    cc1.upper.insert([1, 2], 1)
    cc1.upper.insert([1, 2], 2)
    cc1.upper.insert([2, 3], 2)
    cc1.upper.insert([3, 1], 2)
    cc1.upper.insert([1, 2, 3], 3)
    # add simplices to the lower complex
    cc1.lower.insert([1], 1)
    cc1.lower.insert([1, 3], 2)
    cc1.lower.insert([1, 2], 3)
    cc1.lower.insert([2, 3], 3)
    cc1.metadata = {'test': [[1, 2, 3]]}
    # add the filtration to the database
    db.add_filtration(cc1)

    # create a second filtration object
    cc2 = CLFiltration()
    cc2.ladder_length = 4
    # add simplices to the upper complex
    cc2.upper.insert([1, 2], 1)
    cc2.upper.insert([1, 2], 2)
    cc2.upper.insert([2, 3], 2)
    cc2.upper.insert([3, 1], 2)
    cc2.upper.insert([1, 2, 3], 3)
    cc2.upper.insert([2, 3, 4], 3)
    cc2.upper.insert([3, 4, 1], 3)
    cc2.upper.insert([4, 1, 2], 3)
    cc2.upper.insert([1, 2, 3, 4], 4)
    # add simplices to the lower complex
    cc2.lower.insert([1], 1)
    cc2.lower.insert([1, 3], 2)
    cc2.lower.insert([1, 2], 3)
    cc2.lower.insert([2, 3], 3)
    cc2.metadata = {'test': [[1, 2, 3, 4]]}
    # add the filtration to the database
    db.add_filtration(cc2)

    # yield the database object
    yield db  

    # teardown code, called after the tests have run
    db.conn.close()

# create a test that checks that the filtrations have been added correctly
def test_read_filtration(clf_db):
    # read all the filtrations from the database
    filtrations = clf_db.read_all()
    # check that there are two filtrations
    assert len(filtrations) == 2
    # check that the ladder length of the first filtration is 3
    assert filtrations[0].ladder_length == 3
    # check that the ladder length of the second filtration is 4
    assert filtrations[1].ladder_length == 4
    # check that the metadata of the first filtration is correct
    assert filtrations[0].metadata == {'test': [[1, 2, 3]]}
    # check that the h-parameters of the
