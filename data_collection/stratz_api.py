import requests
import json
import os
from gql import Client, gql

from gql.dsl import DSLSchema, DSLQuery, dsl_gql

from gql.transport.requests import RequestsHTTPTransport

def query_stratz_api(matchids):
    STRATZ_API_KEY = os.getenv('STRATZ_API_KEY')
    if not STRATZ_API_KEY:
        raise NameError('No "STRATZ_API_KEY" found in the system environment')


    endpoint = f"https://api.stratz.com/graphql"
    headers = {"Authorization": f"Bearer {STRATZ_API_KEY}"}

    transport = RequestsHTTPTransport(
        url=endpoint,
        headers=headers,
        use_json=True,
    )

    client = Client(
        transport=transport,
        fetch_schema_from_transport=True,
    )

    query_text = (
        f"\u007b\n"
         	f"matches(ids:{matchids})\u007b\n"
                f"id\n"
        	   f"didRadiantWin\n"
               f"players\u007b\n"
              f"isRadiant\n"
              f"heroId\n"
              f"role\n"
              f"lane\n"
            f"\u007d\n"
          f"\u007d\n"
        f"\u007d\n"
    )

    #print(query_text)

    query = gql(query_text)

    result = client.execute(query)
    #print(result)
    return result
