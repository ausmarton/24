#!/usr/bin/env python

from bottle import abort, get, run, template
from py2neo.neo4j import GraphDatabaseService, CypherQuery


INDEX = """\
<html>
<body>
<h1>24 Wiki</h1>
<ul>
    <li><a href="/char/">Characters</a></li>
    <li><a href="/killers/">Killers</a></li>
</ul>
</body>
</html>
"""

CHAR_LIST = """\
<html>
<body>
<h1>Characters</h1>
<ul>
%for char in chars:
    <li><a href="/char/{{char.name}}">{{char.name}}</a></li>
%end
</ul>
</body>
</html>
"""

CHAR = """\
<html>
<body>
<h1>{{char["name"]}}</h1>
<dl>
    <dt>Nationality:</dt>
    <dd>{{char["nationality"]}}</dd>
    <dt>Played by:</dt>
    <dd>{{actor["name"]}}</dd>
    <dt>Appearances:</dt>
    <dd>
        <ul>
        %for appearance in appearances:
            <li>{{appearance.end_node["name"]}} ({{appearance["episodes"]}} episodes)</li>
        %end
        </ul>
    </dd>
    <dt>Killed:</dt>
    <dd>
        <ul>
        %for victim in victims:
            <li><a href="/char/{{victim.end_node['name']}}">{{victim.end_node['name']}}</a></li>
        %end
        </ul>
    </dd>
</dl>
<p><a href="/char/">Return to character list</a></p>
</body>
</html>
"""

# Set up a link to the local graph database.
graph = GraphDatabaseService()

@get('/')
def index():
    """ Simply return the index page.
    """
    return template(INDEX)

@get('/char/')
def char_list():
    """ Fetch a list of all known characters, ordered by name and render
    them within the CHAR_LIST template.
    """
    query = "MATCH (c:Character) RETURN c.name AS name ORDER by c.name"
    return template(CHAR_LIST, chars=CypherQuery(graph, query).execute())

@get('/char/<name>')
def char(name):
    """ Display details of a particular character.
    """
    # Look for a node with a "Character" label and a "name" property
    # matching the name passed in.
    found = graph.find("Character", "name", name)
    try:
        # Pick up the first node found.
        char = next(found)
    except StopIteration:
        # If no nodes are found, throw a 404.
        abort(404, "Character not found")
    else:
        # Otherwise pick up some more data and render a template.
        actor = next(char.match_incoming("STARRED_AS")).start_node
        appearances = char.match_outgoing("APPEARED_IN")
        victims = char.match_outgoing("KILLED")
        
        return template(CHAR, char=char, actor=actor, appearances=appearances, victims=victims)

if __name__ == "__main__":
    run(host="localhost", port=8080)

