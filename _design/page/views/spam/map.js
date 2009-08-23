function (doc) {
  // !code lib/sha256.js
  
  if (doc.itemType == "page" && doc.is_spam) {
    doc.thash = hex_sha256(doc.title);
    emit(doc.site, doc);
  }
}
