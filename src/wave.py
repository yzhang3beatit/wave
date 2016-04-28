import sys
import os
import re
from types import MethodType

class DxMmlItem:

    def __str__(self):
        tmp = ",".join(sorted([ "%s=%s" % (item, getattr(self, item)) for item in dir(self)
                                if not item.startswith("_") and getattr(self, item) != None and
                                    type(getattr(self, item)) is not MethodType ] ))
        for i in xrange(len(tmp)):
            if ord(tmp[i]) > 127:
                tmp = tmp.replace(tmp[i], " ")
        return tmp

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.__str__()
    
    def __getitem__(self, attribute):
        try:
            if not attribute.startswith("_") and getattr(self, attribute) != None and type(getattr(self, attribute)) is not MethodType:
                return getattr(self, attribute)       
        except:
                pass        
            
        return None    
    

class DxMmlDict(dict):
    
    def __init__(self,*args):
        dict.__init__(self,*args)
        self.ordered_keys = []
        
    def __str__(self):
        try:
            tmp = "\n".join([ key + ':' + str(self[key]) for key in self.ordered_keys ])
            for i in xrange(len(tmp)):
                if ord(tmp[i]) > 127:
                    tmp = tmp.replace(tmp[i], " ")
            return tmp
        except AttributeError:
            return ""

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.__str__()

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self,key)
        except:
            pass
        if type(key) == type(1):
            try:
                return dict.__getitem__(self, self.ordered_keys[key])
            except:
                pass
        return None

    def __setitem__(self, key, item):
        dict.__setitem__(self, key, item)
        try:
            if key in self.ordered_keys:
                self.ordered_keys.remove(key)
            self.ordered_keys.append(key)
        except AttributeError:
            self.ordered_keys = [key, ]

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.ordered_keys.remove(key)

    def __getattr__(self, name):
        if len(self) != 1:
            raise AttributeError
        return getattr(self.values()[0], name)

    def length(self):
        return len(self)

    def _get_empty_container(self):
        return DxMmlDict()

    def sort(self,*args):
        try:
            self.ordered_keys.sort(*args)
        except AttributeError:
            pass

class Patch(DxMmlItem):
    def __init__(self, diffs_list, index):
        self.patches = []
        self.patche = []
        self.function = None
        self.lineno = 0
        self.lasting = 0
        self._analysis(diffs_list[index:])

    def _analysis(self, list):
        for i, line in enumerate(list):
            if line.startswith('diff --git'):
                return
            if line.startswith('@@'):
                new_ = line.split('+')[1].split(',')
                self.lineno = int(new_[0])
                last_ = new_[1].split('@@')
                self.lasting = int(last_[0])
                        
                if last_[1]:
                    self.function = last_[1].strip()
                else:
                    self.function = list[i+1].strip()
            else:
                if line.startswith('+'):
                    if not self.patche:
                        self.patche.append(self.function)
                    self.patche.append(self.lineno)
                if self.lasting == 1:
                    if self.patche:
                        self.patches.append(self.patche)
                        self.patche = []
                if not line.startswith('-'):
                    self.lineno = self.lineno + 1
                    self.lasting = self.lasting - 1
  
    def _get_items(self):
        return self.patches


class Diffs(DxMmlDict):
    def __init__(self, diffs):
        self.filename = None
        self.path = None
        self.patch = False
        self.isEoF = False
        self.lineno = 0
        self._analysis(diffs)
        
    def _analysis(self, diffs):
        diffs_list = diffs.splitlines()
        for line in diffs_list:
            if line.startswith('@@') and self.isEoF:
                self.isEoF = False
                if self.filename.endswith('.c') or self.filename.endswith('.cpp'):
                    self.patch = Patch(diffs_list, self.lineno)
                    self[self.path] = self.patch._get_items()
            else:
                if line.startswith('diff --git'):
                    self.filename, self.path = self._get_filename(line)
                    self.isEoF = True
            self.lineno = self.lineno + 1
    
        
    
    def _get_filename(self, str_line):
        pattern = re.compile('diff\s--git\sa(.+)\sb(.+)')
        match = pattern.match(str_line)
        if match:
            return match.groups()[1].split('/')[-1], match.groups()[1]           
     
def print_list(lists):
    for list in lists:
        if type(list) == type([]):
            print_list(list)
        else:
            print list

def print_dict(dicts):
    for key, dict in dicts.items():
        print key       
        if type(dict) == type([]):
            print_list(dict)
        else:
            print dict
              
def read_diff(path):
    with open(path) as f:
        diff_ = f.read()
    diff = Diffs(diff_)
    
    return diff

def read_gcov(path):
    with open(path) as f:
        gcov_ = f.read()
    return gcov_

def translate_lineno(gcov_lines, no):
    for i, line in enumerate(gcov_lines):
        if no == int(line.split(':')[1]):
            break
    return i+1

def append_lines(lines, gcov_lines, show_nos, gcov_nos):
    for i, no in enumerate(show_nos):
        if no in gcov_nos:
            gcov_lines[no - 1]='+' + gcov_lines[no - 1][1:]

        lines.append(gcov_lines[no - 1])
    return lines

def append_linenos(nos, no, max):
    wide = 4
    no_ = no - wide
    for i in range(wide*2-1):
        no_ = no_ + 1
        if  no_ > 0 and not no_ in nos and no_ <= max:
            nos.append(no_)
    nos.sort()
    return nos
        

def fetch_lines(patch, gcov_lines):
    lines = []
    lineno_to_show = []
    lineno_in_gcov = []

    for no in patch:
        no = translate_lineno(gcov_lines, no)
        lineno_in_gcov.append(no)
        lineno_to_show = append_linenos(lineno_to_show, no, len(gcov_lines))
  
    lines = append_lines(lines, gcov_lines, lineno_to_show, lineno_in_gcov)
    
    return lines

def make_changed_gcov(patches, gcov):
    cgcov_ = []
    gcov_lines = gcov.splitlines()
    for i, patch in enumerate(patches):
        cgcov_.append(['\n@@\t' + patch[0].strip()])
        cgcov_[i].append(fetch_lines(patch[1:], gcov_lines))
    
    return cgcov_

def before_count(line):
    cov_words = filter(bool, line.split(' '))[1]
    return cov_words[:-1]

def count_covered(line):
    cov_words = before_count(line)
    if str.isdigit(cov_words):
        if int(cov_words) > 0:
            return True
    
    return False 

def count_changed(line):
    cov_words = before_count(line)
    if cov_words == '-':
        return False
    
    return True



def count_function_gcov(func):
    covered = 0
    changed = 0
    
    for line in func:
        if line.startswith('+'):
            if count_changed(line):
                changed = changed + 1
            if count_covered(line):
                covered = covered + 1
            
    return covered, changed

def count_gcov(cgcov):
    covered = 0
    changed = 0

    for block in cgcov:
        co_, cd_ = count_function_gcov(block[1:][0])            
        covered = covered + co_
        changed = changed + cd_
            
    return covered, changed

def fetch_gcov(patches, gcov_dir):
    covered = 0
    changed = 0
    gcovs = {}
    for path, patch in patches.items():
        filename = path.split('/')[-1]
        gcov_ = read_gcov(gcov_dir + '/' + filename + '.gcov')
        cgcov_ = make_changed_gcov(patch, gcov_)
        co_, cd_ = count_gcov(cgcov_)
        covered = covered + co_
        changed = changed + cd_

        gcovs[path] = ['\nUT Gcov:\t' + str(co_), 'Changed:\t' + str(cd_), cgcov_]
        
    return covered, changed, gcovs

def examine_ut_coverage(diff_path, gcov_dir):
    patches = read_diff(diff_path)
    co, cd, gcov = fetch_gcov(patches, gcov_dir)
    
    print 'Total covered:', co
    print 'Total changed:', cd
    print_dict(gcov)
    print
     

if __name__ == "__main__":
    pjd = r"T:\change_ut\test/"
    dfp = 'src'
    tst = 'tst/build'
    dfn = '/log.diff'
    
    if len(sys.argv) != 3:
        print 
        print 'Usage:'
        print sys.argv[0], '<diff filename> <gcov folder> '
        print
    else:
        examine_ut_coverage(sys.argv[1], sys.argv[2])
#        examine_ut_coverage(pjd + tst + dfn, pjd + tst)
