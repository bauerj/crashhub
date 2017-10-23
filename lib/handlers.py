class CrashReportHandler(object):
    def __init__(self, db):
        self.db = db

    def on_post(self, req, resp):
        crash = req.media
        print(crash)