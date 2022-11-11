from operator import itemgetter
import networkx as nx
from mediawiki import MediaWiki
import matplotlib.pyplot as plt
wikipedia = MediaWiki()


Topic = "Bubble Tea".title()
degree=2
#ignore non-wiki article pages
IgnoreLinksWith = ("International Standard Serial Number",
    "International Standard Book Number",
    "National Diet Library",
    "International Standard Name Identifier",
    "International Standard Book Number (Identifier)",
    "Pubmed Identifier", 
    "Pubmed Central",
    "Digital Object Identifier", 
    "Arxiv",
    "Proc Natl Acad Sci Usa", 
    "Bibcode",
    "Library Of Congress Control Number", 
    "Jstor",
    "Doi (Identifier)",
    "Isbn (Identifier)",
    "Pmid (Identifier)",
    "Arxiv (Identifier)",
    "Bibcode (Identifier)",
    "Issn (Identifier)",
    "hdl (identifier)")
ToDoList = [(0, Topic)] # Initialize the list of links
ToDoSet = set(Topic) # Make a set of the article title
FinishedSet = set() # Set of parsed article titles
g = nx.DiGraph()
layer, article = ToDoList[0]


while layer < degree:
# Remove the current page from ToDoList, and add it to FinishedSet 
# it will skip over the page if it sees it again
  
    del ToDoList[0]
    FinishedSet.add(article)
  
  # test intial should be Topic page
    print(layer, article) 
  
  # if page no loady
    try:
        wiki = wikipedia.page(article)
    except:
        layer, article = ToDoList[0]
        print(article,"did not work")
        continue
  
    for link in wiki.links:
        link = link.title()
        
        #added last part to catch other identifier pages
        if link not in IgnoreLinksWith and not link.startswith("List Of") and "(Identifier)" not in link:
            if link not in ToDoSet and link not in FinishedSet:
                ToDoList.append((layer + 1, link))
                ToDoSet.add(link)
            g.add_edge(article, link)
    layer, article = ToDoList[0]
    
# remove self loops
g.remove_edges_from(nx.selfloop_edges(g))

# identify duplicates like "apple" and "apples"
duplicates = [(node, node + "s")
              for node in g if node + "s" in g
             ]

for dup in duplicates:
  # *dup is a technique named "unpacking"
  g = nx.contracted_nodes(g, *dup, self_loops=False)

print(duplicates)

#more filterings: page "x-y" is the same as "x y" 
duplicates = [(x, y) for x, y in 
              [(node, node.replace("-", " ")) for node in g]
                if x != y and y in g]
print(duplicates)

for dup in duplicates:
    g = nx.contracted_nodes(g, *dup, self_loops=False)

    # nx.contracted creates a new node/edge attribute called contraction
    # the value of the attribute is a dictionary, but GraphML
    # does not support dictionary attributes
nx.set_node_attributes(g, 0,"contraction")
nx.set_edge_attributes(g, 0,"contraction")

# filter nodes by degree
core = [node for node, deg in dict(g.degree()).items() if deg >= degree]

# select a subgraph with filtered nodes
gsub = nx.subgraph(g, core)

print("{} nodes, {} edges".format(len(gsub), nx.number_of_edges(gsub)))

# convert graph to gelphi format *UNTESTED*
nx.write_gexf(gsub, "wikipedia.gexf")