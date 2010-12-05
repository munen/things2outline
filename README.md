ABOUT
-----

This Python script parses a [Things](http://culturedcode.com/things/) database
and writes an outline. 

Outlines can be greatly edited with [Vimoutliner](http://www.vimoutliner.org) or [Emacs
Org-Mode](http://orgmode.org/).

Usage
-----

    $python ReadThingsDB.py 
    Usage: ReadThingsDB.py [options]

    Options:
      -h, --help            show this help message and exit
      -d DB, --database=DB  path to things Database.xml
      -o OTL, --output=OTL  Output outline

Todo
----

Find those in TODO.otl


Sample Output
-------------

    [INBOX]
            Write script to emulate DynDNS
    [NEXT]
            Take out the trash
    [MAYBE]
            Learn to play the piano
    [TRASH]
            Notes in Things trash
    [Review]
            Gather loose papers
            Process notes
            Review Someday
            Review previous calendar data
            Review waiting for
            Review "Action" re Mail
            Review upcoming calendar data
            Review "Deferred" re Mail
            Review "Waiting" re Mail
            Review project lists
            Review next action list
            Empty head
            Review "Incubation" re Mail
            Review "Respond" re Mail
