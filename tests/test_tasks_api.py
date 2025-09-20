def test_tasks_list_response_401(anonymous_client):
    response = anonymous_client.get('todos/tasks/')
    assert response.status_code == 401

def test_tasks_list_response_200(auth_client):
    response = auth_client.get("todos/tasks")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_tasks_detail_response_200(auth_client, random_task):
    task_object = random_task
    response = auth_client.get(f"todos/tasks/{task_object.id}")
    assert response.status_code == 200

def test_tasks_detail_response_401(auth_client):
    response = auth_client.get(f"todos/tasks/1000")
    assert response.status_code == 404