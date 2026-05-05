import { createRouter, createWebHashHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'
import HomeView from '../views/HomeView.vue'
import RegulationView from '../views/RegulationView.vue'
import RegulationListView from '../views/RegulationListView.vue'
import AuthorityView from '../views/AuthorityView.vue'
import SettingsView from '../views/SettingsView.vue'
import DataManagerView from '../views/DataManagerView.vue'

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: LandingView },
    { path: '/home', component: HomeView },
    { path: '/regulations', component: RegulationListView },
    { path: '/regulation/:id+', component: RegulationView },
    { path: '/authority', component: AuthorityView },
    { path: '/settings', component: SettingsView },
    { path: '/data-manager', component: DataManagerView },
  ],
})
