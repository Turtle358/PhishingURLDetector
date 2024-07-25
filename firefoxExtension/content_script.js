document.addEventListener('click', function(event) {
    let target = event.target;
    while (target && target.tagName !== 'A') {
        target = target.parentElement;
    }
    if (target && target.href) {
        browser.runtime.sendMessage({ url: target.href });
    }
}, true);
