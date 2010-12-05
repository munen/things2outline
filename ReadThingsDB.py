# -*- coding: utf-8 -*-

from xml.dom import minidom
import sys
from optparse import OptionParser

def readThingsDB(things_xml_path, outline_file):
  """
    Wrapper method. Reading things database, extracing all projects and todos,
    Then writing an outline.
  """

  xml = minidom.parse(things_xml_path)
  objects = xml.getElementsByTagName("object")
  
  projects = getProjects(objects)
  projects.insert(0, getTodosInCategory(objects, 'FocusTrash'))
  projects.insert(0, getTodosInCategory(objects, 'FocusMaybe'))
  projects.insert(0, getTodosInCategory(objects, 'FocusNextActions'))
  projects.insert(0, getTodosInCategory(objects, 'FocusInbox'))
  
  projects = getTodos(projects, objects)
 
  writeOutline(outline_file, projects)


def getTodosInCategory(objects, things_category):
  """ Get todos in inbox/trash/next/maybe """

  # <attribute name="identifier" >FocusInbox</attribute>
  #<relationship name="focustodos" idrefs="z8663 z7372 "></relationship>

  for object in objects:
    if object.attributes["type"].value != 'FOCUS':
      continue
    attribute_nodes = object.getElementsByTagName("attribute")
    for attribute_node in attribute_nodes:

      if attribute_node.childNodes[0].nodeValue == things_category: 
        relationship_nodes = object.getElementsByTagName("relationship")
        for relationship_node in relationship_nodes:
          try:
            if relationship_node.attributes['name'].value == 'focustodos':
              inbox_todos = relationship_node.attributes['idrefs'].value
          except:
            # The inbox could be empty
            inbox_todos = ""

  # Switch Things naming with something more familiar
  title = {'FocusTrash': 'TRASH', 'FocusMaybe': 'MAYBE', 'FocusInbox': 'INBOX',
    'FocusNextActions': 'NEXT'}[things_category]

  # Same format as in getProjects for a regular project
  return {'title': title, 'ref_ids': inbox_todos, 'todos':[]}

def writeOutline(outline_file, projects):
  """ Writes the project information to an outline file """

  fp = open(outline_file, "w")
  for project in projects:
    fp.write("[" + project['title'] + "]\n")
    for todo, note in project['todos']:
      fp.write("\t%s"%todo + "\n")
      if note: fp.write("\t\t%s"%note + "\n")
    fp.write("\n")
  fp.close()


def getTodos(projects, objects):
  """
    Get todos for each project
  """

  for project in projects:
    for ref_id in project['ref_ids'].split():
      for object in objects:
        if object.attributes['id'].value == ref_id:
          attribute_nodes = object.getElementsByTagName("attribute")
          title = ""
          content = ""
          for attribute_node in attribute_nodes:
            if attribute_node.attributes['name'].value == 'title':
              title = attribute_node.childNodes[0].nodeValue.encode("utf-8")
              break
          # Check if todo has a note attached
          if title:
            for attribute_node in attribute_nodes:
              if attribute_node.attributes['name'].value == 'content':
                content = attribute_node.childNodes[0].nodeValue.encode("utf-8")
                # todo: In content there is a lot of junk. Clean it out!
                content = "HAS NOTE"
                break

          project['todos'].append([title, content])
  return projects


def getProjects(objects):
  """
    Reads all projects into a dictionary
  """
  
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
  return projects

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
