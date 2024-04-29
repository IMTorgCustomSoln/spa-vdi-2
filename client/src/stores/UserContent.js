import { defineStore } from "pinia"

import { TopicRecord, NoteRecord } from "./data"
import { camelize } from '@/components/support/utils.js'


export const useUserContent = defineStore('userContent', {
    state:() => {
        return{
            name: 'John Doe',

            //temporary staging
            processedFiles: [],
            //documents: [],

            //permanent
            selectedDocument: '1',        //TODO:make explicit that this is the doc.id and it is a string
            selectedSnippet: null,
            
            documentsIndex: {
              documents: [],
              indices: {
                lunrIndex: {},
                strIndex: ''
              }
            },
            newNote: null,
            managedNotes: {
              topics: [],
              notes: []
            },

            //search
            showTablePanel: false,
            searchTableResults: {
              query: '',
              searchTerms: [],
              resultIds: [],
              resultGroups: []
            },
        }
    },
    getters:{/*
      getDocuments(){
        if(this.showTablePanel){
          return this.documents
        }else{
          return []
        }
      }*/
      getSelectedDocument: (state)=>state.selectedDocument > -1 ? state.selectedDocument : 0
    },
    actions:{
        getName(){
            return this.name
        },
        createIndex(records) {
          //create lunr index
          //const records = this.$props.records
          const lunrIndex = lunr(function () {
              this.ref('id')
              this.field('clean_body')
              this.metadataWhitelist = ['position']
              records.forEach(function (rec) {
                  this.add(rec)
              }, this)
          })
          //add to context
          this.documentsIndex.indices.lunrIndex = lunrIndex
        },
        setPlaceholders(){
          for(let idx=1; idx<=2; idx++){     //change for testing
            let text = `<Placeholder for item ${idx}>`
            let note = new NoteRecord(idx.toString(), 'stagingNotes', 'hand', '', text)
            this.managedNotes.notes.push(note)
          
            let title = `<Topic-${idx} placeholder>`
            let edited_title = title.trim()
            let topic = new TopicRecord(idx.toString(), edited_title, camelize(edited_title) + Date.now())
            this.managedNotes.topics.push(topic)
          }
        },
        addRecordsFromImport(){
            //check file for uniqueness in reference_number, then append
            let refNums = []
            let maxId = 0
            if(this.documentsIndex.documents.length>0){
              refNums.push(...this.documentsIndex.documents.map(item => item.reference_number) )
              const ids = this.documentsIndex.documents.map(item => parseInt(item.id)).filter(item => isNaN(item)==false)
              maxId = Math.max(...ids)
            }
            //for(let file of newRecords){
            for(let file of this.processedFiles){
              if(!refNums.includes(file.reference_number)){
                file.id = String( maxId + 1 )
                this.documentsIndex.documents.push( file )
                maxId++
              }
            }
            this.showTablePanel = true
            this.processedFiles.length = 0
          },
          addNewNoteToManager(){
            this.managedNotes.notes.push(this.newNote)
          }

    }
})