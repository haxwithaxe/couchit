function (doc) {
    if (doc.itemType == 'page') {
        emit([doc.site, doc.title.replace(/ /g, "_")], doc);
    }
}