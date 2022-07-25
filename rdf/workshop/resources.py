import logging
import os
import requests
logging.basicConfig(level=logging.DEBUG)


class WebResource:
    def __init__(self, save: bool = False, file_save_path: str = None, url: str = 'https://schema.org/version/latest/schemaorg-current-https.rdf', testing: bool = True) -> None:
        self.save = save
        self.url = url
        self.file_save_path = file_save_path
        self.request = None
        self.text = None
        self.testing = testing
        self._test()

    def _test(self):
        if not self.testing:
            self.get_request()
        self.save_as_file()

    def get_request(self):
        self.request = requests.get(self.url)
        self.text = self.request.text
        logging.debug(
            f'request response {self.request.status_code} from {self.url}')

    def set_file_path(self):
        logging.warning(f'get file name from url: {self.url}')
        setattr(self, 'file_save_path', os.path.join(
            os.getcwd(), 'assets', self.url.split('/')[-1]))
        return self.file_save_path

    def save_as_file(self) -> str:
        """Save file in the same folder if no path was given. Get file name from url."""
        if not self.file_save_path:
            self.set_file_path()

        if self.save:
            with open(self.file_save_path, 'w') as f:
                logging.warning(f'saving under {self.file_save_path}')
                f.write(self.text)
                f.close()

        logging.debug(f'file path: {self.file_save_path}')
        return self.file_save_path


if __name__ == "__main__":

    result = WebResource(save=False)
