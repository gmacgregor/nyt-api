import simplejson as json
import hashlib
import urllib2
from urllib import quote, quote_plus, urlencode

MOVIE_REVIEWS_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
ARTICLE_SEARCH_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
BEST_SELLERS_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
COMMUNITY_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
TIMES_TAGS_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
TIMES_PEOPLE_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

def fetch_data(url):
    data = urllib2.urlopen(url).read()
    return data
        
class NYT(object):
    def __init__(self, key):
        self.key = key
        self.uri = 'api.nytimes.com/svc'
        self.version = 'v1'
        self.response_format = 'json'

class TimesTags(NYT):
    """A wrapper around the NYTimes TimesTags API
        
        tags = TimesTags(TIMES_TAGS_KEY)
        filter = ['Per','Des']
        data = tags.suggest('obama', filter)
    """
    def __init__(self, key):
        super(TimesTags, self).__init__(key)
        self.baseURI = 'http://%s/timestags/suggest' % self.uri
    
    def suggest(self, query, filter=[], max=100):
        reqarg = urlencode({
            'query': query,
            'filter': ','.join(['(%s)' % f for f in filter]),
            'max': max,
            'api-key': self.key
        })
        url = ''.join([self.baseURI, '?', reqarg])
        print url
        data = fetch_data(url)
        data = json.loads(data)
        return data
        
class TimesPeople(NYT):
    """A wrapper around the NYTimes TimesPeople API
        
        tp = TimesPeople(TIMES_PEOPLE_KEY)
        uid = tp.get_user_id('email@example.com')
        data = tp.get_user_data(uid, 'activities')
    """
    def __init__(self, key):
        super(TimesPeople, self).__init__(key)
        self.baseURI = 'http://%s/timespeople/api/%s/user/' % (self.uri, self.version)
    
    def get_user_id(self, email_address):
        email = email_address.lower()
        email_hash = hashlib.md5(email).hexdigest()
        url = self.baseURI+'%s/id.%s?api-key=%s'% (email_hash, self.response_format, self.key)
        data = fetch_data(url)
        data = json.loads(data)
        return data['results']['user_id']
    
    def get_user_data(self, user_id, data_type):
        url = self.baseURI+'%s/%s.%s?api-key=%s'% (user_id, data_type, self.response_format, self.key)
        data = fetch_data(url)
        data = json.loads(data)
        return data['results']


class ArticleSearch(NYT):
    """A wrapper around the NYTimes Article Search API
        
        articles = ArticleSearch(ARTICLE_SEARCH_KEY)
        terms = 'awesomesauce'
        results = articles.search(terms, rank='oldest')
        
        See main() for more...
        
    """
    def __init__(self, key):
        super(ArticleSearch, self).__init__(key)
        self.baseURI = 'http://%s/search/%s/article' % (self.uri, self.version)
    
    def search(self, terms=None, query_facets={}, query_fields={}, response_fields=[], facets=[], **kwargs):
        q = terms.strip()
        q += ''.join([' %s:%s' % (k,val) for k,v in query_fields.items() for val in v])
        q += ''.join([' %s:[%s]' % (k,val) for k,v in query_facets.items() for val in v])
        reqarg = urlencode({'query':q,
                            'facets': ','.join(facets),
                            'fields':','.join(response_fields),
                            'api-key': self.key})
        reqarg += ''.join(['&%s=%s' % (k,v) for k,v in kwargs.items()])
        url = ''.join([self.baseURI, '?', reqarg])
        print url
        data = fetch_data(url)
        data = json.loads(data)
        return data


def main():
    nyt = ArticleSearch(ARTICLE_SEARCH_KEY)
    terms = 'banking'
    query_fields = {
        'title': ['economy'],
        'body': ['stimulus package'],
    }
    query_facets = {
        'per_facet':['OBAMA, BARACK'],
        'des_facet':['UNITED STATES POLITICS AND GOVERNMENT','UNITED STATES ECONOMY'],
    }
    facets = ['des_facet','per_facet','geo_facet']
    response_fields = ['body','byline','date','title','url','lead_paragraph','desk_facet']
    q = nyt.search(
                terms,
                query_fields=query_fields,
                query_facets=query_facets,
                facets=facets,
                response_fields=response_fields,
                rank='newest',
            )
    print q

if __name__ == "__main__":
    main()