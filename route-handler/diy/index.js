// 不同模块代码分离
import plate from './userMgr/plate.router'
import subjectaud from './commentMgr/subjectAudit.router'
import subjectmgr from './commentMgr/subjectMgr.router'
import subjectrec from './commentMgr/subjectRecycle.router'
import criticismMgr from './commentMgr/criticismMgr.router'
import labelMgr from './commentMgr/labelMgr.router'
import sqbannerMgr from './homeMgr/sqbannerMgr.router'
import sqRecomPostMgr from './homeMgr/sqRecomPostMgr.router'
import sqSubjectMgr from './homeMgr/sqSubjectMgr.router'
import sectionRecentHotMgr from './commentMgr/sectionRecentHotMgr.router'
import sectionSwiperMgr from './commentMgr/sectionSwiperMgr.router'
import qz from './userMgr/qz.router'
import collectionMgr from './commentMgr/collectionMgr.router'
import zanMgr from './commentMgr/zanMgr.router'
import userActionMgr from './userMgr/userActionMgr.router'
import auditTransformPass from './userMgr/auditTransformPass.router'
import postChangeMgr from './userMgr/postChangeMgr.router'

var routes = [];
routes.push(postChangeMgr._router[0]);
routes.push(plate._router[0]);
routes.push(subjectaud._router[0]);
routes.push(subjectmgr._router[0]);
routes.push(subjectrec._router[0]);
routes.push(criticismMgr._router[0]);
routes.push(labelMgr._router[0]);
routes.push(sqbannerMgr._router[0]);
routes.push(sqRecomPostMgr._router[0]);
routes.push(sqSubjectMgr._router[0]);
routes.push(sectionRecentHotMgr._router[0]);
routes.push(sectionSwiperMgr._router[0]);
routes.push(qz._router[0]);
routes.push(collectionMgr._router[0]);
routes.push(zanMgr._router[0]);
routes.push(userActionMgr._router[0]);
routes.push(auditTransformPass._router[0]);

export default {
  routes: routes
}
