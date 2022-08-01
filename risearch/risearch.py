import requests


class ResourceIndexSearch:
    def __init__(self, language="sparql", riformat="CSV", ri_endpoint="https://porter.lib.utk.edu/fedora/risearch", auth=('admin', 'admin')):
        self.risearch_endpoint = ri_endpoint
        self.valid_languages = ("itql", "sparql")
        self.valid_formats = ("CSV", "Simple", "Sparql", "TSV")
        self.language = self.validate_language(language)
        self.format = self.validate_format(riformat)
        self.base_url = (
            f"{self.risearch_endpoint}?type=tuples"
            f"&lang={self.language}&format={self.format}"
        )

    @staticmethod
    def escape_query(query):
        return (
            query.replace("*", "%2A")
                .replace(" ", "%20")
                .replace("<", "%3C")
                .replace(":", "%3A")
                .replace(">", "%3E")
                .replace("#", "%23")
                .replace("\n", "")
                .replace("?", "%3F")
                .replace("{", "%7B")
                .replace("}", "%7D")
                .replace("/", "%2F")
        )

    def validate_language(self, language):
        if language in self.valid_languages:
            return language
        else:
            raise Exception(
                f"Supplied language is not valid: {language}. Must be one of {self.valid_languages}."
            )

    def validate_format(self, user_format):
        if user_format in self.valid_formats:
            return user_format
        else:
            raise Exception(
                f"Supplied format is not valid: {user_format}. Must be one of {self.valid_formats}."
            )

    @staticmethod
    def __clean_csv_results(split_results, uri_prefix):
        results = []
        for result in split_results:
            if result.startswith(uri_prefix):
                new_result = result.split(",")
                results.append(
                    (new_result[0].replace(uri_prefix, ""), int(new_result[1]))
                )
        return sorted(results, key=lambda x: x[1])

    def get_files(self, pid):
        if self.language != "sparql":
            raise Exception(
                f"You must use sparql as the language for this method.  You used {self.language}."
            )
        sparql_query = self.escape_query(
            f"SELECT $files FROM <#ri> WHERE {{ <info:fedora/{pid}> "
            f"<info:fedora/fedora-system:def/view#disseminates> $files . }}"
        )
        results = requests.get(f"{self.base_url}&query={sparql_query}").content.decode('utf-8').split('\n')
        return [result.split('/')[-1] for result in results if result.startswith('info')]


if __name__ == "__main__":
    print(ResourceIndexSearch().get_files('brehm:3'))
