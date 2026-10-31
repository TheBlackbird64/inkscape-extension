from pull import Pull

class Manage(Pull):
    """Open the window listing the server files, even if the document is already linked to one of them"""

    def effect(self):
        self.browse()


if __name__ == '__main__':
    Manage().run()
