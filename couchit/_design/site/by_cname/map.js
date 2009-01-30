function (doc) {
    if (doc.itemType == "site") {
        emit(doc.cname, doc);
    }
}