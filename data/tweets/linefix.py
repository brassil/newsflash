import sys
from os import path


def fix_newlines(fp):
	with open(fp, 'rU') as f:
		x = f.read()

	x = x.replace('],\n', '123456123456123456123456')
	x = x.replace('\n','\t')
	x = x.replace('123456123456123456123456', '],\n')

	name = path.splitext(fp)
	with open(name[0]+'_linefix'+name[1], 'w') as f:
		f.write(x)


if __name__ == '__main__':
	fix_newlines(sys.argv[1])