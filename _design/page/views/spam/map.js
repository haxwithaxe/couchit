function (doc) {
    if (doc.itemType == "page" && doc.is_spam) {
        emit(doc.site, doc);
    }
}
