function (doc) {
    if (doc.itemType == 'token') {
        emit([doc._id, doc.site], doc);
    }
}
