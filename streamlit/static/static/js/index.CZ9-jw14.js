import{r as s,J as d,j as S,bt as x,c4 as U}from"./index.NJJ4tUjP.js";import{a as V}from"./useBasicWidgetState.tV0z-xZk.js";import"./FormClearHelper.WZJn9vbQ.js";const v=(t,e)=>t.getIntValue(e),h=t=>t.default??null,C=t=>t.value??null,F=(t,e,o,a)=>{e.setIntValue(t,o.value,{fromUi:o.fromUi},a)},I=({disabled:t,element:e,widgetMgr:o,width:a,fragmentId:u})=>{const{options:n,help:c,label:i,labelVisibility:r,placeholder:m}=e,[f,l]=V({getStateFromWidgetMgr:v,getDefaultStateFromProto:h,getCurrStateFromProto:C,updateWidgetMgrState:F,element:e,widgetMgr:o,fragmentId:u}),g=s.useCallback(b=>{l({value:b,fromUi:!0})},[l]),p=d(e.default)&&!t;return S(U,{label:i,labelVisibility:x(r==null?void 0:r.value),options:n,disabled:t,width:a,onChange:g,value:f,help:c,placeholder:m,clearable:p})},E=s.memo(I);export{E as default};
