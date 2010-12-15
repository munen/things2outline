#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
from time import strftime
from xml.dom import minidom
import sys, os
import re
import lxml.html
import time

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
  if outline_file:
    fp = open(outline_file, "w")
  else:
    fp = sys.stdout
  for project in projects:
    fp.write("[" + project['title'] + "]\n")
    for todo, note, created, modified, completed, tags in project['todos']:
      fp.write("\t%s"%todo + "\n")
      if tags:
        fp.write("\t\t:tags %s" % ", ".join(tags) + "\n")
          
      fp.write("\t\t:created %s"%created + "\n")
      if created != modified:
        fp.write("\t\t:modified %s"%modified + "\n")
      if completed:
        fp.write("\t\t:completed %s"%completed + "\n")
      if note:                         
          for n in note:
              fp.write("\t\t%s" % n.encode('utf-8') + "\n")
    fp.write("\n")
  fp.close()

def convertCocoaEpoch(cocoa_timestamp):
  """
    Convert Cocoa epoch timestamp to human readble format.
    Cocoa epoch is set on 01.01.2001. Things stores dates in cocoa epoch with
    double precision floats: '310744066.04055202007293701172'
  """

  # 01.01.2001 as unix epoch timestamp
  unix_epoch_gap = 978307200

  # We only need the seconds.
  cocoa_timestamp = int(cocoa_timestamp.split('.')[0])
  timestamp = cocoa_timestamp + unix_epoch_gap
  
  return strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timestamp))

def getTags(objects):
  objects = [o for o in objects if o.attributes["type"].value == 'TAG']
  tags = {}
  for object in objects:
    attribute_nodes = object.getElementsByTagName("attribute")   
    for attribute_node in attribute_nodes:
      if attribute_node.attributes['name'].value == 'title':
        if attribute_node.childNodes:
            tags[object.attributes['id'].value] = attribute_node.childNodes[0].nodeValue.encode("utf-8")
    
  return tags

def getTodos(projects, objects):
  """
    Get todos for each project
  """
  tags_dict = getTags(objects)
  for project in projects:
    for ref_id in project['ref_ids'].split():
      for object in objects:
        if object.attributes['id'].value == ref_id:
          attribute_nodes = object.getElementsByTagName("attribute")
          title        = ""
          content      = ""
          datemodified = ""
          datecreated  = ""
          datecompleted= ""
          tags         = ""           
          for attribute_node in attribute_nodes:
            if attribute_node.attributes['name'].value == 'title':
              if attribute_node.childNodes:
                  title = attribute_node.childNodes[0].nodeValue.encode("utf-8")
                  break
          # Check if todo has a note attached
          if title:
            for attribute_node in attribute_nodes:
              # <attribute name="datemodified" >309306984.40529602766036987305
              if attribute_node.attributes['name'].value == 'datemodified':
                datemodified = convertCocoaEpoch(attribute_node.childNodes[0].\
                    nodeValue.encode("utf-8"))
              # <attribute name="datecreated" >306520491.00000000000000000000
              if attribute_node.attributes['name'].value == 'datecreated':
                datecreated = convertCocoaEpoch(attribute_node.childNodes[0].\
                    nodeValue.encode("utf-8"))
              #<attribute name="datecompleted" type="date">292880221.18648099899291992188
              if attribute_node.attributes['name'].value == 'datecompleted':
                datecompleted = convertCocoaEpoch(attribute_node.childNodes[0].\
                    nodeValue.encode("utf-8"))
              if attribute_node.attributes['name'].value == 'content':
                content = attribute_node.childNodes[0].nodeValue #.encode("utf-8")
                # lets encode in writeOutline               
                # I think we need to translate all this things
                html = content.replace('\\u3c00', '<').replace('\\u3e00', '>') 
                html = html.replace('\u2600', '&')
                html = lxml.html.fromstring(html)
                content = html.text_content().split('\n')
                for l in html.iterlinks():
                    content += [l[2]]
            relationship_nodes = object.getElementsByTagName("relationship")
            for relationship_node in relationship_nodes:
              if relationship_node.attributes['name'].value == 'tags':
                try:
                  tags_id = relationship_node.attributes['idrefs'].value
                  tags = [tags_dict[t_id] for t_id in tags_id.split()]
                except:
                  tags = ""

          project['todos'].append([title, content, datecreated, datemodified, datecompleted, tags])
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

def getDefaultThingsXml():
  """docstring for getDefaultDb"""
  return 
  pass


DEFAULT_THINGS_XML = os.path.expanduser('~') + \
                     '/Library/Application Support/Cultured Code/Things/Database.xml'


if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-d", "--database", 
                    help="path to things Database.xml", metavar="DB")
  parser.add_option("-o", "--output", 
                    help="Output outline", metavar="OTL")
  
  (options, args) = parser.parse_args()

  database = None
  if os.path.exists(DEFAULT_THINGS_XML):
    database = DEFAULT_THINGS_XML 
  output_file = None
  if options.database:
    database = options.database
  if options.output:
    output_file = options.output
  if not database:     
    parser.print_help()
    sys.exit(1)
  readThingsDB(database, output_file)
    
