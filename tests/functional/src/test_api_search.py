import pytest
from pydantic import BaseModel

from api_test_data import api_test_data
from response import Response


@pytest.fixture(params=api_test_data)
def params_for_testing(request):
    return request.param


@pytest.mark.asyncio
async def test_search_detailed(config_test_env, make_get_request, params_for_testing):

    # method = params_for_testing.method
    # params = params_for_testing.params
    # model = params_for_testing.model
    # status_code = params_for_testing.status
    # count = params_for_testing.count
    method = params_for_testing["method"]
    params = params_for_testing["params"]
    model = params_for_testing["model"]
    status_code = params_for_testing["status"]
    count = params_for_testing["count"]

    # Выполнение запроса
    http_response = await make_get_request(method, params)
    testing_response = Response(http_response)

    # Проверка результата
    testing_response.status_code(status_code)
    testing_response.len(count)
    testing_response.validate(model)
