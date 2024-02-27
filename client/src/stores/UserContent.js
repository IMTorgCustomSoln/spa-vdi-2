import { defineStore } from "pinia"

export const useUserContent = defineStore('userContent', {
    state:() => {
        return{
            name: 'John Doe',

            //temporary staging
            processedFiles: [],
            //documents: [],

            //permanent
            selectedDocument: 0,
            selectedSnippet: null,
            
            documentsIndex: {
              documents: [],
              indices: {
                lunrIndex: {},
                strIndex: ''
              }
            },
            managedNotes: [],

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
    },
    actions:{
        getName(){
            return this.name
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

    }
})