import mainbody from '../../../components/layout/layout.mainBody.vue'
import list from '../../../views/diy/commentMgr/sectionSwiperMgr/index.vue'
import appInfo from '../../../config/appInfo'
export default {
  _router: [{
    path: '/diy/:module/',
    component: mainbody,
    children: [{
      path: 'sectionswipermgr',
      component: list,
      meta: {
        requiresAuth: true,
        siteId: appInfo.diy
      }
    }]

  }]
}
