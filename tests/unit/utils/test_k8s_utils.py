from exalsius.utils.k8s_utils import get_colony_objects, get_ddp_jobs


def test_noop():
    """
    A no-op test that always passes.
    This is a placeholder for future tests.
    """
    assert True


def test_return_types():
    """
    Test that the functions return the correct types.
    This is a basic structural test.
    """
    jobs, error = get_ddp_jobs()
    assert isinstance(jobs, list) or jobs is None
    assert isinstance(error, str) or error is None

    colonies, error = get_colony_objects()
    assert isinstance(colonies, list) or colonies is None
    assert isinstance(error, str) or error is None
