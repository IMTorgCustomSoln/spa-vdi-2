<template>
    <!-- Open modal button -->
    <b-button id='btnImport' v-b-modal="'import-modal'" :class="{ 'btn-success': componentBtn }" class="fixed-large">
        {{ btnText }}
    </b-button>
    <b-popover id="btnImportPop" target="btnImport" triggers="manual" :show.sync="componentBtn" placement="top"
        container="null">
        Click to import files and populate a table. Follow
        the green buttons if you're a new user.
    </b-popover>

    <!-- modal -->
    <b-modal id="import-modal" ok-only>
        <template #modal-title>
            Import files or workspace
        </template>
        <p>
            To begin, import individual files or continue from a previous state by
            uploading from a saved workspace file.
        </p>

        <!-- tabs -->
        <b-tabs v-model="activeTab" active-nav-item-class="font-weight-bold" content-class="mt-3">

            <!-- Files -->
            <b-tab title="Files" active id="tabFiles">
                <!--  // maybe some explanation for why the Workspace tab is disabled is needed
                <b-popover
                    target="tabFiles"
                    triggers="hover"
                    :show.sync="disableWorkspaceBtn"
                    placement="top"
                    container="null"
                    >
                    Workspace tab is disabled.  Loading a Workspace after loading 
                    files is not allowed as it will remove all current data.  To 
                    load a Workspace, reload the app, first.
                </b-popover>
                -->

                <form name="uploadForm">
                    <div>
                        <label for="uploadInput" class="custom-file-upload">
                            <b-icon-cloud-arrow-up-fill class="h2 mb-0" variant="success" /> Upload
                        </label>
                        <input id="uploadInput" type="file" accept=".pdf" @change="previewFiles" multiple />
                        <br />
                        <ul class="no-li-dot">
                            <li><label for="fileCount">Files: &nbsp</label> <output id="fileCount">{{ preview.fileCount
                            }}</output></li>
                            <li><label for="fileSize">Total size: &nbsp</label> <output id="fileSize"> {{ preview.fileSize
                            }}</output></li>
                            <li><label for="estimatedTime">Approximate time to upload and process: &nbsp</label> <output
                                    id="estimatedTime"> {{ preview.estimateProcessTime }}</output></li>
                        </ul>
                    </div>
                </form>

                <!-- Progress Bar -->
                <div>
                    <b-progress class="progress" :max="progressBar.maxProgress" height="1rem" show-progress animated>
                        <b-progress-bar :value="progressBar.fileProgress" :variant="progressBar.variant">
                            <span>
                                <!--ORIGINAL: Processed <strong>{{ progressBar.fileProgress }} of {{ progressBar.maxProgress }} bytes</strong> -->
                                Processed <strong>{{ getFileProgressDisplay }} of {{ getMaxProgressDisplay }} </strong>
                                <!--TODO issue: PREFERRED : Processed <strong>{{ getFormattedFileSize(progressBar.fileProgress, 'numeric') }} of {{ getFormattedFileSize(progressBar.max, 'unit') }} bytes</strong>-->
                            </span>
                        </b-progress-bar>
                    </b-progress>
                    <br />

                    <!-- Conditional Results Display -->
                    <div v-if="resultDisplay.display">
                        <bold style="font-weight: bold">Results: </bold><br />
                        Actual upload time was {{ resultDisplay.actualProcessTime }}<br />
                        <div v-if="resultDisplay.checkFilesUsable.length > 0" style="color: red">
                            The following files are not loaded because they do not appear to be searchable:<br />
                            <div v-for="filepath in resultDisplay.checkFilesUsable">
                                <div>{{ filepath }}</div>
                            </div>
                        </div>
                        <div v-else style="color: #28a745">
                            All files are loaded
                        </div>
                        <b-button size="sm" variant="primary" class="fixed-small" @click="exportLogsToText">
                            Logs
                        </b-button>
                    </div><br />

                    <!-- Notes -->
                    <div>
                        <em>
                            Note that at this time:
                            <ul>
                                <li>only PDF files with selectable text (not images) can be used.</li>
                                <li>limit single upload batch to less than 20 files for processing performance. Multiple
                                    batches may be performed.</li>
                                <li>subsequent uploads are only performed on files with different reference numbers. If no
                                    reference number is available in file name, a unique hash of the file name is created
                                    for reference.</li>
                                <li>workspace session may not be saveable after 50MB.</li>
                            </ul>
                        </em>
                    </div>
                </div>
            </b-tab>


            <!-- Workspace -->
            <b-tab title="Workspace" :disabled=disableWorkspaceBtn id="tabWorkspace"> <!-- popover placed in tab-0 -->
                <div>
                    <form name="uploadForm">
                        <p>
                            Select a previously saved session file (ie. <code>VDI_ApplicationStateData_v*.*.*.gz'</code>) to
                            continue your work.
                        </p>
                        <label for="uploadAppDataInput" class="custom-file-upload">
                            <b-icon-cloud-arrow-up-fill class="h2 mb-0" variant="success" /> Upload
                        </label><br />
                        <input id="uploadAppDataInput" type="file" @change="previewWorkspace" accept=".gz" />
                        <ul class="no-li-dot">
                            <li><label for="fileName">File: &nbsp</label><output id="fileName">{{ preview.fileName
                            }}</output></li>
                            <li><label for="fileSize">Size: &nbsp</label><output id="fileSize">{{ preview.fileSize
                            }}</output></li>
                        </ul>
                    </form>
                </div>
            </b-tab>


            <!-- Server -->
            <b-tab title="Server" :disabled=disableServerBtn id="tabServer"> <!-- popover placed in tab-0 -->
                <div>
                    <form name="uploadForm">
                        <p>
                            Select files from the server.
                        </p>
                        <b-form-select v-model="preview.serverFiles" :options="preview.availableServerFiles" multiple
                            :select-size="6">
                        </b-form-select>
                        <ul class="no-li-dot">
                            <li><label for="fileCount">Files: &nbsp</label> <output id="fileCount">{{
                                preview.serverFiles.length
                            }}</output></li>
                            <li><label for="fileSize">Total size: &nbsp</label> <output id="fileSize"> {{ getFilesSize
                            }}</output></li>
                        </ul>
                    </form>
                </div>
            </b-tab>


        </b-tabs>



        <!-- Control -->
        <template #modal-footer>
            <div v-if="activeTab == 0">
                <b-button @click="uploadInput" v-b-modal.modal-close_visit class="btn-sm m-1"
                    :class="{ 'btn-success': !uploadBtn }" :disabled=uploadBtn>Upload Files</b-button>
                <b-button @click="processData" v-b-modal.modal-close_visit class="btn-sm m-1"
                    :class="{ 'btn-success': !processBtn }" :disabled=processBtn>Process Data</b-button>
            </div>
            <div v-else-if="activeTab == 1">
                <b-button @click="uploadAppDataInput" v-b-modal.modal-close_visit class="btn-sm m-1"
                    :class="{ 'btn-success': !uploadWorkspaceBtn }" :disabled=uploadWorkspaceBtn>Upload</b-button>
            </div>
            <div v-else-if="activeTab == 2">
                <b-button @click="uploadServerInput" v-b-modal.modal-close_visit class="btn-sm m-1"
                    :class="{ 'btn-success': !uploadServerBtn }" :disabled=uploadServerBtn>Load</b-button>
            </div>
        </template>

    </b-modal>
</template>






<script>
import { ExportLogsFileName } from '@/stores/constants.js'
//import { DocumentIndexData, ManagedNotesData } from '@/stores/data.js'
import { DocumentRecord } from '@//stores/data.js'

import { getFileRecord } from '@/components/support/pdf_extract.js'
import { isEmpty, getEstimatedProcessTime, getFormattedMilliseconds } from '@/components/support/utils.js'
import { getDateFromJsNumber, getFormattedFileSize, getFileReferenceNumber } from '@/components/support/utils.js'

import { toRaw } from 'vue'
import { mapStores } from 'pinia'
import { useAppDisplay } from '@/stores/AppDisplay'
import { useUserContent } from '@/stores/UserContent'


export default {
    name: 'ImportData',
    compatConfig: {
        //MODE: 3,
        //COMPONENT_V_MODEL: false
    },
    emits: ['imported-records', 'imported-workspace'],
    data() {
        return {
            uploadIcon: ["success", "secondary"],   //TODO task:change to blue after docs selected
            btnText: 'Import',
            activeTab: 0,
            componentBtn: true,
            uploadBtn: true,
            processBtn: true,
            uploadWorkspaceBtn: true,
            disableWorkspaceBtn: false,
            uploadServerBtn: true,
            disableServerBtn: false,

            /*TODO note: keep code that would enable deconstruction to independent component
            documentsIndex: DocumentIndexData,
            managedNotes: ManagedNotesData,
            */

            preview: {
                availableServerFiles: [],
                serverFiles: [],
                fileCount: 0,
                fileName: '',
                fileSize: 0.0,
                estimateProcessTime: '0.0 sec'
            },

            //both arrays are epemeral and will always be emptied after use
            importedFiles: [],
            processedFiles: [],

            progressBar: {
                variant: "success",
                importLogs: [],
                fileProgress: 0,
                totalProgress: 0,
                maxProgress: 0
            },

            resultDisplay: {
                display: false,
                actualProcessTime: 0,
                checkFilesUsable: [],
            }
        }
    },
    mounted() {
        this.$root.$on('bv::modal::show', async (bvEvent, modalId) => {
            if (modalId == "import-modal") {
                this.componentBtn = false
                await this.getFilesFromServer()
            }
        })
        /* //not necessary
        this.$root.$on('bv::modal::hide', (bvEvent, modalId)=> {
            if(modalId=="import-modal" ){
                this.componentBtn = true
            }
        })*/
    },
    computed: {
        ...mapStores(useUserContent, useAppDisplay),
        getFileProgressDisplay() {
            return getFormattedFileSize(this.progressBar.fileProgress, 'decimal')
        },
        getMaxProgressDisplay() {
            return getFormattedFileSize(this.progressBar.maxProgress, 'unit')
        },
        getFilesSize() {
            const sizesOfSelectedGroups = this.preview.availableServerFiles.filter(
                (item) => { return this.preview.serverFiles.indexOf(item.name) != -1 }
            ).map(item => item.bytes)
            const sum = sizesOfSelectedGroups.reduce((partialSum, a) => partialSum + a, 0)
            if (this.preview.serverFiles.length > 0) {
                this.uploadServerBtn = false
            } else {
                this.uploadServerBtn = true
            }
            return getFormattedFileSize(sum)
        }
    },
    methods: {
        async getFilesFromServer() {
            //'http://localhost:8000/api/documentgroups/?format=json'
            const endpoint = this.appDisplayStore.api.server + this.appDisplayStore.api.documentGroup + '?format=json'
            const resp = await fetch(endpoint, {
                headers: { 'Content-type': 'application/json' },
            }).then(res => res.json()).then((response) => {
                const resp = response.map((item) => ({
                    ...item,
                    text: item.name,
                    value: item.name
                }))
                this.preview.availableServerFiles = resp
                return resp
            }).catch((error) => {
                console.log('Error, getting files from server: \n', error);
            })
            return true
        },
        previewFiles() {
            // Preview files to upload and process
            let numberOfBytes = 0;
            const fileCount = uploadInput.files.length
            for (const file of uploadInput.files) {
                numberOfBytes += file.size;
            }
            this.progressBar = { ...this.progressBar, maxProgress: numberOfBytes }
            this.preview = { ...this.preview, fileCount: fileCount }
            const fileSize = getFormattedFileSize(numberOfBytes)
            this.preview = { ...this.preview, fileSize: fileSize }
            const estimatedTime = getEstimatedProcessTime(fileCount, numberOfBytes)
            this.preview = { ...this.preview, estimateProcessTime: estimatedTime }
            this.uploadBtn = false
        },
        uploadInput() {
            // Load files into records
            this.uploadBtn = true
            uploadFiles.bind(this)(uploadInput.files).then(
                (recs) => {
                    this.importedFiles.push(...recs)
                    this.getResultDisplay()
                    this.processBtn = false
                })
        },
        processData() {
            // Process files by adding / modifying attributes
            const processedFiles = processFiles(this.importedFiles)
            this.userContentStore.processedFiles.push(...processedFiles)

            //this.$emit('imported-records', this.processedFiles)
            this.disableWorkspaceBtn = true
            this.resetModal()
            this.btnText = 'Add More Files'

            //TODO:note
            this.userContentStore.addRecordsFromImport()            //TODO:should this be placed elsewhere?
            this.appDisplayStore.viewSelection()

        },
        getResultDisplay() {
            //actual process time
            const finalLogItemIdx = this.progressBar.importLogs.length
            const finalLogItem = this.progressBar.importLogs[finalLogItemIdx - 1]
            const endTime = parseInt(finalLogItem.split(':')[0])
            const startTime = parseInt(this.progressBar.importLogs[0].split(':')[0])
            const duration = endTime - startTime    //in milliseconds, index based on performance.now() integer length
            this.resultDisplay = { ...this.resultDisplay, actualProcessTime: getFormattedMilliseconds(duration) }

            //check files for searchable text
            for (const file of this.processedFiles) {
                check_PageCount = file.bodyArr.filter(pageCharCount => pageCharCount < 1000)
                if (check_PageCount.length > 0) {
                    this.resultDisplay.checkFilesUsable.push(file.filepath)
                }
            }
            this.resultDisplay.display = true
        },


        previewWorkspace() {
            // Preview files to upload and process
            const file = uploadAppDataInput.files[0]
            const fileSize = getFormattedFileSize(file.size)
            this.preview = { ...this.preview, fileSize: fileSize }
            this.preview = { ...this.preview, fileName: file.name }
            this.uploadWorkspaceBtn = false
        },
        /*
        previewServer() {
            // Preview files to upload and process
            const file = uploadAppDataInput.files[0]
            const fileSize = getFormattedFileSize(file.size)
            this.preview = { ...this.preview, fileSize: fileSize }
            this.preview = { ...this.preview, fileName: file.name }
            this.uploadWorkspaceBtn = false
        },*/


        /*
        async uploadAppDataInputORIGINAL(){
            const file = uploadAppDataInput.files[0]
            const object = await parseJsonFile(file)

            this.documentsIndex.documents.length = 0
            this.managedNotes.topics.length = 0
            this.managedNotes.notes.length = 0

            Object.assign(this.documentsIndex, object.documentsIndex)
            Object.assign(this.managedNotes.topics, object.managedNotes.topics)
            Object.assign(this.managedNotes.notes, object.managedNotes.notes)

            this.$emit('imported-workspace', true)
            this.disableWorkspaceBtn = true
            this.resetModal()
            this.btnText = 'Add More Files'
        },*/
        async uploadAppDataInput() {
            let buffer = ''
            let stream = uploadAppDataInput.files[0].stream()
            //const reader = stream.getReader()
            //const decompressedStream = stream.pipeThrough(new TextDecoderStream())
            const decompressedStream = stream.pipeThrough(new DecompressionStream('gzip'))    //.pipeThrough(new TextDocoderStream())  TODO: decoding fails
            const reader = decompressedStream.getReader();
            while (true) {
                const { done, value } = await reader.read()
                if (done) { break; }
                console.log("received a new buffer", value.byteLength)
                buffer += new TextDecoder().decode(value)
            }
            const object = JSON.parse(buffer)
            for(const [idx, doc] of Object.entries(object.documentsIndex.documents) ){
                const doc_rec = new DocumentRecord()
                const check1 = await doc_rec.setAttrWithObj(doc)
                if(doc_rec.accumPageChars==null){
                    const check2 = await doc_rec.setProcessedFileData()
                }
                const check3 = await doc_rec.setDataArray()
                object.documentsIndex.documents[idx] = doc_rec
            }
            /*documents
            await object.documentsIndex['documents'].forEach(
                async function(value, idx, arr){
                    const doc_rec = new DocumentRecord()
                    doc_rec.setAttrWithObj(value)
                    if(doc_rec.accumPageChars==null){
                        const check1 = await doc_rec.setProcessedFileData()
                    }
                    const check2 = await doc_rec.setDataArray()
                    if(check2){
                        arr[idx] = doc_rec
                    }
                })*/
            //lunr index
            if(isEmpty(object.documentsIndex.indices.lunrIndex)==true){
                this.userContentStore.createIndex( object.documentsIndex['documents'] )
            }

            this.userContentStore.documentsIndex.documents.length = 0
            this.userContentStore.managedNotes.topics.length = 0
            this.userContentStore.managedNotes.notes.length = 0

            Object.assign(this.userContentStore.documentsIndex, object.documentsIndex)
            Object.assign(this.userContentStore.managedNotes.topics, object.managedNotes.topics)
            Object.assign(this.userContentStore.managedNotes.notes, object.managedNotes.notes)

            this.$emit('imported-workspace', true)
            this.disableWorkspaceBtn = true
            this.resetModal()
            this.btnText = 'Add More Files'

        },
        uploadServerInput() {
            //TODO:get data from server


        },


        resetModal() {
            this.importedFiles.length = 0
            this.processedFiles.length = 0

            this.componentBtn = false
            this.uploadBtn = true
            this.processBtn = true
            this.uploadWorkspaceBtn = true
            this.$bvModal.hide("import-modal")

            this.preview.fileName = ''
            this.preview.fileSize = 0.0
            this.preview.fileCount = 0

            this.progressBar.fileProgress = 0
            this.progressBar.totalProgress = 0
            this.progressBar.maxProgress = 0

            this.resultDisplay.display = false
            this.resultDisplay.actualProcessTime = 0
            this.resultDisplay.checkFilesUsable.length = 0

            this.processBtn = true
        },
        exportLogsToText(e) {
            const create = e.target
            const output = [...this.progressBar.importLogs]
            const strOutput = output.join(' ')
            const a = document.createElement('a')
            var link = create.appendChild(a)
            link.setAttribute('download', ExportLogsFileName)
            link.href = makeTextFile(strOutput)
            document.body.appendChild(link)

            // wait for the link to be added to the document
            window.requestAnimationFrame(function () {
                var event = new MouseEvent('click')
                link.dispatchEvent(event)
                document.body.removeChild(link)
            })
        },
    }
}








function makeTextFile(text) {
    let textFile = null
    const data = new Blob([text], { type: 'text/plain' })
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


async function uploadFiles(files) {
    // process files selected for upload and return an array of records
    let idx = 0
    const importedFiles = []
    const progress = {
        loaded: 0,
        total: 0
    }
    for (const file of files) {
        const FileStore = {
            idx: idx,
            file: file,
            ctx: this.progressBar
        }
        let record = await getFileRecord(FileStore)

        // file indexing
        record.id = String(idx)

        var re = /(?:\.([^.]+))?$/
        let extension = re.exec(file.name)[1]
        record.filename_original = file.name.replace('.' + extension, '')
        record.filepath = file.webkitRelativePath ? file.webkitRelativePath + '/' + record.filename_original : './' + record.filename_original
        record.filename_modified = null
        record.reference_number = getFileReferenceNumber(file.name)

        // raw
        record.file_extension = extension
        record.filetype = file.type
        record.file_size_mb = file.size
        record.date = file.lastModified

        /*inferred / searchable
        none

        //frontend field*/
        record.sort_key = 0     //record.id
        record.hit_count = 0
        record.summary = 'TODO:summary'
        record.snippets = []
        record._showDetails = false

        importedFiles.push(record)
        idx++
    }
    return importedFiles;
}



function processFiles(files) {
    // process files selected for upload and return an array of records
    const processedFiles = []
    for (const file of files) {
        const check = file.setProcessedFileData()
        if(check){
            processedFiles.push(file)
        }
    }
    return processedFiles;
}

</script>


<style scoped>
/*
#btnImport {
  margin: 5px;
}*/
.no-li-dot {
    list-style-type: none;
    padding-left: 10px;
    margin-bottom: 0px !important;
}

.no-li-dot label {
    margin: 0px;
}

em {
    font-size: .85rem;
}

.fixed-small {
    width: 105px !important;
}

.btn-sm {
    padding: .25rem .5rem;
    font-size: .875rem;
    line-height: 1.5;
    border-radius: .2rem;
}

/*
.fixed-large{
    width: 150px !important;
}
*/

input[type="file"] {
    display: none;
}

.custom-file-upload {
    display: inline-block;
    padding: 6px 12px;
    cursor: pointer;
}

.progress {
    margin-top: 30px;
}
</style>