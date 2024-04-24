<template>
    <!-- Search -->
    <b-row id="table-panel">
        <b-col>
            <h5 style="display:inline">Search: </h5>
            <Guide v-bind="guides.search" />
            <b-input-group>
                <template #prepend>
                    <b-dropdown 
                        :text="queryOptions[selectedIdx].value" 
                        v-model="selectedIdx" 
                        variant="outline-primary"
                        >
                        <b-dropdown-item v-for="option in queryOptions" :key="option.id" @click="changeItem(option)">
                            {{ option.value }}
                        </b-dropdown-item>
                    </b-dropdown>
                </template>

                <b-form-input type="text" class="form-control" id="search-field" v-model="query" @input="searchQuery"
                    :disabled="queryOptions[selectedIdx].disablePrompt" placeholder="type search text here..." />
            </b-input-group>
            <div id="results-summary">
                <div v-if="searchDisplayResults.searchTerms">
                    <div v-if="!searchDisplayResults.errorMsg" style="white-space: pre-line">{{ searchResultsCount }}</div>
                    <div v-else class="errorMsg"> {{ searchDisplayResults.errorMsg }}</div>
                </div>
            </div>
        </b-col>
    </b-row>
</template>    


<script>
import { mapStores } from 'pinia'
import { useUserContent } from '@/stores/UserContent'

import Guide from '@/components/support/Guide.vue'
//import {DocumentIndexData} from '@/components/support/data'

export default {
    name: 'SearchBar',
    props: {
        records: Array
    },
    watch: {
        records: {
            handler: function (newVal, oldVal) {
                //console.log('Prop changed: ', newVal, ' | was: ', oldVal)
                if (Array.isArray(this.$props.records) &&
                    this.$props.records.length > 0
                ) {
                    //this.createIndex()
                    this.userContentStore.createIndex(this.$props.records)
                }
            },
            deep: true
        }
    },
    emits: ['search-table-results'],
    components: {
        Guide
    },
    data() {
        //this.indices = DocumentIndexData.value.indices
        return {
            selectedIdx: 0,
            query: '',
            queryOptions: [
                {id:0, value:'Fuzzy', disablePrompt:false},
                {id:1, value:'Exact', disablePrompt:false},
                {id:2, value:'Concept', disablePrompt:false},
                {id:3, value:'Models', disablePrompt:true}
            ],
            searchTableResults: {
                type: null,
                query: '',
                terms: [],
                resultIds: [],
                resultGroups: []
            },
            searchDisplayResults: {
                count: 0,
                totalDocuments: 0,
                searchTerms: '',
                displayLimit: 0,
                errorMsg: '',
                mouseOverSnippet: ''
            },
            guides: {
                search: {
                    id: 'search',
                    title: 'Search Patterns',
                    markdown: `The following types of search are possible:
* Fuzzy match - matches terms' stem to using different patterns
* Exact match - precisely matches the terms
* Concept search - finds terms that are conceptually similar
* (Pre-run) Models search - work with models previously applied to the documents (no search terms necessary)
                                        

_Fuzzy match_ - terms are matched on their stem by default 
* \`foo\` - all search is on stemmed terms so don't worry about case or word ending ('-ed', '-es', '-ing', ...)
* \`+foo +bar\` - for logical AND search; otherwise, all search use OR by default
* \`+foo bar -baz\` - match pattern without 'baz'
* \`*foo\` - search terms with characters before foo ('*' is a _wildcard_)
* \`title: foo\` - only search document titles for term foo
* \`foo^10 bar\` - weight term foo 10-times the importance of bar
* \`foo~1\` - one edit distance of foo (fuzzy matching)

_Exact match_ - terms are matched exactly (case sensitive)\n` +
                        '* \`foo bar\` - single exact match \n' +
                        '* \`foo bar, bar baz\` - multiple exact matches separated by comma\n' +
                        `
The results are ordered by the 'Score' column, which is a weighted formula of the matching pattern.`
                }
            }
        }
    },
    mounted() {
        //this.createIndex()
        this.userContentStore.createIndex(this.$props.records)
    },
    computed: {
        ...mapStores(useUserContent),
        searchResultsCount() {
            return this.query != '' ? `Search returned ${this.searchDisplayResults.count} hits, in ${this.searchDisplayResults.totalDocuments} documents \nTerms used: ${this.searchDisplayResults.searchTerms}` : ''
        },
    },
    methods: {
        changeItem(option){
            this.selectedIdx = option.id
            console.log(option.id)
            this.resetAllItems()
            this.searchQuery()
        },/*
        createIndex() {
            //create lunr index
            const records = this.$props.records
            const lunrIndex = lunr(function () {
                this.ref('id')
                this.field('clean_body')
                this.metadataWhitelist = ['position']
                records.forEach(function (rec) {
                    this.add(rec)
                }, this)
            })
            //add to context
            this.userContentStore.documentsIndex.indices.lunrIndex = lunrIndex
        },*/
        continueWorkspaceIndex() {
            //TODO: use previous index if saved Workspace file is loaded
        },
        searchFuzzy(){
            //query lunrjs index
            const queryVal = this.query
                var searchTerms = ''
                var results = ''
                try {
                    searchTerms = this.userContentStore.documentsIndex.indices.lunrIndex.pipeline.run(lunr.tokenizer(queryVal))
                    this.searchDisplayResults = { ...this.searchDisplayResults, searchTerms: searchTerms }
                    results = this.userContentStore.documentsIndex.indices.lunrIndex.search(queryVal).map(resultFile => { return resultFile })
                } catch (error) {
                    this.searchDisplayResults = { ...this.searchDisplayResults, errorMsg: error }
                    this.resetAllItems()
                    return false
                }
                const resultIds = results.map(resultFile => resultFile.ref)
                console.log(`resultdIds: ${resultIds}`)
                this.searchTableResults = { ...this.searchTableResults, resultIds: resultIds }
                this.searchDisplayResults = { ...this.searchDisplayResults, totalDocuments: resultIds.length }

                //get hit counts for individual doc and total docs
                const resultGroups = []
                for (let resultFile of results) {
                    let new_keys = Object.keys(resultFile.matchData.metadata)
                    let counts = []
                    let positions = []
                    let rec = {}
                    rec['ref'] = resultFile.ref
                    rec['score'] = resultFile.score.toFixed(3)
                    for (let key of new_keys) {
                        counts.push(resultFile.matchData.metadata[key].clean_body.position.length)
                        positions.push(...resultFile.matchData.metadata[key].clean_body.position)
                    }
                    rec['count'] = counts.reduce((pv, cv) => { return pv + cv }, 0)
                    rec['positions'] = positions.sort(compareByFirstItem)
                    resultGroups.push(rec)
                }
                let totalCount = 0
                totalCount = resultGroups.reduce(function (pv, cv) { return pv + cv.count }, 0)
                this.searchDisplayResults = { ...this.searchDisplayResults, count: totalCount }
                this.searchTableResults = { ...this.searchTableResults, resultGroups: resultGroups }
                console.log(`resultGroups (array of all hits within a doc): `); console.log(resultGroups)

                this.$emit('search-table-results', this.searchTableResults)

        },
        searchExact(){
            //TODO, fix: not working!
            //collect phrases
            const phrases = []
                let substr = ''
                let select = false
                //phrases are separated by commas ','
                if( this.query.includes(',') == false ){
                    phrases.push(this.query)
                } else {
                    for (let char of this.query) {
                        if (char == ',' && select == false) {
                            select = true
                        } else if (char == ',' && select == true) {
                            select = false
                            phrases.push(substr)
                            substr = ''
                        } else if (select) {
                            substr += char
                        }
                    }
                }
                /*
                for (let char of this.query) {
                    if (char == '`' && select == false) {
                        select = true
                    } else if (char == '`' && select == true) {
                        select = false
                        phrases.push(substr)
                        substr = ''
                    } else if (select) {
                        substr += char
                    }
                }*/
                //select hits for each phrase
                const resultGroups = []
                try {
                    for (let record of this.$props.records) {
                        const result = {
                            ref: record.id,
                            phrase: [],
                            score: "0.0",
                            count: 0,
                            positions: []
                        }
                        for (let phrase of phrases) {
                            const hit = record.clean_body.includes(phrase)
                            if (hit) {
                                const indices = getIndicesOf(phrase, record.clean_body, true)
                                result.phrase.push(phrase)
                                result.count = result.count + indices.length
                                result.positions.push(...indices)
                            }
                        }
                        resultGroups.push(result)
                    }
                } catch (error) {
                    this.searchDisplayResults = { ...this.searchDisplayResults, errorMsg: error }
                    this.resetAllItems()
                    return false
                }
                const totalCount = resultGroups.map(item => item.positions.length).map((sum => value => sum += value)(0))[resultGroups.length - 1]
                const resultIds = removeDuplicatesUsingSet(resultGroups.filter(item => item.positions.length > 0).map(result => result.ref))
                resultGroups.map(result => result.score = parseFloat(result.count / totalCount).toFixed(2))

                this.searchDisplayResults = { ...this.searchDisplayResults, searchTerms: phrases }
                this.searchDisplayResults = { ...this.searchDisplayResults, totalDocuments: resultIds.length }
                this.searchDisplayResults = { ...this.searchDisplayResults, count: totalCount }

                this.searchTableResults = { ...this.searchTableResults, query: this.query }
                this.searchTableResults = { ...this.searchTableResults, searchTerms: phrases }
                this.searchTableResults = { ...this.searchTableResults, resultIds: resultIds }
                this.searchTableResults = { ...this.searchTableResults, resultGroups: resultGroups }

                this.$emit('search-table-results', this.searchTableResults)

        },
        searchConcept(){

        },
        searchModel(){
            /*
            models = {"search":"FS","target":" Do we each want to do an intro or something?","timestamp":[0,1.8],"pred":1}
            steps:
                * <Table> $props.search
                * filterTable()
                * expandAdditionalInfo(row) > createSearchSnippets(row, MARGIN = 250)
                * v-if='models' , then show selectable confidence_level range
            
            */
           this.query = '< pre-run models >'
           const phrases = []
           const type = null
           const query = ''
           const resultIds = []
           const resultGroups = []
           for(const [idx, rec] of Object.entries(this.$props.records) ){
            resultIds.push(rec.id)
            const sum = rec.models.map(item => item.pred).reduce((partial_sum, a) => partial_sum + a,0)
            const totalScore = sum / rec.models.length
            const result = {
                            ref: rec.id,
                            phrase: [],
                            score: String(totalScore),
                            count: 0,
                            positions: []
                        }
            for(const model of rec.models){
                const hit = rec.clean_body.includes(model.target)
                if (hit) {
                    const indices = getIndicesOf(model.target, rec.clean_body, true)
                    result.phrase.push( model.target ) //String([model.timestamp]) )                 //TODO:ISSUE - `[0,N.N]` should be a complete string from python
                    result.count = result.count + indices.length
                    result.positions.push(...indices)
                }
            }
            resultGroups.push(result)
            }
            const totalCount = resultGroups.map(item => item.positions.length).map((sum => value => sum += value)(0))[resultGroups.length - 1]
            //const resultIds = removeDuplicatesUsingSet(resultGroups.filter(item => item.positions.length > 0).map(result => result.ref))
            phrases.push( ...removeDuplicatesUsingSet(resultGroups.map(item => item.phrase)) )
            const formattedPhrases = [phrases[0].slice(0,3).join('\u00A0 ...\n \u00A0\u00A0\u00A0\u00A0')]

            this.searchDisplayResults = { ...this.searchDisplayResults, searchTerms: formattedPhrases }
            this.searchDisplayResults = { ...this.searchDisplayResults, totalDocuments: resultIds.length }
            this.searchDisplayResults = { ...this.searchDisplayResults, count: totalCount }

            this.searchTableResults = { ...this.searchTableResults, query: this.query }
            this.searchTableResults = { ...this.searchTableResults, searchTerms: phrases }
            this.searchTableResults = { ...this.searchTableResults, resultIds: resultIds }
            this.searchTableResults = { ...this.searchTableResults, resultGroups: resultGroups }

            this.$emit('search-table-results', this.searchTableResults)

        },
        searchQuery() {
            /* Provide tableFilter of selected rows' id based on `this.query` input

            :query str - from text input, should match lunrjs patterns
            :filter [] - selected files' ids
            */
           this.searchQuery.type = this.queryOptions[this.selectedIdx]

            console.log(`query: ${this.query}`)
            this.searchTableResults = { ...this.searchTableResults, query: this.query }
            this.searchDisplayResults = { ...this.searchDisplayResults, errorMsg: '' }
            //const backticksLength = (this.query.match(/`/g) || []).length
            //const checkBackticks = backticksLength > 0 && backticksLength % 2 == 0

            // no query input
            if (this.query == null && this.searchQuery.type.disablePrompt == false){
                return false

            } else if(this.query.length === 0 && this.searchQuery.type.disablePrompt == false) {
                this.resetAllItems()
                this.$emit('search-table-results', this.searchTableResults)
                return false

                // exact phrase search
            } else if (this.searchQuery.type.value == 'Exact') {
                this.searchExact()

                // concept search
            } else if (this.searchQuery.type.value == 'Concept') {
                this.searchConcept()

                // prior-run models search
            } else if (this.searchQuery.type.value == 'Models') {
                this.searchModel()
                
                // lunrJs query
            //} else if (this.userContentStore.documentsIndex.indices.lunrIndex) {
            } else if (this.searchQuery.type.value == 'Fuzzy' && this.userContentStore.documentsIndex.indices.lunrIndex) {
                this.searchFuzzy()
            } else {
                return false
            }
        },
        resetAllItems() {
            this.query = ''
            this.searchTableResults = { ...this.searchTableResults, query: '' }
            this.searchTableResults = { ...this.searchTableResults, resultIds: [] }
            this.searchTableResults = { ...this.searchTableResults, resultGroups: [] }

            this.searchDisplayResults = { ...this.searchDisplayResults, count: 0 }
            this.searchDisplayResults = { ...this.searchDisplayResults, totalDocuments: 0 }
            this.searchDisplayResults = { ...this.searchDisplayResults, searchTerms: '' }
            this.searchDisplayResults = { ...this.searchDisplayResults, displayLimit: 0 }
        },
    },
}




function compareByFirstItem(a, b) {
    if (a[0] < b[0]) {
        return -1;
    }
    if (a[0] > b[0]) {
        return 1;
    }
    return 0;
}

function getIndicesOf(searchStr, str, caseSensitive = false) {
    const searchStrLen = searchStr.length
    if (searchStrLen == 0) {
        return []
    }
    let startIndex = 0, index, indices = []
    if (!caseSensitive) {
        str = str.toLowerCase()
        searchStr = searchStr.toLowerCase()
    }
    while ((index = str.indexOf(searchStr, startIndex)) > -1) {
        indices.push([index, searchStrLen])
        startIndex = index + searchStrLen
    }
    return indices
}

function removeDuplicatesUsingSet(arr) {
    let outputArray = Array.from(new Set(arr))
    return outputArray
}

</script>



<style scoped>
.text {
    white-space: pre-wrap;
}
#table-panel{
    padding-bottom: 30px;
}
#results-summary{
    padding-left: 25px;
}
</style>