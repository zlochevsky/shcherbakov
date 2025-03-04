(()=>{(function(r){r.fn.transpose=function(h){var i=r.extend({},r.fn.transpose.defaults,h),o=null,u=[{name:"Ab",value:0,type:"F"},{name:"A",value:1,type:"N"},{name:"A#",value:2,type:"S"},{name:"B",value:2,type:"F"},{name:"H",value:3,type:"N"},{name:"C",value:4,type:"N"},{name:"C#",value:5,type:"S"},{name:"Db",value:5,type:"F"},{name:"D",value:6,type:"N"},{name:"D#",value:7,type:"S"},{name:"Eb",value:7,type:"F"},{name:"E",value:8,type:"N"},{name:"F",value:9,type:"N"},{name:"F#",value:10,type:"S"},{name:"Gb",value:10,type:"F"},{name:"G",value:11,type:"N"},{name:"G#",value:0,type:"S"}],m=function(e){e.charAt(e.length-1)=="m"&&(e=e.substring(0,e.length-1));for(var a=0;a<u.length;a++)if(e.toUpperCase()==u[a].name.toUpperCase())return u[a]},f=function(e){return e.length>1&&(e.charAt(1)=="b"||e.charAt(1)=="#")?e.substr(0,2):e.substr(0,1)},p=function(e,a,n){var t=m(e).value+a;t>11?t-=12:t<0&&(t+=12);var s=0;if(t==0||t==2||t==5||t==7||t==10)switch(n.name){case"A":case"A#":case"B":case"C":case"C#":case"D":case"D#":case"E":case"F#":case"G":case"G#":case"H":for(;s<u.length;s++)if(u[s].value==t&&u[s].type=="S")return u[s];default:for(;s<u.length;s++)if(u[s].value==t&&u[s].type=="F")return u[s]}else for(;s<u.length;s++)if(u[s].value==t)return u[s]},j=function(e){switch(e.charAt(e.length-1)){case"b":return"F";case"#":return"S";default:return"N"}},d=function(e,a){return e>a?0-(e-a):e<a?0+(a-e):0},y=function(e,a){var n=m(a);if(o.name!=n.name){var t=d(o.value,n.value);r("span.c",e).each(function(s,l){g(l,t,n)}),o=n}},g=function(e,a,n){var t=r(e),s=t.text(),l=f(s),c=p(l,a,n),v=c.name+s.substr(l.length);l==l.toLowerCase()&&(v=v.toLowerCase()),t.text(v);var C=t[0].nextSibling;console.log(C)},A=function(e,a,n){return e>a?n+(e-a):e<a?n-(a-e):n},S=function(e,a){for(var n=[],t=0;t<a;t++)n.push(e);return n.join("")},N=function(e){for(var a=e.replace(/\s+/," ").split(" "),n=0;n<a.length;n++)if(!r.trim(a[n]).length==0&&!a[n].match(i.chordRegex))return!1;return!0},b=function(e){return e.replace(i.chordReplaceRegex,"<span class='c'>$1</span>")};return r(this).each(function(){var e=r(this).attr("data-key");if((!e||r.trim(e)=="")&&(e=i.key),!e||r.trim(e)=="")throw"Starting key not defined.";o=m(e);var a=[];r(u).each(function(s,l){o.name==l.name?a.push("<a href='#' class='selected'>"+l.name+"</a>"):a.push("<a href='#'>"+l.name+"</a>")});var n=r(this),t=r("<div class='transpose-keys'></div>");t.html(a.join("")),r("a",t).click(function(s){return s.preventDefault(),y(n,r(this).text()),r(".transpose-keys a").removeClass("selected"),r(this).addClass("selected"),!1}),r(this).parent().find(".transpose-wrapper").html(t),r(this).find("span.ch").each(function(s,l){var c=r(l).html();r(l).html(b(c))})})},r.fn.transpose.defaults={chordRegex:/^[A-Ha-h][b\#]?(2|4|5|6|7|9|11|13|6\/9|7\-5|7\-9|7\#5|7\#9|7\+5|7\+9|b5|#5|#9|7b5|7b9|7sus2|7sus4|add2|add4|add9|aug|dim|dim7|m\/maj7|m6|m7|m7b5|m9|m11|m13|maj7|maj9|maj11|maj13|mb5|m|sus|sus2|sus4)*(\/[A-H][b\#]*)*$/,chordReplaceRegex:/([A-Ha-h][b\#]?(2|4|5|6|7|9|11|13|6\/9|7\-5|7\-9|7\#5|7\#9|7\+5|7\+9|b5|#5|#9|7b5|7b9|7sus2|7sus4|add2|add4|add9|aug|dim|dim7|m\/maj7|m6|m7|m7b5|m9|m11|m13|maj7|maj9|maj11|maj13|mb5|m|sus|sus2|sus4)*)/g}})(jQuery);})();
/*!
 * jQuery Chord Transposer plugin v1.0
 * http://codegavin.com/projects/transposer
 *
 * Copyright 2010, Jesse Gavin
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://codegavin.com/license
 *
 * Date: Sat Jun 26 21:27:00 2010 -0600
 */
