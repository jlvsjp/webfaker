

class EXT(object):

    @classmethod
    def do(cls, url):
        print "This is EXT do!"
        return cls.handle

    @classmethod
    def handle(cls, header, body):
        print "This is EXT handle!"
        return (header, body)
