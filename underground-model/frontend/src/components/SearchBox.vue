<template>
  <v-container>
    <v-layout
      text-xs-center
      wrap
    >
      <v-flex xs12 class="button-row">
        <v-text-field
          v-model="query"
          label="What would you like to know?"
          ref="query"
          outline
          @keyup.enter="process_query"
        />
        <v-btn
          :disabled="loading"
          :loading="loading"
          class="white--text"
          color="blue darken-2"
          @click="process_query"
        >
          Tell me!
        </v-btn>
      </v-flex>
      <v-flex v-if="result && success" xs12>
        {{ result }}
      </v-flex>
      <v-flex v-else xs12>
        I can answer the following questions (in these exact forms, I'm really very dumb):
        <ul>
          <li>How do I get from -A- to -B-?</li>
          <li>What lines does -station- serve?</li>
        </ul>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import {queryApi} from "../api";

  export default {
    data: () => ({
      query: "",
      result: "",
      loading: false,
      success: false
    }),
    methods: {
      async process_query() {
        this.loading = true;
        [this.result, this.success] = await queryApi(this.query);
        this.loading = false;
      }
    }
  }
</script>

<style scoped>
.button-row {
  display: flex;
  flex-direction: row;
}

</style>
