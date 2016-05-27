__author__ = 'masslab'

def pretty_statusbrowser(browser, d, indent=0):
   for key, value in d.iteritems():
      browser.append('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         browser.append('\t' * (indent+1) + str(value))


def pretty(d, indent=0):
   for key, value in d.iteritems():
      print '\t' * indent + str(key)
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print '\t' * (indent+1) + str(value)

