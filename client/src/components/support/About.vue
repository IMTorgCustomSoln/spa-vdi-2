<template>
    <!-- Open modal button -->
    <b-button
         id='btnAbout' 
         v-b-modal="'about-modal'"
         variant="primary"
         class=""
         >
         About
     </b-button>
 
     <!-- modal -->
     <b-modal id='about-modal' ok-only>
         <template #modal-title>
             About Visual Document Index (VDI)
         </template>
         <br>

         <div>
             <p>
             The Visual Document Index (VDI) browser application is designed to solve two problems:
             <ul>
                <li>flexibly search large amounts of text across multiple documents</li>
                <li>select, organize, and output references for follow-on work</li>
             </ul>
             It addresses these problems fairly well, but with some caveats.  Please review 
             the <code>Add More Files</code> modal for details.  
             
             These caveats will be addressed as the project progresses.
             </p>
         </div>
 
     </b-modal>
 </template>


<script>

export default {
    name: "About"
}

</script>


<style scoped>
.fixed-large{
    width: 150px !important;
    margin: 5px;
}
</style>