import os
import dropbox

DROPBOX_ACCESS_TOKEN = os.environ['DROPBOX_ACCESS_TOKEN']
DOC_ID = '1NRlljWSK3U6GaIZ7er5j'

APPEND_POLICY = dropbox.paper.PaperDocUpdatePolicy('append')
EXPORT_FORMAT = dropbox.paper.ExportFormat('markdown')
IMPORT_FORMAT = dropbox.paper.ImportFormat('markdown')

def append(title, body):
  # Convert title and body into Markdown-formatted bytes string
  data = str.encode('<br>\n\n# ' + title + '\n\n' + body)

  dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

  # Get basic information about the Paper document. Note: We don't actually need the
  # document contents, despite this method name. We just need the document revision
  # number to update the document.
  doc, res = dbx.paper_docs_download(DOC_ID, EXPORT_FORMAT)

  # The response body is not consumed, so call close() on the response object
  # otherwise we will max out the available connections.
  res.close()

  # Append data to the Paper document
  dbx.paper_docs_update(data, DOC_ID, APPEND_POLICY, doc.revision, IMPORT_FORMAT)
