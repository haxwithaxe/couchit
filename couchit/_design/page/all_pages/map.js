function (doc) {
    if (doc.itemType == "page") {
        emit(doc.site, doc);
    }
}
