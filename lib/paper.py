import os
import dropbox

DOC_ID = '1NRlljWSK3U6GaIZ7er5j'

APPEND_POLICY = dropbox.paper.PaperDocUpdatePolicy('append')
EXPORT_FORMAT = dropbox.paper.ExportFormat('markdown')
IMPORT_FORMAT = dropbox.paper.ImportFormat('markdown')

def append(token, content):
  # Append a linebreak to the beginning.
  data = str.encode('<br>\n\n' + content)

  dbx = dropbox.Dropbox(token)

  # Get basic information about the Paper document. Note: We don't actually need the
  # document contents, despite this method name. We just need the document revision
  # number to update the document.
  doc, res = dbx.paper_docs_download(DOC_ID, EXPORT_FORMAT)

  # The response body is not consumed, so call close() on the response object
  # otherwise we will max out the available connections.
  res.close()

  # Append data to the Paper document
  dbx.paper_docs_update(data, DOC_ID, APPEND_POLICY, doc.revision, IMPORT_FORMAT)
