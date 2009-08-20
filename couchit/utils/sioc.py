# -*- coding: utf-8 -
#
# Copyright (c) 2008,2009 Benoit Chesneau <benoitc@e-engura.com> 
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

from rdflib.Graph import ConjunctiveGraph as Graph
from rdflib import Namespace, Literal, BNode, RDF, URIRef

from couchit.http import BCResponse

RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
SIOC = Namespace("http://rdfs.org/sioc/ns#")
DC = Namespace("http://purl.org/dc/elements/1.1/")

class SiocWiki(object):
    def __init__(self, uri, title=None, created=None):
        self.graph = Graph()
        self.graph.bind('sioc', SIOC)
        self.graph.bind('dc', DC)
        self.graph.bind('dcterms', DCTERMS)
        self.graph.bind('rdf', RDF)
        
        self._add_site(uri, title)
        
        
    def _add_site(self, uri, title):
        node = URIRef(uri)
        self.graph.add((node, RDF.type, SIOC['Site']))
        self.graph.add((node, DC['title'], Literal(title)))
        return node
        
    def add_page(self, content, title, uri, updated):
        node = URIRef(uri)
        self.graph.add((node, RDF.type, SIOC['Wiki']))      
        self.graph.add((node, SIOC['link'], URIRef(uri)))
        self.graph.add((node, DC['title'], Literal(title)))
        self.graph.add((node, DC['content'], Literal(content)))
        self.graph.add((node, DCTERMS['updated'], Literal(updated)))
    
    def to_str(self):
        return self.graph.serialize(format="pretty-xml")
        
def send_sioc(data):
    resp = BCResponse(data)
    resp.add_etag()
    resp.headers['content-type'] = 'application/rdf+xml'
    return resp
