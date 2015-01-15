#courtesy of @_Ninji

import sys
import traceback

def print_error(info):
  print("----- BEGIN -----")
  traceback.print_exception(info[0], info[1], info[2])
  print("-----  END  -----")

# Am I even supposed to subclass StandardError??
# dunno, don't care
class ScriptError(StandardError):
  pass

class UserError(StandardError):
  pass

class Plugin(object):
  def __init__(self, name):
    self.name = name
    self.success = False

    # This may throw an exception, caller should catch it
    self.module = __import__(name)

    # Call init function
    if hasattr(self.module, '_init'):
      try:
        self.module._init()
      except Exception, e:
        self.unload()
        raise e

    self.success = True

  def unload(self):
    del sys.modules[self.name]

class PluginManager(object):
  def __init__(self):
    self.plugins = {}

  def load(self, name):
    if name in self.plugins:
      raise ScriptError('Plugin {0} already loaded'.format(name))

    # This may throw an exception, caller should catch it
    plug = Plugin(name)
    self.plugins[name] = plug

  def unload(self, name):
    if name not in self.plugins:
      raise ScriptError('Plugin {0} not loaded'.format(name))

    self.plugins[name].unload()
    del self.plugins[name]

  def dispatch_event(self, c, name, *args):
    for plugname, plugin in self.plugins.iteritems():
      if hasattr(plugin.module, name):
        f = getattr(plugin.module, name)

        try:
          f(c, *args)
        except Exception, exc:
          print('----- Error in {0} -----'.format(plugname))
          print_error(sys.exc_info())