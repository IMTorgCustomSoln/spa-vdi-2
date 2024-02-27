import { createPinia } from 'pinia'
import { createPersistedState } from 'pinia-plugin-persistedstate'

import { IdbConfig } from './idb_mgmt'
import { DatabaseName, DbVersion, StoreNamesAndKeyFields } from './constants'


const idbConfig = new IdbConfig(DatabaseName, DbVersion, StoreNamesAndKeyFields)
const supported = await idbConfig.checkIdbSupport()
if (supported) {
  await idbConfig.createAllStoresInDb()
  const testResults = await idbConfig.testConfig()
  console.log(testResults)
}


export const pinia = createPinia()

/*TODO: use for production
pinia.use(createPersistedState({
    auto: true,
    storage: localStorage
  }))*/