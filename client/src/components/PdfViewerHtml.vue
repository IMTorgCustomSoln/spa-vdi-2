<template>
    <div id="pageContainer">
        <div id="viewer" class="pdfViewer"></div>
    </div>
</template>

<script>
import * as pdfjsLib from "pdfjs-dist/build/pdf"
import *  as pdfjsViewer from "pdfjs-dist/web/pdf_viewer"
import * as pdfWorker from "pdfjs-dist/build/pdf.worker.mjs"

// Setting worker path to worker bundle.
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker
export { pdfjsLib }
pdfjsLib.GlobalWorkerOptions.workerSrc = "pdfjs-dist/build/pdf.worker.mjs"  //"https://cdn.jsdelivr.net/npm/pdfjs-dist@2.0.943/build/pdf.worker.min.js"
export { pdfjsViewer }
import "pdfjs-dist/web/pdf_viewer.css"


export default {
    name: "PdfViewer",
    //props: { docPath: String },
    data() {
        return {
            docPath: "./tests/data/10469527483063392000-cs_nlp_2301.09640.pdf"
        }
    },
    async mounted() {
        await this.getPdf();
    },
    methods: {
        async getPdf() {
            let container = document.getElementById("pageContainer");
            //getDocument
            // Some PDFs need external cmaps.
            const CMAP_URL = "pdfjs-dist/cmaps/"
            const CMAP_PACKED = true
            const SANDBOX_BUNDLE_SRC = new URL("pdfjs-dist/build/pdf.sandbox.mjs",
                window.location
            )
            const ENABLE_XFA = true
            const SEARCH_FOR = "Trace";     //test term
            //PdfViewer
            const eventBus = new pdfjsViewer.EventBus();
            // (Optionally) enable hyperlinks within PDF files.
            const pdfLinkService = new pdfjsViewer.PDFLinkService({
                eventBus,
            });
            // (Optionally) enable find controller.
            const pdfFindController = new pdfjsViewer.PDFFindController({
                eventBus,
                linkService: pdfLinkService,
            });
            // (Optionally) enable scripting support.
            const pdfScriptingManager = new pdfjsViewer.PDFScriptingManager({
                eventBus,
                sandboxBundleSrc: SANDBOX_BUNDLE_SRC,
            });
            let pdfViewer = new pdfjsViewer.PDFViewer({
                container,
                eventBus,
                linkService: pdfLinkService,
                findController: pdfFindController,
                scriptingManager: pdfScriptingManager,
            });
            pdfLinkService.setViewer(pdfViewer)
            pdfScriptingManager.setViewer(pdfViewer)
            eventBus.on("pagesinit", function () {
              // We can use pdfViewer now, e.g. let's change default scale.
              pdfViewer.currentScaleValue = "page-width";
              // We can try searching for things.
              if (SEARCH_FOR) {
                eventBus.dispatch("find", { type: "", query: SEARCH_FOR }, );
              }
            });
            let pdf = await pdfjsLib.getDocument({
                url: this.docPath,
                cMapUrl: CMAP_URL,
                cMapPacked: CMAP_PACKED,
                enableXfa: ENABLE_XFA,
            }).promise;
            console.log(`PDF Document proxy: ${pdf}`)
            console.log(`Document contains ${pdf.numPages} pages`)
            await pdfViewer.setDocument(pdf);
        },
    },
}
</script>
  
<style>
#pageContainer {
    position: absolute;
    /*
    overflow: auto;
    
    margin: auto;
    width: 80%;*/
}
/*
div.page {
    display: inline-block;
}*/
</style>