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

import sys
import re
import urllib
import copy
import nltk 
from region import Region
from lxml import etree, html
from lxml.html import HtmlComment
from lxml.html.clean import Cleaner 
from terminal_colors import Tcolors
 
VALID_TAGS = ['div','td','span','p','form','dd','dt','li']
STRONG_TAGS = ['div','td','dd','dt','li']
MODEL_TAGS = ["article", "comments", "multiple_regions"]
TAGS = ['a','img','strong','b','i','br','script','style',
        'h4','h5','h6','strong', 'noscript','em','center']
ARGS = {'meta':False, 'safe_attrs_only':False, 'page_structure':False, 
       'scripts':True, 'style':True, 'links':True, 'remove_tags':TAGS}
T1 = 50 # max density region distance threshold
T2 = 20 # min region density threshold

class SDAlgorithm():
    
    def __init__(self):
        self.valid_nodes = {}
        self.regions = []
        self.max_region = None
        self.max_region_density = None
        self.min_region_level = 10000
        self.min_region_level_counter = 0
        self.page_model = None
        self.url = None
    
    def analyze_page(self):
                
        print("[*] Create DOM tree...")
        tree = self.construct_page_tree() 
        node = tree.getroot()
        self.cross_tree(node) 
        print("[*] Calculating initial groups...")
        print("[*] Merging groups...")
        self.merge_groups(tree) 
        print("[*] Creating regions...")
        self.create_regions(tree) 
        print("[*] Calculating distances from max region...")
        self.calculate_distances_from_max(tree)  
        print("[*] Printing regions...\n")
        for region in self.regions:
            region._print()  
            
        article, comments, multiple = self.classify_page()

        if article is not None and comments is None:
            return 'article', article, None, None
        elif article is not None:
            return 'comment', article, comments
        else:
            return 'multiple', None, None, multiple
    
    
    def construct_page_tree(self):
        """
        Downloads the HTML page given the URL and creates the DOM page tree.
        Only the nodes that are useful for the segmentation are kept.
        """
        page = urllib.urlopen(self.url)
        html_body = page.read()  
        doc = html.fromstring(html_body)
        cleaner = Cleaner(**ARGS)
        try:
            doc = cleaner.clean_html(doc)
        except:
            pass
        tree = doc.getroottree() 
        return tree 
        
    
    def classify_page(self):
        """
        Characterize the page according to i) has main article (has_article()),
        ii) has main article with comments (is_full_article()), iii) has multiple 
        opinions like a forum (is_discussion()).
        """        
        validated = False

        [biggest_regions, grouped_comments]= self.group_regions()
        [article_exists, article] = self.has_article(biggest_regions)

        if article_exists: 
            max_group = self.get_candidate_article(article, grouped_comments)

            if grouped_comments.has_key(max_group): 
                if grouped_comments != {}:
                    validated = self.candidate_group_level_validated(max_group, article, grouped_comments)
                
                context_validated =  self.candidate_context_validated(article, grouped_comments, max_group)            
                if self.big_areas_in_same_level(article, grouped_comments, max_group) and not validated:
                    print(Tcolors.INFO + " Multiple similar regions detected!")
                    print("Class: ")
                    print(Tcolors.RES + " " + grouped_comments[max_group][0].class_name)
                    print("Texts: " )
                    for reg in grouped_comments[max_group]:
                        print(reg.full_text)
                    return None, None, grouped_comments[max_group]
                elif not context_validated: 
                    print()
                    self.print_article(article)
                    print()
                    print(Tcolors.INFO + " No comments found.")                
                    return article, None, None
                elif context_validated:
                    print()
                    print(Tcolors.INFO + " Article with comments detected!")
                    self.print_article(article)
                    print()
                    print("Comment class:")
                    print(Tcolors.RES + " " + max_group) 
                    print("Comments:")
                    for com in grouped_comments[max_group]:
                        print(com.full_text)
                    return article, grouped_comments[max_group], None
            else:
                self.print_article(article)
                return article, None, None
        else: 
            print(Tcolors.INFO + " Multiple similar regions detected!" ) 
            print(Tcolors.RES)
            print("Texts: ")
            for reg in biggest_regions:
                print(reg.full_text)
            return None, None, biggest_regions
    
    def group_regions(self):
        """
        Compute and return two groups of regions, namely the one for those that have 
        distance smaller or equal to the max density region distance threshold (T1)
        and the second the regions that can be grouped based on their CSS classes.
        """
        biggest_regions = []    
        grouped_comments = {}
        
        for region in self.regions: 
            if region.distance_from_max <= T1:
                biggest_regions.append(region)        
                if region.distance_from_root < self.min_region_level \
                   and self.combined_region_level_exceeded(region): 
                    self.min_region_level_counter += 1
                    self.min_region_level = region.distance_from_root
                    
            pr_com = (len(region.tree.xpath(region.root)) > 0 and\
                      region.tree.xpath(region.root)[0].getparent().attrib.has_key('class') and \
                     region.tree.xpath(region.root)[0].getparent().attrib["class"].count('comment') > 0)
            if region.distance_from_max != 0 and (region.class_name != "" or \
               (region.class_name == "" and pr_com)):
                if not grouped_comments.has_key(region.class_name):
                    grouped_comments[region.class_name] = [region]
                else:
                    grouped_comments[region.class_name].append(region)
                 
        return biggest_regions, grouped_comments
    
    
    def combined_region_level_exceeded(self, region):
        """
        Check whether the candidate article region is close to the root
        and has an HTML title in some of its nearest ancestors.
        """
        level = region.distance_from_root
        title_level = region.ancestor_title_level
        return level - title_level > level / 2
    
    
    def has_article(self, biggest_regions):
        """
        Check whether the candidate regions have a potential article and 
        return the possible candidate.
        """
        article_region = None
        if len(biggest_regions)==1:
            return True, biggest_regions[0]
        elif biggest_regions is None:        
            return False, None 
        biggest_regions = [reg for reg in biggest_regions if reg.ancestor_title\
                           is not None and reg.distance_from_root <= self.min_region_level\
                           and self.combined_region_level_exceeded(reg)]    
        if self.min_region_level_counter > 1 or biggest_regions == []:
            pass
        else:
            article_region = self.find_article_region(biggest_regions) 
            if article_region:
                return True, article_region
        
        return False, article_region
    
    
    def find_article_region(self, biggest_regions):
        """
        Return the region that has the minimum title level among the 
        biggest regions.
        """
        region_min_title_level = None 
        min_title_level = 1000 
        for reg in biggest_regions:        
            if reg.ancestor_title_level < min_title_level:
                min_title_level = reg.ancestor_title_level
                region_min_title_level = reg
        article = region_min_title_level
        return article       
    
    
    def get_candidate_article(self, article, grouped_comments):
        """ 
        Check whether the candidate article region is on the same level with the
        candidate group of comments and return the maximum density group that 
        the candidate article belongs to.
        """
        min_dist = 1000
        max_path_level = 0
        min_dist_group = None
        max_group_density = 0
        
        if article.root_node.getparent() is not None:
            article_parent_path = self.get_path(article.root_node.getparent())
        else:
            article_parent_path = ""
        max_group = None
        groups_level = {}        
        groups_below_article_tags = []
        
        if grouped_comments is not None:
            groups_tuple = grouped_comments.items()
            for group in groups_tuple:
                if group[1][0].root != article.root:
                    comment_parent_path = self.get_path(group[1][0].root_node.getparent())
                    common_path =  self.extract_common(article_parent_path,comment_parent_path)
                    common_path_level = common_path.count("/")   
                    comment_path_level = comment_parent_path.count("/")
                    article_level =  article_parent_path.count("/") 
                    groups_level[group[0]] = common_path_level
                    equal = comment_path_level == article_level
                    if common_path_level > max_path_level and common_path_level <= article_level :
                        max_path_level = common_path_level
                    
        groups_below_article_tags = [group[0] for group in groups_level.items() if \
                                     group[1]==max_path_level]
              
        for group in groups_below_article_tags:
            group_density = self.find_group_density(grouped_comments[group])
            if group_density > max_group_density:
                max_group_density = group_density
                max_group = group
        return max_group
    
    
    def extract_common(self, a, b):
        """
        Extract common path between two node paths.
        """
        m = min(len(a), len(b))
        for i in range(m):
            if a[i] != b[i]:
                return self.common_path(a[:i])
        return self.common_path(a[:m])
        

    def common_path(self, a): 
        """
        Parse the string of the path of a given node and find the 
        closest valid position for a legitimate path.
        """
        if (len(a) - 1) >= 0 and (a.endswith("[") or a[len(a)-1].isdigit()):
            a_arr = a.split("/")
            a_final = a_arr[:len(a_arr) - 1] 
            a = "/".join(a_final)
        elif a.endswith("/"):
            a = a[:len(a) - 1]
        return a

    def find_group_density(self, groups):
        """
        Find the group with the maximum density with respect to the number
        of characters that are included in their content.
        """
        total_density = 0
        for region in groups:
            for content in region.contents:
                content_text = region.root_node.xpath(content)[0].text_content()
                if content_text is not None:
                    total_density += len(re.sub(r"  |\n|\r|\t","",content_text))
        return total_density
    
    
    def candidate_group_level_validated(self, max_group, article, grouped_comments):
        """
        Validate whether the maximum detected group qualifies for an article.
        """
        validated = True
        article_path = article.root
        comment_path = grouped_comments[max_group][0].root
        common = self.extract_common(article_path, comment_path)
        article_path = article_path.replace(common, "")
        comment_path = comment_path.replace(common,"")
        article_remaining_nodes = article_path.split("/")
        comment_remaining_nodes = comment_path.split("/")
        
        if len(article_remaining_nodes) > 1 and len(comment_remaining_nodes) > 1:
            article_number = re.search("\d",article_remaining_nodes[0])
            comment_number = re.search("\d",comment_remaining_nodes[0])
            if article_number and comment_number:
                article_number.start()
                comment_number.start()
                if article_number >= comment_number:
                    del grouped_comments[max_group]
                    validated = False
            else:
                comment_not_found = True
                validated = False
                try:
                    common_node = article.tree.xpath(common)
                except:
                    common_node = []
                    
                if common_node != []:
                    for child in common_node[0].iterdescendants():
                        if self.get_path(child) == article.root and comment_not_found:
                            validated = True
                            break
                        if self.get_path(child) == grouped_comments[max_group][0].root:
                            comment_not_found = False
                            
        if validated and article.distance_from_root - common.count("/") <= 4:
            pass
        else:
            validated = False 
        return validated
    
    
    def big_areas_in_same_level(self, article, grouped_comments, max_group):
        """
        Check if the big regions (or areas) belong to the same level in the 
        HTML tree structure.
        """
        if grouped_comments.has_key(max_group):
            first_candidate_comment = grouped_comments[max_group][0] 
            return article.distance_from_root == first_candidate_comment.distance_from_root\
                   and self.combined_region_level_exceeded(article)
        else:
            return self.combined_region_level_exceeded(article)
    
    
    def candidate_context_validated(self, article, grouped_comments, max_group):
        """
        Check whether the candidate comment regions validate as such based on
        the keywords that are detected in their content.
        """
        print(Tcolors.ACT + " Validating candidate comment group based on its content...")
        COMMENT_TAGS = ['comment', 'reply', 'response', 'ident', 'said:', 'rate','user','inner','wrote:']
        STRONG_COMMENT_TAGS = ['comment','reply','user','said:','wrote:']
        
        first_candidate_comment = grouped_comments[max_group][0]
        comment_parent = first_candidate_comment.root_node.getparent()
        total_detected = 0
        detected_on_attributes = 0
        strong_tag_detected = False
        found_tags = []
        
        for des in list(comment_parent.iterdescendants()) + [comment_parent]:
            classname = id = ""
            if des.attrib.has_key("class"):
                classname = des.attrib['class']
            if des.attrib.has_key("id"):
                id = des.attrib['id']
            for ctag in COMMENT_TAGS:
                contents = (des.text_content() + classname + id).lower() 
                if contents.count(ctag) > 0:
                    total_detected += contents.count(ctag) 
                    detected_on_attributes += (classname + id).lower().count(ctag) 
                    if (classname + id).lower().count("policy") > 0\
                        or (classname + id).lower().count("footer") > 0:
                        detected_on_attributes = 0
                        strong_tag_detected = 0
                        found_tags = []
                        break
                    if ctag not in found_tags:
                        found_tags.append(ctag)
                    if ctag in STRONG_COMMENT_TAGS:
                        strong_tag_detected = True
        
        attribute_variety = len(found_tags)                
        if not self.big_areas_in_same_level(article, grouped_comments, max_group)\
           and (detected_on_attributes > 0 or strong_tag_detected
           or (total_detected > 0 and attribute_variety > 3))\
           and len(grouped_comments[max_group]) >= 1:     
            return True
        return False
    
    def print_article(self, article):
        """
        Print the details of a detected article (class, title and text).
        """
        print(Tcolors.INFO + " Article detected!" )
        print("Article class: ")
        print(Tcolors.RES + " " + repr(article.class_name))
        print("Article title: ")
        print(article.get_ancestor_title()) 
        print("Article text: ")
        print(article.full_text.replace("\n"," ")) 
    
    def merge_groups(self, tree):
        """
        Detect and merge groups of nodes according to the strong tags definition.
        """
        tmp_nodes = copy.copy(self.valid_nodes)
        for group in tmp_nodes:
            node = tree.xpath(group)[0]
            parent = node.getparent()
            if parent is not None:
                parent_path = self.get_path(parent)
                if self.valid_nodes.has_key(parent_path):
                    self.valid_nodes[parent_path].append(group)
                    self.valid_nodes[parent_path].extend(self.valid_nodes[group])
                    del self.valid_nodes[group]
                elif node.tag not in STRONG_TAGS:
                    self.valid_nodes[parent_path] = [group]
                    self.valid_nodes[parent_path].extend(self.valid_nodes[group])
                    del self.valid_nodes[group]     
                    
    def create_regions(self, tree): 
        """
        Create region instances from the tree nodes of the tree and compute the 
        maximum density region.
        """
        max = 0 
        for group in self.valid_nodes.items(): 
            region = Region(tree,group[0],group[1])
            self.regions.append(region)
            if region.density > max:
                max = region.density
                self.max_region = region
                
    def content_appears_in_other_region(self, region):
        """
        Returns a boolean value that represents whether some of the content
        of the region appears in smaller regions or not.
        """
        for reg in self.regions:
            if reg.full_text in region.full_text and reg.density >= region.density/2:
                return True
        return False
    
    def close_diff_from_second_max(self):
        """
        Returns a boolean value that represents whether the second maximum 
        density region is in close proximity with the maximum density region 
        or not.
        """
        for region in self.regions:
            if region.root != self.max_region.root:
                d = ((float)(region.density)/(float)(self.max_region.density)) * 100
                if 100 - d <= 20: 
                    return True 
        return False
    
    def recompute_max_density_region(self):
        """
        Recalculates the max density region. Useful when some regrouping is 
        taking place.
        """
        max_density = 0 
        for region in self.regions:
            if region.density > max_density:
                max_density = region.density
                self.max_region = region
    
    
    def calculate_distances_from_max(self, tree, fixed_regions=False):  
        """
        Calculates all the region distances from maximum density region.
        """
        tmp_regions = self.regions
        for i,region in enumerate(tmp_regions):
            previous_max_density = self.max_region.density
            d = ((float)(region.density)/(float)(self.max_region.density)) * 100
            region.distance_from_max = 100 - d
            if region.distance_from_max == 0 and region.parts == 1 \
                and not fixed_regions and len(list(region.root_node.getchildren())) > 1\
                and (self.content_appears_in_other_region(region)\
                or self.close_diff_from_second_max(self.max_region)): #and
                self.regions.remove(region)
                self.recompute_max_density_region()
                fixed_regions = True
                self.calculate_distances_from_max(tree, fixed_regions)
    
    def find_node_text(self, node):
        """
        Finds and returns node text (if it exists) other than that of the descendants' text.
        """
        node_text = "" 
        try:
            t = node.text
            t = True
        except:
            t = False
        if t and node.text is not None: 
            node_text = node.text
        else:
            try: 
                itertext = list(node.itertext())
            except: 
                itertext = []
            itertexts = [text for text in itertext if text is not None and re.sub(r"\n|\r|\t| |,|\.","",text) != ""]
            descendants = [des for des in list(node.iterdescendants())]
            descendants_length = len(descendants)
            iter_texts_length = len(itertexts) 

            if descendants_length <= iter_texts_length:
                descendant_texts = [] 
                for descendant in descendants: 
                    if descendant.text is not None:
                        des_txt = descendant.text
                        descendant_texts.append(des_txt)
            
                for i,text in enumerate(itertexts):
                    if "".join(descendant_texts).find(text) == -1 and text is not None\
                       and text != "" and text not in descendant_texts:
                        node_text += text     

        reduced = re.sub(r"\n|\r|\t| |,|\.","",node_text)
        if node_text.find(".") == -1:
            node_text = ""
        elif(reduced == ""):
           node_text = reduced
        elif reduced != "":
           node_text = re.sub(r"\r|\t|\n|  |,,","",node_text) 
            
        return node_text 
    
    def cross_tree(self, node, node_text=None, level=0):
        '''
        Visit all the nodes of the tree and keep those that have character 
        density greater than the T2 threshold.
        '''
        if node_text is None:        
            node_text = self.find_node_text(node)
            
        if node.attrib.has_key("class") and node.attrib["class"] == "wrappers":
            dess = []
            for d,des in enumerate(node.iterdescendants()):
                if des.text is not None:
                    dess.append(des)
            tt_ar=[]
            for t,tt in enumerate(node.itertext()): 
                tt_ar.append(tt)

        if level > 0: 
            if len(node_text) > T2:
                self.group_node(node, node_text)
        
        for child in node.getchildren():
            child_text = self.find_node_text(child)  
            if len(child_text) > T2:
                self.group_node(child, child_text)
            if len(child.getchildren()) > 0:
                self.cross_tree(child, child_text,level + 1)
                  
    
    def get_next_valid_parent(self, node, level=0):
        """
        Get the next parent of a given node that has tag among the
        pre-defined valid ones.
        """ 
        parent = node.getparent()
        if parent is None or level > 3:
            return node 
        if parent.tag in VALID_TAGS:
            return parent 
        return self.get_next_valid_parent(parent,level+1)
    
    
    def has_visible_parents(self, node):
        """
        Check the visibility of the parent nodes of a given node using 
        the CSS style attribute.
        """
        parent = node
        if parent is None:
            return True  
        else:
            style = self.get_style(parent)
        if style is not None and style.replace(" ","").find("display:none") >= 0:
            return False
        return self.has_visible_parents(parent.getparent())
        
    def get_style(self, node):
        """
        Get the style attribute of the node if it exists.
        """
        if node.attrib.has_key("style"):
            style = node.attrib.get('style')
        else:
            style = ""
        return style
    
    def group_node(self, node, node_text):
        """
        Group node to the closest possible node which has a strong tag.
        """
        valid_parent = self.get_next_valid_parent(node) 
        node_path = self.get_path(node)
        parent_path = self.get_path(valid_parent)
        if node.tag in STRONG_TAGS:
            parent_path = node_path 
            
        if parent_path not in ["/html","/html/body"] and node_text is not None\
           and node.tag != 'body' and self.has_visible_parents(valid_parent):
            if not self.valid_nodes.has_key(parent_path):
                self.valid_nodes[parent_path] = [node_path] 
            else:
                if node_path not in self.valid_nodes[parent_path]:
                    self.valid_nodes[parent_path].append(node_path)
        
    def get_path(self, node):
        """
        Get the tree path of a given node.
        """
        return node.getroottree().getpath(node)
    
if __name__ == '__main__': 
    url = sys.argv[1]
    sd = SDAlgorithm()
    sd.url = url
    sd.analyze_page()

# Article with comments
# python sd_algorithm.py http://www.care2.com/greenliving/chocolate-may-reduce-risk-of-heart-failure.html
# Article
# python sd_algorithm.py http://www.bbc.co.uk/news/world-africa-12328506
# Multiple
# python sd_algorithm.py "http://www.lonelyplanet.com/thorntree/forum.jspa;jsessionid=57DA8CB66960A9D820CAB16BB221094D.app01?forumID=34&errorMsg=The%20thread%20requested%20is%20not%20currently%20available"
