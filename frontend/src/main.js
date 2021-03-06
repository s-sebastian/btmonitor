import Vue from 'vue'
import App from './App.vue'

import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.use(BootstrapVue)

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faArrowCircleDown,
  faArrowCircleUp,
  faCircleNotch,
  faExchangeAlt,
  faExclamationTriangle,
  faHistory,
  faPowerOff,
  faSpinner,
  faSyncAlt,
} from '@fortawesome/free-solid-svg-icons'

library.add(
  faArrowCircleDown,
  faArrowCircleUp,
  faCircleNotch,
  faExchangeAlt,
  faExclamationTriangle,
  faHistory,
  faPowerOff,
  faSpinner,
  faSyncAlt,
)
Vue.component('font-awesome-icon', FontAwesomeIcon)

Vue.config.productionTip = false

new Vue({
  render: h => h(App)
}).$mount('#app')
