import wikipedia

print wikipedia.summary("Wikipedia")
print wikipedia.search("Barack")
ny = wikipedia.page("New York")
print ny.title
print  ny.url
print ny.content

print 
#wikipedia.set_lang("fr")
#print wikipedia.summary("Facebook", sentences=1)