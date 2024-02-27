<template>
        <!-- Search -->
        <b-row id="table-panel">
            <b-col>
                <span>
                    <h5 style="display:inline">Search: </h5>
                    <Guide v-bind="guides.search"/>
                    <input 
                        type="text" 
                        class="form-control" 
                        id="search-field" 
                        v-model="query" 
                        @input="searchQuery" 
                        placeholder="type search text here..." 
                        />
                    <div v-if="searchDisplayResults.searchTerms">
                        <div v-if="!searchDisplayResults.errorMsg" style="white-space: pre-line">{{ searchResultsCount }}</div>
                        <div v-else class="errorMsg"> {{ searchDisplayResults.errorMsg }}</div>
                    </div>
                </span>
            </b-col>
        </b-row>
</template>    

<script>
import { mapStores } from 'pinia'
import { useUserContent } from '@/stores/UserContent'

import Guide from '@/components/support/Guide.vue'
//import {DocumentIndexData} from '@/components/support/data'

export default{
    name: 'SearchBar',
    props:{
        records: Array
    },
    watch: { 
        records: {
            handler: function(newVal, oldVal) {
                //console.log('Prop changed: ', newVal, ' | was: ', oldVal)
                if (Array.isArray(this.$props.records) && 
                    this.$props.records.length > 0
                    ){
                    this.createIndex()
                }
            },
            deep: false
        }
    },
    emits:['search-table-results'],
    components: {
        Guide
    },
    data(){
        //this.indices = DocumentIndexData.value.indices
        
        return{
            searchTableResults:{
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
                search:{
                    id:'search',
                    title:'Search Patterns',
                    markdown:`The following are patterns used in search terms:

_Fuzzy match_ - terms are matched on their stem by default 
* \`foo\` - all search is on stemmed terms so don't worry about case or word ending ('-ed', '-es', '-ing', ...)
* \`+foo +bar\` - for logical AND search; otherwise, all search use OR by default
* \`+foo bar -baz\` - match pattern without 'baz'
* \`*foo\` - search terms with characters before foo ('*' is a _wildcard_)
* \`title: foo\` - only search document titles for term foo
* \`foo^10 bar\` - weight term foo 10-times the importance of bar
* \`foo~1\` - one edit distance of foo (fuzzy matching)

_Exact match_ - terms surrounded by backticks '\`' (not quotes) are matched exactly (case sensitive)\n` +
'* \`` `foo bar` `\` - single exact match \n' + 
'* \`` `foo bar` `\` \`` `bar baz` `\` - multiple exact matches\n' + 
`
The results are ordered by the 'Score' column, which is a weighted formula of the matching pattern.`
                }
            }
        }
    },
    computed: {
        ...mapStores(useUserContent),
        searchResultsCount(){
            return this.query != '' ? `Search returned ${this.searchDisplayResults.count} hits, in ${this.searchDisplayResults.totalDocuments} documents \nTerms used: ${this.searchDisplayResults.searchTerms}`  : ''
        },
    },
    methods: {
        createIndex(){
            //create lunr index
            const records = this.$props.records
            const lunrIndex = lunr(function() {
                this.ref('id')
                this.field('clean_body')
                this.metadataWhitelist = ['position']
                records.forEach(function(rec) {
                    this.add(rec)
                }, this)
            })
            //add to context
            this.userContentStore.documentsIndex.indices.lunrIndex = lunrIndex
        },
        continueWorkspaceIndex(){
            //TODO: use previous index if saved Workspace file is loaded
        },
        searchQuery() {
            /* Provide tableFilter of selected rows' id based on `this.query` input

            :query str - from text input, should match lunrjs patterns
            :filter [] - selected files' ids
            */
            console.log(`query: ${this.query}`)
            this.searchTableResults = {...this.searchTableResults, query: this.query}
            this.searchDisplayResults = {...this.searchDisplayResults, errorMsg: ''}
            const backticksLength = (this.query.match(/`/g) || []).length
            const checkBackticks = backticksLength > 0 && backticksLength % 2 == 0

            // no query input
            if (this.query.length === 0){
                this.resetAllItems()
                this.$emit('search-table-results', this.searchTableResults)
                return false

            // exact phrase search using backticks
            } else if (checkBackticks) {
                //collect phrases
                const phrases = []
                let substr = ''
                let select = false
                for(let char of this.query){
                    if(char=='`' && select==false){ 
                        select=true
                    } else if(char=='`' && select==true){
                        select=false
                        phrases.push(substr)
                        substr = '' 
                    } else if(select){
                        substr += char
                    } 
                }
                //select hits for each phrase
                const resultGroups = []
                try{
                    for(let record of this.$props.records){
                        const result = {
                            ref: record.id,
                            phrase: [],
                            score: "0.0",
                            count: 0,
                            positions: []
                            }
                        for(let phrase of phrases){
                            const hit = record.clean_body.includes(phrase)
                            if(hit){
                                const indices = getIndicesOf(phrase, record.clean_body, true)
                                result.phrase.push(phrase)
                                result.count = result.count + indices.length 
                                result.positions.push(...indices)
                            }
                        }
                        resultGroups.push(result)
                    }
                } catch (error) {
                    this.searchDisplayResults = {...this.searchDisplayResults, errorMsg: error}
                    this.resetAllItems()
                    return false
                }
                const totalCount = resultGroups.map(item => item.positions.length).map((sum => value => sum +=value)(0))[ resultGroups.length - 1 ]
                const resultIds = removeDuplicatesUsingSet( resultGroups.filter(item => item.positions.length > 0 ).map(result => result.ref) )
                resultGroups.map(result => result.score = parseFloat(result.count / totalCount).toFixed(2)  )

                this.searchDisplayResults = {...this.searchDisplayResults, searchTerms: phrases}
                this.searchDisplayResults = {...this.searchDisplayResults, totalDocuments: resultIds.length}
                this.searchDisplayResults = {...this.searchDisplayResults, count: totalCount}

                this.searchTableResults = {...this.searchTableResults, query: this.query}
                this.searchTableResults = {...this.searchTableResults, searchTerms: phrases}
                this.searchTableResults = {...this.searchTableResults, resultIds: resultIds}
                this.searchTableResults = {...this.searchTableResults, resultGroups: resultGroups}

                this.$emit('search-table-results', this.searchTableResults)

            // lunrJs query
            } else if (this.userContentStore.documentsIndex.indices.lunrIndex) {
                
                //query lunrjs index
                const queryVal = this.query
                var searchTerms = ''
                var results = ''
                try {
                    searchTerms = this.userContentStore.documentsIndex.indices.lunrIndex.pipeline.run(lunr.tokenizer(queryVal))
                    this.searchDisplayResults = {...this.searchDisplayResults, searchTerms: searchTerms}
                    results = this.userContentStore.documentsIndex.indices.lunrIndex.search(queryVal).map(resultFile => { return resultFile })
                } catch (error) {
                    this.searchDisplayResults = {...this.searchDisplayResults, errorMsg: error}
                    this.resetAllItems()
                    return false
                }
                const resultIds = results.map(resultFile => resultFile.ref)
                console.log(`resultdIds: ${resultIds}`)
                this.searchTableResults = {...this.searchTableResults, resultIds: resultIds}
                this.searchDisplayResults = {...this.searchDisplayResults, totalDocuments: resultIds.length}

                //get hit counts for individual doc and total docs
                const resultGroups = []
                for(let resultFile of results){
                    let new_keys = Object.keys( resultFile.matchData.metadata )
                    let counts = []
                    let positions = []
                    let rec = {}
                    rec['ref'] = resultFile.ref
                    rec['score'] = resultFile.score.toFixed(3)
                    for (let key of new_keys){
                        counts.push( resultFile.matchData.metadata[key].clean_body.position.length )
                        positions.push( ...resultFile.matchData.metadata[key].clean_body.position )
                    }
                    rec['count'] = counts.reduce((pv,cv)=>{return pv+cv}, 0)
                    rec['positions'] = positions.sort(compareByFirstItem)
                    resultGroups.push( rec )
                    }
                let totalCount = 0
                totalCount = resultGroups.reduce(function(pv,cv) {return pv + cv.count}, 0)
                this.searchDisplayResults = {...this.searchDisplayResults, count: totalCount}
                this.searchTableResults = {...this.searchTableResults, resultGroups: resultGroups}
                console.log(`resultGroups (array of all hits within a doc): `); console.log(resultGroups)

                this.$emit('search-table-results', this.searchTableResults)
            } else {
                return false
            }
        },
        resetAllItems(){
            this.searchTableResults = {...this.searchTableResults, query: ''}
            this.searchTableResults = {...this.searchTableResults, resultIds: []}
            this.searchTableResults = {...this.searchTableResults, resultGroups: []}

            this.searchDisplayResults = {...this.searchDisplayResults, count: 0}
            this.searchDisplayResults = {...this.searchDisplayResults, totalDocuments: 0}
            this.searchDisplayResults = {...this.searchDisplayResults, searchTerms: ''}
            this.searchDisplayResults = {...this.searchDisplayResults, displayLimit: 0}
        },
    },
}




function compareByFirstItem( a, b ) {
  if ( a[0] < b[0] ){
    return -1;
  }
  if ( a[0] > b[0] ){
    return 1;
  }
  return 0;
}

function getIndicesOf(searchStr, str, caseSensitive=false){
    const searchStrLen = searchStr.length
    if(searchStrLen == 0){
        return []
    }
    let startIndex = 0, index, indices = []
    if(!caseSensitive){
        str = str.toLowerCase()
        searchStr = searchStr.toLowerCase()
    }
    while( (index = str.indexOf(searchStr, startIndex)) > -1){
        indices.push([index, searchStrLen])
        startIndex = index + searchStrLen
    }
    return indices
}

function removeDuplicatesUsingSet(arr){
    let outputArray = Array.from(new Set(arr))
    return outputArray
}



</script>




<style scoped>
.text{
    white-space: pre-wrap;
}

</style>