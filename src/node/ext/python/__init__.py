from node.ext import directory
from nodes import (
    Module,
    Docstring,
    ProtectedSection,
    Import,
    Attribute,
    Decorator,
    Function,
    Class,
    Block,
)
from interfaces import Call


directory.file_factories['.py'] = Module


import parser
Docstring.parserfactory = parser.BaseParser
ProtectedSection.parserfactory = parser.BaseParser
Block.parserfactory = parser.BaseParser
Module.parserfactory = parser.ModuleParser
Import.parserfactory = parser.ImportParser
Attribute.parserfactory = parser.AttributeParser
Decorator.parserfactory = parser.DecoratorParser
Function.parserfactory = parser.FunctionParser
Class.parserfactory = parser.ClassParser


import renderer
Docstring.rendererfactory = renderer.DocstringRenderer
ProtectedSection.rendererfactory = renderer.ProtectedSectionRenderer
Block.rendererfactory = renderer.BlockRenderer
Module.rendererfactory = renderer.ModuleRenderer
Import.rendererfactory = renderer.ImportRenderer
Attribute.rendererfactory = renderer.AttributeRenderer
Decorator.rendererfactory = renderer.DecoratorRenderer
Function.rendererfactory = renderer.FunctionRenderer
Class.rendererfactory = renderer.ClassRenderer
