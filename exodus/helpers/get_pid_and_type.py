import risearch


class MembershipDetails:
    def __init__(self, pid):
        self.initial_details = risearch.ResourceIndexSearch(riformat='JSON').get_members_types_and_collections(pid)
        self.results =  self.__clean()

    def __clean(self):
        all_pids = {}
        for result in self.initial_details['results']:
            pid = result['pid'].replace('info:fedora/', '')
            if pid not in all_pids and result['work_type'] != 'info:fedora/fedora-system:FedoraObject-3.0':
                all_pids[pid] = {
                    'work_type': result['work_type'],
                    'collection': [result['collection'].replace('info:fedora/', '')]
                }
            elif result['work_type'] != 'info:fedora/fedora-system:FedoraObject-3.0':
                all_pids[pid]['collection'].append(result['collection'].replace('info:fedora/', ''))
        return all_pids


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Find unique work types in collection.')
    parser.add_argument(
        "-c", "--collection", dest="collection", help="Specify collection.", required=True
    )
    args = parser.parse_args()
    unique_work_types = []
    x = MembershipDetails(args.collection).results
    for k, v in x.items():
        if v['work_type'] not in unique_work_types:
            unique_work_types.append(v['work_type'])
    print(unique_work_types)