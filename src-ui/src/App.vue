<template>
    <div class="container">
        <h1 class="py-5">
            IPZS Document classification demo
        </h1>
        <div v-if="loading_page">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
        <div v-else>
            <form>
                <div class="row mb-3">
                    <div class="col-md-12">
                        <label for="title_field" class="form-label">Inserire il titolo:</label>
                        <input id="title_field" class="form-control" type="text" v-model.trim="title">
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-12">
                        <label for="text_field" class="form-label">Inserire il testo:</label>
                        <textarea id="text_field" rows="5" class="form-control" v-model.trim="text"></textarea>
                    </div>
                </div>
                <div class="row form-group">
                    <label class="mb-3 col-6 col-md-3 col-xl-1 col-form-label text-end">
                        Modello:
                    </label>
                    <div class="mb-3 col-6 col-md-6 col-xl-3">
                        <select class="form-select" v-model="model">
                            <option selected="selected" value="">[Seleziona]</option>
                            <option v-for="(t, index) in models" :key="index" :value="index">
                                {{ index }}
                            </option>
                        </select>
                    </div>
                    <div class="mb-3 col-12 col-md-3 col-xl-2 ps-5 text-center">
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="checkbox" id="greedy" value="greedy" v-model="greedy"
                                   :disabled="!use_max || !use_threshold">
                            <label class="form-check-label" for="greedy">Greedy</label>
                            <span class="ms-2" data-bs-toggle="tooltip"
                                  data-bs-title="Stabilisce se le due regole seguenti vanno in AND oppure in OR"><i class="bi bi-info-circle"></i></span>
                        </div>
                        <label class="col-form-label">
                            &nbsp;
                        </label>
                    </div>
                    <div class="mb-3 col-6 col-xl-2 text-end">
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="checkbox" id="max_check" value="max_check"
                                   v-model="use_max">
                            <label class="form-check-label" for="max_check">Usa</label>
                        </div>
                        <label class="col-form-label">
                            Max risultati:
                        </label>
                    </div>
                    <div class="mb-3 col-6 col-xl-1">
                        <input class="form-control" name="max" v-model="max" type="number" min="1" max="50"
                               :disabled="!use_max"/>
                    </div>
                    <div class="mb-3 col-6 col-xl-2 text-end">
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="checkbox" id="threshold_check" value="threshold_check"
                                   v-model="use_threshold">
                            <label class="form-check-label" for="threshold_check">Usa</label>
                        </div>
                        <label class="col-form-label">
                            Soglia:
                        </label>
                    </div>
                    <div class="mb-3 col-6 col-xl-1">
                        <input class="form-control" name="max" v-model="threshold" type="number" min="1" max="100"
                               :disabled="!use_threshold"/>
                    </div>
                </div>
                <div class="row row-cols-lg-auto g-3 align-items-center">
                    <div class="col-12" style="margin-left: auto;">
                        <button class="btn btn-primary" @click.prevent="send">Invia dati</button>
                    </div>
                </div>
            </form>
            <div v-if="launched">
                <h2 class="py-4">
                    Results
                </h2>
                <div v-if="loading_results">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
                <div v-else>
                    <div v-if="results.length == 0">
                        No results to show.
                    </div>
                    <ul v-else class="list-group">
                        <li class="list-group-item" v-for="(result, index) in results" :key="index">
                            <span class="badge text-bg-primary">{{ result.score.toFixed(2) }}</span>
                            <span class="badge text-bg-success ms-2">{{ model_type }}-{{ result.label }}</span>
                            {{ result.description }}
                            <span v-if="result.mapping" class="badge text-bg-warning ms-2">→ euvoc-{{
                                    result.mapping.label
                                }} - {{ result.mapping.description }}</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</template>

<script>

import axios from "axios";
import {Tooltip} from 'bootstrap'

export default {
    name: 'App',
    data() {
        return {
            models: {},
            use_threshold: true,
            use_max: true,
            greedy: true,
            title: "",
            text: "",
            threshold: 50,
            max: 10,
            model: "",
            loading_results: false,
            loading_page: true,
            launched: false,
            results: [],
            model_type: ""
        }
    },
    methods: {
        send: function () {

            let thisBak = this;

            if (!this.model) {
                alert("Please select model");
                return;
            }

            if (!this.text && !this.title) {
                alert("Please insert title or text");
                return;
            }

            this.launched = true;
            this.loading_results = true;
            let requestData = {};
            requestData["title"] = this.title;
            requestData["text"] = this.text;
            requestData['model'] = this.model;
            if (this.use_threshold) {
                requestData["threshold"] = this.threshold / 100;
            }
            if (this.use_max) {
                requestData["top_k"] = this.max;
            }
            if (this.use_max && this.use_threshold) {
                requestData['greedy'] = this.greedy;
            }
            let post_config = {headers: {"Token": process.env.VUE_APP_TOKEN}};
            axios.post(process.env.VUE_APP_API_URL + "/api", requestData, post_config).then(function (response) {
                thisBak.results = response.data;
                thisBak.model_type = thisBak.models[thisBak.model];
            }).catch(function () {
                alert("Error!");
            }).then(function () {
                thisBak.loading_results = false;
            });
        }
    },
    mounted() {
        new Tooltip(document.body, {
            selector: "[data-bs-toggle='tooltip']",
        })
        let thisBak = this;
        axios.get(process.env.VUE_APP_API_URL + "/").then(function (response) {
            thisBak.models = response.data;
        }).catch(function () {
            alert("Unable to get the list of models, please try again.")
        }).then(function () {
            thisBak.loading_page = false;
        });
    }
}
</script>

<style>
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    /*text-align: center;*/
    color: #2c3e50;
    /*margin-top: 60px;*/
}

</style>
