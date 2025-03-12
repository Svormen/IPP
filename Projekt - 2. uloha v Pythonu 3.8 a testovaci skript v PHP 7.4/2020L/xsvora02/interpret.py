# File: interpret.py
# Project: IPPcode21 
# Date: 3.4.2021
# Author: Slavomír Svorada - xsvora02

import sys
import getopt
import xml.etree.ElementTree as ET
import re

def main():
    # check number of arguments
    if len(sys.argv) == 3: 
        x, y = check_arguments()
    else:
        x, y = check_arguments()

    # find source path
    path = x

    # open file and check format
    if  y == True:
        tree = ET.ElementTree(file=sys.stdin)
    else:
        try:
            tree = ET.ElementTree(file=path)
        except IOError:
            errors.errors_msg(errors.err_file, "ERROR! problem with opening input file")
        except ET.ParseError:
            errors.errors_msg(errors.err_XML_str, "ERROR! wrong XML format in input file")

    if y == False:
        in_number = ""
    else:
        with open(x) as src:
            in_number = src.read()

    # root 
    root = tree.getroot()

    number_ins = Intpr.root_check(root)
    Intpr.do_intpr(root, in_number, number_ins)

    # Everything OK
    sys.exit(0)
    
# function for checking arguments
def check_arguments():
    src_inp_res = True
    
    # check number of arguments
    if ((len(sys.argv) < 2) or (len(sys.argv) > 4)):
        errors.errors_msg(errors.err_arg, "ERROR! wrong number of arguments")
    else:
        # use getopt and set for -source= and -input=
        try:    
            opts, args = getopt.getopt(sys.argv[1:], "", ['help', 'source=', 'input='])
        except:
            errors.errors_msg(errors.err_arg, "ERROR! wrong arguments")

        # check -source= and -input= and put next argument to variable arg_src and arg_inp from arg
        if len(sys.argv) == 2:
            opts = opts[0]
            opt,arg = opts

            if opt in ['--help']:
                print("Skript interpret.py načte XML reprezentaci programu.")
                print("Tento program s využitím vstupu dle parametrů příkazové řádky interpretuje a generuje výstup.")
                print("Vstupní XML reprezentace je např. generována skriptem parse.php. ze zdrojového kódu v IPPcode21.")
                sys.exit(0)
            if opt in ['--source']:
                arg_src = arg
                src_inp_res = False
                return arg_src, src_inp_res
            elif opt in ['--input']:
                arg_inp = arg
                return arg_inp, src_inp_res

        elif len(sys.argv) == 3:
            for opt, arg in opts:
                if opt in ['--source']:
                    arg_src = arg
                elif opt in ['--input']:
                    arg_inp = arg
            return arg_src, arg_inp
        else:
            errors.errors_msg(errors.err_arg, "ERROR! wrong arguments")

# class for errors
class errors:

    # chýbajúci parameter skriptu alebo použitie zakázanej kombinácie parametrov
    err_arg = 10
    # chyba pri otváraní vstupných súborov
    err_file = 11
    # chyba pri otvorení výstupných súborov pre zápis
    err_op_wr = 12
    # interná chyba
    err_intern = 99
    # chybný XML formát vo vstupnom súbore
    err_XML_str = 31
    # neočakávaná štruktúra XML či lexikálna alebo syntaktická chyba textových elementov a atribútov vo vstupnom XML súbore
    err_XML_sl = 32
    # rámec neexistuje
    err_frame_emp = 55
    # chýbajúca hodnota v premennej, na dátovom zásobníku alebo v zásobníku volania
    err_stack_emp = 56
    # zlá hodnota operandu
    err_oprd = 57
    err_cst = 59
    # var exist
    err_var_ex = 54
    # semantic error
    err_sem = 52
    # structure error
    err_str = 31
    # operand error
    err_t_oprd = 53
    # string error
    err_srg = 58
    # error exit
    err_exit = 42

    @staticmethod
    def errors_msg(type_error, messsage):
        print("{0}".format(messsage), file=sys.stderr)
        sys.exit(type_error)   

# class frames for storing values
class frames:
    
    # global
    global_frame = {}
    # stack
    stack_frame = []
    # local
    local_frame = None
    # temporary
    tf_frame = None
    
    @classmethod
    def give(cls, title):
        new_frame = cls.find_frames(title)
        
        # removing first 3 characters 
        title = title[3:]

        # check diplicity 
        if title in new_frame:
            errors.errors_msg(errors.err_XML_sl, "ERROR: '{0}' exist in frame".format(title))

        new_frame[title] = None
    
    @classmethod
    def formed(cls, title, t_value):
        new_frame = cls.find_frames(title)

        # removing first 3 characters 
        title = title[3:]

        # check diplicity 
        if title not in new_frame:
            errors.errors_msg(errors.err_var_ex, "ERROR: not exist '{0}' ".format(title))

        if type(t_value) == t_var:
            t_value = t_value.find_value()

        # value for frame
        new_frame[title] = t_value
    
    @classmethod
    def put(cls, title):
        new_frame = cls.find_frames(title)

        # removing first 3 characters 
        title = title[3:]

        # check diplicity 
        if title not in new_frame:
            errors.errors_msg(errors.err_var_ex, "ERROR: '{0}' not exist".format(title))
        
        type_res = new_frame[title]

        # compare 2 types
        if type(type_res) == type(None):
            errors.errors_msg(errors.err_stack_emp, "ERROR: missing value in variable")

        return type_res

    @classmethod
    def find_frames(cls, title):

        # found GF@
        if title[:3] == "GF@":
            new_frame = cls.global_frame

        # found LF@
        elif title[:3] == "LF@":
            new_frame = cls.local_frame

        # found TF@
        elif title[:3] == "TF@":
            new_frame = cls.tf_frame

        # incorrect prefix 
        else:
            errors.errors_msg(errors.err_XML_sl, "ERROR: Wrong prefix in frame")

        # if it is None
        if new_frame is None:
            errors.errors_msg(errors.err_frame_emp, "ERROR: Wrong access")

        # return outcome
        return new_frame
         

# class for stack
class d_stack:
    def __init__(self):
        self.stack = []

    # empty stack
    def empty(self):
        return self.stack == []
    
    # push to stack
    def push(self, item):
        self.stack.append(item)

    # pop from stack
    def pop(self):
        if len(self.stack) == 0:
            errors.errors_msg(errors.err_stack_emp, "ERROR! stack is empty")
        
        return self.stack.pop()
    
    # get stack
    def get(self):
        return self.stack
# TODO coments
class M_lbl:
    m_lbl = {}

    @classmethod
    def give(cls, title):
        title = str(title)

        if title in cls.m_lbl:
            errors.errors_msg(errors.err_sem, "ERROR! '{0}' exist".format(title))
        cls.m_lbl[title] = Intpr.instr_cnt

    @classmethod
    def jmp(cls, title):
        title = str(title)

        if title not in cls.m_lbl:
            errors.errors_msg(errors.err_sem, "ERROR! '{0}' not exist".format(title))
        Intpr.instr_cnt = cls.m_lbl[title]

# class for label type
class t_label:
    def __init__(self, title):
        self.title = title

    # for a string representation
    def __str__(self):
        return self.title

# class for symb
class t_symb:
    pass

# class for var type
class t_var:
    def __init__(self, title):
        self.title = title
    
    # found stored value
    def find_value(self):
        return frames.put(self.put_title())
    
    # return title
    def put_title(self):
        return self.title

    # overwrite value
    def formed_value(self, t_value):
        frames.formed(self.put_title(), t_value)

    def type_value(self, get_type):
        # find stored value
        t_value = self.find_value()
        # compare with str
        if type(t_value) == get_type:
            return t_value
        else:
            errors.errors_msg(errors.err_arg, "ERROR! Wrong type")
        # return outcome
        

    # int stored
    def __int__(self):
        return self.type_value(int)

    # bool stored
    def __bool__(self):
        return self.type_value(bool)

    # str stored
    def __str__(self):
        return self.type_value(str)
 

# class for interpret
class Intpr():
    instr_cnt = 1
    v_data_stack = d_stack()
    c_data_stack = d_stack()
    instr_in = ""

    @staticmethod
    def root_check(root):
        # check if there is program
        if root.tag != "program":
            errors.errors_msg(errors.err_XML_sl, "ERROR! problem with root")

        # check allowed attributes
        for attr in root.attrib:
            if attr not in ["name", "description", "language"]:
                errors.errors_msg(errors.err_arg, "ERROR! Wrong attribute elements")

        # check 'language' attribute
        if "language" not in root.attrib:
            errors.errors_msg(errors.err_arg, "ERROR! Missing 'language' attribute")

        # check if 'language' attribute contains 'IPPCODE21'
        if str(root.attrib["language"]).upper() != "IPPCODE21":
            errors.errors_msg(errors.err_XML_sl, "ERROR! Missing IPPCODE21")

        # Check instructions
        numbers_ins = []
        for sub_root in root:
            # check name of element
            if sub_root.tag != "instruction":
                errors.errors_msg(errors.err_XML_sl, "ERROR! Wrong name element instruction")

            # check 'opcode' attribute
            if "opcode" not in  sub_root.attrib:
                errors.errors_msg(errors.err_XML_sl, "ERROR! Missing 'opcode' attribute")
             
            # check 'order' attribute
            if "order" not in  sub_root.attrib:
                errors.errors_msg(errors.err_XML_sl, "ERROR! Missing 'order' attribute")
            else:
                if sub_root.attrib["order"] not in numbers_ins:
                    numbers_ins.append(sub_root.attrib["order"])
                else:
                    errors.errors_msg(errors.err_XML_sl, "ERROR! Duplicit 'order' attribute")

            if sub_root.attrib["order"] == "0":
                errors.errors_msg(errors.err_XML_sl, "ERROR! Negative or zero 'order' attribute")

            
        return numbers_ins     

    @classmethod
    # loading instructions from file
    def do_intpr(cls, root, instr_get, number_ins):
        
        cls.instr_in = instr_get
        # find all   
        find_instr = root.findall("./")
        instr_len = len(find_instr)

        check_ins = number_ins.copy()
        check_ins.sort()

        cls.do_label(find_instr)
        cls.instr_cnt = 1

        # go throught whole cycle
        while cls.instr_cnt <= instr_len:
            #do_instr = find_instr[cls.instr_cnt-1]
            do_instr = find_instr[number_ins.index(check_ins[cls.instr_cnt-1])]
            # skipping
            if do_instr.attrib["opcode"].lower() == "label":
                cls.instr_cnt = cls.instr_cnt + 1
                continue
            
            # process instructions
            get_instr = Instr(do_instr)
            get_instr.hang_fnc()

            # increase
            cls.instr_cnt = cls.instr_cnt + 1
    
    @classmethod
    def do_label(cls, find_instr):
        for lbl in find_instr:
            if lbl.attrib["opcode"].lower() == "label":
                cls.instr_cnt = int(lbl.attrib["order"])
                get_instr = Instr(lbl)
                get_instr.hang_fnc()


    @staticmethod
    def type_values(type_xml, value_xml, res):
        # integer or boolean or string type
        if type_xml == "int" or type_xml == "bool" or type_xml == "string":

            # check integer type
            if type_xml == "int": 
                if (not re.search(r"^[+-]?\d+$$", value_xml) and res == True) or value_xml is None:
                    errors.errors_msg(errors.err_XML_sl, "ERROR! Wrong integer value")
                else:
                    return int(value_xml)

            # check boolean type
            elif type_xml == "bool":
                if not value_xml in ["true", "false"] or value_xml is None:
                    errors.errors_msg(errors.err_XML_sl, "ERROR! Wrong boolean value")
                elif value_xml == "true":
                    bool_res = True
                elif value_xml == "false":
                    bool_res = False
                else:
                    if res == False:
                        return False
                    else:
                        errors.errors_msg(errors.err_XML_sl, "ERROR! Wrong boolean value ({})".format(value_xml))
                return bool_res
            
            # check string type
            elif type_xml == "string":
                if value_xml is None:
                    value_xml = ""
                if re.search(r"(?!\\[0-9]{3})[\s\\#]", value_xml):
                    if res == False:
                        return ""
                    else:
                        errors.errors_msg(errors.err_XML_sl, "ERROR! Wrong string value")
                
                seq = re.findall(r"\\([0-9]{3})", value_xml)
                seq = list(set(seq))

                for sq in seq:
                    if sq == "092":
                        value_xml = re.sub("\\\\092", "\\\\", value_xml)
                        continue
                    value_xml = re.sub("\\\\{0}".format(sq), chr(int(sq)), value_xml)
                return value_xml

        # check nil type
        elif type_xml == "nil": 
            if not value_xml in ["nil"] or value_xml is None:
                errors.errors_msg(errors.err_XML_sl, "ERROR! Wrong nil value")
            return value_xml

        # check label type
        elif type_xml == "label":
            if not re.search(r"^[\w_\-$&%*][\w\d_\-$&%*]*$", value_xml) or value_xml is None:
                errors.errors_msg(errors.err_XML_sl, "ERROR! Wrong label value")
            return t_label(value_xml)

        # check type type
        elif type_xml == "type":
            if not re.search(r"^(int|string|bool|nil)$", value_xml) or value_xml is None:
                errors.errors_msg(errors.err_XML_sl, "ERROR! Wrong type value")
            return value_xml

        elif type_xml == "var":
            if not re.search(r"^(LF|TF|GF)@[\w_\-$&%*][\w\d_\-$&%*]*$", value_xml) or value_xml is None:
                errors.errors_msg(errors.err_XML_sl, "ERROR! Wrong var value")
            return t_var(value_xml)

        else:
            errors.errors_msg(errors.err_XML_sl, "ERROR! Wrong type argument ({})".format(type_xml))

class Instr():

    def __init__(self, instr):
        self.ins_code = instr.attrib["opcode"].upper()
        self.argmnt = self.get_args(instr)
        self.arguments_cnt = len(self.argmnt)

    def get_args(self, instr_arg):
        argmnt = [None] * len(instr_arg)
        for ins_argmnt in instr_arg:
            if ins_argmnt.tag[:3] != "arg":
                errors.errors_msg(errors.err_XML_sl, "ERROR! Missing arg")

            arg_idx = int(ins_argmnt.tag[3:])-1

            if len(argmnt) <= arg_idx:
                errors.errors_msg(errors.err_XML_sl, "ERROR! wrong range")

            if argmnt[arg_idx] != None:
                errors.errors_msg(errors.err_str, "ERROR! arg duplicated")

            # store argument value   
            argmnt[arg_idx] = Intpr.type_values(ins_argmnt.attrib["type"], ins_argmnt.text, True)
        
        for arg in argmnt:
            if arg is None:
                errors.errors_msg(errors.err_str, "ERROR! missing arg")

        return argmnt
    
    def args_check(self, *wanted_arguments):
        if self.arguments_cnt != len(wanted_arguments):
            errors.errors_msg(errors.err_XML_sl, "ERROR! wrong arg cnt")

        # convert to list
        wanted_arguments = list(wanted_arguments)
        number = 0
        for arg in self.argmnt:
            if wanted_arguments[number] == t_symb:
                wanted_arguments[number] = [int, bool, str, t_var]

            type_of_arg = type(arg)

            if type(wanted_arguments[number]) == type:
                if type_of_arg != wanted_arguments[number]:
                    errors.errors_msg(errors.err_t_oprd, "ERROR! Wrong type argument ({})".format(wanted_arguments[number]))
            elif type(wanted_arguments[number]) == list:
                if type_of_arg not in wanted_arguments[number]:
                    errors.errors_msg(errors.err_t_oprd, "ERROR! Wrong type argument ({})".format(wanted_arguments[number]))
            else:
                errors.errors_msg(errors.err_intern, "ERROR: wrong param.")
            number = number + 1
    # look at opcode and  
    def hang_fnc(self):
        if self.ins_code == "MOVE":
		        self.Move()
        elif self.ins_code == "CREATEFRAME":
		        self.Createframe()
        elif self.ins_code == "PUSHFRAME":
		        self.Pushframe()
        elif self.ins_code == "POPFRAME":
		        self.Popframe()
        elif self.ins_code == "DEFVAR":
	            self.Defvar()
        elif self.ins_code == "CALL":
		        self.Call()
        elif self.ins_code == "RETURN":
		        self.Return()
        elif self.ins_code == "PUSHS":
		        self.Pushs()
        elif self.ins_code == "POPS":
	        	self.Pops()
        elif self.ins_code == "ADD":
	            self.Add()
        elif self.ins_code == "SUB":
	        	self.Sub()
        elif self.ins_code == "MUL":
	            self.Mul()
        elif self.ins_code == "IDIV":
		        self.Idiv()
        elif self.ins_code == "LT":
	            self.Lt()
        elif self.ins_code == "GT":
                self.Gt()
        elif self.ins_code == "EQ":
                self.Eq()
        elif self.ins_code == "AND":
                self.And()
        elif self.ins_code == "OR":
	            self.Or()
        elif self.ins_code == "NOT":
		        self.Not()
        elif self.ins_code == "INT2CHAR":
		        self.Int2char()
        elif self.ins_code == "STRI2INT":
	            self.Str2int()
        elif self.ins_code == "READ":
	            self.Read()
        elif self.ins_code == "WRITE":
		        self.Write()
        elif self.ins_code == "CONCAT":
		        self.Concat()
        elif self.ins_code == "STRLEN":
                self.Strlen()	
        elif self.ins_code == "GETCHAR":
		        self.Getchar()
        elif self.ins_code == "SETCHAR":
	            self.Setchar()
        elif self.ins_code == "TYPE":
	            self.Type()		
        elif self.ins_code == "LABEL":	# Called from Interpret.__findLabels()
	            self.Label()
        elif self.ins_code == "JUMP":
		        self.Jump()
        elif self.ins_code == "JUMPIFEQ":
                self.Jumpifeq_jumpifneq(True)
        elif self.ins_code == "JUMPIFNEQ":
		        self.Jumpifeq_jumpifneq(False)
        elif self.ins_code == "DPRINT":
	            pass
        elif self.ins_code == "BREAK":
                pass
        elif self.ins_code == "EXIT":
                self.Exit()
        else:
                errors.errors_msg(errors.err_XML_sl, "ERROR: Wrong instruction")

    # check MOVE instr.
    def Move(self):
        self.args_check(t_var, t_symb)
        self.argmnt[0].formed_value(self.argmnt[1])

    # check CREATEFRAME instr.
    def Createframe(self):
        self.args_check()
        frames.tf_frame = {}

    # check PUSHFRAME instr.
    def Pushframe(self):
        self.args_check()
        if frames.tf_frame is None:
            errors.errors_msg(errors.err_frame_emp, "ERROR: withoput def of frame")
        frames.stack_frame.append(frames.tf_frame)
        frames.local_frame = frames.stack_frame[-1]
        frames.tf_frame = None

    # check POPFRAME instr.
    def Popframe(self):
        self.args_check()
        if frames.local_frame is None:
            errors.errors_msg(errors.err_frame_emp, "ERROR: withoput def of LF")
        frames.tf_frame = frames.stack_frame.pop()
        frames.local_frame = None

    # check DEFVAR instr.
    def Defvar(self):
        self.args_check(t_var)
        frames.give(self.argmnt[0].put_title())

    # check CALL instr.
    def Call(self):
        Intpr.c_data_stack.push(Intpr.instr_cnt)
        self.Jump()

    # check RETURN instr.
    def Return(self):
        self.args_check()
        Intpr.instr_cnt = Intpr.c_data_stack.pop()

    # check PUSHS instr.
    def Pushs(self):
        self.args_check(t_symb)
        Intpr.v_data_stack.push(self.argmnt[0])

    # check POPS instr.
    def Pops(self):
        self.args_check(t_var)
        tmp = Intpr.v_data_stack.pop()
        self.argmnt[0].formed_value(tmp)

    # check ADD instr.
    def Add(self):
        self.args_check(t_var, [int, t_var], [int, t_var])
        tmp = int(self.argmnt[1]) + int(self.argmnt[2])
        self.argmnt[0].formed_value(tmp)

    # check SUB instr.
    def Sub(self):
        self.args_check(t_var, [t_var, int], [t_var, int])
        tmp = int(self.argmnt[1]) - int(self.argmnt[2])
        self.argmnt[0].formed_value(tmp)

    # check MUL instr.
    def Mul(self):
        self.args_check(t_var, [int, t_var], [int, t_var])
        tmp = int(self.argmnt[1]) * int(self.argmnt[2])
        self.argmnt[0].formed_value(tmp)

    # check IDIV instr.
    def Idiv(self):
        self.args_check(t_var, [t_var, int], [t_var, int])

        if int(self.argmnt[2]) == 0:
            errors.errors_msg(errors.err_oprd, "ERROR: div by 0")
        
        tmp = int(self.argmnt[1]) // int(self.argmnt[2])
        self.argmnt[0].formed_value(tmp)

    # check LT instr.
    def Lt(self):
        self.args_check(t_var, t_symb, t_symb)
        if type(self.argmnt[1]) == t_var:
            tmp1 = self.argmnt[1].find_value
        else:
            tmp1 = self.argmnt[1]

        if type(self.argmnt[2]) == t_var:
            tmp2 = self.argmnt[2].find_value
        else:
            tmp2 = self.argmnt[2]

        if type(tmp1) != type(tmp2):
            errors.errors_msg(errors.err_t_oprd, "ERROR: dif types")

        tmp = tmp2 > tmp1
        self.argmnt[0].formed_value(tmp)

    # check GT instr.
    def Gt(self):
        self.args_check(t_var, t_symb, t_symb)
        if type(self.argmnt[1]) == t_var:
            tmp1 = self.argmnt[1].find_value
        else:
            tmp1 = self.argmnt[1]

        if type(self.argmnt[2]) == t_var:
            tmp2 = self.argmnt[2].find_value
        else:
            tmp2 = self.argmnt[2]

        if type(tmp1) != type(tmp2):
            errors.errors_msg(errors.err_t_oprd, "ERROR: dif types")

        tmp = tmp2 < tmp1
        self.argmnt[0].formed_value(tmp)

    # check EQ instr.
    def Eq(self):
        self.args_check(t_var, t_symb, t_symb)
        if type(self.argmnt[1]) == t_var:
            tmp1 = self.argmnt[1].find_value
        else:
            tmp1 = self.argmnt[1]

        if type(self.argmnt[2]) == t_var:
            tmp2 = self.argmnt[2].find_value
        else:
            tmp2 = self.argmnt[2]

        if type(tmp1) != type(tmp2):
            errors.errors_msg(errors.err_t_oprd, "ERROR: dif types")

        tmp = tmp2 == tmp1
        self.argmnt[0].formed_value(tmp)

    # check AND instr.
    def And(self):
        self.args_check(t_var, [t_var, bool], [t_var, bool])
        tmp = bool(self.argmnt[2]) and bool(self.argmnt[1])
        self.argmnt[0].formed_value(tmp)

    # check OR instr.
    def Or(self):
        self.args_check(t_var, [t_var, bool], [t_var, bool])
        tmp = bool(self.argmnt[2]) or bool(self.argmnt[1])
        self.argmnt[0].formed_value(tmp)

    # check NOT instr.
    def Not(self):
        self.args_check(t_var, [t_var, bool])
        tmp = not bool(self.argmnt[1])
        self.argmnt[0].formed_value(tmp)

    # check INT2CHAR instr.
    def Int2char(self):
        self.args_check(t_var, [t_var, int])
        tmp = int(self.argmnt[1])

        try:
            tmp1 = chr(tmp)
        except ValueError:
            errors.errors_msg(errors.err_srg, "ERROR: int2char problem")

        self.argmnt[0].formed_value(tmp1)

    # check STR2INT instr.
    def Str2int(self):
        self.Getchar()
        tmp = ord(self.argmnt[0].find_value())

        self.argmnt[0].formed_value(tmp)

    # check READ instr.
    def Read(self):
        self.args_check(t_var, str)
        if Intpr.instr_in != "":
            addmision = Intpr.instr_in
        else:
            addmision = input()
        addmision = addmision.lower()
        tmp = Intpr.type_values(self.argmnt[1], addmision, False)
        self.argmnt[0].formed_value(tmp)

    # check WRITE instr.
    def Write(self):
        self.args_check(t_symb)
        if type(self.argmnt[0]) != t_var:
            tmp = self.argmnt[0]
        else:
            tmp = self.argmnt[0].find_value()
        if type(tmp) == bool:
            if tmp != True:
                tmp = "false"
            else:
                tmp = "true"
        if tmp == "nil":
            print("", end="")
        else:
            print(str(tmp), end="")

    # check CONCAT instr.
    def Concat(self):
        self.args_check(t_var, [t_var, str], [t_var, str])
        tmp = str(self.argmnt[1]) + str(self.argmnt[2])
        self.argmnt[0].formed_value(tmp)

    # check STRLEN instr.
    def Strlen(self):
        self.args_check(t_var, [t_var, str])
        tmp = len(str(self.argmnt[1]))
        self.argmnt[0].formed_value(tmp)

    # check GETCHAR instr.
    def Getchar(self):
        self.args_check(t_var, [t_var, str], [t_var, int])
        tmp_s = str(self.argmnt[1])
        tmp_i = int(self.argmnt[2])

        if tmp_i >= len(tmp_s):
            errors.errors_msg(errors.err_srg, "ERROR: missing range (getchar)")
        
        tmp = tmp_s[tmp_i]
        self.argmnt[0].formed_value(tmp)

    # check SETCHAR instr.
    def Setchar(self):
        self.args_check(t_var, [t_var, int], [t_var, str])
        tmp_s = str(self.argmnt[0])
        tmp_i = int(self.argmnt[1])
        tmp_c = str(self.argmnt[2])

        if tmp_i >= len(tmp_s):
            errors.errors_msg(errors.err_srg, "ERROR: missing range (setchar)")
        if len(tmp_c) == 0:
            errors.errors_msg(errors.err_srg, "ERROR: missing character (setchar)")

        tmp = tmp_s[:tmp_i] + tmp_c[0] + tmp_s[tmp_i+1:]
        self.argmnt[0].formed_value(tmp)

    # check TYPE instr.
    def Type(self):
        self.args_check(t_var, t_symb)
        if type(self.argmnt[1]) != t_var:
            tmp = self.argmnt[1]
        else:
            tmp = self.argmnt[1].find_value()

        res_tmp = re.search(r"<class '(str|bool|int)'>", str(type(tmp))).group(1)

        if res_tmp != "str":
            tmp1 = res_tmp
        else:
            tmp1 = "string"

        self.argmnt[0].formed_value(tmp1)

    # check LABEL instr.
    def Label(self):
        self.args_check(t_label)
        M_lbl.give(self.argmnt[0])

    # check JUMP instr.
    def Jump(self):
        self.args_check(t_label)
        M_lbl.jmp(self.argmnt[0])

    # check JUMPIFEQ_JUMPIFNEQ instr.
    def Jumpifeq_jumpifneq(self, outcome):
        self.args_check(t_label, t_symb, t_symb)
        
        if type(self.argmnt[1]) == t_var:
            tmp1 = self.argmnt[1].find_value()
        else:
            tmp1 = self.argmnt[1]
        if type(self.argmnt[2]) != t_var:
            tmp2 = self.argmnt[2]
        else:
            tmp2 = self.argmnt[2].find_value()

        if type(tmp1) != type (tmp2):
            errors.errors_msg(errors.err_oprd, "ERROR: dif types")

        tmp = tmp1 == tmp2
        if tmp == outcome:
            M_lbl.jmp(self.argmnt[0])

    # check EXIT instr.
    def Exit(self):
        self.args_check(t_symb)
        if (int(self.argmnt[0]) > 0) and (int(self.argmnt[0]) < 49):
            sys.exit(int(self.argmnt[0]))
        else:
            errors.errors_msg(errors.err_exit, "ERROR: dif exit value")

# calling main function
main()
