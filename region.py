#!/usr/bin/env python
# -*- coding: UTF-8 -*

####################################################################
# Licence:    Creative Commons (see COPYRIGHT)                     #
# Authors:    Nikolaos Pappas, Georgios Katsimpras                 #
#             {nik0spapp, gkatsimpras}@gmail.com                   # 
# Supervisor: Efstathios stamatatos                                #
#             stamatatos@aegean.gr                                 #
# University of the Aegean                                         #
# Department of Information and Communication Systems Engineering  #
# Information Management Track (MSc)                               #
# Karlovasi, Samos                                                 #
# Greece                                                           #
####################################################################

import re 
from terminal_colors import Tcolors
from lxml.html import HtmlComment 

class Region():
    
    def __init__(self, tree, root, contents):
        self.tree = tree
        self.root = root
        self.root_node = self.tree.xpath(root)[0]
        self.contents = contents
        self.density = 0
        self.parts = len(contents)
        self.distance_from_max = 0
        self.distance_from_root = self.calculate_distance_from_root()
        self.class_name = self.calculate_class_name()
        self.id = self.calculate_id()
        self.full_text = ""
        self.calculate_info()
        self.ancestor_title = None
        self.ancestor_title_level = 0
    
    def has_title_at_ancestors(self, nodechild, node, level=0): 
        """
        Checks whether a given node has an ancestor with title tag (h1,h2)
        and returns a boolean value for existence and the level in which
        it was detected. It also stores the text of the title node.
        """ 
        if node is not None:
            
            for sibling in node.iterchildren():
                if nodechild is not None \
                   and self.tree.getpath(sibling) == self.tree.getpath(nodechild):
                    break
                
                VALID_TAGS = ['h2','h1']
                if nodechild is not None:
                    VALID_TAGS += ['h3']
                if sibling.tag in VALID_TAGS:
                    self.ancestor_title = sibling.text_content()
                    self.ancestor_title_level = level
                    return  True, level
                 
                for child in sibling.iter():
                    if child.tag in VALID_TAGS:
                        self.ancestor_title = child.text_content()
                        self.ancestor_title_level = level
                        return  True, level
                level += 1
        else:
            return False
        return self.has_title_at_ancestors(node, node.getparent(),level + 1)
        
    def find_node_text(self,node):
        """
        Finds and returns node text (if it exists) other than that of the descendants' text.
        """
        node_text = "\n" 
        for des in node.iter():
			try:
				if des.text is not None and (des.tag not in ['script', 'style','h1','h2']\
		           and not isinstance(des, HtmlComment) and re.sub(r"\n|\r|\t| |,|;|\.","",des.text) != ""\
		           or (des.tag == "p")) and des.text.find(".") > -1 and node_text.find(des.text_content()) == -1:
					node_text += re.sub(r"\n|\r|\t","",des.text_content())
					if des.tag == 'p':
						node_text += "\n"   
					elif des.tail is not None and des.tag in ['table']:
						node_text += des.tail
			except:
				node_text += ""
                          
        node_text = node_text.replace("&gt",">")
        node_text = re.sub(r"  |,,|--|==|<!--(.|\s)*?-->|<!\[CDATA(.|\s)*?\]\]>","",node_text)  
        return node_text
    
    def get_ancestor_title(self):
        """
        Computes and returns the title of the ancestor (None if it doesn't exist).
        """
        self.has_title_at_ancestors(None, self.root_node)
        return self.ancestor_title

    def calculate_info(self): 
        """
        Calculates the full text and the density of the given region.
        """
        density = 0
        full_text = self.find_node_text(self.root_node)
        self.full_text = full_text
        self.density = len(self.full_text)
    
    
    def calculate_distance_from_root(self):
        """
        Returns the distance of the region from the root node.
        """
        return self.root.count("/")

    def calculate_id(self):
        """
        Returns the id attribute of the node if it exists, otherwise it returns 
        an empty string.
        """
        if self.root_node.attrib.has_key('id'):
            return self.root_node.attrib['id']
        else:
            return ""
        
    def calculate_class_name(self):
        """
        Returns the CSS class attribute of the node if it exists, otherwise it returns 
        an empty string.
        """
        if self.root_node.attrib.has_key('class'):
            return self.root_node.attrib['class']
        else:
            return ""
        
    def _print(self): 
        # Uncomment the following for debugging of the regions.
        """
        print Tcolors.CYAN  + "[x] Region:", self.root
        print "-----------------------------------------------------------------------------"
        print Tcolors.ENDC + Tcolors.WARNING + " Tag:", self.root_node.tag
        print " Class:", self.class_name
        print " Id:", self.id
        print " Level:", self.distance_from_root
        print " Parts:", self.parts
        print " Density:", self.density
        print " Distance from max:", self.distance_from_max
        print " Has title on ancestors:", self.has_title_at_ancestors(None, self.root_node)
        print " Full text: \n", self.full_text 
        print "\n" + Tcolors.ENDC
        """
    	pass 

