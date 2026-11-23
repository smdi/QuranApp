# Noble Quran Reader

Single-page Quran reader with recitation audio. Text: Uthmani (Hafs) from quran-json (CC BY 4.0), cross-checked against a second source. Open index.html via GitHub Pages.

## Tests
`python3 tests/test_word_audio.py index.html tests/word_files_expected.json` checks the sound file chosen for every one of the 77,321 supported words (and simulates taps). Needs Python + playwright + Chrome.
