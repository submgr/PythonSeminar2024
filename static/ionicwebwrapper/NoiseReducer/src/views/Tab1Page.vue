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
        <div id="app" style="margin-left: 4vw; margin-right: 5vw; margin-top: 10vh;">
        <FilePond @processfile="handleFileUploaded" name="assets" credits="false" allow-multiple="true" max-files="1"
          server="http://127.0.0.1:5000/fileUploadTemporary" />
      </div>
      </div>
      <div v-if="stage == 'processing'">
        <h1>File Uploaded Successfully. {{ fileid_onserver }}<br/>Please wait...</h1>
      </div>
      <div v-if="stage == 'ready'">
        <h1>File is ready.</h1>
        <a :href="fileurl_onserver_output"> {{ fileurl_onserver_output }}</a>
      </div>
    </ion-content>
  </ion-page>
</template>

<script lang="ts">
import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent } from '@ionic/vue';
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
    IonPage, IonHeader, IonToolbar, IonTitle, IonContent
  },
  data: function () {
    return { stage: "init", fileid_onserver: null, fileurl_onserver_output: null};
  },
  methods: {
    tryToFetchOutputFile(filename = null){
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
        if(response.status == 202){
          setInterval(() => {
            parent_this.tryToFetchOutputFile(filename);
          }, 2000);
        }else if(response.status == 200){
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
    if (server_address) {
      localStorage.setItem('API_SERVER_URL', server_address);
    } else {
      localStorage.setItem('API_SERVER_URL', 'http://127.0.0.1:5000/');
    }
    //@ts-ignore
    let parent_this = this;
    document.addEventListener('FilePond:processfile', (e) => {
      //@ts-ignore
      console.log('FilePond Widget Info: File Process Event', e.detail);
      //@ts-ignore
      if(e.detail.error == null) {
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
