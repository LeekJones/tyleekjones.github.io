#!/usr/bin/env python

import lxml.etree as etree
import pandas as pd
import sys,os,importlib
from IPython.display import display
import jinja2

plugins_dir = "crif_parser_plugins"
assert(os.path.isdir(plugins_dir))

def dynamic_import(in_file):
    return importlib.import_module(in_file)

ignore_files = set(['__pycache__'])

#module_paths = [(plugins_dir + '/' + in_file) for in_file in os.listdir(os.path.abspath(plugins_dir))]
#module_import_names = [plugins_dir + '.' + in_file.split('.')[0] if in_file not in ignore_files else None for in_file in os.listdir(os.path.abspath(plugins_dir))]

#for module in module_import_names:
#    if module is not None:
#        dynamic_import(module)
from crif_parser_plugins.PcieRegPrinter import PcieRegPrinter
from crif_parser_plugins.Analyzer import Analyzer

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', 12)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.precision', 3)

def recursive_add(each):
    if len(each) == 0:
        return each.text
    new_dict = {}
    for item in each:
        if new_dict.get(item.tag) == None:
            new_dict[item.tag] = recursive_add(item)
        else:    
            if type(new_dict[item.tag]) == list:
                new_dict[item.tag].append(recursive_add(item))
            else:    
                temp = new_dict[item.tag]
                new_dict[item.tag] = []
                new_dict[item.tag].append(temp)
                new_dict[item.tag].append(recursive_add(item))
    return new_dict

def parse_xml(root):
    new_dict = {root.tag:{}}
    for each in root:
        if new_dict[root.tag].get(each.tag) == None:
            new_dict[root.tag][each.tag] = recursive_add(each)
        else:
            if type(new_dict[root.tag][each.tag]) == list:
                new_dict[root.tag][each.tag].append(recursive_add(each))
            else:    
                temp = new_dict[root.tag][each.tag]
                new_dict[root.tag][each.tag] = []#added
                new_dict[root.tag][each.tag].append(temp)
                new_dict[root.tag][each.tag].append(recursive_add(each))
    return  new_dict 

def print_item(str_item, indent_lvl):
    print('    '*indent_lvl + str_item)

def print_key_val(in_dict, key, indent_lvl):
    print('    '*indent_lvl + str(key) + ': ' + str(in_dict[key]))

def rec_print_tree(in_item, indent_lvl):
    if type(in_item) == dict:
        for each in in_item:
            if type(in_item[each]) == dict:
                print_item(each,indent_lvl)
                rec_print_tree(in_item[each], indent_lvl+1)
            elif type(in_item[each]) == list:
                for entry in in_item[each]:
                    print_item(each,indent_lvl)
                    rec_print_tree(entry, indent_lvl+1)
            else:
                print_key_val(in_item,each,indent_lvl)
    elif type(in_item) == list:
        for each in in_item:
            rec_print_tree(each, indent_lvl)
    else:
        print_item(in_item,indent_lvl)
                

def print_tree(in_dict):
    indent_lvl = 0
    
    rec_print_tree(in_dict,indent_lvl)

def quit():
    print("Thank you for using crif parser!")
    sys.exit(0)

def print_menu1(df,cur_dict):
   return select_dict

def viewer(df,orig_dict):
    dataset = pd.DataFrame(orig_dict)
    cur_dict = orig_dict
    prev_dicts = []
    prev_dfs = []
    columns = []
    df = pd.DataFrame.from_dict(orig_dict)
    while(True):
        df_for_html = df
        html = df_for_html.to_html(classes=["sortable"], index = False)

        template = jinja2.Template("""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit">
    <link href="https://fonts.googleapis.com/css2?family=Armata&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
    <link href="https://cdn.jsdelivr.net/npm/simple-datatables@latest/dist/style.css" rel="stylesheet" type="text/css">
    <script src="https://cdn.jsdelivr.net/npm/simple-datatables@latest" type="text/javascript"></script>
    <link rel="stylesheet" href="css/style.css">
    <title>Crif Crawler</title>
</head>

<body>
    <div class="wrapper d-flex align-items-stretch">
        <nav id="sidebar">
            <div class="p-4 pt-5">
                <a href="#" class="img logo rounded-circle mb-5" style="background-image: url(images/logo.jpg);"></a>
                <ul class="list-unstyled components mb-5">
                    <li class="active">
                        <a href="#homeSubmenu" data-toggle="collapse" aria-expanded="false"
                            class="dropdown-toggle">Home</a>
                        <ul class="collapse list-unstyled" id="homeSubmenu">
                            <li>
                                <a href="My_dashboard.html">My Dashboard</a>
                            </li>
                            <li>
                                <a href="My_Profile.html">My Profile</a>
                            </li>
                        </ul>
                    </li>
                    <li>
                        <a href="Register_view.html">Viewer</a>
                    </li>
                    <li>
                        <a href="#pageSubmenu" data-toggle="collapse" aria-expanded="false"
                            class="dropdown-toggle">Files</a>
                        <ul class="collapse list-unstyled" id="pageSubmenu">
                            <li>
                                <a href="My_files.html">My Files</a>
                            </li>
                            <li>
                                <a href="Upload.html">Upload</a>
                            </li>
                            <li>
                                <a href="Global.html">Global Files and Plugins</a>
                            </li>
                        </ul>
                    </li>
                    <li>
                        <a href="Plugins.html">Plugins</a>
                    </li>

                </ul>

                <div class="footer">
                    <p>
                        <!-- Link back to Colorlib can't be removed. Template is licensed under CC BY 3.0. -->
                        Copyright &copy;<script>
                            document.write(new Date().getFullYear());
                        </script> All rights reserved | This Website was made in collab with the PVAMU College of
                        Engineering Program <i class="icon-heart" aria-hidden="true"></i>
                    </p>
                </div>

            </div>
        </nav>

        <!-- Page Content  -->
        <div id="content" class="p-4 p-md-5">

            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <div class="container-fluid">

                    <button type="button" id="sidebarCollapse" class="btn btn-primary">
                        <i class="fa fa-bars"></i>
                        <span class="sr-only">Toggle Menu</span>
                    </button>



                </div>
            </nav>
            
            <div class="dt-buttons">
                <div class="dt-buttons btn-group">
                    <a class="btn btn-default buttons-copy buttons-html5" tabindex="0" aria-controls="example"
                        href="#"><span>Copy</span></a>
                    <a class="btn btn-default buttons-csv buttons-html5" tabindex="0" aria-controls="example"
                        href="#"><span>CSV</span></a>
                    <a class="btn btn-default buttons-excel buttons-html5" tabindex="0" aria-controls="example"
                        href="#"><span>Excel</span></a>
                    <a class="btn btn-default buttons-pdf buttons-html5" tabindex="0" aria-controls="example"
                        href="#"><span>PDF</span></a>
                    <a class="btn btn-default buttons-print" tabindex="0" aria-controls="example"
                        href="#"><span>Print</span></a>
                </div>
            </div>
            
            <div contenteditable class="table-responsive">
                {{dataframe}}
            </div>
        </div>

        <!--Register view-->
        
    </div>



    <script src="js/jquery.min.js"></script>
    <script src="js/popper.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <script src="js/main.js"></script>
    <script src="js/viewer.js"></script>
    <script defer type="text/javascript">
        let myTable = new simpleDatatables.DataTable("#myTable");
    </script>
</body>

</html>
""")
        output_html = template.render(dataframe=df.to_html(table_id="myTable"))
        
        # write generated html to file.
        with open("Register_view.html", "w", encoding="utf-8") as file_obj:
            file_obj.write(output_html)
        
        display(df)
        select_dict = {}
        print("Selectable options: ")
        options = "    " + "(q)uit, (b)ack, (p)rint tree, "
        if type(cur_dict) == dict:
            columns = df.columns.values
            for i,opt in enumerate(columns):
                select_dict[str(i)] = opt
                options += str(i) + ") " + str(opt) + " "
        elif type(cur_dict) == list:
            options += "row "
            for j in range(0,len(cur_dict)):
                select_dict[str(j)] = j
                options += str(j) + " "

        options = options[:-1]
        print(options)
        selection = input()
        if selection == 'q':
            quit()
        elif selection == 'b':
            if len(prev_dicts) > 0:
                cur_dict = prev_dicts.pop()
                df = prev_dfs.pop()
            else:
                print_start_menu(orig_dict)
        elif selection == 'p':
            print_tree(cur_dict)
        elif selection.isdigit():
            select_str = select_dict.get(selection)
            if select_str == None:
                print("Invalid number, please try again.")
            else:
                print("You selected " + str(select_str))
                prev_dicts.append(cur_dict)
                if type(cur_dict) == dict:
                    cur_dict = cur_dict[select_str]
                elif type(cur_dict) == list:
                    cur_dict = cur_dict[select_str]
                prev_dfs.append(df)
                try:
                    df = pd.DataFrame.from_dict(cur_dict)
                except ValueError:
                    print(str(select_str) + "= " + str(cur_dict))

def print_start_menu(orig_dict, tree, in_file):
    df = pd.DataFrame.from_dict(orig_dict)
    print("Would you like to (v)iew the crif data, (p)rint registers, (a)nalyze the data or (q)uit?")
    user_input = input()
    if user_input == 'v':
        viewer(df,orig_dict)
    elif user_input == 'q':
        quit()
    elif user_input == 'a':
        analyzer = Analyzer(in_file,[],[])
    elif user_input == 'p':
        print("Which format would you like to use for output?")
        p_opts = ""
        print("    (p)cie register file")
        format_input = input()

        if format_input == 'p':
            while True:
                print("(l)oad a config file, (q)uit, or (h)elp")
                uip = input()
                if uip == 'l':
                    print("Enter the config file path: ")
                    cfg_path = input()
                    assert(os.path.isfile(cfg_path))
                    pcie_reg_printer = PcieRegPrinter(tree, in_file, cfg_path)
                    pcie_reg_printer.print_by_category() 
                    break
                elif uip == 'h':
                    PcieRegPrinter.cfg_help()
                elif uip == 'q':
                    quit()
                else:
                    print('Invalid input!')
    else:
        print("Error, please try again!")
        print_start_menu(orig_dict)

def main():
    in_file = sys.argv[1]
    assert(os.path.isfile(in_file))
    with open(in_file,"r") as f:
        parser = etree.XMLParser()
        tree = etree.parse(f,parser)
    root = tree.getroot()
    orig_dict = parse_xml(root)
    df = pd.DataFrame.from_dict(orig_dict)
#display(df)
    print_start_menu(orig_dict, tree, in_file)

if __name__ == "__main__":
    main()
