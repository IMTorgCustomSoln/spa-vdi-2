
import { openDB, deleteDB, wrap, unwrap } from 'idb'

import { getFormattedFileSize } from '@/components/support/utils.js'
import { DocumentRecord } from './data.js'





export class IdbConfig{
    constructor(dbName, dbVersion, storeNamesAndKeyFields){
        this.dbName = dbName
        this.dbVersion = dbVersion
        this.storeNamesAndKeyFields = storeNamesAndKeyFields
        this.isSupported = null
    }

    async checkIdbSupport(){
        // Check for IndexedDB support
        //notes: Chrome now lets an origin use 60% of the storage device's space (Real nitty gritty: "storage device" is the partition containing the chrome profile directory).
        //ref: https://web.dev/articles/indexeddb
        if (!('indexedDB' in window)) {
          // Can't use IndexedDB
          console.log("ERROR: This browser doesn't support IndexedDB")
          this.isSupported = false
        } else {
          // Do IndexedDB stuff here:
          // ...
          console.log("This browser supports IndexedDB")
          this.isSupported = true
          await getIdbAvalabileSpace()
        }
        return this.isSupported
    }
    async testConfig(IdbConfig){
        const record = new DocumentRecord()
        record.id = 'test'
        const testData = [0,0,0,0,0]
        const result1 = await record.setDataArray(testData)
        const check1 = isNaN(result1[0])==false 
        console.log(check1) 

        const result2 = await record.getDataArray()
        const check2 = JSON.stringify(result2.dataArray) == JSON.stringify(testData) 
        console.log(check2 )

        return 'Database tests complete'
}

    async createAllStoresInDb(){
        //const item = this.storeNamesAndKeyFields[0]
        //const db = await this.createStoreInDb(this.dbName, this.dbVersion, item.storeName, item.keyField)
        //TODO:this fails
        const tasks = []
        for(const item of this.storeNamesAndKeyFields){
            //await this.createStoreInDb(this.dbName, this.dbVersion, item.storeName, item.keyField)
            tasks.push( this.createStoreInDb(this.dbName, this.dbVersion, item.storeName, item.keyField) )
        }
        await Promise.all(tasks)
        return true
    }
async createStoreInDb(dbName, dbVersion, storeName, storeKeyField){
    const dbPromise = await openDB(dbName, dbVersion, {
      upgrade (db) {
        if (!db.objectStoreNames.contains(storeName)) {
          db.createObjectStore(storeName, { keyPath: storeKeyField });
        }
      }
    })
  }
}


export async function getIdbAvalabileSpace(){
    // Get space available for IndexedDb
    //notes: The StorageManager isn't implemented in all browsers yet, so you must feature detect it before using it. Even when it is available, you must still catch over-quota errors (see below). In some cases, it's possible for the available quota to exceed the actual amount of storage available.
    //ref: https://web.dev/articles/storage-for-the-web#:~:text=In%20many%20browsers%2C%20you%20can%20use%20the%20StorageManager,to%20calculate%20the%20approximate%20remaining%20storage%20space%20available.
    if (navigator.storage && navigator.storage.estimate) {
        const quota = await navigator.storage.estimate();
        // quota.usage -> Number of bytes used.
        // quota.quota -> Maximum number of bytes available.
        const percentageUsed = (quota.usage / quota.quota) * 100;
        console.log(`You've used ${percentageUsed}% of the available storage.`);
        const remaining = quota.quota - quota.usage;
        console.log(`You can write up to ${getFormattedFileSize(remaining)} more bytes.`);
      }
}
  

// Set
export async function updateItemsInStore(dbName, dbVersion, storeName, arrayRecords){
  const db = await openDB(dbName, dbVersion);
  const tx = db.transaction(storeName, 'readwrite');

  // Update multiple items in the store in a single transaction:
    const tasks = []
    for(const record of arrayRecords){
        tasks.push( tx.store.put(record) )
    }
    const check = await Promise.all(tasks)
    tx.done
    return check
    /*
    tx.store.put({
      name: 'Sandwich',
      price: 5.99,
      description: 'A MORE tasty sandwich!',
      updated: new Date().getTime() // This creates a new field
    }),
    tx.store.put({
      name: 'Eggs',
      price: 3.99,
      description: 'Some even NICER eggs you can cook up!',
      updated: new Date().getTime() // This creates a new field
    }),
    tx.done
  ]);*/
}


// Get
export async function getItemFromStore(dbName, dbVersion, storeName, key) {
    const db = await openDB(dbName, dbVersion);
    const value = await db.get(storeName, key);
    return value
  }
  