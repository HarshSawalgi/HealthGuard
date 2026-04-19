function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'en',
        includedLanguages: 'en,hi',
        autoDisplay: false
    }, 'google_translate_element');
}

/* Force remove top bar after load */
setInterval(function () {
    const frame = document.querySelector('.goog-te-banner-frame');
    if (frame) {
        frame.style.display = 'none';
    }
    document.body.style.top = '0px';
}, 100);

function translateToHindi() {
    var select = document.querySelector(".goog-te-combo");
    select.value = "hi";
    select.dispatchEvent(new Event("change"));
}

function translateToEnglish() {
    var select = document.querySelector(".goog-te-combo");
    select.value = "en";
    select.dispatchEvent(new Event("change"));
}

function googleTranslateElementInit() {
    new google.translate.TranslateElement(
        { pageLanguage: 'en', includedLanguages: 'hi,en' },
        'google_translate_element'
    );
}

function translateToHindi() {
    var select = document.querySelector(".goog-te-combo");
    select.value = "hi";
    select.dispatchEvent(new Event("change"));
}

function translateToEnglish() {
    var select = document.querySelector(".goog-te-combo");
    select.value = "en";
    select.dispatchEvent(new Event("change"));
}

function googleTranslateElementInit() {
    new google.translate.TranslateElement(
        { pageLanguage: 'en', includedLanguages: 'hi,en' },
        'google_translate_element'
    );
}