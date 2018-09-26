import mainbody from '../../../components/layout/layout.mainBody.vue'
import list from '../../../views/bbsCloud/postChangeMgr/index.vue'
import appInfo from '../../../config/appInfo'
export default {
  _router: [{
    path: '/diy/:module/',
    component: mainbody,
    children: [{
      //produc路由
      path: 'postchangemgr',
      component: list,
      meta: {
        requiresAuth: true,
        siteId: appInfo.diy
      }
    }]

  }]
}
