""" File for testing meta functionality such as PyLint for GitHub actions workflows  """

import pytest

@pytest.mark.pytest
def test_pytest():
    """ This output doesn't matter, it's just a method
    to check if the pylinter scores the code 6.5 or above.
    """

    assert True

