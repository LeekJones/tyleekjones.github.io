#!/usr/bin/env python

import sys
import lxml.etree as etree
from os.path import exists

class Analyzer(object):
    
    def __init__(self,in_file,columns,ranges):
        self.tree = None

        parser = etree.XMLParser()
        assert(exists(in_file))
        with open(in_file) as f:
            try:
                self.tree = etree.parse(f,parser)
            except UnicodeDecodeError as ex:
                traceback.print_exc()
        register_files = self.tree.findall('registerFile')
        reg_file_dict = {}
        for i,register_file in enumerate(register_files):
            if i in columns or len(columns) == 0:
                reg_file_dict[i] = []
                reg_file_dict[i].append('/'.join(register_file.findtext('name').split('/')[-2:]))#[-20:])
                bar = register_file.findtext('bar')
                min = 0xFFFFFFFFFFFFFFFF
                max = -1 
                reg_count = 0
                for item in register_file:
                    if item.tag == "register":
                        if len(columns) != 0 or len(ranges) != 0:
                            if len(ranges) == 0 or (reg_count >= ranges[0] and reg_count < ranges[1]):
                                reg_file_dict[i].append(item.findtext("name") + " " + item.findtext("addressOffset"))
                        hex_val = '0x' + item.findtext("addressOffset").split('\'')[1].lstrip('h')
                        hex_val = int(hex_val,16)
                        if hex_val > max:
                            max = hex_val
                        if hex_val < min:
                            min = hex_val
                        reg_count += 1    
                if bar:
                    reg_file_dict[i].append("bar= " + bar)
                    bar_val = None
                    try:
                        bar_val = int(bar,16)
                    except ValueError as ex:
                        reg_file_dict[i].append("min,max= " + hex(min) + " " + hex(max))
                        reg_file_dict[i].append("Unparsable bar value.")
                    if bar_val != None:   
                        reg_file_dict[i].append("min,max= " + hex(min+int(bar,16)) + " " + hex(max+int(bar,16)))
                else:
                    reg_file_dict[i].append("min,max= " + hex(min) + " " + hex(max))
                reg_file_dict[i].append("")


        if len(columns) != 0 or len(ranges) != 0:
            i = 0
            while True:
                item_exists = False
                for j,key in enumerate(reg_file_dict):
                    p_line = ""
                    try:
                        p_line = reg_file_dict[key][i]
                        item_exists = True
                    except IndexError as ex:
                        pass
                    p_line_len = len(p_line)
                    print(p_line,end=" "*(30-p_line_len))
                if not item_exists:
                    break
                i += 1
                print("") #Needed for newline character
        else:
            for key in reg_file_dict:
                print(key,end="\t")
                for i,item in enumerate(reg_file_dict[key]):
                    if i == 0:
                        print(item)
                    else:    
                        print("\t"+(" "*(2-len(str(key))))+item)
            
    def usage(self):
        print("""python crif_analyzer.py in_file_name.xml <[column_numbers]> <[start:end]>""")

if __name__ == "__main__":
    columns = []
    ranges = []
    in_file = sys.argv[1]
    if len(sys.argv) > 2:
        columns = sys.argv[2].strip("[]")
        columns = columns.split(',')
        n_columns = []
        for string in columns:
            n_columns.append(int(string))
        columns = n_columns    
    if len(sys.argv) > 3:    
        ranges = sys.argv[3].strip("[]")
        ranges = ranges.split(":")
        assert(len(ranges) == 2)
        n_ranges = []
        for string in ranges:
            n_ranges.append(int(string))
        ranges = n_ranges    
    
    analyzer = Analyzer(in_file,columns,ranges)
