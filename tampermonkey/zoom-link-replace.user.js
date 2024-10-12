// ==UserScript==
// @name         Direct link to zoom meeting
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Direct link to zoom meeting
// @author       roypur
// @match        https://moodle.hsky.fi/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=hsky.fi
// @updateURL    https://github.com/roypur/scripts/raw/master/tampermonkey/zoom-link-replace.user.js
// @downloadURL  https://github.com/roypur/scripts/raw/master/tampermonkey/zoom-link-replace.user.js
// @grant        none
// ==/UserScript==

(() => {
  const links = document.getElementsByTagName("a");
  for (const link of links) {
    const url = new URL(link.href);
    if (url.hostname.includes("zoom.us")) {
      const splitted = url.pathname.split("/");
      let meetingId = null;
      for (const part of splitted) {
        if (part) {
          meetingId = part;
        }
      }
      url.pathname = `/wc/join/${meetingId}`;
      link.href = url.href;
      link.innerText = url.href;
    }
  }
})();
