<template>
    <div>
        <!-- The button -->
        <b-button id='btnSidebar' ref='btnSidebar' variant="primary" v-b-toggle.sidebar class="">
            Notes
        </b-button>

        <!-- The sidebar -->
        <b-sidebar id="sidebar" title="Notes Manager" width="500px" right :backdrop-variant="variant" backdrop shadow>
            <div class="px-3 py-2">
                <div class="section">
                    <div class="description">
                        <p>Create notes and organize them by topics. Save your notes to a file for use in future sessions,
                            and share them with your team.
                            <Guide v-bind="guides.managedNotes" />
                            <NotesIO />
                        </p>
                    </div>
                </div>

                <hr style="border: 1px solid black" />
                <div class="section">
                    <h3>Staging Notes</h3>
                    <div class="description">
                        <p>Create manual notes or add selections directly from the document search results.</p>
                    </div>
                    <div>
                        <!--<label for="noteName">New note:</label>-->
                        New note:
                        <input type="text" name="noteName" ref="noteName" style="margin-left:8px" autofocus
                            placeholder="add manual note..." @keyup.enter="addNote">
                    </div>
                    <Draggable :listName="stagingNotesList" />
                </div>

                <hr />
                <div class="section">
                    <h3>Topics</h3>
                    <div class="description">
                        <p>Create topics of interest then organize your notes by dragging them underneath desired topic.</p>
                    </div>
                    <div>
                       <!--<label for="topicName">New topic:</label>-->
                        New topic:
                        <input type="text" name="topicName" ref="topicName" style="margin-left:8px" autofocus
                            placeholder="add topic..." @keyup.enter="addTopic">
                    </div>
                    <div>
                        <div v-for="topic in getTopics" :key="topic.id">
                            <hr />
                            <div>
                                <h5>{{ topic.title }}<b-icon-x-square class="h5 mb-1 destroy" font-scale="0.5"
                                        @click="removeTopic(topic)" />
                                </h5>
                            </div>
                            <Draggable :listName="topic.dropZoneName" />
                        </div>
                    </div>
                </div>
            </div>
        </b-sidebar>
    </div>
</template>
  
  
  
<script>
//import {NoteRecord, TopicRecord} from './support/data.js'
//import { ManagedNotesData } from '@/components/support/data.js'
import { camelize } from '@/components/support/utils.js'

import Draggable from '@/components/support/Draggable.vue'
import NotesIO from '@/components/support/NotesIO.vue'
import Guide from '@/components/support/Guide.vue'

import { mapStores } from 'pinia'
import { useAppDisplay } from '@/stores/AppDisplay'
import { useUserContent } from '@/stores/UserContent'

const stagingNotesList = 'stagingNotes'


export default {
    name: 'Sidebar',
    /*
    props: ['note'],
    watch: {
        note: {
            handler: function (newNote, oldNote) {
                //console.log('Prop changed: ', newNote, ' | was: ', oldNote)
                const noteItem = JSON.parse(JSON.stringify(newNote))
                this.userContentStore.managedNotes.notes.push(noteItem)
                this.$refs.btnSidebar.click()
            },
            deep: true
        }
    },*/
    components: {
        Draggable,
        NotesIO: NotesIO,
        Guide
    },
    data() {
        return {
            //topics: ManagedNotesData.value.topics,
            //notes: ManagedNotesData.value.notes,

            stagingNotesList: stagingNotesList,
            dropZoneName: {
                createDropList: ''
            },

            guides: {
                managedNotes: {
                    id: 'managedNotes',
                    title: 'Notes Manager',
                    markdown: `This sidebar allows the user to create Notes
  and organize them by Topics.  These can be \`Exported\` to a file, saved for 
  continued work or shared with other users, then \`Imported\` in to a new 
  session.
  
  The \`Staging Notes\` section allows the user to automatically add notes 
  from document search results, or manually add user-created notes, before
  assigning (by dragging) them to a Topic.  Notes can be deleted by clicking 
  the chevron button \`>>\` beneath them.
  
  The \`Topics\` section allows the user to create (or delete) Topics.  Notes 
  from the Staging area, or other Topics, can be dragged beneath any Topic.  
  By clicking the boxed \`X\` to the right of the Topic, the Topic and all 
  associated Notes are deleted.`
                }
            }
        }
    },
    mounted(){
        this.userContentStore.setPlaceholders()
    },
    computed:{
        ...mapStores(useAppDisplay, useUserContent),
        getTopics(){
            return this.userContentStore.managedNotes.topics
        }
    },
    methods: {
        // Topics
        addTopic(e) {
            const value = e.target.value.trim()
            if (!value) {
                return
            }
            const dzName = camelize(value) + Date.now()
            this.dropZoneName = { ...this.dropZoneName, createDropList: dzName }
            const topicRecord = {
                id: Date.now(),
                title: value,
                dropZoneName: dzName
            }
            this.userContentStore.managedNotes.topics.push(topicRecord)
            e.target.value = ''
        },
        removeTopic(topic) {
            this.userContentStore.managedNotes.topics.splice(this.userContentStore.managedNotes.topics.indexOf(topic), 1)
        },

        // Notes
        addNote(e) {
            const value = e.target.value.trim()
            if (!value) {
                return
            }
            const noteRecord = {
                id: Date.now(),
                list: stagingNotesList,
                type: 'hand',
                innerHTML: '',
                innerText: value,
            }
            this.userContentStore.managedNotes.notes.push(noteRecord)
            e.target.value = ''
        },
        removeNote(note) {
            this.userContentStore.managedNotes.notes.splice(this.userContentStore.managedNotes.notes.indexOf(note), 1)
        },
        /*TODO: editNote could be used to edit an existing note, but maybe this is overly-complicated
        editNote(topic) {
            this.beforeEditCache = topic.title
            this.editedTopic = topic
        },*/
        checkMove: function (e) {
            //window.console.log("Future index: " + e.draggedContext.futureIndex);
        },
        log: function (e) {
            //window.console.log(e);
        }
    }
}


// Support Functions



/*
TODO: ~~is this promise needed to create a NoteRecord object?~~ I don't understand the purpose of this function, maybe remove?
async function addNoteFromTable(newNote){
    return new Promise(function(resolve, reject){
        const noteRec = new NoteRecord(
                newNote.id, 
                stagingNotesList, 
                'auto', 
                newNote.innerHTML, 
                newNote.innerText
                )
        resolve(noteRec)
    })
}*/


</script>
  
  
  
<style scoped>
hr {
    border: ".75px solid black";
}

#btnSidebar {
    margin: 5px;
}

.fixed-large {
    width: 150px !important;
}

.note {
    font-size: 12px;
}

.description {
    font-size: .75rem;
}

.destroy {
    position: absolute;
    right: 0px;
    margin-right: 35px;
}

.section h3 {
    padding-top: 20px;
}

.ghost {
    opacity: 0.5;
    background: #c8ebfb;
}


/*ref: https://vuejs.org/examples/#todomvc
  .destroy {
      display: none;
      position: absolute;
      top: 0;
      right: 10px;
      bottom: 0;
      width: 40px;
      height: 40px;
      margin: auto 0;
      font-size: 30px;
      color: #949494;
      transition: color 0.2s ease-out;
  }
  .destroy:hover,
  .destroy:focus {
      color: #C18585;
  }
  .destroy:after {
      content: '×';
      display: block;
      height: 100%;
      line-height: 1.1;
  }*/
</style>