<template>
  <div>
    <b-navbar toggleable="lg" type="dark" variant="dark">

      <b-navbar-brand href="#">Logo</b-navbar-brand>

      <!--TOOD issue: why the warning-->
      <b-navbar-nav class="ml-auto middle">
        <!--<ImportData />-->

        <!--<b-button-group>-->
          <b-nav-form>
            <ImportData />
            <Sidebar :note="note" />
            <SaveWork />
            
          </b-nav-form>
        <!--</b-button-group>-->
      </b-navbar-nav>

      <!-- Right aligned nav items-->
      <b-navbar-nav class="ml-auto" right>
        <b-nav-form>
        <!--TODO task: fix profile
        <b-button sz="sm" class="my-2 my-sm-0" @click="modalAccount">-->
          <b-button @click="modalAccount">
          {{ this.userContentStore.name }}
        </b-button>
        <!--<b-nav-item href="#">About</b-nav-item>-->
        <About />
        </b-nav-form>
      </b-navbar-nav>

    </b-navbar>
  </div>

  <div class="navbar-bottom">
    <b-form-group>
      <b-form-radio-group id="btn-radios-1" v-model="appDisplayStore.views.viewSelection"
        :options="appDisplayStore.views.viewOptions" name="radios-btn-default" buttons size="sm" v-on:input="viewInput">
      </b-form-radio-group>
    </b-form-group>
  </div>
</template>


<script>
import ImportData from '@/components/ImportData.vue'
import Sidebar from '@/components/SideBar.vue'
import SaveWork from '@/components/support/SaveWork.vue'
import About from '@/components/support/About.vue'

import { mapStores } from 'pinia'
import { useAppDisplay } from '@/stores/AppDisplay'
import { useUserContent } from '@/stores/UserContent'


export default {
  name: 'NavbarTop',
  components: {
    ImportData,
    Sidebar,
    SaveWork,
    About

  },
  data() {
    return {
      //name: 'John Doe'
    }
  },
  computed: {
    ...mapStores(useAppDisplay, useUserContent),

  },
  methods: {
    viewInput(checked) {
      this.appDisplayStore.viewSelection(checked)
    }
  }
}

</script>

<style scoped>
.navbar-brand {
  margin-right: 40px;
  margin-left: 40px;
}

.middle {
  margin-right: 40px;
  margin-left: 40px;
}

.navbar-bottom {
  background-color: black;
}

.btn-group {
  margin-left: 40px;
}
</style>