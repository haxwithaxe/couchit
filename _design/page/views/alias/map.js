function(doc) {
    if (doc.itemType == 'alias_page')
        emit([doc.site, doc.title.toLowerCase().replace(/ /g, "_")], doc);
}