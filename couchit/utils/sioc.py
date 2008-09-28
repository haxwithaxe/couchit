# -*- coding: utf-8 -
# Copyright 2008 by Benoît Chesneau <benoitc@e-engura.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
