import * as model from "@/../tests/py/results.json"



// ProcessData

export function getEstimatedProcessTime(fileCount, fileSizeInBytes){
  /* Get the estimated time to process a file, in human-
  readable minutes or seconds.
  TODO: this is entirely dependent on platform from which the 
  function is run.
  */
  let formatted = ''
  let result = ''
  const {size, file_count} = model.coefs['0.75']    //TODO:add high estimate to this median estimate to give users a better range of values

  if (Number.isInteger(fileCount) && Number.isFinite(fileSizeInBytes)){
    const log_fileCount = Math.log(fileCount)
    const log_Size = Math.log(fileSizeInBytes)
    const log_milliseconds = size * log_fileCount + file_count * log_Size
    const milliseconds = Math.exp(log_milliseconds)

    if (Number.isFinite(milliseconds )){
      result = getFormattedMilliseconds(milliseconds)
    } else {
      result = '-1'
    }
    return result
  } else {
    result = '-1'
  }
}

export function getFormattedMilliseconds(milliseconds){
  let formatted = ''
  if (milliseconds >= 60000){
    const intermediate = milliseconds / 60000 
    formatted = `${intermediate.toFixed(2)} min`
  } else if (milliseconds < 60000 && milliseconds >= 1000){
    const intermediate = milliseconds / 1000 
    formatted = `${intermediate.toFixed(2)} sec`
  } else {
    formatted = `${milliseconds.toFixed(2)} milliseconds`
  }
  return formatted
}

/* FAIL: this is too complicated, but may be something to consider in future
export function getFileReferenceNumber(filename, searchTermOrIndexArray=/(^\d+)(.+$)/i, regex=true){
  /* Get a file reference number from file name
  This unique identifier is used throughout the app.  If no ref number is used, then a hash
  of the file name will be applied for uniqueness.
  ref: https://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript

  The `searchTermOrIndexArray` argument should be one of the following:
   * Array [start, stop] - index numbers to slice
   * String (chars) - simple search term to slice(0, first_index)
   * String (regex) - regex pattern to hit
    
   ('54931863796627370000-econ_2301.00410.pdf').replace(regex, '$1')
   '54931863796627370000'
  *//*
 let reference = ''
 if (Array.isArray(searchTermOrIndexArray)==true && searchTermOrIndexArray.length==2){
  let idx1,idx2
  [idx1, idx2] = searchTermOrIndexArray
  let tmp = filename.slice(idx1, idx2)
  if (Number.isInteger(tmp)){
    reference = tmp
  } else {
    reference = filename.hashCode()
  }
 } else if (typeof(searchTermOrIndexArray)=="string"){
      if (!regex){
        const idx = filename.indexOf(searchTermOrIndexArray)
        reference = filename.slice(0, idx)
      } else if (regex){
        let tmp = (filename).replace(searchTermOrIndexArray, '$1')
        if (tmp.length <= 20 ){
          console.log(tmp)
          reference = tmp
        }
      }
 } else {
  const reference = filename.hashCode()
}
return reference
}*/


export function getFileReferenceNumber(filename){
  /* Get a file reference number from file name
  This unique identifier is used throughout the app.  If no ref number is used, then a hash
  of the file name will be applied for uniqueness.
  
   ('54931863796627370000-econ_2301.00410.pdf').replace(regex, '$1')
   '54931863796627370000'
  */
 let reference = ''
 const regex = /(^\d+)(.+$)/i
 const rslt = (filename).replace(regex, '$1')
 if (rslt.length <= 20 && (Number.parseInt(rslt)).toString().length == rslt.length){
  reference = rslt
 } else {
  reference = filename.hashCode()
 }
 return reference
}


String.prototype.hashCode = function(seed = 0) {
  // Generate hash from string
  //ref: https://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript
  let h1 = 0xdeadbeef ^ seed, h2 = 0x41c6ce57 ^ seed;
  for(let i = 0, ch; i < this.length; i++) {
      ch = this.charCodeAt(i);
      h1 = Math.imul(h1 ^ ch, 2654435761);
      h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1  = Math.imul(h1 ^ (h1 >>> 16), 2246822507);
  h1 ^= Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2  = Math.imul(h2 ^ (h2 >>> 16), 2246822507);
  h2 ^= Math.imul(h1 ^ (h1 >>> 13), 3266489909);

  return 4294967296 * (2097151 & h2) + (h1 >>> 0);
};


export const getDateFromJsNumber = num => {
  // Integer to string date
  let result = ''
  if (typeof(num)=='number'){
      if (String(num).length > 10) {
          let dt = new Date(num)
          result = `${dt.getMonth()+1}/${dt.getDate()}/${dt.getFullYear()}`;
      }
  } else if (typeof(num)=='string' && num.length > 10) {
      const int = parseInt(num) 
      let dt = new Date(int)
      result = `${dt.getMonth()+1}/${dt.getDate()}/${dt.getFullYear()}`;
  } 
  return result;
};


export function getFormattedFileSize(numberOfBytes, format='both') {
  /* Approximate to the closest prefixed unit
  
  format = <decimal, unit, both>
  getFormattedFileSize(139070, 'decimal')  >>> "135.81"
  getFormattedFileSize(139070, 'unit')  >>> "135.81 KiB"
  getFormattedFileSize(139070, 'both')  >>> "135.81 KiB (139070 bytes)"
  */
  const units = [
      "B",
      "KiB",
      "MiB",
      "GiB",
      "TiB",
      "PiB",
      "EiB",
      "ZiB",
      "YiB",
  ];
  if(numberOfBytes<=0){return 0}
  const exponent = Math.min(
      Math.floor(Math.log(numberOfBytes) / Math.log(1024)),
      units.length - 1
  );
  const approx = numberOfBytes / 1024 ** exponent;
  let output = ''
  if(format == 'both'){
    output = exponent === 0 ?
          `${numberOfBytes} bytes` :
          `${approx.toFixed(2)} ${
                units[exponent]
              } (${numberOfBytes} bytes)`
  }else if (format == 'unit'){
    output =
          exponent === 0 ?
          `${numberOfBytes} bytes` :
          `${approx.toFixed(2)} ${
                units[exponent]}`
  }else if (format == 'decimal'){
    output =
    exponent === 0 ?
    `${numberOfBytes} bytes` :
    `${approx.toFixed(2)}`
  }
  return output
}




const getDateFromPythonString = str => {
  /* Usage:
  const dt = getDateFromString(value)
  const formattedDate = dt.toLocaleDateString()
  return formattedDate;
  */
  if (str.length > 10) {
      const [date, time] = str.split(" ");
      long_date = `${date}T${time}.000Z`; // reformat string into YYYY-MM-DDTHH:mm:ss.sssZ
      dt = new Date(long_date)
  } else {
      dt = new Date(str)
  }
  return dt;
};



function serializeObject(obj){
  // implement JSON.stringify serialization
  JSON.stringify = JSON.stringify || function (obj) {
  	var t = typeof (obj);
  	if (t != "object" || obj === null) {
  		// simple data type
  		if (t == "string") obj = '"'+obj+'"';
  		return String(obj);
  	}
  	else {
  		// recurse array or object
  		var n, v, json = [], arr = (obj && obj.constructor == Array);
  		for (n in obj) {
  			v = obj[n]; t = typeof(v);
  			if (t == "string") v = '"'+v+'"';
  			else if (t == "object" && v !== null) v = JSON.stringify(v);
  			json.push((arr ? "" : '"' + n + '":') + String(v));
  		}
  		return (arr ? "[" : "{") + String(json) + (arr ? "]" : "}");
  	}
  }
}



function deserializeObject(str){
  // implement JSON.parse de-serialization
  JSON.parse = JSON.parse || function (str) {
  	if (str === "") str = '""';
  	eval("var p=" + str + ";");
  	return p;
  }
}


export function camelize(str) {
  //Turn any string into camelCase
  return str.replace(/(?:^\w|[A-Z]|\b\w)/g, function(word, index) {
      return index === 0 ? word.toLowerCase() : word.toUpperCase();
  }).replace(/\s+/g, '');
}





/*
No longer used, but good reference.
Reference for this solution to register pdfjs-dist:
https://erindoyle.dev/using-pdfjs-with-vite/


import pdfjs from 'pdfjs-dist/build/pdf';
import pdfjsWorker from 'pdfjs-dist/build/pdf.worker?worker';
import * as Sentry from '@sentry/vue';


const init = async () => {
  
  try {
    if (typeof window === 'undefined' || !('Worker' in window)) {
      throw new Error('Web Workers not supported in this environment.');
    }
    window.pdfjsWorker = pdfjsWorker;
    pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;
  } catch (error) {
    Sentry.captureException(`Unable to load pdfjs: ${error}`);
  }
};

export default {
  install: (app) => {
    init();
    pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;
    app.config.globalProperties.$pdf = pdfjs;
  }
};
*/