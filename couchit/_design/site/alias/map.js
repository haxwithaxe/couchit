function(doc) {
  if (doc.itemType && doc.itemType == 'site')
       emit(doc.alias, doc);
}