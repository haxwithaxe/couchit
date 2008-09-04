function(doc) {
    if (doc.itemType == "page") {
        emit([doc._id, doc.nb_revision], doc);
    } else if (doc.itemType == "revision") {
        emit([doc.parent, doc.nb_revision], doc);
    }

}