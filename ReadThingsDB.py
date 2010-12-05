# -*- coding: utf-8 -*-

from xml.dom import minidom
import sys
from optparse import OptionParser

def readThingsDB(things_xml_path, outline_file):
  xml = minidom.parse(things_xml_path)
  objects = xml.getElementsByTagName("object")
  
  # Get projects
  projects = []
  for object in objects:
    if object.attributes["type"].value != 'TODO':
      continue
    attribute_nodes = object.getElementsByTagName("attribute")
    title = ""
    for attribute_node in attribute_nodes:
      # Get all project names
      # <attribute name="title" type="string">Movies</attribute>
      if attribute_node.attributes['name'].value == 'title':
        try:
          title = attribute_node.childNodes[0].nodeValue.encode("utf-8")
        except:
          continue
        
        # Get ref_ids of all todos for current project
        relationship_nodes = object.getElementsByTagName("relationship")
        ref_ids = ''
        for relationship_node in relationship_nodes:
          try:
            # <relationship name="children" idrefs="z4383 z2529 z6641...">
            if relationship_node.attributes['name'].value == 'children' and\
                relationship_node.attributes['idrefs'].value != '':
              ref_ids = relationship_node.attributes['idrefs'].value
              break
          except:
            # Not all projects have todos -> hence the lookup for 'idrefs' can fail
            pass
        
        # Todos and Projects both are objects with attributes 'todo'. They differ
        #in that projects have multile ref_ids.
        if len(ref_ids.split()) > 1:
          projects.append({'title': title, 'ref_ids': ref_ids, 'todos':[]})
  
  # Get todos for each project
  for project in projects:
    for ref_id in project['ref_ids'].split():
      for object in objects:
        if object.attributes['id'].value == ref_id:
          attribute_nodes = object.getElementsByTagName("attribute")
          title = ""
          for attribute_node in attribute_nodes:
            if attribute_node.attributes['name'].value == 'title':
              title = attribute_node.childNodes[0].nodeValue.encode("utf-8")
              break
          project['todos'].append(title)
 
  fp = open(outline_file, "w")
  for project in projects:
    fp.write(project['title'] + "\n")
    for todo in project['todos']:
      fp.write("\t%s"%todo + "\n")
    print "\n"
  fp.close()

if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-d", "--database", 
                    help="path to things Database.xml", metavar="DB")
  parser.add_option("-o", "--output", 
                    help="Output outline", metavar="OTL")
  
  (options, args) = parser.parse_args()
  if not options.database or not options.output:
    parser.print_help()
    sys.exit(1)
  else:
    readThingsDB(options.database, options.output)
