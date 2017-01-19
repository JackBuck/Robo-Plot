from xml.dom import minidom

doc = minidom.parse("freesample.svg")  # parseString also exists
path_strings = [path.getAttribute('d') for path
                in doc.getElementsByTagName('path')]
				
print(path_strings)
path = path_strings[0]
splitPath = []
numbers = []
doc.unlink()
