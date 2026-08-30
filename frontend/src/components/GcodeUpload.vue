<script setup>
    import { ref } from 'vue'
    import axios from 'axios'

    const props = defineProps({
      machineId: {
        type: Number,
        default: 1
      }
    })


    const raw_file = ref(null)

    
    const file_name = ref("")

    const file_input = ref(null)

    const trigger_file_select = () => {
        file_input.value.click()
    }

    const on_file_selected = (event) => {
        const file = event.target.files[0]

        if (file) {
            file_name.value = file.name
            raw_file.value = file
        }
    }

    const upload_gcode = async () => {
      if (!raw_file.value) {
        alert("Please select a G-code file")
        return
      }
      try {
        const form_data = new FormData()
        

        form_data.append('file', raw_file.value)
        form_data.append('machine_id', props.machineId)

        await axios.post(`http://127.0.0.1:8000/telemetry/machines/${props.machineId}/upload-gcode`,
          form_data,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
        )
        
        
        alert("Success")

        ///////////////////////////////////////////////////
        const current_time = new Date();
        const generated_session_id = "session_" + current_time.getFullYear() + 
          String(current_time.getMonth() + 1).padStart(2, '0') + 
          String(current_time.getDate()).padStart(2, '0') + "_" + 
          String(current_time.getHours()).padStart(2, '0') + 
          String(current_time.getMinutes()).padStart(2, '0');
        
        console.log("[TRACE 1.3] Сгенерирован сессионный ID:", generated_session_id);
        
        await axios.post(`http://localhost:8000/telemetry/machines/${props.machineId}/set_session`, {
          session_id: generated_session_id
        })
        console.log("[TRACE 1.4] Запрос set_session улетел на FastAPI.");
        const commandPayload = {
          command: "RESET" 
        }
    
        
        await axios.post(`http://localhost:8000/telemetry/machines/${props.machineId}/set_command`, commandPayload)
        console.log("[TRACE 1.5] Команда RESET улетела на FastAPI.");
        ///////////////////////////////////////////////////
        raw_file.value = null      
        file_name.value = ""      
        
        if (file_input.value) {
            file_input.value.value = "" 
        }
      } catch (error) {
        console.log('Error: ', error)
      }
    }
</script>
<template>
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
    <h2 class="text-lg font-bold text-white mb-4">G-code uploading</h2>
    
    <div class="flex flex-col md:flex-row items-end gap-4">
      
      
      <div class="w-full md:w-1/4">
        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Target Machine ID</label>
        <input 
          v-model="props.machineId"
          type="number" 
          min="1"
          class="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white font-mono focus:outline-none focus:border-blue-500 transition"
        />
      </div>

      <input 
        type="file" 
        ref="file_input"
        class="hidden" 
        @change="on_file_selected"
      />

      <div class="w-full md:w-2/4 cursor-pointer" @click="trigger_file_select">
        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Selected G-code File</label>
        <div class="bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-slate-400 font-mono text-sm truncate">
            <span v-if="file_name === ''" class="text-slate-600">No file selected...</span>
            <span v-else class="text-slate-600">📄 {{ file_name }}</span>
        </div>
      </div>

      <div class="w-full md:w-1/4">
        <button
            @click="upload_gcode"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-200 cursor-pointer">
          Upload to Server
        </button>
      </div>

    </div>
  </div>
</template>