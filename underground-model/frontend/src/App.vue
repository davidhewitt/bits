<template>
  <v-app>
    <v-toolbar app>
      <v-toolbar-title class="headline text-uppercase">
        <span>underground</span>
        <span class="font-weight-light">Guru</span>
      </v-toolbar-title>
    </v-toolbar>

    <v-content>
      <SearchBox/>
    </v-content>
  </v-app>
</template>

<script>
import SearchBox from './components/SearchBox'

export default {
  name: 'App',
  components: {
    SearchBox
  },
  data () {
    return {
      //
    }
  }
}
</script>
