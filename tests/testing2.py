from collections import namedtuple

# make a basic Link class
Link = namedtuple('Link', ['id', 'submitter_id', 'submitted_time', 'votes',
						   'title', 'url'])

# list of Links to work with
links = [
	Link(0, 60398, 1334014208.0, 109,
		 "C overtakes Java as the No. 1 programming language in the TIOBE index.",
		 "http://pixelstech.net/article/index.php?id=1333969280")]


# links is a list of Link objects. Links have a handful of properties. For
# example, a Link's number of votes can be accessed by link.votes if "link" is a
# Link.

def build_link_index():
	index = {}
	for l in links:
		index[l.id] = l
	return index


link_index = build_link_index()
print link_index


def link_by_id(link_id):
	return link_index.get(link_id)


# QUIZ - implement the function add_new_link() that both adds a link to the
# "links" list and updates the link_index dictionary.
def add_new_link(link):
	links.append(link)
	link_index[link.id] = link

link_new = Link(10, 23944, 1333943632.0, 188,
		 "The LOVE game framework version 0.8.0 has been released - with GLSL shader support!",
		 "https://love2d.org/forums/viewtopic.php?f=3&amp;t=8750")
print add_new_link(link_new)
print link_index
