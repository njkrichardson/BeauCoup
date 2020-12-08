from os.path import dirname, abspath
import sys 

src_path = dirname(dirname(abspath(__file__))) 
sys.path.insert(0, src_path)
