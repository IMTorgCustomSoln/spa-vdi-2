<!--
ref:[Adding Drag and Drop to Your Vue3 Project](www.youtube.com/watch?v=-kZLD40d-tl)
* uses the Drag and Drop Web API

@dragover.prevent
-->

<template>
  <div class="drop-zone"
    @drop="onDrop($event, listName)"
    @dragenter.prevent    
    @dragover="onDragOver($event)"
    @dragleave="onDragLeave($event)"
    >
    <div v-for="item in getList(listName)"
      :key="item.id" 
      class="drag-el"
      draggable="true"
      @dragstart="startDrag($event, item)"
      >
      <div>
        <div v-if="item.innerHTML" v-html="item.innerHTML"></div>
        <div v-else>{{ item.innerText }}</div>
        <b-icon-chevron-double-right class="h5 mb-1 destroy" font-scale="0.8"  @click="removeNote(item)"/>
      </div>
    </div>
  </div>
</template>


<script>
import {ManagedNotesData} from './data.js'

export default ({
  name: "Draggable",
  props: {listName: String},
  data(){
    return{
      items: ManagedNotesData.value.notes
    }
   },
   methods: {
    getList(list){
      return this.items.filter(item=>item.list == list)
    },
    removeNote(item){
      this.items.splice(this.items.indexOf(item), 1)
    },
    startDrag(event, item){
      //console.log(item)
      event.dataTransfer.dropEffect = 'move'      //visual effect
      event.dataTransfer.effectAllowed = 'move'   //move instead of copy
      event.dataTransfer.setData('itemID',item.id)
    },
    onDragOver(event){
      event.preventDefault()
      event.target.style.background = "#ffeecf"
    },
    onDragLeave(event){
      event.target.style.background = ""
    },
    onDrop(event, list){
      event.target.style.background = ""
      const itemId = event.dataTransfer.getData('itemID')
      const item = this.items.find(item => item.id==itemId)    //find selected item
      item.list = list                                    //change items list
    }
   }
  })
</script>


<style scoped>
.drop-zone{
  width: 90%;
  margin: 10px auto;
  background-color: rgb(248, 249, 250);
  padding: 10px;
  min-height: 10px;
  font-size: 8px;
}
.drag-el{
  padding-bottom: 10px;
}
</style>