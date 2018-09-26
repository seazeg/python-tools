import mainbody from '../../../components/layout/layout.mainBody.vue'
import list from '../../../views/diy/homeMgr/sqHomeMgr/sqSubjectMgr/index.vue'
import appInfo from '../../../config/appInfo'
export default {
  _router: [{
    path: '/diy/:module/',
    component: mainbody,
    children: [{
      path: 'sqsubjectmgr',
      component: list,
      meta: {
        requiresAuth: true,
        siteId: appInfo.diy
      }
    }]

  }]
}
