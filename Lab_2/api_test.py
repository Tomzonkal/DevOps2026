import config
import pytest
import requests
the_list = config.id_list
@pytest.mark.parametrize("id", the_list)
def test_api_models(id):
    url = 'http://localhost:5000/api/model_'+id

    # Sample input data
    input_data = {"input":[[1,2,3,4]]}
    # Send POST request with JSON data
    response = requests.post(url, json=input_data)  
    # Check if the request was successful (status code 200)
    assert(response.status_code == 200)
    result=response.json()["result"]
    assert(result[0]==2.0)
    assert(result[1]==2.0)
    assert(result[2]==2.0)


    