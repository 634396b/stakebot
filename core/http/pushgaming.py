from core.http.util  import async_post, async_get, async_put

def start_session(session_url, payload):
    return async_post(session_url, data=payload)


def post_action(action_url, payload, session_id=''):
    headers = {'authorization': f'Bearer {session_id}'}
    return async_post(action_url, data=payload, headers=headers)


def get_latest(get_latest_url, session_id):
    headers = {'authorization': f'Bearer {session_id}'}
    return async_get(get_latest_url, headers=headers)


def put_action(action_url, action_id, session_id):
    payload = {}
    headers = {'authorization': f'Bearer {session_id}'}
    url = f'{action_url}/{action_id}'
    return async_put(url, headers=headers, data=payload)

"""
Required to notify the server the client's states 
"""
def put_client_states(client_states_url, action_id, round_over, spin_index, session_id, game_code):
    payload = {
        'clientState': {
            'actionId': action_id,
            'roundOver': round_over,
            'spinIndex': spin_index,
            'type': game_code
        }
    }
    headers = {'authorization': f'Bearer {session_id}'}
    return async_put(client_states_url, headers=headers, data=payload)
