import Vue, { createApp } from '@vue/compat'
import BootstrapVue, {BIcon, BootstrapVueIcons} from 'bootstrap-vue'
import {pinia} from '@/stores/config_stores'
import App from '@/components/App.vue'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

import * as pdfjsLib from "pdfjs-dist/build/pdf"
//import *  as pdfjsViewer from "pdfjs-dist/web/pdf_viewer"
import * as pdfjsWorker from "pdfjs-dist/build/pdf.worker.mjs"


Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons)
Vue.component('b-icon', BIcon)

export const app = createApp(App)
app.use(pinia)
app.config.globalProperties.$pdf = pdfjsLib
app.config.globalProperties.$pdf.GlobalWorkerOptions.workerSrc = pdfjsWorker 

app.mount('#app')
window.$app = app