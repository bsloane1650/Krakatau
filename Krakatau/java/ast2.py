from . import ast
from .stringescape import escapeString as escape

class MethodDef(object):
    def __init__(self, class_, flags, name, retType, paramDecls, body):
        self.flagstr = flags + ' ' if flags else ''
        self.retType, self.paramDecls = retType, paramDecls
        self.body = body
        self.comment = None

        if name == '<clinit>':
            self.isStaticInit, self.isConstructor = True, False
            self.name=''
        elif name == '<init>':
            self.isStaticInit, self.isConstructor = False, True
            self.name = ast.TypeName((class_.name, 0))
        else:
            self.isStaticInit, self.isConstructor = False, False
            self.name = escape(name)

    def fullName(self):
        return str(self.name)+str(map(lambda x:x.print_(),self.paramDecls))

    def print_(self):
        argstr = ', '.join(decl.print_() for decl in self.paramDecls)
        if self.isStaticInit:
            header = 'static'
        elif self.isConstructor:
            name = self.name.print_().rpartition('.')[-1]
            header = '{}{}({})'.format(self.flagstr, name, argstr)
        else:
            header = '{}{} {}({})'.format(self.flagstr, self.retType.print_(), self.name, argstr)

        if self.comment:
            header = '//{}\n{}'.format(self.comment, header)

        if self.body is None:
            return header + ';\n'
        else:
            return header + '\n' + self.body.print_()

class FieldDef(object):
    def __init__(self, flags, type_, name, expr=None):
        self.flagstr = flags + ' ' if flags else ''
        self.type_ = type_
        self.name = escape(name)
        self.expr = None if expr is None else ast.makeCastExpr(type_.tt, expr) 

    def print_(self):
        if self.expr is not None:
            return '{}{} {} = {};'.format(self.flagstr, self.type_.print_(), self.name, self.expr.print_()) 
        return '{}{} {};'.format(self.flagstr, self.type_.print_(), self.name)

class ClassDef(object):
    def __init__(self, flags, isInterface, name, superc, interfaces, fields, methods):
        self.flagstr = flags + ' ' if flags else ''
        self.isInterface = isInterface
        self.isEnum= superc == 'java/lang/Enum'
        self.name = ast.TypeName((name,0))
        self.super = ast.TypeName((superc,0)) if superc is not None else None
        self.interfaces = [ast.TypeName((iname,0)) for iname in interfaces]
        self.fields = fields
        self.methods = methods
        if superc == 'java/lang/Object':
            self.super = None
        if self.isEnum:
            self.super = None;
            blacklist=["values[]","valueOf['String s']","TypeName "+self.name.print_()+"['String s', 'int i']"]
            self.methods=filter(lambda x:not x.fullName() in blacklist,self.methods)
            self.enumElements=filter(lambda x:x.type_.print_()==self.name.print_(),self.fields)
            self.fields=filter(lambda x:not x in self.enumElements,self.fields)
            self.fields=filter(lambda x:x.name!='$VALUES',self.fields)
            self.flagstr=self.flagstr.replace('final ','')

    def print_(self):
        contents = ''
        if self.isEnum:
            contents += ','.join(x.name for x in self.enumElements)+';'
        if self.fields:
            contents += '\n'.join(x.print_() for x in self.fields)
        if self.methods:
            if contents:
                contents += '\n\n' #extra line to divide fields and methods
            contents += '\n\n'.join(x.print_() for x in self.methods)

        if self.isEnum:
            #Remove the assignments in the static{} block
            newContents=[]
            blacklist=['new '+self.name.print_()+'(', '$VALUES =']
            for x in self.enumElements:
                blacklist.append(x.name+' =')
            for line in contents.split('\n'):
                works=True
                for x in blacklist:
                    works = works and not x in line
                if works:
                    newContents.append(line)
            contents='\n'.join(newContents)

        indented = ['    '+line for line in contents.splitlines()]
        name = self.name.print_().rpartition('.')[-1]
        if self.isInterface:
            defname='interface'
        elif self.isEnum:
            defname='enum'
        else:
            defname='class'
        header = '{}{} {}'.format(self.flagstr, defname, name)

        if self.super:
            header += ' extends ' + self.super.print_()
        if self.interfaces:
            if self.isInterface:
                assert(self.super is None)
                header += ' extends ' + ', '.join(x.print_() for x in self.interfaces)
            else:
                header += ' implements ' + ', '.join(x.print_() for x in self.interfaces)

        lines = [header + ' {'] + indented + ['}']
        return '\n'.join(lines)
