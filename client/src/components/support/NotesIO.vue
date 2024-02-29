<!--
    ref: https://stackoverflow.com/questions/21012580/is-it-possible-to-write-data-to-file-using-only-javascript
-->

<template>
    <div id="sidebar-btns">
    <b-button v-b-modal.export-notes-modal size="sm" variant="primary" class="fixed-small">Export</b-button>
    <b-modal id="export-notes-modal">
        <template #modal-title>
            Determine type of export
        </template>
        
        <p>
            <ul><b>Human-readable format:</b> write notes to text file for reporting purposes.</ul>
            <ul><b>AI-drafted memo format:</b> a rough draft of your memo is created using generative-AI.  Ensure the `AI status` is ready before using.  <div><code>AI status: {{ getFormattedLlmConfigStatus }}</code></div></ul>
            <ul><b>Data storage format:</b> save your work to a .json file so you can Import the file,
                and return to your current state, later, or share your work with teammates.  
                <i>Note:</i> this is the only method to save your work.</ul>
        </p>
        <br/>
            <template #modal-footer>
                <b-button @click="exportToText" v-b-modal.modal-close_visit class="btn-sm m-1" variant="primary" >Human-Readable</b-button>
                <b-button disabled @click="exportToTextWithAI" v-b-modal.modal-close_visit class="btn-sm m-1" variant="primary" >AI-Drafted</b-button>
                <b-button @click="exportToJson" v-b-modal.modal-close_visit class="btn-sm m-1" variant="primary" >Data Storage</b-button>
            </template>
    </b-modal>

    <b-button v-b-modal.import-notes-modal size="sm" variant="primary" class="fixed-small">Import</b-button>
    <b-modal id="import-notes-modal">
        <template #modal-title>
            Select Notes Manager file
        </template>
        <form name="uploadForm">
            <label for="uploadInput" class="custom-file-upload">
                <b-icon-cloud-arrow-up-fill class="h2 mb-0" variant="success" /> Upload
            </label><br/>
            <input id="uploadInput" 
                   type="file" 
                   @change="previewFile"
                   accept=".json"
            />
            <label for="fileName">File: &nbsp</label>
            <output id="fileName">{{ file }}</output>
        </form><br/>
            Select whether to append to existing notes or replace them:
            <template #modal-footer>
                <b-button @click="appendNotes" v-b-modal.modal-close_visit class="btn-sm m-1" variant="primary" >Append</b-button>
                <b-button @click="replaceNotes" v-b-modal.modal-close_visit class="btn-sm m-1" variant="primary" >Replace</b-button>
            </template>
    </b-modal>
    </div>
</template>

<script>
import { isProxy, toRaw } from 'vue'
import {ExportFileName, ExportTextName} from '@/stores/constants.js'
//import {ExportFileName, ExportTextName, ManagedNotesData} from '@/stores/constants.js'

import { mapStores } from 'pinia'
import { useAppDisplay } from '@/stores/AppDisplay'
import { useUserContent } from '@/stores/UserContent'



//placeholder for when LLM is used
class LLM {
    static run = true
    static init_label = ''
    static generate_label = ''
    static chat = ''

    static async configure(){
        return true
    }
}


export default{
    name: 'NotesIO',
    data(){
        return {
            //topics: ManagedNotesData.value.topics,
            //notes: ManagedNotesData.value.notes,
            file: '',

            llm: LLM,
        }
    },
    computed:{
        ...mapStores(useAppDisplay, useUserContent),
        getFormattedLlmConfigStatus(){
            const check1 = this.llm.init_label == ''
            const check2 = this.llm.init_label.includes('/')
            if(check1){
                return 'not available'
            } else if (check2){
                const fraction = this.llm.init_label.split(']')[0].split('[')[1]
                const num = parseInt( fraction.split('/')[0 ])
                const denom = parseInt( fraction.split('/')[1] )
                if(num/denom == 1){
                    return 'ready'
                }else{
                    return 'loading ' + fraction
                }
            }else{
                return 'ready'
            }
        }
    },
    async mounted(){
        if(navigator.gpu && navigator.gpu.requestAdapter() && this.llm.run){
            console.log('loading llm...')
            await this.llm.configure()
            if (this.llm.createDialogue){
                //await this.llm.createDialogue()   //only for testing
                console.log('llm loading completed')
            } else {
                console.log('llm not available')
            }
        }
    },
    methods:{
        exportToText(e){
            const create = e.target
            const output = []
            const initial = `# Notes`
            output.push(initial)
            let allTopics = [...this.userContentStore.managedNotes.topics]
            const staging = {title:'Staging Notes', 
                            dropZoneName:'stagingNotes'
                        }
            allTopics.push(staging)
            for (let topic of allTopics){
                let hdr = `\n\n\n## ${topic.title}\n\n`
                output.push(hdr)
                for (let note of this.userContentStore.managedNotes.notes){
                    if (note.list == topic.dropZoneName){
                        if (note.type == "hand"){
                            let ul = `* ${note.innerText}\n`
                            output.push(ul)
                        } else if (note.type == "auto"){
                            let ul = `* ${note.id}\n${note.innerText}\n`
                            output.push(ul)
                        } else {
                            continue
                        }
                    }
                }
            }
            const strOutput = output.join(' ')
            const a = document.createElement('a')
            var link = create.appendChild(a)
            link.setAttribute('download', ExportTextName)
            link.href = makeTextFile(strOutput)
            document.body.appendChild(link)

            // wait for the link to be added to the document
            window.requestAnimationFrame(function () {
                var event = new MouseEvent('click')
                link.dispatchEvent(event)
                document.body.removeChild(link)
            })
            this.$bvModal.hide("export-notes-modal")
        },
        async exportToTextWithAI(e){
            const create = e.target
            const output = []
            const initial = `# Notes`
            output.push(initial)
            let allTopics = [...this.userContentStore.managedNotes.topics]
            const staging = {title:'Staging Notes', 
                            dropZoneName:'stagingNotes'
                        }
            allTopics.push(staging)
            for (let topic of allTopics){
                let hdr = `\n\n\n## ${topic.title}\n\n`
                output.push(hdr)

                for (let note of this.userContentStore.managedNotes.notes){
                    if (note.list == topic.dropZoneName){
                        if (note.type == "hand"){
                            let ul = `* ${note.innerText}\n`
                            output.push(ul)
                        } else if (note.type == "auto"){
                            //let ul = `* ${note.id}\n${note.innerText}\n`
                            let prompt = `In one sentence, describe how ${note.innerText} causes ${topic}`
                            console.log(prompt)
                            let reply = await this.llm.createDialogue(prompt)
                            let ul = `* ${reply}`
                            console.log(ul)
                            output.push(ul)
                        } else {
                            continue
                        }
                    }
                }
            }

            const strOutput = output.join(' ')
            const a = document.createElement('a')
            var link = create.appendChild(a)
            link.setAttribute('download', ExportTextName)
            link.href = makeTextFile(strOutput)
            document.body.appendChild(link)

            // wait for the link to be added to the document
            window.requestAnimationFrame(function () {
                var event = new MouseEvent('click')
                link.dispatchEvent(event)
                document.body.removeChild(link)
            })
            this.$bvModal.hide("export-notes-modal")

        },
        exportToJson(e){
            const create = e.target
            const object = {
                topics: this.userContentStore.managedNotes.topics,
                notes: this.userContentStore.managedNotes.notes
            }
            const jsonObj = JSON.stringify( toRaw(object) )
            const a = document.createElement('a')
            var link = create.appendChild(a)
            link.setAttribute('download', ExportFileName)
            link.href = makeTextFile(jsonObj)
            document.body.appendChild(link)

            // wait for the link to be added to the document
            window.requestAnimationFrame(function () {
                var event = new MouseEvent('click')
                link.dispatchEvent(event)
                document.body.removeChild(link)
            })
            this.$bvModal.hide("export-notes-modal")
        },
        previewFile() {
            const file = uploadInput.files[0]
            this.file = file.name
        },
        async appendNotes(){
            const file = uploadInput.files[0]
            const object = await parseJsonFile(file)
            this.userContentStore.managedNotes.topics.push(...object.topics)
            this.userContentStore.managedNotes.notes.push(...object.notes)
            this.$bvModal.hide("import-notes-modal")
        },
        async replaceNotes(){
            const file = uploadInput.files[0]
            const object = await parseJsonFile(file)
            this.userContentStore.managedNotes.topics.length = 0
            this.userContentStore.managedNotes.notes.length = 0
            Object.assign(this.userContentStore.managedNotes.topics, object.topics)
            Object.assign(this.userContentStore.managedNotes.notes, object.notes)
            this.$bvModal.hide("import-notes-modal")
        }
    }
}


function makeTextFile(text) {
    let textFile = null
    const data = new Blob([text], {type: 'text/plain'})            
    // If we are replacing a previously generated file we need to
    // manually revoke the object URL to avoid memory leaks.
    if (textFile !== null) {
      window.URL.revokeObjectURL(textFile)
    }         
    textFile = window.URL.createObjectURL(data)          
    return textFile
}

async function parseJsonFile(file) {
  return new Promise((resolve, reject) => {
    const fileReader = new FileReader()
    fileReader.onload = event => resolve(JSON.parse(event.target.result))
    fileReader.onerror = error => reject(error)
    fileReader.readAsText(file)
  })
}







</script>


<style scoped>
/*TODO: align right
#sidebar-btns{
    margin-left: auto; 
    margin-right: 0;
    display: block;
    display: inline-block;
    float: right;
}#si */

.fixed-small{
    width: 61px !important;
}

.btn-sm {
    font-size:12px;
    padding:2px;
    margin:5px;
}

</style>