import { default as autoComplete } from "@tarekraafat/autocomplete.js";
require("@tarekraafat/autocomplete.js/dist/css/autoComplete.02.css");
const md5 = require("js-md5");

const now = new Date();
const today =
  now.getUTCFullYear() +
  "-" +
  (now.getUTCMonth() + 1) +
  "-" +
  now.getUTCDate() +
  " " +
  now.getUTCHours() +
  ":" +
  now.getUTCMinutes();

document.getElementsByTagName("main")[0].innerHTML = `
  <div id="result"></div>
  <input id="autoComplete" />
  <ul id="guesses"></ul>
  <small>${today}</small>
`;

const corpus = await require("./films.json");
const labels = Object.keys(corpus);

const answer =
  labels[parseInt(md5(today).substring(0, 10), 16) % labels.length];

function highlight(guessInfo, answerInfo) {
  if (Array.isArray(answerInfo)) {
    return `<span class="${
      answerInfo.includes(guessInfo) ? "right" : "wrong"
    }">${guessInfo}</span>`;
  } else {
    return `<span class="${
      guessInfo === answerInfo ? "right" : "wrong"
    }">${guessInfo}</span>`;
  }
}

function renderGuess(corpus, selection, answer) {
  let html = `
    <h2>${highlight(selection, answer)}</h2>
    <p>Decade: ${highlight(corpus[selection].decade, corpus[answer].decade)}</p>
    `;

  if (corpus[selection].actors) {
    html += `
        <p>Cast: ${corpus[selection].actors
          .map((x) => {
            return highlight(x, corpus[answer].actors);
          })
          .join(", ")}</p>
    `;
  }
  if (corpus[selection].directors) {
    html += `
        <p>Director(s): ${corpus[selection].directors
          .map((x) => {
            return highlight(x, corpus[answer].directors);
          })
          .join(", ")}</p>
    `;
  }
  if (corpus[selection].composers) {
    html += `
        <p>Music by: ${corpus[selection].composers
          .map((x) => {
            return highlight(x, corpus[answer].composers);
          })
          .join(", ")}</p>
    `;
  }
  if (corpus[selection].genres) {
    html += `
        <p>Genres: ${corpus[selection].genres
          .map((x) => {
            return highlight(x, corpus[answer].genres);
          })
          .join(", ")}</p>
    `;
  }
  if (corpus[selection].subjects) {
    html += `
        <p>Subjects: ${corpus[selection].subjects
          .map((x) => {
            return highlight(x, corpus[answer].subjects);
          })
          .join(", ")}</p>
    `;
  }
  if (corpus[selection].settings) {
    html += `
        <p>Set in: ${corpus[selection].settings
          .map((x) => {
            return highlight(x, corpus[answer].settings);
          })
          .join(", ")}</p>
    `;
  }
  return html;
}

const config = {
  placeHolder: "Guess a Film...",
  data: {
    src: labels,
  },
  resultItem: {
    highlight: true,
  },
  events: {
    input: {
      selection: (event) => {
        const selection = event.detail.selection.value;
        if (selection === answer) {
          document.getElementById(
            "result",
          ).innerHTML = `<p class="right">${selection} is correct!</p>`;
        } else {
          document.getElementById(
            "result",
          ).innerHTML = `<p class="wrong">Not ${selection}!</p>`;
        }

        const guess = document.createElement("li");
        guess.innerHTML = renderGuess(corpus, selection, answer);
        document
          .getElementById("guesses")
          .insertBefore(guess, document.getElementById("guesses").firstChild);

        // Disallow guessing this again
        autoCompleteJS.data.src = autoCompleteJS.data.src.filter(
          (x) => x !== selection,
        );

        // Return focus back to guess box for quick feedback loops
        autoCompleteJS.input.value = "";
        autoCompleteJS.input.focus();
      },
    },
  },
};

const autoCompleteJS = new autoComplete(config);
autoCompleteJS.input.focus();
