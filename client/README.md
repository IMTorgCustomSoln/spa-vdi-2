# Visual Document Index

## Build

This project builds into a single file: `./dist/index.html` using the [plugin](https://github.com/richardtallent/vite-plugin-singlefile) with command:

```
npm run build
```

## Develop

Begin interactive (hot-reload) development with command:

```
npm run dev
```

If you need to re-evaluate the model estimates, this can be done using python.  Either run the pytest `test_create_estimation_model.py`, interactively, or directly via the commandline:

```
python create_estimation_model.py --input_dir = "./tests/logs/"
```

## References

* Bootstrap-vue is not quite ready for Vue3 (explained [here](https://bootstrap-vue.org/vue3))
* Vue3 compat(ability) [setup](https://stackblitz.com/edit/bootstrap-vue-with-compat?file=main.js) is used


## Requirements

* Export
  - ~~workspace
* Import data
  - ~~files
  - ~~workspace
  - server
* Search
  - ~~fuzzy
  - ~~exact
  - ~~models 
    + with sensitivity filter
  - concept
* Read
  - ~~file selection
  - ~~snippets
  - ~~reader highlighter selection
  - ~~model highlighter
* Notes
  - Export
  - Import




## ToDo

__Staging__

* style
  - ~~sort Score by descending~~
  - ~~terms used: get key terms~~
  - READ > text block: try / catch for PdfViewer
  - ~~READ > text block: enable scrolling~~
  - ~~READ > improve space efficiency in panels~~
  - READ > text block: allow text selection to Notes

* search 
  - ~~dropdown for search type~~
  - ~~searchExact() does not work~~
  - ~~fix Guide which no longer uses backticks: `checkBackticks`~~
  - implement concept search
    + [orama client vector search db: full text and vector](https://github.com/askorama/orama)
    + [mediapipe](https://developers.google.com/mediapipe/solutions/text/text_embedder/web_js)
    + [winknlp](https://winkjs.org/wink-nlp/similarity.html)

* important
  - fix PdfViewer highlight, text selection so that rectangle scales with change in viewer dimensions, similar to Search
    + `window.PDFViewerApplication.pdfViewer._pages[10].textLayer`
  - find way to highlight results of backend models

* refinements
  - ~~display Table on ingest of documents~~
  - fix Table field `Score`, which does not update
    + `Table.vue, ln.247` - `this.items[0].sort_key` is updated, but does not change within the component
  - remove need for placeholder: `/annotation-highlight.pdf`

* pwa design for long-term evolution
  - move current data stores to pinia state management: `documentsIndex`, `managedNotes`
  - create `documentsIndex` within python
  - load data from server-streamed gzip, [ref](https://stackoverflow.com/questions/957577/serving-gzipped-content-from-django)
  - autosave to file
  - send notes to word document
    + enable format ingest to standardize output
    + [ref](https://www.npmjs.com/package/docx)

__Planned__

* snippet generation is not aligned to doc pages (`./support/utils.js (ln.37)`)

* exact phrase search
  - ~~page for snippet is sometimes incorrect, ensure this is aligned; ex: search:`result` in prob,~~  
    + ~~pg.4|char2094 is actually on pg5., at beginning~~
    + ~~pg.5|char.1648~~
  - ~~fix score for failed exact match~~
  - first snippet in column does not respond to hover for move-to-page
  - exact match snippets get too much text; ex: "`2. Mir` `3. The`" for `econ_2301.00410.pdf`
  - exact match add AND, OR operators; ex: "+`2. Mir` +`3. The`"
  - fuzzy match doesn't exclude individual terms; `+main +result`
  - fix `query` var to show actual terms searched and formatted nicely with logical operators
  - Notes' export / import modals' buttons need style
  - About modals' buttons need style
  
* file loading
  - checks
    + add batch_idx to log output
    + set upload limits: number of documents, total upload size
    + ~~fix progress bar (maybe load.event)~~
    + ~~provide load results instead of immediately exiting modal~~
    + ~~logs and export of import times~~
    + ~~check whether actual pdf or pdf of images (scanned) (acrobat enables OCR to make searchable)~~ DANGER OF NOT SEARCHING, SO DO NOT ADD TO FILES []
    + ~~provide estimate for load time (min,sec) based on (file count, file size)~~
    + create output report with model estimates (coef, rsq, ...)
    + find limits for upload capacity: number of files and total size, [ref](https://queue.acm.org/detail.cfm?id=3595862)
    + checks to determine if file load takes too long
    + additional error handling for the browser

* test
  - unit testing - vitest, jest: https://vuejs.org/guide/scaling-up/testing.html
  - load testing File Reader

* concept search to find topics
  - use word vectors


* use generative-AI to create rough draft of memo
  - gen-AI working in `apply-gen-ai` branch
  - study problem: hyp) need to select exact text to make prompt statement
  - apply prompt to make output

* search
  - search opens activeTab to image (tried many times earlier)
  - highlight snippet in page image
  - drop-down for search type (stem, exact, proximity, word vector)
  - search within distance (proximity)
  - big pdf, ppt, excel, docx
  - 30-40 pdfs for loan file (hand-written, signatures, etc.)

* additional support
  - edge examples of what text is parsed (lines, equations, tables, graphs[wierdly]...) and what isn't (formatting [tables, endnotes, ...], style, line breaks)
  - add Tour, About, and Settings buttons (https://driverjs.com/docs/installation/)
  - add other fields to search: keywords, summary
  - adjust row details to reasonable height
  - zoom on bootstrap-vue image carousel
  - row details small, (more) btn click to lengthen down
  - highlight text snippet in document image (remove `char.` locator)
  - useTextSelection: https://vueuse.org/core/useTextSelection/
  - custom scss for: modal z-index, button sizes

* output
  - output to Word document
  - extract / capture images and diagrams to place in managed notes

* prepare for performance
  - what size dataset should we expect?
  - what should be done on the server? [ref](https://stackoverflow.com/questions/17078210/searching-a-large-amount-of-text-using-javascript-and-html5-storage)
  - writing to file: `Uncaught InternalError: allocation size overflow`
  - read files in chunks: [ref](https://stackoverflow.com/questions/14438187/javascript-filereader-parsing-long-file-in-chunks), [ref](https://stackoverflow.com/questions/50254537/how-to-read-any-local-file-by-chunks-using-javascript), [ref](https://stackoverflow.com/questions/55468777/json-stringify-large-object-optimization)
  - write files in [streams](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_writable_streams)
  - do not search until ready by pressing return
  - separate return hits and snippet generation
  - lazily return snippets
  - do not automatically move to page on snippet hover; instead, require a click
  - improve search speed

* wink nlp
  - subject
  - keywords
  - snippet - extract summary
  - snippet - improve search results
* ~~file-type: ensure only `.pdf` can be uploaded~~
* ~~import pdf nested loops~~
  - promises in loop: https://stackoverflow.com/questions/40328932/javascript-es6-promise-for-loop
  - extract pdf: [ref-1](https://stackoverflow.com/questions/1554280/how-to-extract-text-from-a-pdf-in-javascript?rq=3), [ref-2](https://stackoverflow.com/questions/40635979/how-to-correctly-extract-text-from-a-pdf-using-pdf-js), [ref-3](https://stackoverflow.com/questions/40482569/troubles-with-pdf-js-promises/40494019#40494019), [ref-4](https://stackoverflow.com/questions/61669405/forcing-a-function-to-wait-until-another-function-is-complete)