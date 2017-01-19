from svgpathtools import svg2paths2
paths, attributes, svg_attributes = svg2paths2('freesample.svg')

for path in paths:
	print(path)
#print(paths)

#for k in len(range(attributes)):
#    print(attributes[k]['d'])