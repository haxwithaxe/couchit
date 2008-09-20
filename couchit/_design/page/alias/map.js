function(doc) {
    if (doc.itemType == 'aliaspage')
        emit([doc.site, doc.title.toLowerCase().replace(/ /g, "_"), doc);
}