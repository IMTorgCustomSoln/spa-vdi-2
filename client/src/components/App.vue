<template>
    <NavbarTop @input="viewInput" />

    <b-container fluid class="fluid-wide">
        <div v-if="userContentStore.documentsIndex.documents"> <!--TODO issue: Why is this not working??? -->
            <div v-show="appDisplayStore.views.viewSelection == 'search'">
                <b-row>
                    <b-col>
                        <SearchBar :records="userContentStore.documentsIndex.documents"
                            v-on:search-table-results="searchTable">
                        </SearchBar>
                    </b-col>
                </b-row>
            </div>

            <b-row>
                <b-col :cols="this.appDisplayStore.views.attrs.table.cols">
                    <Table :records="userContentStore.documentsIndex.documents" :search="searchTableResults"
                        :tableFields="this.appDisplayStore.views.attrs.table.fields"
                        :expansionBtn="this.appDisplayStore.views.attrs.table.toggleExpansionBtn"
                        >
                        {{ createTable }}
                    </Table>
                </b-col>

                <b-col :cols="this.appDisplayStore.views.attrs.pdfViewer.cols">
                    <div
                        v-if="appDisplayStore.views.viewSelection == 'read' && userContentStore.documentsIndex.documents.length > 0">
                        <PdfViewer />
                    </div>
                </b-col>
            </b-row>
        </div>
    </b-container>
</template>


<script>
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
        PdfViewer
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
    max-width: 2000px;
}
</style>