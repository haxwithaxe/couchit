function (doc) {
    if (doc.itemType == "page" && (typeof doc.is_spam != "undefined" && doc.is_spam) {
        emit(doc.site, doc);
    }
}
