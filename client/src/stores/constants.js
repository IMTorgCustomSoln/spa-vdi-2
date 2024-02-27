



// Export
export const ExportAppStateFileName = `${__EXPORT_APP_STATE_FILE_NAME__}_v${__VERSION__}.gz`
export const ExportFileName = `${__EXPORT_FILE_NAME__}_v${__VERSION__}.json`
export const ExportTextName = `${__EXPORT_TEXT_NAME__}_v${__VERSION__}.txt` 
export const ExportLogsFileName  = `${__UPLOAD_LOGS_TEXT_NAME__}_v${__VERSION__}.log`


// Idb
export const DatabaseName = `DocDb`
export const DbVersion = 1
export const StoreNameDocumentRecord = `Document`
export const StoreNamesAndKeyFields = [
    {storeName: StoreNameDocumentRecord, keyField: 'dataArrayKey'},
]