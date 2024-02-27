import { DocumentRecord } from "../../stores/data"

// Upload Input

export async function getFileRecord(filestore){     
  return new Promise(function(resolve, reject) {
      const reader = new FileReader()
      filestore.startTime = performance.now()
      addListeners(reader, filestore)
      reader.onload = (e) => {
          let typedarray = new Uint8Array(e.target.result)
          const loadingTask = pdfjsLib.getDocument(typedarray)
          loadingTask.typedarray = typedarray
          loadingTask.promise.then(async pdf => {
              //document is loaded 
              const record = new DocumentRecord()
              record.page_nos = pdf.numPages
              const dataArray = await pdf.getData()
              record.setDataArray(dataArray)
              /*(commented-out b/c already assigned)
              record.length_lines_array = []
              record.body_chars = {}
              record.body_pages = {}*/

              createMetadata(pdf, record)
              createOutline(pdf, record)
              
              for (let i = 1; i <= record.page_nos; i++) {
                  pdf.getPage(i).then(function(page) {
                      let n = page.pageNumber;
                      let page_text = ""
                      createCanvasImage(page, n, record)
                      page.getTextContent().then(function(textContent) {
                          for (let item of textContent.items) {
                              page_text += String(item.str)
                              if (item.hasEOL==true){ page_text += ' '}   //>>>alternative: ' <EOL> '
                          }
                          let edit1 = page_text//.replaceAll('- ','')
                          record.body_pages[n] = edit1 + "<br><br>" //+ "\n\n"    //TODO:BAD => must separate frontend display from actual text, this destroys mapping to correct page if doc is long
                          record.body_chars[n] = edit1.length
                          let approxCharsInSentence = 10
                          let sentence_count = edit1.split('.').filter(item => item.length > approxCharsInSentence).length    //orig:`(edit1.match(/./g) || []).length` 
                          record.length_lines_array.push(sentence_count)
                      });
                      //console.log(`Page ${n} of ${pdf.numPages} for file ${file.name}`)
                  });
              };
              //console.log(`${file} pdf loaded with body: ${record.layers}`)
              //record.body = record.layers.length > 0 ? record.layers.reduce((partialSum, a) => partialSum += (a || 0)) : '';
              resolve(record)
          }).catch((error)=>{
            console.log(error)
          })
      }
      reader.readAsArrayBuffer(filestore.file)
      reader.onerror = reject
  })
}


function addListeners(reader, filestore) {
  /* Add listeners and event handlers to the reader object.

  This is directly dependent upon the ImportData component and 
  TODO: should be moved into ImportData component because it is tightly coupled
  */
  reader.idx= filestore.idx
  reader.file = filestore.file
  reader.startTime = filestore.startTime
  reader.ctx = filestore.ctx
  const log = `${filestore.startTime}: file ${filestore.idx} - ${filestore.file.name} underwent event 'start' with 0 bytes transferred\n`
  filestore.ctx.importLogs.push( log )

  reader.addEventListener("loadstart", handleEvent)
  reader.addEventListener("load", handleEvent)
  reader.addEventListener("loadend", handleEvent)
  reader.addEventListener("progress", handleEvent)
  reader.addEventListener("error", handleEvent)
  reader.addEventListener("abort", handleEvent)

  function handleEvent(event) {
    let update = 0
    const log = `${performance.now()}: file ${filestore.idx} - ${event.currentTarget.file.name} underwent event '${event.type}' with ${event.loaded} bytes transferred\n`
    event.currentTarget.ctx.importLogs.push( log )
    //console.log(log)

    //successful events
    if (event.type=='loadstart'){
      update = event.currentTarget.ctx.totalProgress + 1
      event.currentTarget.ctx.fileProgress = update
    } else if (event.type=='load'){
      update = event.currentTarget.ctx.totalProgress + event.loaded
      event.currentTarget.ctx.totalProgress = update
      event.currentTarget.ctx.fileProgress = update
    } else if (event.type=='progress'){
      update = event.currentTarget.ctx.fileProgress = event.currentTarget.ctx.totalProgress + event.loaded
      event.currentTarget.ctx.fileProgress = update
    } 
    //file progress should always include total progress
    if (event.currentTarget.ctx.fileProgress < event.currentTarget.ctx.totalProgress){
      event.currentTarget.ctx.fileProgress = event.currentTarget.ctx.totalProgress
    }
    //console.log(event.currentTarget.ctx.fileProgress)
  }
}

function createMetadata(pdf, record){
  pdf.getMetadata().then(meta => {
    record.title = meta.info.Title
    record.subject = meta.info.Subject
    record.author = meta.info.Author
    record.date_created = meta.info.CreationDate
    record.date_mod = meta.info.ModDate
    record.keywords = meta.info.Keywords
    })
}

function createOutline(pdf, record){
  //ref: https://medium.com/@csofiamsousa/creating-a-table-of-contents-with-pdf-js-4a4316472fff
  pdf.getOutline().then(async outline => {    
    if (outline){
      for (let i =0; i< outline.length; i++){
        const title = outline[i].title
        const dest = outline[i].dest
        pdf.getDestination(dest).then(function(dest){
          const ref = dest[0]
          pdf.getPageIndex(ref).then(function(id){
            record.toc.push({title: title, pageNumber: parseInt(id)+1})
          })
        })
      }
    }
  })
}

function createCanvasImage(page, idx, record){
  //ref: https://stackoverflow.com/questions/62744470/turn-pdf-into-array-of-pngs-using-javascript-with-pdf-js
  var scale = 1.5;
  var viewport = page.getViewport({ scale: scale })
  var canvas = document.createElement('canvas')

  // Prepare canvas using PDF page dimensions
  var context = canvas.getContext('2d')
  canvas.height = viewport.height
  canvas.width = viewport.width

  // Render PDF page into canvas context
  var renderContext = { canvasContext: context, viewport: viewport }
  const renderTask = page.render(renderContext)
  renderTask.promise.then(function() {
    let image = canvas.toDataURL('image/png')
    record.canvas_array.push( {idx:idx, img:image} )
  })
}