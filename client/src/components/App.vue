<template>
    <NavbarTop @input="viewInput" />

    <b-container fluid class="fluid-wide">
        <div v-if="userContentStore.documentsIndex.documents.length > 0">
            <div v-show="appDisplayStore.views.viewSelection == 'search'">
                <b-row>
                    <b-col>
                        <SearchBar :records="userContentStore.documentsIndex.documents"
                            v-on:search-table-results="searchTable">
                        </SearchBar>
                    </b-col>
                </b-row>
            </div>
            <div>
                <b-row>
                    <b-col cols="12">
                        <splitpanes class="default-theme" vertical style="height: 100%; width=100%;">
                            <pane :size="this.appDisplayStore.views.attrs.table.size">
                                <Table :records="userContentStore.documentsIndex.documents" :search="searchTableResults"
                                    :tableFields="this.appDisplayStore.views.attrs.table.fields"
                                    :expansionBtn="this.appDisplayStore.views.attrs.table.toggleExpansionBtn">
                                    {{ createTable }}
                                </Table>
                            </pane>
                            <pane :size="this.appDisplayStore.views.attrs.pdfViewer.size">
                                <div
                                    v-if="appDisplayStore.views.viewSelection == 'read' && userContentStore.documentsIndex.documents.length > 0">
                                    <PdfViewer />
                                </div>
                            </pane>
                        </splitpanes>
                    </b-col>
                </b-row>
            </div>
        </div>
    </b-container>
</template>


<script>
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'

import NavbarTop from '@/components/NavbarTop.vue'
import SearchBar from '@/components/SearchBar.vue'
import Table from '@/components/Table.vue'
import PdfViewer from '@/components/PdfViewer.vue'


import { mapStores } from 'pinia'
import { useAppDisplay } from '@/stores/AppDisplay'
import { useUserContent } from '@/stores/UserContent'


export default {
    name: 'App',
    components: {
        NavbarTop,
        SearchBar,
        Table,
        PdfViewer,

        Splitpanes, Pane
    },
    data() {
        return {
            view: {
                tableAttrs: {
                    colsTable: 12,
                    fields: [],
                    toggleExpansionBtn: true,
                },
                viewerAttrs: {
                    colsPdfViewer: 10,
                }
            },
            searchTableResults: {
                query: '',
                searchTerms: [],
                resultIds: [],
                resultGroups: []
            }
        }
    },
    computed: {
        ...mapStores(useAppDisplay, useUserContent),
    },
    methods: {
        searchTable(results) {
            this.searchTableResults = { ...this.searchTableResults, query: results.query }
            this.searchTableResults = { ...this.searchTableResults, searchTerms: results.searchTerms }
            this.searchTableResults = { ...this.searchTableResults, resultIds: results.resultIds }
            this.searchTableResults = { ...this.searchTableResults, resultGroups: results.resultGroups }
        },

    }
}

</script>

<style>
.fluid-wide {
    max-width: 2200px;
}
</style>