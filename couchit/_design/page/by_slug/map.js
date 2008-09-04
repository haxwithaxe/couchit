function (doc) {
    if (doc.itemType == 'page') {
        emit([doc.site, doc.toLowerCase().title.replace(/ /g, "_")], doc);
    }
}
