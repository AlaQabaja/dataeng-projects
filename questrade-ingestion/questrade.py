import logging
from typing import Any, Dict, List, Optional, Union

import requests
import yaml
logging.basicConfig(level=logging.INFO,  format='%(asctime)s - %(levelname)s - %(message)s')

class Questrade:
    """Questrade baseclass.
    This class holds the methods to get data from different Questrade APIs
    """

    def __init__(
        self,
        access_token,
        api_server
    ):
        self.access_token = access_token
        self.api_server = api_server
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
    
    def _send_message(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:  # pylint: disable=R0913
        """Send an API request.

        Parameters
        ----------
        endpoint: str
            Endpoint (to be added to base URL)
        Returns
        -------
        dict/list:
            JSON response
        """
        request_url = self.api_server + 'v1/' +  endpoint
        logging.info(f'Making request to {request_url}')
        response = requests.get(request_url, headers= self.headers, params= params)
        data = response.json()
        return data

    def get_account_ids(self) -> Dict:
        """Get account ID.

        This method gets the accounts ID connected to the token.

        Returns
        -------
        list:
            List of account IDs and their types.
        """
        logging.info("Getting account ID...")
        response = self._send_message("accounts")
        account_ids = {}
        try:
            for account in response["accounts"]:
                account_ids[account["number"]] =  account["type"]
        except Exception:
            logging.error(response)
            raise Exception
        self.account_ids = account_ids
        logging.info(f'return the following accounts {account_ids}')
        return account_ids
    
    def get_accounts_info(self) -> List[Dict]:
        logging.info("Getting account info ....")
        response = self._send_message("accounts")
        try:
            acccounts = response["accounts"]
        except Exception:
            logging.error(response)
            raise Exception
        return acccounts

    def get_account_positions(self, account_id: int) -> List[Dict]:
        """Get account positions.

        This method will get the positions for the account ID connected to the token.

        The returned data is a list where for each position, a dictionary with the following
        data will be returned:

        .. code-block:: python

            {'averageEntryPrice': 1000,
            'closedPnl': 0,
            'closedQuantity': 0,
            'currentMarketValue': 3120,
            'currentPrice': 1040,
            'isRealTime': False,
            'isUnderReorg': False,
            'openPnl': 120,
            'openQuantity': 3,
            'symbol': 'XYZ',
            'symbolId': 1234567,
            'totalCost': 3000}


        Parameters
        ----------
        account_id: int
            Account ID for which the positions will be returned.

        Returns
        -------
        list:
            List of dictionaries, where each list entry is a dictionary with basic position
            information.

        """
        logging.info("Getting account positions...")
        response = self._send_message("accounts/" + str(account_id) + "/positions")
        try:
            positions = response["positions"]
        except Exception:
            logging.error(response)
            raise Exception
        return positions

    def get_account_balances(self, account_id: int) -> Dict:
        """Get account balances.

        This method will get the account balance for a given account ID.

        Parameters
        ----------
        account_id: int
            Accound ID for which the activities will be returned.

        Returns
        -------
        dict:
            Dictionary holding balance information
        """
        logging.info("Getting account balance...")
        response = self._send_message("accounts/" + str(account_id) + "/balances")
        try:
            return response
        except Exception:
            logging.error(response)            
            raise Exception

    def get_account_activities(self, account_id: int, start_date: str, end_date: str) -> List[Dict]:
        """Get account activities.

        This method will get the account activities for a given account ID in a given time
        interval.

        This method will in general return a list of dictionaries, where each dictionary represents
        one trade/account activity. Each dictionary is of the form

        .. code-block:: python

            {'action': 'Buy',
            'commission': -5.01,
            'currency': 'CAD',
            'description': 'description text',
            'grossAmount': -1000,
            'netAmount': -1005.01,
            'price': 10,
            'quantity': 100,
            'settlementDate': '2018-08-09T00:00:00.000000-04:00',
            'symbol': 'XYZ.TO',
            'symbolId': 1234567,
            'tradeDate': '2018-08-07T00:00:00.000000-04:00',
            'transactionDate': '2018-08-09T00:00:00.000000-04:00',
            'type': 'Trades'}

        Parameters
        ----------
        account_id: int
            Accound ID for which the activities will be returned.
        start_date: str
            Start date of time period, format YYYY-MM-DD
        end_date: str
            End date of time period, format YYYY-MM-DD

        Returns
        -------
        list:
            List of dictionaries, where each list entry is a dictionary with basic order & dividend
            information.

        """
        payload = {
            "startTime": str(start_date) + "T00:00:00-05:00",
            "endTime": str(end_date) + "T00:00:00-05:00",
        }

        logging.info("Getting account activities...")
        response = self._send_message("accounts/" + str(account_id) + "/activities", params=payload)

        try:
            activities = response["activities"]
        except Exception:
            print(response)
            raise Exception

        return activities

    def get_account_executions(self, account_id: int, start_date: str, end_date: str) -> List[Dict]:
        """Get account executions.

        This method will get the account executionss for a given account ID in a given time
        interval.

        This method will in general return a list of dictionaries, where each dictionary represents
        one account execution. Each dictionary is of the form

        .. code-block:: python


            {"symbol": "AAPL",
            "symbolId": 8049,
            "quantity":   10,
            "side":  "Buy",
            "price": 536.87,
            "id": 53817310,
            "orderId": 177106005,
            "orderChainId": 17710600,
            "exchangeExecId": "XS1771060050147",
            "timestam":  2014-03-31T13:38:29.000000-04:00,
            "notes":  "",
            "venue":  "LAMP",
            "totalCost":   5368.7,
            "orderPlacementCommission": 0,
            "commission":    4.95,
            "executionFee": 0,
            "secFee": 0,
            "canadianExecutionFee": 0,
            "parentId": 0,
           }

        Parameters
        ----------
        account_id: int
            Accound ID for which the executionss will be returned.
        start_date: str
            Start date of time period, format YYYY-MM-DD
        end_date: str
            End date of time period, format YYYY-MM-DD

        Returns
        -------
        list:
            List of dictionaries, where each list entry is a dictionary with execution
            information.

        """
        payload = {
            "startTime": str(start_date) + "T00:00:00-05:00",
            "endTime": str(end_date) + "T00:00:00-05:00",
        }

        logging.info("Getting account executions...")
        response = self._send_message(
            "accounts/" + str(account_id) + "/executions", params=payload
        )

        try:
            executions = response["executions"]
        except Exception:
            logging.error(response)
            raise Exception

        return executions

    def ticker_information(self, tickers: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
        """Get ticker information.

        This function gets information such as a quote for a single ticker or a list of tickers.

        Parameters
        ----------
        tickers: str or [str]
            List of tickers or a single ticker

        Returns
        -------
        dict or [dict]
            Dictionary with ticker information or list of dictionaries with ticker information
        """
        if isinstance(tickers, str):
            tickers = [tickers]

        payload = {"names": ",".join(tickers)}

        logging.info("Getting ticker data...")
        response = self._send_message("get", "symbols", params=payload)
        try:
            symbols = response["symbols"]
        except Exception:
            logging.error(response)
            raise Exception

        if len(tickers) == 1:
            symbols = symbols[0]

        return symbols

    @staticmethod
    def _valid_intervals():
        return set(["OneDay", "OneWeek", "OneMonth", "OneYear"])