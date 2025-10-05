import re
import os
import sys

class c_struct_analyser:
     
    def __init__(self):
            self.__c_files=[]
            self.__c_structs={} # __c_structs element: struct_name:[members] 
            self.__string_expd =''


    def __list_all_files(self,base_dir):
        if os.path.isdir(base_dir) is False:
            return 
        else:
            for file_name in os.listdir(base_dir):
                abs_path=os.path.join(base_dir,file_name)
                if os.path.isfile(abs_path) and re.match(r'^\w+\.[ch]$',file_name) is not None:
                     self.__c_files.append(abs_path)
                elif os.path.isdir(abs_path):
                     self.__list_all_files(abs_path)
                else:
                     pass 
    
    def __remove_comment_strings(self,file_strings):
        patterns=( r'/\*[\s\S]*?\*/', r'//.*\n')
        for pattern in patterns:
            file_strings = re.sub(pattern=pattern,string=file_strings,repl='')
        return file_strings

    def __extract_a_file_c_structures(self,file_path):
        file_content = ""
        with open(file_path,mode='r',encoding='utf-8') as file:
            for line in file:
                file_content += line 

        file_content = self.__remove_comment_strings(file_content)    # remove all comment strings 

        c_struct_pattern=[  (r'struct\s+(\w+)\s*\{([\s\S]*?)\}\s*;'             ,0),
                            (r'typedef\s+struct\s*\{([\s\S]*?)\}\s*(\w+)\s*;'   ,1)
                         ]
        for sct_pattern in c_struct_pattern:
            matched_struct_list = re.findall(pattern=sct_pattern[0],string=file_content)
            for struct_info in matched_struct_list:
                s_name = struct_info[sct_pattern[1]]
                s_member_str = struct_info[1-sct_pattern[1]]                 
                s_member = self.__extract_struct_members(s_member_str)
                if s_name in self.__c_structs.keys():
                    print(f'c type struct [{s_name}] in file [{file_path}] already recorded before, skip record this class.')
                else:
                    if s_member is not None:
                        self.__c_structs[s_name] = s_member
                    else:
                        print(f'extract member string of struct [{s_name}] in file [{file_path}] failed, skip record this class.')
        
    def __extract_struct_members(self,struct_member_str):
        s_member=[]
        members = str(struct_member_str).split(';')
        for member_line  in members:
            member_line = re.sub(pattern= r'\s+',string=member_line,repl=' ')
            member_line = str(member_line).strip()
            if len(member_line) !=0:
                if re.match(pattern=r'[\w\[\] :]+',string=member_line) is not None:
                    s_member.append(member_line)
                else:                    
                    return None
        return s_member

    def __extract_struct(self,base_dir):
        self.__list_all_files(base_dir=base_dir)
        for file in self.__c_files:
            self.__extract_a_file_c_structures(file_path=file)
    
    def  __expend_struct_recuresive(self,struct_name,expend_level ): 
        mm_prefix = '\t' * expend_level 
        brc_prefix = '\t' * (expend_level-1)
        if struct_name not in self.__c_structs.keys():
            return 'baseType'
        

        self.__string_expd += brc_prefix + 'struct\n' + brc_prefix +'{\n' 
        member_list = self.__c_structs[struct_name]
        for member_string in member_list:
            re_res = re.findall(r'\w+',member_string)
            if len(re_res) == 0:
                print(f'member {member_string} extract failed')
                os._exit(1)
            type_word = re_res[0]
            if type_word == struct_name:    # prevent expending struct endlessly by expending the same struct
                continue 
            rest_word = member_string[str(member_string).index(type_word)+len(type_word):]
            ret_type = self.__expend_struct_recuresive(struct_name=type_word,expend_level = expend_level+1)
            if ret_type == 'baseType':
                self.__string_expd += mm_prefix + member_string +';\n'
            else:
                self.__string_expd +=   rest_word +';\n'
                
        self.__string_expd += brc_prefix +  '} '
        return 'classType'
            
 
        pass

    def analyse_a_struct(self,base_dir,struct_name):
        self.__extract_struct(base_dir=base_dir)
        self.__string_expd += 'typedef '
        self.__expend_struct_recuresive(struct_name=struct_name,expend_level=1)
        self.__string_expd += struct_name + ';'
        return self.__string_expd
 

    

analyser = c_struct_analyser() 
if sys.argv[1] == '?':
    print('''
arg1    :   base directory to search the struct informatin
arg2    :   struct name to be searched        
''')
else:    
    res = (analyser.analyse_a_struct(base_dir=sys.argv[1],struct_name=sys.argv[2]))
    print('\noutput struct:>>\n')
    print(res)
