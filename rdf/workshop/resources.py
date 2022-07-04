import logging
import os
import requests
import rdflib as r
logging.basicConfig(level=logging.DEBUG)


class _Nested:
    pass


class WebResource:
    webresources = _Nested()
    webresources.SDO = None

    def __init__(self, save: bool = False, file_save_path: str = None, url: str = 'https://schema.org/version/latest/schemaorg-current-https.rdf') -> None:
        self.url = url
        self.file_save_path = file_save_path
        self.request = requests.get(url)
        self.text = self.request.text
        logging.debug(
            f'request response {self.request.status_code} from {self.url}')

        if save:
            self.save_as_file()

    def save_as_file(self, format: str = "xml") -> str:
        """Save file in the same folder if no path was given. Get file name from url."""
        if not self.file_save_path:
            logging.warning(f'get file name from url: {self.url}')
            setattr(self, 'file_save_path', os.path.join(
                os.getcwd(), self.url.split('/')[-1]))

        with open(self.file_save_path, 'w') as f:
            logging.warning(f'saving under {self.file_save_path}')
            f.write(self.webresource)
            f.close()

        return self.file_save_path


if __name__ == "__main__":

    result = WebResource(save=False)
