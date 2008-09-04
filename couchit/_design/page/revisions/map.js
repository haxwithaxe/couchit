function(doc) {
    if (doc.itemType == "revision") {
        emit([doc.parent, doc.updated], doc);
    }
}