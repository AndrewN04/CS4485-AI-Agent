import{M as a,c5 as i,r as o}from"./index.NJJ4tUjP.js";class l{manageFormClearListener(r,s,t){a(this.formClearListener)&&this.lastWidgetMgr===r&&this.lastFormId===s||(this.disconnect(),i(s)&&(this.formClearListener=r.addFormClearedListener(s,t),this.lastWidgetMgr=r,this.lastFormId=s))}disconnect(){var r;(r=this.formClearListener)==null||r.disconnect(),this.formClearListener=void 0,this.lastWidgetMgr=void 0,this.lastFormId=void 0}}function d({element:e,widgetMgr:r,onFormCleared:s}){o.useEffect(()=>{if(!i(e.formId))return;const t=r.addFormClearedListener(e.formId,s);return()=>{t.disconnect()}},[e,r,s])}export{l as F,d as u};
