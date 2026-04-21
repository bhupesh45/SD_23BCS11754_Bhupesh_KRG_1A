const ws = new WebSocket("ws://127.0.0.1:8000/ws");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  const el = document.getElementById("opt-" + data.option_id);
  if (el) el.innerText = data.votes;
};

let currentPollId = null;

let selectedVotes = {};

async function createPoll() {
  const question = document.getElementById("question").value;
  const inputs = document.querySelectorAll("#options-input input");

  let options = [];
  inputs.forEach((i) => {
    if (i.value.trim()) options.push({ text: i.value });
  });

  await fetch("/polls", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, options }),
  });

  loadPolls();
}

async function selectPoll(id) {
  currentPollId = id;

  const res = await fetch(`/polls/${id}`);
  const data = await res.json();

  document.getElementById("selected-question").innerText = data.question;

  const container = document.getElementById("options");
  container.innerHTML = "";

  data.options.forEach((opt) => {
    const div = document.createElement("div");

    div.innerHTML = `
            <button class="vote-btn" id="btn-${opt.id}" onclick="vote(${opt.id})">
                ${opt.text}
            </button>
            Votes: <span id="opt-${opt.id}">${opt.votes}</span>
        `;

    container.appendChild(div);
  });

  highlightSelected();
}

async function vote(option_id) {
  const previous = selectedVotes[currentPollId] || null;

  if (previous === option_id) return; // same click ignore

  await fetch("/vote", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      option_id: option_id,
      previous_option_id: previous,
    }),
  });

  selectedVotes[currentPollId] = option_id;

  highlightSelected();
}

function highlightSelected() {
  const selected = selectedVotes[currentPollId];

  document.querySelectorAll(".vote-btn").forEach((btn) => {
    btn.style.opacity = "0.6";
  });

  if (selected) {
    const btn = document.getElementById("btn-" + selected);
    if (btn) btn.style.opacity = "1";
  }
}

async function loadPolls() {
  const res = await fetch("/polls");
  const polls = await res.json();

  const container = document.getElementById("poll-list");
  container.innerHTML = "";

  polls.forEach((p) => {
    const div = document.createElement("div");
    div.className = "poll";

    div.innerHTML = `
            <b>${p.question}</b>
            <button onclick="selectPoll(${p.id})">Open</button>
        `;

    container.appendChild(div);
  });
}

function addOption() {
  const div = document.getElementById("options-input");
  const input = document.createElement("input");
  input.placeholder = "New option";
  div.appendChild(input);
}

loadPolls();
