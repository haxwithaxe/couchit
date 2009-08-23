function (doc) {
    if (doc.itemType == "page" && (!doc.is_spam || doc.title == "Home")) {
        emit(doc.site, doc);
    }
}
