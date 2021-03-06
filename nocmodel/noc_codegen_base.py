#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# NoC Code generator
#   This module defines the basic structure for code generation
#
# Author:  Oscar Diaz
# Version: 0.2
# Date:    11-11-2011

#
# This code is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software  Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA
#

#
# Changelog:
#
# 11-11-2011 : (OD) initial release
#

"""
Base for code generation support

This module defines:
* Class 'noc_codegen_base'
* Class 'noc_codegen_ext'
"""

from myhdl import intbv, SignalType
from nocmodel import *

#import scipy
#import networkx as nx
from copy import deepcopy
from sys import exc_info
import warnings

class noc_codegen_base():
    """
    Base class for code generator
    
    This class holds a basic model of a hardware description. Although inspired 
    in VHDL, it also holds for Verilog.
    
    Note that its necessary a defined noc model to generate this code model.
    
    Note that this class is meant to be extended by a particular code generator:
    VHDL generator, Verilog generator, etc.
    
    This object will assume a module has the following sections:
    --------------------
    <docheader>  : File header and documentation about the module
    <libraries>  : Declarations at the beginning (VHDL: libraries declarations)
    <modulename> : Module name (VHDL: entity name)
    <generics>   : Parameters for the module (VHDL: generics inside an entity)
    <ports>      : Declaration of inputs and outputs (VHDL: ports inside an entity)
    <implementation> : Code implementation (pure VHDL or Verilog code)
    --------------------
    
    Objects type:
    * docheader, libraries, modulename and implementation are simple strings.
    * generics are list of dictionaries with this required keys:
        * "class" : always "generic"
        * "name"
        * "type" : string formatted data type 
        * "type_array" : 2-element list of strings that declares array boundaries 
            either using numbers or generics names. None for simple data types
        * "default_value"
        * "current_value" 
        * "description"
    * ports are list of dictionaries with this required keys:
        * "class" : always "port"
        * "name"
        * "type" : port type, if applicable
        * "nocport" : index to related port in the nocobject' ports dictionary or
            others signal containers in the nocobject.
        * "signal_list" : list of signals that compose the port
        * "description"
    * external_signals are list of signals that aren't related to any port.
    * signals are dictionaries with this required keys:
        * "class" : always "signal"
        * "name"
        * "type" : string formatted data type 
        * "type_array" : 2-element list of strings that declares array boundaries 
            either using numbers or generics names. None for simple data types
        * "direction"
        * "default_value"
        * "related_generics" : when the data type is an array, this list has 
            references to generics to be used to build array declaration.
        * "description"
        
    Attributes:
    * modulename
    * nocobject_ref
    * docheader
    * libraries
    * generics
    * ports
    * external_signals
    * implementation
    * interface_hash
        
    Notes:
    * Code generation methods are meant to return strings. The user is 
      responsible to write it in files.
    * This object maintains the code model and use it to generate code. Any
      particular changes or adjustments to the model should be done by a 
      'noc_codegen_ext' object. 
    * This code generation model are restricted to noc models, because 
      routers and ipcores are generated by MyHDL code converter (this 
      could change if the noc objects needs to keep hierarchy in its 
      internal implementation). 
      This converter keeps routers and ipcores hierarchy.
    """
    
    def __init__(self, nocobject_ref, **kwargs):
        # nocobject reference
        if not isinstance(nocobject_ref, (nocobject, noc)):
            raise TypeError("Argument must be an instance of nocobject or noc class")
        self.nocobject_ref = nocobject_ref
        
        # External conversion flag
        self.external_conversion = False

        # string type objects
        self.docheader = ""
        self.libraries = ""
        self.modulename = ""
        
        # list of dictionaries (generic and port)
        self.generics = []
        self.ports = []
        self.external_signals = []
        
        # implementation 
        self.implementation = ""
        
        # module hash
        self.interface_hash = ""
        
        # optional arguments
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
       
    # main methods
    def generate_file(self):
        """
        Generate the entire file that implements this object.
        """
        raise NotImplementedError("What language for code generation?")
    
    def generate_component(self):
        """
        Generate a component definition for this object.
        """
        raise NotImplementedError("What language for code generation?")

    def generate_generic_declaration(self, generic=None, with_default=False):
        """
        Generate a generic declaration for this object.
        
        Arguments:
        * generic : either a name or a list index for a particular generic
        * with_default : True to add the default value
        
        Returns:
        * A string when generic argument is used
        * A list of strings with all generics 
        """
        raise NotImplementedError("What language for code generation?")

    def generate_port_declaration(self, port=None, with_default=False):
        """
        Generate a port declaration for this object.
        
        Arguments:
        * port : either a name or a list index for a particular port
        * with_default : True to add the default value
        
        Returns:
        * A list of strings with all signals in port when port argument is used
        * A list of strings with all signals in all ports
        """
        raise NotImplementedError("What language for code generation?")
        
    def generate_signal_declaration(self, inport=None, signal=None, with_default=False):
        """
        Generate a signal declaration for this object.
        
        Arguments:
        * inport : either a name or a list index for a particular port. None 
            means use the external_signals list
        * signal : either a name or a list index for a particular signal
        * with_default : True to add the default value
        
        Returns:
        * A string when signal argument is used
        * A list of strings with all signals
        """
        raise NotImplementedError("What language for code generation?")
        
    def make_comment(self, data):
        """
        Convert string data to language comment
        
        Argument:
        * data: string or list of strings to convert
        
        Returns: string or list of strings with comments added.
        """
        raise NotImplementedError("What language for code generation?")
        
    def add_tab(self, data, level=1):
        """
        Add an indentation level to the string
        
        Argument:
        * data: string or list of strings
        * level: how many indentation levels to add. Default 1
        
        Returns: string or list of strings with <level> indentation levels.
        """
        raise NotImplementedError("What language for code generation?")
        
    def to_valid_str(self, str_in):
        """
        Convert an input string, changing special characters used on
        the HDL language. Useful for set names .
        
        Argument:
        * str_in: string to convert
        
        Returns: the converted string.
        """
        raise NotImplementedError("What language for code generation?")

    # codegen model management
    def add_generic(self, name, value, description="", **kwargs):
        """
        Add a generic to the model. 

        Arguments:
        * name : must be a string
        * value : default value for this generic
        * description : 
        * Optional arguments (just for method call format)
        
        Returns:
        * Reference to added generic dictionary.
        
        Note:
        * This method can override an existing generic entry.
        * This basic method just add name, default value and description. 
          Extended class methods must fill correct type arguments.
        """
        if not isinstance(name, str):
            raise TypeError("Name must be string, not '%s'." % repr(name))

        # supported types:
        if not isinstance(value, (bool, int, intbv, str)):
            raise TypeError("Unsupported type '%s'." % repr(type(value)))

        # check if new entry
        g = filter(lambda x: x["name"] == name, self.generics)
        if len(g) == 0:
            g = get_new_generic(name = name)
            self.generics.append(g)
        else:
            g = g[0]
        g.update(default_value = value, description = description)
        # optional kwargs
        g.update(kwargs)
        # return reference to added generic dict
        return g
        
    def add_port(self, name, signal_desc=None, description="", **kwargs):
        """
        Add a port to the model. 

        Arguments:
        * name : must be a string
        * signal_desc : optional dictionary with signal information included. 
          None to just add/update port without changing its signals.
        * description : 
        * Optional arguments (just for method call format)
        
        Returns:
        * Reference to added port dictionary.
        
        Note:
        * This method can add a new port or update an existing port with new 
          signals.
        * This basic method just add name and description, and update a signal 
          using signal_desc information. Extended class methods must fill 
          correct type arguments in the updated signal.
        """
        if not isinstance(name, str):
            raise TypeError("Name must be string, not '%s'." % repr(name))

        # check signal dict keys: must have at least class and name
        if signal_desc is not None:
            if not all([x in signal_desc for x in ("class", "name")]):
                raise TypeError("Argument signal_desc must be a signal dict ('%s')." % repr(signal_desc))
            if signal_desc["class"] != "signal":
                raise TypeError("Argument signal_desc must be a signal dict ('%s')." % repr(signal_desc))

        # check if new entry
        p = filter(lambda x: x["name"] == name, self.ports)
        if len(p) == 0:
            p = get_new_port(name = name)
            self.ports.append(p)
        else:
            p = p[0]

        # only update description when string is non-empty
        if description != "":
            p.update(description = description)

        # check existing signal
        if signal_desc is not None:
            sig = filter(lambda x: x["name"] == signal_desc["name"], p["signal_list"])
            if len(sig) == 0:
                p["signal_list"].append(signal_desc)
            else:
                sig[0].update(signal_desc)
                
        # optional kwargs
        p.update(kwargs)
        # return reference to added/updated port dict
        return p
        
    def add_external_signal(self, name, direction, value, description="", **kwargs):
        """
        Add a external signal to the model. 

        Arguments:
        * name : must be a string
        * direction : "in" or "out"
        * value : initial value for this port
        * description
        * Optional arguments (just for method call format)
        
        Returns:
        * Reference to added external_signals dictionary.
        
        Note:
        * This method can override an existing signal entry.
        * This basic method just add name, direction, intial value and 
          description. Extended class methods must fill correct type arguments.
        """
        if not isinstance(name, str):
            raise TypeError("Name must be string, not '%s'." % repr(name))

        # supported types:
        if isinstance(value, SignalType):
            value = value._init
        if not isinstance(value, (bool, int, intbv)):
            raise TypeError("Unsupported type '%s'." % repr(type(value)))
        if direction not in ["in", "out"]:
            raise ValueError("Direction must be 'in' or 'out', not '%s'." % repr(direction))
        # check if new entry
        sig = filter(lambda x: x["name"] == name, self.external_signals)
        if len(sig) == 0:
            sig = get_new_signal(name = name)
            self.external_signals.append(sig)
        else:
            sig = sig[0]
        sig.update(direction = direction, default_value = value, description = description)
        # optional kwargs
        sig.update(kwargs)
        # return reference to added generic dict
        return sig
        
    def build_implementation(self):
        """
        Try to generate the implementation section. Check if a "codemodel" 
        object exists and try to call "generate_implementation" method.
        
        If the call is successful, self.implementation will store its return
        string. Do nothing on failure (report a warning).
        """
        if hasattr(self.nocobject_ref, "codemodel"):
            implementation = ""
            if not hasattr(self.nocobject_ref.codemodel, "generate_implementation"):
                warnings.warn("Method 'generate_implementation()' not found.")
            elif not callable(self.nocobject_ref.codemodel.generate_implementation):
                warnings.warn("Attribute 'generate_implementation()' not callable")
            else:
                implementation = self.nocobject_ref.codemodel.generate_implementation()
            ##except:
                ### Report a warning instead of the exception
                ##exctype, value = exc_info()[:2]
                ##warnings.warn("%s: %s" % (exctype, value))
            if isinstance(implementation, str):
                self.implementation = implementation

    def model_hash(self):
        """
        Calculate a hash string based on the nocobject interface: Generics, 
        ports and external signals. 
        
        Two nocobject with the same model hash can be instantiated by the same
        module code (with different generics' values).
        
        Returns: a string with a predefined format.
        """
        hash_str = ""
        
        # 1. Generics information
        hash_gen = []
        for g in self.generics:
            hash_gen.append([g["name"], g["type"]])
        # sort generics by name
        hash_gen.sort(key = lambda x: x[0])
        # add a stream of "<name><type>"
        for g in hash_gen:
            hash_str += "%s%s" % (g[0], g[1])
            
        # 2. Ports information
        hash_port = []
        for g in self.ports:
            hash_port.append([g["name"], g["type"], len(g["signal_list"])])
        # sort ports by name
        hash_port.sort(key = lambda x: x[0])
        # add a stream of "<name><type><num-of-signals>"
        for g in hash_port:
            hash_str += "%s%s" % (g[0], g[1])
            
        # 3. External ports information
        hash_ext = []
        for g in self.external_signals:
            hash_ext.append([g["name"], g["type"], g["direction"]])
        # sort external_signals by name
        hash_ext.sort(key = lambda x: x[0])
        # add a stream of "<name><type><direction>"
        for g in hash_ext:
            hash_str += "%s%s" % (g[0], g[1])
            
        self.interface_hash = hash_str
        return hash_str
    
class noc_codegen_ext():
    """
    Extension class for code generator
    
    This class supports an access point to do transformations on a 
    'noc_codegen_base' code model.
    
    This transformation methods should be declared on extended classes of this 
    class, and are close related to the particular noc object.
        
    Notes:
    * This object maintains the code model and use it to generate code. Any
      particular changes or adjustments to the model should be done by a 
      'noc_codegen_ext' object. Usually this object is related to a particular 
      nocobject (router, ipcore or channel).
    """
    
    def __init__(self, codegen_ref):
        # must be related to a noc_codegen_base object
        if not isinstance(codegen_ref, noc_codegen_base):
            raise TypeError("Argument must be an instance of 'noc_codegen_base' class")
        
        self.codegen_ref = codegen_ref
        self.nocobject_ref = codegen_ref.nocobject_ref

# helper structures:
# base objects for generics, ports and signals
_empty_generic = {
    "class": "generic", 
    "name": "", 
    "type": "", 
    "type_array": [None, None],
    "default_value": "",  
    "current_value": "", 
    "description": ""}
_empty_port = {
    "class": "port", 
    "name": "",  
    "type": "",
    "nocport": None,
    "signal_list": [],
    "description": ""}
_empty_signal = {
    "class": "signal", 
    "name": "",  
    "type": "",  
    "type_array": [None, None],
    "direction": "",
    "default_value": "",  
    "related_generics": [], 
    "description": ""}

# new structures generation
def get_new_generic(**kwargs):
    s = deepcopy(_empty_generic)
    s.update(kwargs)
    return s
def get_new_port(**kwargs):
    s = deepcopy(_empty_port)
    s.update(kwargs)
    return s
def get_new_signal(**kwargs):
    s = deepcopy(_empty_signal)
    s.update(kwargs)
    return s
