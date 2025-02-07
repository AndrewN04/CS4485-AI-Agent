import{R as X,r as T}from"./index.NJJ4tUjP.js";import{s as Te}from"./index.yO6T25kw.js";import"./FormClearHelper.WZJn9vbQ.js";import"./withFullScreenWrapper.C7qoDsX8.js";import"./Toolbar.CMZD3DhJ.js";import"./mergeWith.Dl3wzvfK.js";import"./sprintf.C-r3gIuM.js";import"./createDownloadLinkElement.DZMwyjvU.js";import"./toConsumableArray.BX2NO9HQ.js";import"./possibleConstructorReturn.B5jjf7-t.js";import"./createSuper.CTKcxntK.js";import"./FileDownload.esm.C4HCWwTv.js";const Be=Te("div")({name:"NumberOverlayEditorStyle",class:"gdg-n15fjm3e",propsAsIs:!1});function Se(e,t){var r={};for(var n in e)Object.prototype.hasOwnProperty.call(e,n)&&t.indexOf(n)<0&&(r[n]=e[n]);if(e!=null&&typeof Object.getOwnPropertySymbols=="function")for(var a=0,n=Object.getOwnPropertySymbols(e);a<n.length;a++)t.indexOf(n[a])<0&&Object.prototype.propertyIsEnumerable.call(e,n[a])&&(r[n[a]]=e[n[a]]);return r}var re;(function(e){e.event="event",e.props="prop"})(re||(re={}));function q(){}function Fe(e){var t,r=void 0;return function(){for(var n=[],a=arguments.length;a--;)n[a]=arguments[a];return t&&n.length===t.length&&n.every(function(i,l){return i===t[l]})||(t=n,r=e.apply(void 0,n)),r}}function ae(e){return!!(e||"").match(/\d/)}function Y(e){return e==null}function _e(e){return typeof e=="number"&&isNaN(e)}function pe(e){return Y(e)||_e(e)||typeof e=="number"&&!isFinite(e)}function xe(e){return e.replace(/[-[\]/{}()*+?.\\^$|]/g,"\\$&")}function je(e){switch(e){case"lakh":return/(\d+?)(?=(\d\d)+(\d)(?!\d))(\.\d+)?/g;case"wan":return/(\d)(?=(\d{4})+(?!\d))/g;case"thousand":default:return/(\d)(?=(\d{3})+(?!\d))/g}}function Le(e,t,r){var n=je(r),a=e.search(/[1-9]/);return a=a===-1?e.length:a,e.substring(0,a)+e.substring(a,e.length).replace(n,"$1"+t)}function Me(e){var t=T.useRef(e);t.current=e;var r=T.useRef(function(){for(var n=[],a=arguments.length;a--;)n[a]=arguments[a];return t.current.apply(t,n)});return r.current}function se(e,t){t===void 0&&(t=!0);var r=e[0]==="-",n=r&&t;e=e.replace("-","");var a=e.split("."),i=a[0],l=a[1]||"";return{beforeDecimal:i,afterDecimal:l,hasNegation:r,addNegation:n}}function ke(e){if(!e)return e;var t=e[0]==="-";t&&(e=e.substring(1,e.length));var r=e.split("."),n=r[0].replace(/^0+/,"")||"0",a=r[1]||"";return(t?"-":"")+n+(a?"."+a:"")}function ye(e,t,r){for(var n="",a=r?"0":"",i=0;i<=t-1;i++)n+=e[i]||a;return n}function de(e,t){return Array(t+1).join(e)}function be(e){var t=e+"",r=t[0]==="-"?"-":"";r&&(t=t.substring(1));var n=t.split(/[eE]/g),a=n[0],i=n[1];if(i=Number(i),!i)return r+a;a=a.replace(".","");var l=1+i,h=a.length;return l<0?a="0."+de("0",Math.abs(l))+a:l>=h?a=a+de("0",l-h):a=(a.substring(0,l)||"0")+"."+a.substring(l),r+a}function ge(e,t,r){if(["","-"].indexOf(e)!==-1)return e;var n=(e.indexOf(".")!==-1||r)&&t,a=se(e),i=a.beforeDecimal,l=a.afterDecimal,h=a.hasNegation,p=parseFloat("0."+(l||"0")),x=l.length<=t?"0."+l:p.toFixed(t),S=x.split("."),c=i;i&&Number(S[0])&&(c=i.split("").reverse().reduce(function(I,C,g){return I.length>g?(Number(I[0])+Number(C)).toString()+I.substring(1,I.length):C+I},S[0]));var m=ye(S[1]||"",t,r),y=h?"-":"",s=n?".":"";return""+y+c+s+m}function H(e,t){if(e.value=e.value,e!==null){if(e.createTextRange){var r=e.createTextRange();return r.move("character",t),r.select(),!0}return e.selectionStart||e.selectionStart===0?(e.focus(),e.setSelectionRange(t,t),!0):(e.focus(),!1)}}var Ve=Fe(function(e,t){for(var r=0,n=0,a=e.length,i=t.length;e[r]===t[r]&&r<a;)r++;for(;e[a-1-n]===t[i-1-n]&&i-n>r&&a-n>r;)n++;return{from:{start:r,end:a-n},to:{start:r,end:i-n}}}),Pe=function(e,t){var r=Math.min(e.selectionStart,t);return{from:{start:r,end:e.selectionEnd},to:{start:r,end:t}}};function Ke(e,t,r){return Math.min(Math.max(e,t),r)}function ce(e){return Math.max(e.selectionStart,e.selectionEnd)}function We(){return typeof navigator<"u"&&!(navigator.platform&&/iPhone|iPod/.test(navigator.platform))}function Ue(e){return{from:{start:0,end:0},to:{start:0,end:e.length},lastValue:""}}function $e(e){var t=e.currentValue,r=e.formattedValue,n=e.currentValueIndex,a=e.formattedValueIndex;return t[n]===r[a]}function Ge(e,t,r,n,a,i,l){l===void 0&&(l=$e);var h=a.findIndex(function(k){return k}),p=e.slice(0,h);!t&&!r.startsWith(p)&&(t=p,r=p+r,n=n+p.length);for(var x=r.length,S=e.length,c={},m=new Array(x),y=0;y<x;y++){m[y]=-1;for(var s=0,I=S;s<I;s++){var C=l({currentValue:r,lastValue:t,formattedValue:e,currentValueIndex:y,formattedValueIndex:s});if(C&&c[s]!==!0){m[y]=s,c[s]=!0;break}}}for(var g=n;g<x&&(m[g]===-1||!i(r[g]));)g++;var B=g===x||m[g]===-1?S:m[g];for(g=n-1;g>0&&m[g]===-1;)g--;var F=g===-1||m[g]===-1?0:m[g]+1;return F>B?B:n-F<B-n?F:B}function me(e,t,r,n){var a=e.length;if(t=Ke(t,0,a),n==="left"){for(;t>=0&&!r[t];)t--;t===-1&&(t=r.indexOf(!0))}else{for(;t<=a&&!r[t];)t++;t>a&&(t=r.lastIndexOf(!0))}return t===-1&&(t=a),t}function Ze(e){for(var t=Array.from({length:e.length+1}).map(function(){return!0}),r=0,n=t.length;r<n;r++)t[r]=!!(ae(e[r])||ae(e[r-1]));return t}function Ne(e,t,r,n,a,i){i===void 0&&(i=q);var l=Me(function(s,I){var C,g;return pe(s)?(g="",C=""):typeof s=="number"||I?(g=typeof s=="number"?be(s):s,C=n(g)):(g=a(s,void 0),C=n(g)),{formattedValue:C,numAsString:g}}),h=T.useState(function(){return l(Y(e)?t:e,r)}),p=h[0],x=h[1],S=function(s,I){s.formattedValue!==p.formattedValue&&x({formattedValue:s.formattedValue,numAsString:s.value}),i(s,I)},c=e,m=r;Y(e)&&(c=p.numAsString,m=!0);var y=l(c,m);return T.useMemo(function(){x(y)},[y.formattedValue]),[p,S]}function qe(e){return e.replace(/[^0-9]/g,"")}function ze(e){return e}function He(e){var t=e.type;t===void 0&&(t="text");var r=e.displayType;r===void 0&&(r="input");var n=e.customInput,a=e.renderText,i=e.getInputRef,l=e.format;l===void 0&&(l=ze);var h=e.removeFormatting;h===void 0&&(h=qe);var p=e.defaultValue,x=e.valueIsNumericString,S=e.onValueChange,c=e.isAllowed,m=e.onChange;m===void 0&&(m=q);var y=e.onKeyDown;y===void 0&&(y=q);var s=e.onMouseUp;s===void 0&&(s=q);var I=e.onFocus;I===void 0&&(I=q);var C=e.onBlur;C===void 0&&(C=q);var g=e.value,B=e.getCaretBoundary;B===void 0&&(B=Ze);var F=e.isValidInputCharacter;F===void 0&&(F=ae);var k=e.isCharacterSame,j=Se(e,["type","displayType","customInput","renderText","getInputRef","format","removeFormatting","defaultValue","valueIsNumericString","onValueChange","isAllowed","onChange","onKeyDown","onMouseUp","onFocus","onBlur","value","getCaretBoundary","isValidInputCharacter","isCharacterSame"]),z=Ne(g,p,!!x,l,h,S),P=z[0],V=P.formattedValue,L=P.numAsString,W=z[1],M=T.useRef(),U=T.useRef({formattedValue:V,numAsString:L}),$=function(o,u){U.current={formattedValue:o.formattedValue,numAsString:o.value},W(o,u)},J=T.useState(!1),ee=J[0],d=J[1],f=T.useRef(null),N=T.useRef({setCaretTimeout:null,focusTimeout:null});T.useEffect(function(){return d(!0),function(){clearTimeout(N.current.setCaretTimeout),clearTimeout(N.current.focusTimeout)}},[]);var R=l,A=function(o,u){var v=parseFloat(u);return{formattedValue:o,value:u,floatValue:isNaN(v)?void 0:v}},E=function(o,u,v){o.selectionStart===0&&o.selectionEnd===o.value.length||(H(o,u),N.current.setCaretTimeout=setTimeout(function(){o.value===v&&o.selectionStart!==u&&H(o,u)},0))},O=function(o,u,v){return me(o,u,B(o),v)},Q=function(o,u,v){var w=B(u),_=Ge(u,V,o,v,w,F,k);return _=me(u,_,w),_},oe=function(o){var u=o.formattedValue;u===void 0&&(u="");var v=o.input,w=o.source,_=o.event,D=o.numAsString,b;if(v){var K=o.inputValue||v.value,G=ce(v);v.value=u,b=Q(K,u,G),b!==void 0&&E(v,b,u)}u!==V&&$(A(u,D),{event:_,source:w})};T.useEffect(function(){var o=U.current,u=o.formattedValue,v=o.numAsString;(V!==u||L!==v)&&$(A(V,L),{event:void 0,source:re.props})},[V,L]);var te=f.current?ce(f.current):void 0,ne=typeof window<"u"?T.useLayoutEffect:T.useEffect;ne(function(){var o=f.current;if(V!==U.current.formattedValue&&o){var u=Q(U.current.formattedValue,V,te);o.value=V,E(o,u,V)}},[V]);var ue=function(o,u,v){var w=u.target,_=M.current?Pe(M.current,w.selectionEnd):Ve(V,o),D=Object.assign(Object.assign({},_),{lastValue:V}),b=h(o,D),K=R(b);if(b=h(K,void 0),c&&!c(A(K,b))){var G=u.target,Z=ce(G),fe=Q(o,V,Z);return G.value=V,E(G,fe,V),!1}return oe({formattedValue:K,numAsString:b,inputValue:o,event:u,source:v,input:u.target}),!0},le=function(o,u){u===void 0&&(u=0);var v=o.selectionStart,w=o.selectionEnd;M.current={selectionStart:v,selectionEnd:w+u}},De=function(o){var u=o.target,v=u.value,w=ue(v,o,re.event);w&&m(o),M.current=void 0},Ie=function(o){var u=o.target,v=o.key,w=u.selectionStart,_=u.selectionEnd,D=u.value;D===void 0&&(D="");var b;v==="ArrowLeft"||v==="Backspace"?b=Math.max(w-1,0):v==="ArrowRight"?b=Math.min(w+1,D.length):v==="Delete"&&(b=w);var K=0;v==="Delete"&&w===_&&(K=1);var G=v==="ArrowLeft"||v==="ArrowRight";if(b===void 0||w!==_&&!G){y(o),le(u,K);return}var Z=b;if(G){var fe=v==="ArrowLeft"?"left":"right";Z=O(D,b,fe),Z!==b&&o.preventDefault()}else v==="Delete"&&!F(D[b])?Z=O(D,b,"right"):v==="Backspace"&&!F(D[b])&&(Z=O(D,b,"left"));Z!==b&&E(u,Z,D),y(o),le(u,K)},Ce=function(o){var u=o.target,v=function(){var w=u.selectionStart,_=u.selectionEnd,D=u.value;if(D===void 0&&(D=""),w===_){var b=O(D,w);b!==w&&E(u,b,D)}};v(),requestAnimationFrame(function(){v()}),s(o),le(u)},Ee=function(o){o.persist&&o.persist();var u=o.target,v=o.currentTarget;f.current=u,N.current.focusTimeout=setTimeout(function(){var w=u.selectionStart,_=u.selectionEnd,D=u.value;D===void 0&&(D="");var b=O(D,w);b!==w&&!(w===0&&_===D.length)&&E(u,b,D),I(Object.assign(Object.assign({},o),{currentTarget:v}))},0)},Re=function(o){f.current=null,clearTimeout(N.current.focusTimeout),clearTimeout(N.current.setCaretTimeout),C(o)},Ae=ee&&We()?"numeric":void 0,ve=Object.assign({inputMode:Ae},j,{type:t,value:V,onChange:De,onKeyDown:Ie,onMouseUp:Ce,onFocus:Ee,onBlur:Re});if(r==="text")return a?X.createElement(X.Fragment,null,a(V,j)||null):X.createElement("span",Object.assign({},j,{ref:i}),V);if(n){var Oe=n;return X.createElement(Oe,Object.assign({},ve,{ref:i}))}return X.createElement("input",Object.assign({},ve,{ref:i}))}function he(e,t){var r=t.decimalScale,n=t.fixedDecimalScale,a=t.prefix;a===void 0&&(a="");var i=t.suffix;i===void 0&&(i="");var l=t.allowNegative,h=t.thousandsGroupStyle;if(h===void 0&&(h="thousand"),e===""||e==="-")return e;var p=ie(t),x=p.thousandSeparator,S=p.decimalSeparator,c=r!==0&&e.indexOf(".")!==-1||r&&n,m=se(e,l),y=m.beforeDecimal,s=m.afterDecimal,I=m.addNegation;return r!==void 0&&(s=ye(s,r,!!n)),x&&(y=Le(y,x,h)),a&&(y=a+y),i&&(s=s+i),I&&(y="-"+y),e=y+(c&&S||"")+s,e}function ie(e){var t=e.decimalSeparator;t===void 0&&(t=".");var r=e.thousandSeparator,n=e.allowedDecimalSeparators;return r===!0&&(r=","),n||(n=[t,"."]),{decimalSeparator:t,thousandSeparator:r,allowedDecimalSeparators:n}}function Je(e,t){e===void 0&&(e="");var r=new RegExp("(-)"),n=new RegExp("(-)(.)*(-)"),a=r.test(e),i=n.test(e);return e=e.replace(/-/g,""),a&&!i&&t&&(e="-"+e),e}function Qe(e,t){return new RegExp("(^-)|[0-9]|"+xe(e),"g")}function Xe(e,t,r){return e===""?!0:!(t!=null&&t.match(/\d/))&&!(r!=null&&r.match(/\d/))&&typeof e=="string"&&!isNaN(Number(e))}function Ye(e,t,r){var n;t===void 0&&(t=Ue(e));var a=r.allowNegative,i=r.prefix;i===void 0&&(i="");var l=r.suffix;l===void 0&&(l="");var h=r.decimalScale,p=t.from,x=t.to,S=x.start,c=x.end,m=ie(r),y=m.allowedDecimalSeparators,s=m.decimalSeparator,I=e[c]===s;if(ae(e)&&(e===i||e===l)&&t.lastValue==="")return e;if(c-S===1&&y.indexOf(e[S])!==-1){var C=h===0?"":s;e=e.substring(0,S)+C+e.substring(S+1,e.length)}var g=function(f,N,R){var A=!1,E=!1;i.startsWith("-")?A=!1:f.startsWith("--")?(A=!1,E=!0):l.startsWith("-")&&f.length===l.length?A=!1:f[0]==="-"&&(A=!0);var O=A?1:0;return E&&(O=2),O&&(f=f.substring(O),N-=O,R-=O),{value:f,start:N,end:R,hasNegation:A}},B=g(e,S,c),F=B.hasNegation;n=B,e=n.value,S=n.start,c=n.end;var k=g(t.lastValue,p.start,p.end),j=k.start,z=k.end,P=k.value,V=e.substring(S,c);e.length&&P.length&&(j>P.length-l.length||z<i.length)&&!(V&&l.startsWith(V))&&(e=P);var L=0;e.startsWith(i)?L+=i.length:S<i.length&&(L=S),e=e.substring(L),c-=L;var W=e.length,M=e.length-l.length;e.endsWith(l)?W=M:(c>M||c>e.length-l.length)&&(W=c),e=e.substring(0,W),e=Je(F?"-"+e:e,a),e=(e.match(Qe(s))||[]).join("");var U=e.indexOf(s);e=e.replace(new RegExp(xe(s),"g"),function(f,N){return N===U?".":""});var $=se(e,a),J=$.beforeDecimal,ee=$.afterDecimal,d=$.addNegation;return x.end-x.start<p.end-p.start&&J===""&&I&&!parseFloat(ee)&&(e=d?"-":""),e}function et(e,t){var r=t.prefix;r===void 0&&(r="");var n=t.suffix;n===void 0&&(n="");var a=Array.from({length:e.length+1}).map(function(){return!0}),i=e[0]==="-";a.fill(!1,0,r.length+(i?1:0));var l=e.length;return a.fill(!1,l-n.length+1,l+1),a}function tt(e){var t=ie(e),r=t.thousandSeparator,n=t.decimalSeparator,a=e.prefix;a===void 0&&(a="");var i=e.allowNegative;if(i===void 0&&(i=!0),r===n)throw new Error(`
        Decimal separator can't be same as thousand separator.
        thousandSeparator: `+r+` (thousandSeparator = {true} is same as thousandSeparator = ",")
        decimalSeparator: `+n+` (default value for decimalSeparator is .)
     `);return a.startsWith("-")&&i&&(console.error(`
      Prefix can't start with '-' when allowNegative is true.
      prefix: `+a+`
      allowNegative: `+i+`
    `),i=!1),Object.assign(Object.assign({},e),{allowNegative:i})}function rt(e){e=tt(e),e.decimalSeparator,e.allowedDecimalSeparators,e.thousandsGroupStyle;var t=e.suffix,r=e.allowNegative,n=e.allowLeadingZeros,a=e.onKeyDown;a===void 0&&(a=q);var i=e.onBlur;i===void 0&&(i=q);var l=e.thousandSeparator,h=e.decimalScale,p=e.fixedDecimalScale,x=e.prefix;x===void 0&&(x="");var S=e.defaultValue,c=e.value,m=e.valueIsNumericString,y=e.onValueChange,s=Se(e,["decimalSeparator","allowedDecimalSeparators","thousandsGroupStyle","suffix","allowNegative","allowLeadingZeros","onKeyDown","onBlur","thousandSeparator","decimalScale","fixedDecimalScale","prefix","defaultValue","value","valueIsNumericString","onValueChange"]),I=ie(e),C=I.decimalSeparator,g=I.allowedDecimalSeparators,B=function(d){return he(d,e)},F=function(d,f){return Ye(d,f,e)},k=Y(c)?S:c,j=m??Xe(k,x,t);Y(c)?Y(S)||(j=j||typeof S=="number"):j=j||typeof c=="number";var z=function(d){return pe(d)?d:(typeof d=="number"&&(d=be(d)),j&&typeof h=="number"?ge(d,h,!!p):d)},P=Ne(z(c),z(S),!!j,B,F,y),V=P[0],L=V.numAsString,W=V.formattedValue,M=P[1],U=function(d){var f=d.target,N=d.key,R=f.selectionStart,A=f.selectionEnd,E=f.value;if(E===void 0&&(E=""),(N==="Backspace"||N==="Delete")&&A<x.length){d.preventDefault();return}if(R!==A){a(d);return}N==="Backspace"&&E[0]==="-"&&R===x.length+1&&r&&H(f,1),h&&p&&(N==="Backspace"&&E[R-1]===C?(H(f,R-1),d.preventDefault()):N==="Delete"&&E[R]===C&&d.preventDefault()),g!=null&&g.includes(N)&&E[R]===C&&H(f,R+1);var O=l===!0?",":l;N==="Backspace"&&E[R-1]===O&&H(f,R-1),N==="Delete"&&E[R]===O&&H(f,R+1),a(d)},$=function(d){var f=L;if(f.match(/\d/g)||(f=""),n||(f=ke(f)),p&&h&&(f=ge(f,h,p)),f!==L){var N=he(f,e);M({formattedValue:N,value:f,floatValue:parseFloat(f)},{event:d,source:re.event})}i(d)},J=function(d){return d===C?!0:ae(d)},ee=function(d){var f=d.currentValue,N=d.lastValue,R=d.formattedValue,A=d.currentValueIndex,E=d.formattedValueIndex,O=f[A],Q=R[E],oe=Ve(N,f),te=oe.to,ne=function(ue){return F(ue).indexOf(".")+x.length};return c===0&&p&&h&&f[te.start]===C&&ne(f)<A&&ne(R)>E?!1:A>=te.start&&A<te.end&&g&&g.includes(O)&&Q===C?!0:O===Q};return Object.assign(Object.assign({},s),{value:W,valueIsNumericString:!1,isValidInputCharacter:J,isCharacterSame:ee,onValueChange:M,format:B,removeFormatting:F,getCaretBoundary:function(d){return et(d,e)},onKeyDown:U,onBlur:$})}function at(e){var t=rt(e);return X.createElement(He,Object.assign({},t))}function we(){var r,n,a;return((a=(n=(r=Intl.NumberFormat())==null?void 0:r.formatToParts(1.1))==null?void 0:n.find(i=>i.type==="decimal"))==null?void 0:a.value)??"."}function nt(){return we()==="."?",":"."}const St=e=>{const{value:t,onChange:r,disabled:n,highlight:a,validatedSelection:i,fixedDecimals:l,allowNegative:h,thousandSeparator:p,decimalSeparator:x}=e,S=T.useRef();return T.useLayoutEffect(()=>{var c;if(i!==void 0){const m=typeof i=="number"?[i,null]:i;(c=S.current)==null||c.setSelectionRange(m[0],m[1])}},[i]),T.createElement(Be,null,T.createElement(at,{autoFocus:!0,getInputRef:S,className:"gdg-input",onFocus:c=>c.target.setSelectionRange(a?0:c.target.value.length,c.target.value.length),disabled:n===!0,decimalScale:l,allowNegative:h,thousandSeparator:p??nt(),decimalSeparator:x??we(),value:Object.is(t,-0)?"-":t??"",onValueChange:r}))};export{St as default};
