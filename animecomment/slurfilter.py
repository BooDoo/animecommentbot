from wordfilter import Wordfilter
wordfilter = Wordfilter()

def blacklisted(string, *args, **kwargs):
    # sloppily try to work around potential encoding problems
    try:
        return wordfilter.blacklisted(string)
    except UnicodeDecodeError:
        return wordfilter.blacklisted(string.decode('utf8', 'ignore'))

