import pytest
from .split import TrivialDeque


@pytest.fixture
def trivial_deque():
    return TrivialDeque(nb_elements=10, first_node=1)


def test_push_pop(trivial_deque):
    trivial_deque.push_back(2)
    assert trivial_deque.size() == 2
    assert trivial_deque.get_front() == 1
    assert trivial_deque.get_back() == 2

    trivial_deque.pop_front()
    assert trivial_deque.size() == 1
    assert trivial_deque.get_front() == 2
    assert trivial_deque.get_back() == 2


def test_reset(trivial_deque):
    trivial_deque.push_back(2)
    trivial_deque.push_back(3)
    trivial_deque.reset(4)

    assert trivial_deque.size() == 1
    assert trivial_deque.get_front() == 4
    assert trivial_deque.get_back() == 4


def test_get_next_front(trivial_deque):
    trivial_deque.push_back(2)
    trivial_deque.push_back(3)

    assert trivial_deque.get_next_front() == 2


# Test
# if __name__ == "__main__":
#     # Dummy data for testing
#     algo_params = {
#         'seed': 123,
#         'useSwapStar': True,
#         'nbGranular': 20
#     }

#     params = Params(
#         x_coords=[0, 1, 2],
#         y_coords=[0, 1, 2],
#         dist_mtx=[[0, 100000, 200000], [100000, 0, 300000], [200000, 300000, 0]],
#         service_time=[0, 5, 10],
#         demands=[1000, 1000, 1200],
#         vehicleCapacity=1800,
#         durationLimit=100,
#         nbVeh=500,
#         isDurationConstraint=True,
#         verbose=True,
#         ap=algo_params
#     )


if __name__ == "__main__":
    pytest.main()
