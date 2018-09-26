import mainbody from '../../../components/layout/layout.mainBody.vue'
import list from '../../../views/bbsMoudle/commentMgr/subjectAudit/index.vue'
// import list from '../../../views/diy/commentMgr/subjectAudit/index.vue'
import appInfo from '../../../config/appInfo'
export default {
  _router: [{
    path: '/diy/:module/',
    component: mainbody,
    children: [{
      path: 'subjectaud',
      component: list,
      meta: {
        requiresAuth: true,
        siteId: appInfo.diy
      }
    }]

  }]
}
