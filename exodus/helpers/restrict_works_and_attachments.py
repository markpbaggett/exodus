from lxml import etree


class PolicyReader:
    def __init__(self, policy_path):
        self.policy = policy_path
        self.namespaces = {'xacml': "urn:oasis:names:tc:xacml:1.0:policy"}
        self.root = etree.parse(policy_path)
        self.root_as_str = etree.tostring(self.root)
        self.restricted_files = self.__get_restricted_files()
        self.work_restricted = self.__is_work_restricted()

    def __is_work_restricted(self):
        matches = self.root.xpath(
            '//xacml:Rule[@RuleId="deny-access-functions"]',
            namespaces=self.namespaces
        )
        if len(matches) > 0:
            return True
        else:
            return False

    def __get_restricted_files(self):
        matches = self.root.xpath(
            '//xacml:Rule[@RuleId="deny-dsid-mime"]/xacml:Target/xacml:Resources/xacml:Resource/xacml:ResourceMatch/xacml:AttributeValue',
            namespaces=self.namespaces
        )
        if len(matches) > 0:
            return [match.text for match in matches]
        else:
            return []


if __name__ == "__main__":
    import os
    restricted_works = []
    restritced_files = []
    for root, dirs, files in os.walk('collections/rfta_audio/policies'):
        for file in files:
            if file.endswith('.xml'):
                x = PolicyReader(os.path.join(root, file))
                if x.work_restricted:
                    restricted_works.append(file.replace('.xml', ''))
                for restricted_file in x.restricted_files:
                    restritced_files.append(f'{file}_{restricted_file}')
    print(restricted_works)
    print(restritced_files)



