import mainbody from '../../../components/layout/layout.mainBody.vue'
import list from '../../../views/bbsMoudle/userMgr/userActionMgr/index.vue'
import appInfo from '../../../config/appInfo'
export default {
  _router: [{
    path: '/:module/',
    component: mainbody,
    children: [{
      path: 'useractionmgr',
      component: list,
      meta: {
        requiresAuth: true,
        siteId: appInfo.diy
      }
    }]

  }]
}
