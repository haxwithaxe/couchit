function(doc) {
  if (doc.itemType && doc.itemType == 'site')
       emit([doc._id, doc.password], doc);
}