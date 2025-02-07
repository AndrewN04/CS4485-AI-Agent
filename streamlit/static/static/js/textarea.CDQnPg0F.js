import{bx as v,by as T,bU as x,r as d,cc as j,cd as R}from"./index.NJJ4tUjP.js";import{g as $,a as I,b as A,B as F}from"./base-input.oYa0JPWm.js";function _(e,t){var r=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter(function(o){return Object.getOwnPropertyDescriptor(e,o).enumerable})),r.push.apply(r,n)}return r}function s(e){for(var t=1;t<arguments.length;t++){var r=arguments[t]!=null?arguments[t]:{};t%2?_(Object(r),!0).forEach(function(n){E(e,n,r[n])}):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(r)):_(Object(r)).forEach(function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(r,n))})}return e}function E(e,t,r){return t in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}var O=v("div",function(e){return s(s({},$(s(s({$positive:!1},e),{},{$hasIconTrailing:!1}))),{},{width:e.$resize?"fit-content":"100%"})});O.displayName="StyledTextAreaRoot";O.displayName="StyledTextAreaRoot";var m=v("div",function(e){return I(s({$positive:!1},e))});m.displayName="StyledTextareaContainer";m.displayName="StyledTextareaContainer";var g=v("textarea",function(e){return s(s({},A(e)),{},{resize:e.$resize||"none"})});g.displayName="StyledTextarea";g.displayName="StyledTextarea";function b(e){"@babel/helpers - typeof";return b=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(t){return typeof t}:function(t){return t&&typeof Symbol=="function"&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},b(e)}function l(){return l=Object.assign?Object.assign.bind():function(e){for(var t=1;t<arguments.length;t++){var r=arguments[t];for(var n in r)Object.prototype.hasOwnProperty.call(r,n)&&(e[n]=r[n])}return e},l.apply(this,arguments)}function B(e,t){return D(e)||C(e,t)||N(e,t)||z()}function z(){throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function N(e,t){if(e){if(typeof e=="string")return P(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);if(r==="Object"&&e.constructor&&(r=e.constructor.name),r==="Map"||r==="Set")return Array.from(e);if(r==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r))return P(e,t)}}function P(e,t){(t==null||t>e.length)&&(t=e.length);for(var r=0,n=new Array(t);r<t;r++)n[r]=e[r];return n}function C(e,t){var r=e==null?null:typeof Symbol<"u"&&e[Symbol.iterator]||e["@@iterator"];if(r!=null){var n=[],o=!0,i=!1,a,u;try{for(r=r.call(e);!(o=(a=r.next()).done)&&(n.push(a.value),!(t&&n.length===t));o=!0);}catch(y){i=!0,u=y}finally{try{!o&&r.return!=null&&r.return()}finally{if(i)throw u}}return n}}function D(e){if(Array.isArray(e))return e}function K(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function U(e,t){for(var r=0;r<t.length;r++){var n=t[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}function q(e,t,r){return t&&U(e.prototype,t),Object.defineProperty(e,"prototype",{writable:!1}),e}function M(e,t){if(typeof t!="function"&&t!==null)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),Object.defineProperty(e,"prototype",{writable:!1}),t&&h(e,t)}function h(e,t){return h=Object.setPrototypeOf?Object.setPrototypeOf.bind():function(n,o){return n.__proto__=o,n},h(e,t)}function H(e){var t=W();return function(){var n=p(e),o;if(t){var i=p(this).constructor;o=Reflect.construct(n,arguments,i)}else o=n.apply(this,arguments);return L(this,o)}}function L(e,t){if(t&&(b(t)==="object"||typeof t=="function"))return t;if(t!==void 0)throw new TypeError("Derived constructors may only return object or undefined");return f(e)}function f(e){if(e===void 0)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}function W(){if(typeof Reflect>"u"||!Reflect.construct||Reflect.construct.sham)return!1;if(typeof Proxy=="function")return!0;try{return Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],function(){})),!0}catch{return!1}}function p(e){return p=Object.setPrototypeOf?Object.getPrototypeOf.bind():function(r){return r.__proto__||Object.getPrototypeOf(r)},p(e)}function c(e,t,r){return t in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}var Y=function(e){M(r,e);var t=H(r);function r(){var n;K(this,r);for(var o=arguments.length,i=new Array(o),a=0;a<o;a++)i[a]=arguments[a];return n=t.call.apply(t,[this].concat(i)),c(f(n),"state",{isFocused:n.props.autoFocus||!1}),c(f(n),"onFocus",function(u){n.setState({isFocused:!0}),n.props.onFocus(u)}),c(f(n),"onBlur",function(u){n.setState({isFocused:!1}),n.props.onBlur(u)}),n}return q(r,[{key:"render",value:function(){var o=this.props.overrides,i=o===void 0?{}:o,a=T(i.Root,O),u=B(a,2),y=u[0],S=u[1],w=x({Input:{component:g},InputContainer:{component:m}},i);return d.createElement(y,l({"data-baseweb":"textarea",$isFocused:this.state.isFocused,$isReadOnly:this.props.readOnly,$disabled:this.props.disabled,$error:this.props.error,$positive:this.props.positive,$required:this.props.required,$resize:this.props.resize},S),d.createElement(F,l({},this.props,{type:j.textarea,overrides:w,onFocus:this.onFocus,onBlur:this.onBlur,resize:this.props.resize})))}}]),r}(d.Component);c(Y,"defaultProps",{autoFocus:!1,disabled:!1,readOnly:!1,error:!1,name:"",onBlur:function(){},onChange:function(){},onKeyDown:function(){},onKeyPress:function(){},onKeyUp:function(){},onFocus:function(){},overrides:{},placeholder:"",required:!1,rows:3,size:R.default});export{Y as T};
