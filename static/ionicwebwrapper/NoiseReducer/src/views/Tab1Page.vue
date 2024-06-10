<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>NoiseReducer</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content :fullscreen="true">
      <ion-header collapse="condense">
        <ion-toolbar>
          <ion-title size="large">NoiseReducer</ion-title>
        </ion-toolbar>
      </ion-header>

      <div v-if="stage == 'init'">
        <div id="app" style="margin-left: 18px; margin-right: 20px; margin-top: 10vh;">
          <FilePond v-on:processfile="handleFilePondInit" name="assets" credits="false" allow-multiple="true"
            max-files="1" :server="'/fileUploadTemporary'" />
        </div>
      </div>
      <div v-if="stage == 'processing'"style="margin-left: 18px; margin-right: 20px; margin-top: 10vh;">
        <h1>File Uploaded Successfully.</h1>
        <ion-spinner name="circles" style="margin-top: 3vh;"></ion-spinner>
      </div>
      <div v-if="stage == 'ready'"style="margin-left: 18px; margin-right: 20px; margin-top: 10vh;">
        <h1>File is ready!</h1>
        <audio controls :src="fileurl_onserver_output" style="margin-top: 15px;">
          Your browser does not support the audio element.
        </audio>
      </div>
    </ion-content>
  </ion-page>
</template>

<script lang="ts">
import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonSpinner } from '@ionic/vue';
// Import FilePond
import vueFilePond from 'vue-filepond';

// Import plugins
//@ts-ignore
import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type/dist/filepond-plugin-file-validate-type.esm.js';
//@ts-ignore
import FilePondPluginImagePreview from 'filepond-plugin-image-preview/dist/filepond-plugin-image-preview.esm.js';

// Import styles
import 'filepond/dist/filepond.min.css';
import 'filepond-plugin-image-preview/dist/filepond-plugin-image-preview.min.css';

// Create FilePond component
const FilePond = vueFilePond(FilePondPluginFileValidateType, FilePondPluginImagePreview);

export default {
  name: "app",
  components: {
    //@ts-ignore
    FilePond: vueFilePond(),
    IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonSpinner
  },
  data: function () {
    return { stage: "init", fileid_onserver: null, fileurl_onserver_output: null, apiserver: '' };
  },
  methods: {
    handleFilePondInit: function (e = "") {
      //
    },
    fileuploadprogress() {
      console.log('File Upload Progress:');
    },
    tryToFetchOutputFile(filename = null) {
      //@ts-ignore
      let parent_this = this;
      //@ts-ignore
      fetch(localStorage.getItem('API_SERVER_URL') + '/fileCheckOutput/' + this.fileid_onserver, {
        method: 'GET', // or 'POST'
        headers: {
          'Content-Type': 'application/json',
          // 'Authorization': 'Bearer your-token(optional)'
        }
      })
        .then(response => {
          if (response.status == 202) {
            setInterval(() => {
              parent_this.tryToFetchOutputFile(filename);
            }, 5000);
          } else if (response.status == 200) {
            //@ts-ignore
            parent_this.stage = "ready";
            //@ts-ignore
            parent_this.fileurl_onserver_output = localStorage.getItem('API_SERVER_URL') + '/fileGetOutput/' + this.fileid_onserver;
          }
        })
        .then(data => console.log(data))
        .catch((error) => {
          console.error('Error:', error);
        });
    }
  },
  mounted() {
    const urlParams = new URLSearchParams(window.location.search);
    let server_address = urlParams.get('server_address');
    (this as any).apiserver = server_address;
    if (server_address) {
      localStorage.setItem('API_SERVER_URL', server_address);
    } else {
      localStorage.setItem('API_SERVER_URL', 'http://127.0.0.1:8085/');
    }
    //@ts-ignore
    let parent_this = this;
    document.addEventListener('FilePond:processfile', (e) => {
      //@ts-ignore
      console.log('FilePond Widget Info: File Process Event', e.detail);
      //@ts-ignore
      if (e.detail.error == null) {
        console.log('File Uploaded Successfully.');
        //@ts-ignore
        parent_this.fileid_onserver = e.detail.file.serverId;
        //@ts-ignore
        parent_this.stage = "processing";
        //@ts-ignore
        parent_this.tryToFetchOutputFile(e.detail.file.filename);
      }
    });
  }
};
</script>
