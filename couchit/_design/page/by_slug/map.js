function (doc) {
    if (doc.itemType == 'page') {
        emit([doc.site, doc.title.toLowerCase().replace(/ /g, "_")], doc);
    }
}
