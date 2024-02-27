
<template>
    <div class="action-bar">
        <b-icon-chevron-bar-left class="h5 mb-1 border" font-scale="1" @click="selectDisplayedPage(1)"/>
        <b-icon-chevron-compact-left class="h5 mb-1 " font-scale="1" @click="prev()"/>
        <input size="1" v-model="pageNum"/>
        <b-icon-chevron-compact-right class="h5 mb-1 " font-scale="1" @click="next()"/>
        <b-icon-chevron-bar-right class="h5 mb-1 border" font-scale="1" @click="selectDisplayedPage(-1)"/>
    </div>
    <b-carousel 
        ref="myCarousel"
        v-model="pageIdx"
        controls
        indicators
        :interval="0"
        >
        <!-- slides go here -->
        <b-carousel-slide v-for="(page, index) in pages" :img-src="page"></b-carousel-slide>
    </b-carousel>
</template>

<script>

export default {
    name: 'FlipBook',
    props: {
        selectedPage: String,
        imageArray: Array
    },
    watch: {
        pageNum:{
            handler(newVal){
                this.pageIdx = newVal - 1
            }
        },
        selectedPage:{
            handler(newSelectedPage){
                const pg = newSelectedPage.split('pg.')[1].split('|')[0]
                this.pageNum = parseInt(pg)
            }
        },
        imageArray: {
            handler(newImageArray, oldImageArray) {
                this.setupPages()
            },
            deep: true
        },   
    },
    mounted(){
        this.setupPages()
    },
    data(){
        return{
            pageIdx: 0,
            pageNum: 1,
            pages: []
        }
    },
    methods:{
        setupPages(){
            let images = this.$props.imageArray.map(img => img.img)
            this.pages.push(...images)
        },
        selectDisplayedPage(num){
            const n = parseInt(num)
            if (n == -1){
                const idx = this.imageArray.length
                this.pageNum = idx
                this.pageIdx = idx - 1
                this.$refs.myCarousel.setSlide(this.pageIdx)
            } else {
            this.pageNum = n
            this.pageIdx = n - 1
            this.$refs.myCarousel.setSlide(this.pageIdx)
            }
        },
        prev(){
            this.$refs.myCarousel.prev()
            this.pageNum = this.$refs.myCarousel.index + 1
        },
        next(){
            this.$refs.myCarousel.next()
            this.pageNum = this.$refs.myCarousel.index + 1
        }
}
}
</script>

<style scoped>
.action-bar {
  width: 100%;
  height: 30px;
  padding: 10px 0;
  display: flex;
  justify-content: center;
  align-items: center;

/* allow page images to float up and over image*/
  z-index: 10;
  position: absolute;
}
.action-bar input{
    text-align: center;
    border-color: #e1e1e1;
    font-size: 12px;
}
</style>