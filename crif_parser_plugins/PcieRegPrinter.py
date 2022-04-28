from os.path import basename
from datetime import datetime
import math,sys,os,pdb
from lxml import etree as etree

class PcieRegPrinter(object):
    menu_entry_location = "p"

    def __init__(self,tree,parse_file,cfg_file):
        self.test_card_name = ""
        self.hex_set = {}
        self.parse_file = parse_file
        #Stores a copy of the configs
        self.config_vals = {}
        #Tuple: ("register_category_name", [offsetlb, offset_up])
        self.register_range_cache = None
        #Stores the macro functions used in arden_registers.h
        self.macro_dict = {}
        self.category_print = {}
        self.final_print = {}
        self.tree = tree
        self.register_base_address = {}
        self.register_file = []
        self.add_config_file(cfg_file)

    def add_register_range(self,index,line):
        s_line = line.split()
        key = s_line[0].strip()
        vals = s_line[1].strip()
        self.macro_dict[key] = s_line[2].strip()
        base_address = s_line[3].strip()

        for register in s_line[4].strip().split(','):
            register = register.strip()
            assert(register.isnumeric())
            register = int(register)
            self.register_file.append(register)
            self.register_base_address[register] = base_address

        assert(':' in vals)
        s_vals = vals.split(':')
        val_list = []
        for hex_val in s_vals:
            val_list.append(int(hex_val,16))

        self.config_vals[key] = val_list
                       

    def calculate_extended(self,in_hexval):
        if (in_hexval < 0x2000 and in_hexval > 0x10FF) or (in_hexval < 0x1000 and in_hexval > 0x00FF):
            return True
        return False

    def get_hex_offset(self,index,item):

        hex_val = None
        hex_val = item.findtext('addressOffset').split('\'')[1].lstrip('h')
        mask_len = len(self.register_base_address[index][2:])

        if len(hex_val) > mask_len:
            hex_val = hex_val[-mask_len:]
            return int('0x'+hex_val,16)
        elif len(hex_val) == mask_len:
            return int('0x'+hex_val,16)

        hex_val = int('0x'+hex_val,16)
        base_val = int(self.register_base_address[index],16)
        hex_val = hex_val | base_val

        return hex_val

    def get_description(self,item):
        description = item.findtext('description').replace('\n','')
        description = description.replace('\\','')
        return description

    def get_byte_size(self,item):    
            return int(item.findtext('size'))//8

    def add_to_hex_set(self,hex_val,extended_str,non_extended_str,cur_lvl,key=None):
        extended = self.calculate_extended(hex_val)
        if key == None:
            if extended:
                final_prt_str = "\t"*cur_lvl + self.macro_dict[self.register_range_cache[0]] + extended_str
            else:
                final_prt_str = "\t"*cur_lvl + self.macro_dict[self.register_range_cache[0]] + non_extended_str
            final_key = self.register_range_cache[0]

        else:
            if extended:
                final_prt_str = "\t"*cur_lvl + self.macro_dict[key] + extended_str
            else:
                final_prt_str = "\t"*cur_lvl + self.macro_dict[key] + non_extended_str
            final_key = key

        if self.hex_set.get(hex_val) == None:
            self.hex_set[hex_val] = (final_prt_str,final_key)

    def print_arden_format(self,index,item,cur_lvl):

        if item.tag == 'register':
            hex_val = self.get_hex_offset(index,item)
            size = self.get_byte_size(item)

            description = self.get_description(item)
            extended_str = '(\"' + item.findtext('name').lower() + "\", " + hex(hex_val) + ", " + str(size) + ", " + \
                "0x10" + ", \"" + description + '\")'
            non_extended_str = '(\"' + item.findtext('name').lower() + "\", " + hex(hex_val) + ", " + str(size) + ", " + \
                "0" + ", \"" + description + '\")'

            final_key = ""
            final_prt_str = ""

            if self.register_range_cache:
                if hex_val >= self.register_range_cache[1][0] and hex_val <= self.register_range_cache[1][1]:
                    self.add_to_hex_set(hex_val,extended_str,non_extended_str,cur_lvl,None)

                else:
                    for key in self.config_vals:
                        if hex_val >= self.config_vals[key][0] and hex_val <= self.config_vals[key][1]:
                            self.register_range_cache = (key,[self.config_vals[key][0],self.config_vals[key][1]])

                            self.add_to_hex_set(hex_val,extended_str,non_extended_str,cur_lvl,key)

            else:
                for key in self.config_vals:
                    if hex_val >= self.config_vals[key][0] and hex_val <= self.config_vals[key][1]:
                        self.register_range_cache = (key,[self.config_vals[key][0],self.config_vals[key][1]])

                        self.add_to_hex_set(hex_val,extended_str,non_extended_str,cur_lvl,key)

    def rec_cat_print(self,index,register_file,cur_lvl,max_lvls):
        if cur_lvl < max_lvls:
            for item in register_file:
                self.print_arden_format(index,item,cur_lvl)
                self.rec_cat_print(index,item,cur_lvl+1,max_lvls)
        return

    def add_config_file(self,config_file):
        with open(config_file) as f:
            for i,line in enumerate(f):
                if len(line.split()) > 0:
                    if i == 0:
                        self.test_card_name = line.strip()
                    elif i == 1:
                        s_line = line.split()
                        assert(s_line[0].rstrip(':').strip().upper() == "CATEGORY")
                        assert(s_line[1].rstrip(':').strip().upper() == "RANGE")
                        assert(s_line[2].rstrip(':').strip().upper() == "ARDEN_MACRO")
                        assert(s_line[3].rstrip(':').strip().upper() == "TARGET_BASE")
                        assert(s_line[4].rstrip(':').strip().upper() == "REGISTER_FILES")
                    else:
                        self.add_register_range(i,line)

        for key in self.config_vals:
            self.category_print[key] = '\t/*\n\t *\n\t *\n\t * ' +  key.upper() + " Registers " + str(hex(self.config_vals[key][0])) + " - " + \
                    str(hex(self.config_vals[key][1])) + "\n\t *\n\t *\n\t */"
            self.final_print[key] = []

    def print_by_category(self):
        max_lvls=2

        title = " " + self.test_card_name + " Registers "
        parser_used = "Automatically Extracted Using: " + basename(__file__)
        file_parsed = "File parsed: " + self.parse_file
        parsed_date = "File parsed on: " + str(datetime.now())
        asterisks = (120 - math.floor(len(title)/2)) * '*'
        parser_space = (120 - math.floor(len(parser_used)/2)) * ' '
        file_parsed_space = (120 - math.floor(len(file_parsed)/2)) * ' '
        parsed_date_space = (120 - math.floor(len(parsed_date)/2)) * ' '
        print("/*\n *\n *\n " + asterisks + title + asterisks)
        print(" *" + parser_space + parser_used ) 
        print(" *" + file_parsed_space + file_parsed)
        print(" *" + parsed_date_space + parsed_date) 
        print(" */")
        register_files = self.tree.findall('registerFile')
        for i,rf in enumerate(register_files):
            if i in self.register_file:
                self.rec_cat_print(i,rf,1,max_lvls)
        for hex_key in self.hex_set:
            self.final_print[self.hex_set[hex_key][1]].append(self.hex_set[hex_key][0])
        for key in self.final_print:
            print(self.category_print[key])
            for reg_entry in self.final_print[key]:
                print(reg_entry)
            print("")

    @staticmethod
    def cfg_help():
        print("""Config File Def:
                    CardName
                    CATEGORY:   RANGE:                  ARDEN_MACRO:        TARGET_BASE:    REGISTER_FILES:
                    Core =      0xFFFFF:0xFFFFF         ARDEN_MASTER_REG    0x1000          1
                    Global =    0xFFFFF:0xFFFFF         ARDEN_MASTER_REG    0x2000          2,11
                    VM =        0xFFFFF:0xFFFFF         ARDEN_VM_MASTER_REG 0x3000          3
                    Target0 =   0xFFFFF:0xFFFFF         ARDEN_TARGET0_REG   0x4000          4,5,6
                    .
                    .
                    TargetN =   0xFFFFF:0xFFFFF         ARDEN_TARGETN_REG   0x8000          8
                    Misc_Reg0 = 0xFFFFFF:0xFFFFFF       ARDEN_MASTER_REG    0x9000          9
                    .
                    .
                    Misc_RegN = 0xFFFFFF:0xFFFFFF       ARDEN_MASTER_REG    0x100000        10""")

    @staticmethod
    def cmd_line_usage():
        print("Usage: python PcieRegPrinter.py config.cfg parse_file.txt")

    @staticmethod
    def menu_entry():
        return "(p)cie register print"
    
    


if __name__ == '__main__':
    argv = sys.argv[1:]
    if len(argv) < 2 :
        PcieRegPrinter.cmd_line_usage()
        PcieRegPrinter.cfg_help()
        sys.exit(0)
    assert(len(argv) == 2)
    cfg_file = argv[0]
    in_file = argv[1]
    assert(os.path.isfile(cfg_file))
    assert(os.path.isfile(in_file))

    with open(in_file,"r") as f:
        parser = etree.XMLParser()
        tree = etree.parse(f,parser)
    pcie_printer = PcieRegPrinter(tree, in_file, cfg_file)
    pcie_printer.print_by_category()
