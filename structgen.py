from CStructParser.CStructParser import CStructParser
import pprint
import sys

# Initialize parser with structure definition
parser = CStructParser(sys.stdin.read(), endian='little', debug=True)

pprint.pprint(parser.struct_fields)
# print(parser.debug)
# print(parser.print_struct_tree("result"))