import requests
import json
import sys

scope_query = """
    query($handle: String!) {
      team(handle: $handle) {
        structured_scopes() {
          edges {
            node {
              asset_identifier,
              asset_type,
              eligible_for_bounty,
              max_severity,
            }
          }
        }
      }
    }
"""

def hackerone_to_list():
    targets = {
        'domains': [],
        'wildstar': [],
        'bounty_domains': [],
        'code': [],

    }

    program = sys.argv[1]
    with requests.Session() as session:
        r = session.get("https://hackerone.com/{program}".format(
            program=program),
            headers={'Accept': 'application/json'})
        if r.status_code != 200:
            print('unable to retreive %s', program)
            return []

        resp = json.loads(r.text)
        query = json.dumps({'query': scope_query,
                            'variables': {'handle': resp['handle']}})
        r = session.post("https://hackerone.com/graphql",
                         data=query,
                         headers={'content-type': 'application/json'})
        scope_resp = json.loads(r.text)
        print(resp['handle'])

        for e in scope_resp['data']['team']['structured_scopes']['edges']:
            if e['node']['asset_type'] == 'URL' and e['node']['max_severity']  != 'none':
                domain = e['node']['asset_identifier'].strip()
                if domain[0] == '*':
                    targets['wildstar'].append(domain[2:])
                if e['node']['eligible_for_bounty']:
                    targets['bounty_domains'].append(domain)
                targets['domains'].append(domain)
            elif e['node']['asset_type'] == 'SOURCE_CODE' and e['node']['max_severity']  != 'none':
                domain = e['node']['asset_identifier'].strip()
                targets['code'].append(domain)
        return targets


if __name__ == "__main__":
    targets = hackerone_to_list()
    with open('domains.txt', 'w') as f:
        f.write('\n'.join(targets['domains']))
    with open('wildstar.txt', 'w') as f:
        f.write('\n'.join(targets['wildstar']))
    with open('with_bounties.txt', 'w') as f:
        f.write('\n'.join(targets['bounty_domains']))
    with open('code.txt', 'w') as f:
        f.write('\n'.join(targets['code']))
