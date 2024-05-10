<template>
    <h6 class="center">
        {{ file_name }}
    </h6>

<div class="block">
{{ text }}
</div>
</template>


<script>
import { toRaw } from 'vue'
import { mapStores } from 'pinia'
import { useAppDisplay } from '@/stores/AppDisplay'
import { useUserContent } from '@/stores/UserContent'

export default{
    name:"PdfPlaceholder",
    watch: {
        //TODO, note: event source is Table Snippets
        'userContentStore.selectedSnippet': {
            handler: async function (newVal, oldVal) {
                let pg = 0
                let tgtText = ''
                if(newVal.snippet!=''){
                    const txtPg = parseInt(newVal.snippet.split('<b>pg.')[1].split('|')[0])
                    pg = txtPg <= 1 ? txtPg : txtPg - 1
                    tgtText = newVal.snippet.split('<b style="background-color: yellow">')[1].split('</b>')[0]
                }
                //const app = await this.getApp
                await this.loadDoc()
                //this.search(tgtText)
                //app.page = pg
            }
        }
    },
    data(){
        return {
            file_name: null,
            text: null

        }

    },
    computed:{
        ...mapStores(useAppDisplay, useUserContent),
        getDocument() {
            const docId = this.userContentStore.getSelectedDocument
            return this.userContentStore.documentsIndex.documents.filter(item => item.id==docId)[0]         //TODO:must use the Table array that is sorted on Score o/w incorrect
        }

    },
    methods:{
        async loadDoc() {
            //load document from typed array
            //expected workflow: click save doc, open a new document (manually) using `Open File` button, then click load doc 
            //const app = await this.getApp  //document.getElementById('pdf-js-viewer').contentWindow.PDFViewerApplication
            const doc = this.getDocument
            if (doc.id != this.currentDocumentId) {
                this.text = toRaw(doc.clean_body)//.replace('\n','&#13;&#10;')
                this.file_name = toRaw(doc.filename_original)

                /*
                const dataArray = await toRaw(doc.getDataArray())
                const tgt = { data: Object.values(dataArray.dataArray) }
                await app.open(tgt)*/
                this.currentDocumentId = doc.id
            }
        },

    }
}

</script>

<style>
.center {
  text-align: center;
  font-weight: bold;
  font-family: Arial, Helvetica, sans-serif;
  margin: 5px;
}
.block{
    white-space: pre-wrap;
    font-family: Arial, Helvetica, sans-serif;

    /*same as Table.vue > .snippet_container*/
    height: 90vh;
    overflow-y: auto;
}

</style>