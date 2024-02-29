
import {ref} from 'vue'

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
    file_extension, filetype, page_nos, dataArray, length_lines, file_size_mb, date,
    title, author, subject, toc, pp_toc, 
    body_pages, body, clean_body, readability_score, tag_categories, keywords, summary
    ){
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
      this.dataArrayKey =                    //dataArray          //Uint8Array
      this.length_lines = length_lines    //sentences
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

    async setDataArray(arrayBlob){
      const randomSeed = Math.floor(Math.random() * 100)
      const refId = ''.hashCode(randomSeed)
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