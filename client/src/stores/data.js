
import {ref} from 'vue'

import { getDateFromJsNumber, getFormattedFileSize, getFileReferenceNumber } from '@/components/support/utils.js'
import { camelize } from '@/components/support/utils.js'
import * as utils from '@/components/support/utils.js'
import { DatabaseName, DbVersion, StoreNameDocumentRecord, StoreNamesAndKeyFields } from './constants.js'
import { updateItemsInStore, getItemFromStore } from './idb_mgmt.js'



// Managed Notes

export class TopicRecord{
  constructor(id, title, dropZoneName){
    this.id = id
    this.title = title
    this.dropZoneName = dropZoneName
  }
}

export class NoteRecord{
  constructor(id, list, type, innerHTML, innerText){
    this.id = id
    this.list = list
    this.type = type
    this.innerHTML = innerHTML
    this.innerText = innerText
  }
}
/*
const records = []
const topics = []
for (let idx=1; idx<=2; idx++){     //change for testing
  let text = `<Placeholder for item ${idx}>`
  let note = new NoteRecord(idx.toString(), 'stagingNotes', 'hand', '', text)
  records.push(note)

  let title = `<Topic-${idx} placeholder>`
  let edited_title = title.trim()
  let topic = new TopicRecord(idx.toString(), edited_title, camelize(edited_title) + Date.now())
  topics.push(topic)
}
export const ManagedNotesData = ref({
  topics: topics,
  notes: records
})*/




// Upload Input

export class DocumentRecord{
  constructor(
    id, reference_number, filepath, filename_original, filename_modified, 
    file_extension, filetype, page_nos, dataArrayKey, dataArray, length_lines, file_size_mb, date,
    title, author, subject, toc, pp_toc, 
    body_pages, body, clean_body, readability_score, tag_categories, keywords, summary, models
    ){
      //inline
      //file indexing
      this.id = id
      this.reference_number = reference_number
      this.filepath = filepath
      this.filename_original = filename_original
      this.filename_modified = filename_modified

      //raw
      this.file_extension = file_extension
      this.filetype = filetype 
      this.page_nos = page_nos
      this.dataArrayKey = dataArrayKey          //Uint8Array
      this.dataArray = null
      this.length_lines = length_lines          //sentences
      this.file_size_mb = file_size_mb 
      this.date = date

      //inferred / searchable
      this.title = title
      this.author = author 
      this.subject = subject
      this.toc = []
      this.pp_toc = pp_toc

      this.body_chars = {}
      this.body_pages = {}
      this.length_lines_array = []
      this.length_lines = 0
      this.body = body
      this.clean_body = clean_body
      this.readability_score = readability_score
      this.tag_categories = tag_categories
      this.keywords = keywords
      this.summary = summary
      this.models = models

      //added by frontend
      this.html_body = null
      this.date_created = null
      this.date_mod = null
      this.canvas_array = []

      this.sort_key = null
      this.hit_count = null
      this.snippets = null
      this.selected_snippet_page = null
      this._showDetails = false
      this._activeDetailsTab = 0
      this.accumPageLines = null
    }
    async setProcessedFileData(){
      //const item = JSON.parse(JSON.stringify(file))


      /* row items
      let length_lines = 0
      if (this.length_lines_array.length > 0) {
          if (this.length_lines_array.length > 1) {
              length_lines = this.length_lines_array.reduce((s, v) => s += (v | 0))
          } else {
              length_lines = this.length_lines_array[0]
          }
      } else {
          length_lines = 1;
      }
      this.length_lines = length_lines

      let dt = getDateFromJsNumber(this.date)
      this.original_date = this.date
      this.date = dt;

      /* add methods
      const rec = new DocumentRecord
      this.setDataArray = rec.setDataArray
      this.getDataArray = rec.getDataArray
      this.prepareForSave = rec.prepareForSave
      this.prepareForIndexDb = rec.prepareForIndexDb
      */

      // body items
      let bodyArr = Object.values(this.body_pages)
      this.body = bodyArr.length > 0 ? bodyArr.reduce((partialSum, a) => partialSum += (a || 0)) : ''
      let clean_body = this.body
      this.clean_body = clean_body
      this.html_body = clean_body     //.replaceAll("\n\n", "<br>")
      this.summary = clean_body.slice(0, 500)   //TODO:apply model to summarize text
      this.pp_toc = this.toc.map(section => `${section.title} (pg.${section.pageNumber})`)

      // prepare page numbers for search snippets
      //item.accumPageLines = item.length_lines_array.map((sum => value => sum += value)(0))    //.map((sum = 0, n => sum += n))  -> assignment to undeclared variable
      let charArr = Object.values(this.body_chars)
      this.accumPageChars = charArr.map((sum => value => sum += value)(0))    //.map((sum = 0, n => sum += n))  -> assignment to undeclared variable
      // prepare images
      //this.canvas_array = this.canvas_array.sort((a, b) => a.idx - b.idx)
      this.selected_snippet_page = 1

      //processedFiles.push(item)
      return true
    }
    async setDataArray(arrayBlob=null){
      const randomSeed = Math.floor(Math.random() * 100)
      const refId = ''.hashCode(randomSeed)
      if(arrayBlob==null){
        arrayBlob = this.dataArray
      }
      const arrayRecord = [{dataArrayKey: refId, dataArray: arrayBlob}]
      const check = await updateItemsInStore(DatabaseName, DbVersion, StoreNameDocumentRecord, arrayRecord)
      if(check){
        this.dataArrayKey = arrayRecord[0].dataArrayKey
      }
      return check
    }
    async getDataArray(){
      const dataArray = await getItemFromStore(DatabaseName, DbVersion, StoreNameDocumentRecord, this.dataArrayKey)
      return dataArray
    }
    async prepareForSave(){
      this.dataArray = await this.getDataArray()
      return true
    }
    async prepareForIndexDb(){
      this.dataArray = null
      return true
    }
    async setAttrWithObj(obj){

      //inline
      //file indexing
      this.id = obj.id
      this.reference_number = obj.reference_number
      this.filepath = obj.filepath
      this.filename_original = obj.filename_original
      this.filename_modified = obj.filename_modified

      //raw
      this.file_extension = obj.file_extension
      this.filetype = obj.filetype 
      this.page_nos = obj.page_nos
      this.dataArrayKey = obj.dataArrayKey          //Uint8Array
      this.dataArray = obj.dataArray
      this.length_lines = obj.length_lines    //sentences
      this.file_size_mb = obj.file_size_mb 
      this.date = obj.date

      //inferred / searchable
      this.title = obj.title
      this.author = obj.author 
      this.subject = obj.subject
      this.toc = obj.toc
      this.pp_toc = obj.pp_toc

      this.body_chars = obj.body_chars
      this.body_pages = obj.body_pages
      this.length_lines_array = obj.length_lines_array
      this.length_lines = obj.length_lines
      this.body = obj.body
      this.clean_body = obj.clean_body
      this.readability_score = obj.readability_score
      this.tag_categories = obj.tag_categories
      this.keywords = obj.keywords
      this.summary = obj.summary
      this.models = obj.models

      //added by frontend
      this.html_body = obj.html_body
      this.date_created = obj.date_created
      this.date_mod = obj.date_mod
      this.canvas_array = obj.canvas_array

      this.sort_key = obj.sort_key
      this.hit_count = obj.hit_count
      this.snippets = obj.snippets
      this.selected_snippet_page = obj.selected_snippet_page
      this._showDetails = obj._showDetails
      this._activeDetailsTab = obj._activeDetailsTab
      this.accumPageLines = obj.accumPageLines
    }


}

/*
export const DocumentIndexData = ref({
  documents: [],
  indices: {        //TODO: indices are saved / loaded, but indices are currrently created from document records
    lunrIndex: {},
    strIndex: ''
  }
})
*/