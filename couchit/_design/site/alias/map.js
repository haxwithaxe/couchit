function(doc) {
  if (doc.itemType && doc.itemType == 'site')
    for (var i=0; i< doc.alias.length; i++)
       emit(doc.alias[i], doc);
}