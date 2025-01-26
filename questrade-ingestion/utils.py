import requests
import logging
from typing import TypedDict, Optional
import yaml

logging.basicConfig(level=logging.INFO,  format='%(asctime)s - %(levelname)s - %(message)s')
TOKEN_URL = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="

TokenDict = TypedDict(
    "TokenDict",
    {
        "access_token": str,
        "api_server": str,
        "expires_in": int,
        "refresh_token": str,
        "token_type": str,
    },
)

def get_access_token_yaml(token_yaml: str) -> TokenDict:
    """Read in access token yaml.

    Parameters
    ----------
    token_yaml: str
        Path of the token yaml file

    Returns
    -------
    dict
        Dicitonary with the access token parameters
    """
    try:
        with open(token_yaml) as yaml_file:
            logging.info("Loading access token from yaml...")
            token_yaml_payload: TokenDict = yaml.load(yaml_file, Loader=yaml.FullLoader)
    except Exception:
        logging.error("Error loading access token from yaml...")
        raise
    validate_access_token(**token_yaml_payload)
    return token_yaml_payload


def validate_access_token(
    access_token: Optional[str] = None,
    api_server: Optional[str] = None,
    expires_in: Optional[int] = None,
    refresh_token: Optional[str] = None,
    token_type: Optional[str] = None,
):
    """Validate access token.

    This function validates the access token and ensures that all requiered
    attributes are provided.
    """
    logging.info("Validating access token...")
    if access_token is None:
        raise Exception("Access token was not provided.")
    if api_server is None:
        raise Exception("API server URL was not provided.")
    if expires_in is None:
        raise Exception("Expiry time was not provided.")
    if refresh_token is None:
        raise Exception("Refresh token was not provided.")
    if token_type is None:
        raise Exception("Token type was not provided.")

def test_account_payload(existing_access_code, api_server):
    headers = {"Authorization": f"Bearer {existing_access_code}"}
    account_request_url = api_server + 'v1/accounts'
    response = requests.get(account_request_url, headers=headers)
    data = response.json()
    if response.status_code == 200:
        for account in data.get("accounts", []):
            logging.info(f'found acccount {account['type']}')
        return True
    else:
        logging.error(f'Error Making a request to API server with {response.status_code}')
        return False
    
def save_token_to_yaml(access_token_payload, yaml_path: str = "access_token.yaml"):
    with open(yaml_path, "w") as yaml_file:
        logging.info("Saving access token to yaml file...")
        yaml.dump(access_token_payload, yaml_file)

def authorize_access_token(existing_access_code, next_refresh_token, api_server):
    if test_account_payload(existing_access_code, api_server):
        logging.info('The access token in .yaml is valid')
        return True
    else:
        logging.info("Refreshing access token...")
        # Unable to make a connection. We need to get a refreshed token and update the .yaml file 
        url = TOKEN_URL + str(next_refresh_token)
        data = requests.get(url)
        if data.status_code == 200:
            response = data.json()
            validate_access_token(**response)
            # write response to .yaml file
            logging.info("Writing token to yaml file")
            save_token_to_yaml(response)
        else:
            logging.error(f'token refresh returned with {data.status_code}')
            raise Exception(f'token refresh returned with {data.status_code}')

if __name__ == '__main__':
    access_token_yaml = get_access_token_yaml('access_token.yaml')
    existing_access_code, next_refresh_token, api_server = access_token_yaml['access_token'], access_token_yaml['refresh_token'], access_token_yaml['api_server']
    authorize_access_token(existing_access_code, next_refresh_token, api_server)