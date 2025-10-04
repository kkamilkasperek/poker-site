const protocol = location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(`${protocol}://${location.host}/ws/room/${roomId}/?role=${role}`);

const currentActionHandlers = {
    fold: null,
    check: null,
    call: null,
    raise: null,
};

let yourPosition = null;

socket.onopen = () => {
    console.log("WebSocket connection established.");
    socket.send(JSON.stringify({
        type: "init_new_player",
    }));
}

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Message from server:", data);

    switch (data.type) {
        case 'init_participant':
            yourPosition = data.your_position;
            initParticipant(data.players);
            break;
        case 'init_observer':
            initObserver(data.players);
            break;
        case 'new_player':
            newPlayer(data.position, data.username, data.chip_count);
            break;
        case 'player_left':
            deletePlayer(data.position);
            break;
        case 'player_bet':
            playerBet(data.position, data.amount, data.chip_count, data.pot);
            break;
        case 'dealt_cards':
            dealtCards(data.cards, data.active_positions);
            break;
        case 'player_turn':
            playerTurn(data.username);
            break;
        case 'your_turn':
            yourTurn(data.current_bet, data.player_bet, data.chip_count, data.pot);
            break;
        case 'board_cards':
            boardCards(data.cards);
            break;
        case 'clear_betting':
            clearBetting();
            break;
        case 'player_checked':
            playerChecked(data.position);
            break;
        case 'player_fold':
            playerFold(data.position);
            break;
        case 'action_error':
            // console.error(data.message);
            alert(data.message);
            break;
        default:
            console.error("Unknown message type:", data.type);
    }
};

socket.onerror = (error) => {
    messagesDiv = document.querySelector(".room-info");
    paragraph = document.createElement("p");
    paragraph.textContent = `Połączenie websocket nie powiodło się`;
    messagesDiv.appendChild(paragraph);
    console.error("WebSocket error:", error);
}

const relativePosition = (position) => {
    return position - yourPosition >= 0 ? position - yourPosition : position - yourPosition + maxPlayers;
}

/* Initialize players on the board on relative positions
 user position is 0, need to transform from server position to relative position
*/
const initParticipant = (players) => {
    const numberOfPlayers = Object.keys(players).length;
    const playerCountDiv = document.getElementById("current-players-count");
    playerCountDiv.textContent = `${numberOfPlayers}`;
    const entryButton = document.getElementById("entry-button");
    entryButton.textContent = "Odejdź";
    entryButton.addEventListener('click', leaveGame);
    for (const pos in players) {
        const relativePos = relativePosition(pos);
        const playerName = players[pos].username;
        const playerCards = players[pos].cards;
        let cardsHTML = '';
        if (playerCards) {
            cardsHTML = playerCards.join(', ');
        }
        const seatDiv = document.getElementById(`seat-${relativePos}`);
        if (seatDiv) {
            seatDiv.innerHTML = `<hr>
                                Pozycja: ${relativePos} <br>
                                ${playerName} <br>
                                <span class="cards">${cardsHTML}</span> <br>
                                <span class="chips">${players[pos].chip_count}</span> <br>
                                <span class="bet"></span>`;
        }
    }

    const actionPanel = document.querySelector(".action-panel");
    actionPanel.querySelector("#playerChips").textContent = `${players[yourPosition].chip_count}`;

    actionPanel.querySelector("div").hidden = false;

    // temporary solution for initation game
    if (numberOfPlayers >= 2) {
        socket.send(JSON.stringify(
            {
                type: "start_game",
            }
        ))
    }
}

const initObserver = (players) => {
    const playerCountDiv = document.getElementById("current-players-count");
    playerCountDiv.textContent = `${Object.keys(players).length}`;
    const entryButton = document.getElementById("entry-button");
    entryButton.textContent = "Dołącz";
    entryButton.addEventListener('click', joinGame);
    for (const pos in players) {
        const playerName = players[pos].username;
        const playerCards = players[pos].cards;
        let cardsHTML = '';
        if (playerCards) {
            for (const card of playerCards) {
                if (card === 'XX') cardsHTML += 'reverse';
                else cardsHTML += card;
            }
        }
        const seatDiv = document.getElementById(`seat-${pos}`);
        if (seatDiv) {
            seatDiv.innerHTML = `<hr>
                                Pozycja: ${pos} <br>
                                ${playerName} <br>
                                <span class="cards">${cardsHTML}</span> <br>
                                <span class="chips">${players[pos].chip_count}</span> <br>
                                <span class="bet"></span>`;
        }
    }
}

const leaveGame = () => { // leave game as participant and become observer
    document.getElementById('entry-button').removeEventListener('click', leaveGame);
  const url = new URL(window.location.href);
    url.searchParams.set('role', 'observer');
    window.location.href = url.toString();
}



const joinGame = () => { // join game as participant and become participant
    document.getElementById('entry-button').removeEventListener('click', joinGame);
    const url = new URL(window.location.href);
    url.searchParams.set('role', 'participant');
    window.location.href = url.toString();
}

const deletePlayer = (position) => {
    const relativePos = relativePosition(position);
    const seatDiv = document.getElementById(`seat-${relativePos}`);
    if (seatDiv) {
        seatDiv.innerHTML = `<hr>
                            Pozycja: ${relativePos} <br>
                            (wolne miejsce)`;
    }
    const playerCountDiv = document.getElementById("current-players-count");
    const currentCount = parseInt(playerCountDiv.textContent);
    playerCountDiv.textContent = `${currentCount - 1}`;
}

const newPlayer = (position, username, chip_count) => {
    const relativePos = relativePosition(position);
    const seatDiv = document.getElementById(`seat-${relativePos}`);
    if (seatDiv) {
        seatDiv.innerHTML = `<hr>
                            Pozycja: ${relativePos} <br>
                            ${username} <br>
                             <span class="cards"></span> <br>
                             <span class="chips">${chip_count}</span> <br>
                             <span class="bet"></span>`;
    }
    const playerCountDiv = document.getElementById("current-players-count");
    const currentCount = parseInt(playerCountDiv.textContent);
    playerCountDiv.textContent = `${currentCount + 1}`;
}

const playerBet = (position, amount, chip_count, pot) => {
    if (position === yourPosition) {
        const actionPanel = document.querySelector(".action-panel");
        actionPanel.querySelector("#playerChips").textContent = `${chip_count}`;
    }
    const relativePos = relativePosition(position);
    const seatDiv = document.getElementById(`seat-${relativePos}`);
    if (seatDiv) {
        const chipsSpan = seatDiv.querySelector(".chips");
        if (chipsSpan) {
            chipsSpan.textContent = `${chip_count}`;
        }
        const betSpan = seatDiv.querySelector(".bet");
        if (betSpan) {
            betSpan.textContent = `Zakład: ${amount}`;
        }
    }
    const potDiv = document.getElementById("pot-size");
    potDiv.textContent = `${pot}`;
}

const dealtCards = (cards, active_positions) => {
    /* Show cards dealt to player and simulate dealing hidden cards to opponents */
    const seatDiv = document.getElementById(`seat-0`);
    if (seatDiv) {
        const cardsSpan = seatDiv.querySelector(".cards");
        if (cardsSpan) {
            cardsSpan.textContent = cards.join(', ');
        }
    }
    for (const pos of active_positions) {
        if (pos !== yourPosition) {
            const relativePos = relativePosition(pos);
            const seatDiv = document.getElementById(`seat-${relativePos}`);
            if (seatDiv) {
                const cardsSpan = seatDiv.querySelector(".cards");
                if (cardsSpan) {
                    cardsSpan.textContent = 'XX, XX';
                }
            }
        }
    }
}

const boardCards = (cards) => {
    const boardDiv = document.getElementById("board-cards");
    boardDiv.textContent = cards.join(', ');
}

const playerTurn = (username) => {
    const roomInfoDiv = document.querySelector(".room-info");
    const actingPlayerInfo = roomInfoDiv.querySelector("#acting-player")
    actingPlayerInfo.textContent = `Kolej gracza: ${username}`
}

const yourTurn = (current_bet, your_bet, your_chip_count, pot) => {
    const seatDiv = document.getElementById(`seat-0`);
    if (seatDiv) {
        const chipsSpan = seatDiv.querySelector(".chips");
        if (chipsSpan) {
            chipsSpan.textContent = `${your_chip_count}`;
        }
    }
    const actionPanel = document.querySelector(".action-panel");
    const buttonsDiv = actionPanel.querySelector(".action");
    buttonsDiv.hidden = false;
    actionPanel.querySelector("#playerChips").textContent = your_chip_count || '';

    // activate buttons
    const foldButton = buttonsDiv.querySelector(".fold");
    const checkButton = buttonsDiv.querySelector(".check");
    const callButton = buttonsDiv.querySelector(".call");
    const raiseButton = buttonsDiv.querySelector(".raise");
    const raiseInput = buttonsDiv.querySelector(".raise-input");
    const raiseSlider = buttonsDiv.querySelector(".raise-slider");

    // remove previous event listeners
    if (currentActionHandlers.fold) {
        foldButton.removeEventListener('click', currentActionHandlers.fold);
    }
    if (currentActionHandlers.check) {
        checkButton.removeEventListener('click', currentActionHandlers.check);
    }
    if (currentActionHandlers.call) {
        callButton.removeEventListener('click', currentActionHandlers.call);
    }
    if (currentActionHandlers.raise) {
        raiseButton.removeEventListener('click', currentActionHandlers.raise);
    }

    // reset buttons states
    checkButton.disabled = true;
    callButton.disabled = true;
    raiseButton.disabled = true;
    callButton.textContent = 'Call';

    // update max values for input
    raiseInput.min =  (current_bet - your_bet) + 1; // minimum raise is call + 1
    raiseInput.max = your_chip_count;
    raiseInput.value = raiseInput.min;
    raiseSlider.min = raiseInput.min;
    raiseSlider.max = raiseInput.max;
    raiseSlider.value = raiseInput.min;

    // set event listeners for buttons
    currentActionHandlers.fold = () => {
        socket.send(JSON.stringify({
            type: "player_action",
            action: "fold",
        }));
        buttonsDiv.hidden = true;
    };
    foldButton.addEventListener('click', currentActionHandlers.fold, {once: true});

    if (current_bet === your_bet) {
        currentActionHandlers.check = () => {
            socket.send(JSON.stringify({
                type: "player_action",
                action: "call",
                amount: 0,
            }));
            buttonsDiv.hidden = true;
        };
        checkButton.addEventListener('click', currentActionHandlers.check, {once: true});
        checkButton.disabled = false;
    }

    if (your_chip_count >= current_bet - your_bet) {
        currentActionHandlers.call = () => {
            socket.send(JSON.stringify({
                type: "player_action",
                action: "call",
                amount: current_bet - your_bet,
            }));
            buttonsDiv.hidden = true;
        }
        callButton.addEventListener('click', currentActionHandlers.call, {once: true});
        callButton.disabled = false;

        if (your_chip_count > current_bet - your_bet) {
            currentActionHandlers.raise = () => {
                const raiseAmount = parseInt(raiseInput.value);
                if (raiseAmount >= raiseInput.min && raiseAmount <= raiseInput.max) {
                    socket.send(JSON.stringify({
                        type: "player_action",
                        action: "raise",
                        amount: raiseAmount,
                    }));
                    buttonsDiv.hidden = true;
                } else {
                    alert(`Nieprawidłowa kwota podbicia. Kwota musi być pomiędzy ${raiseInput.min} a ${raiseInput.max}.`);
                }
            }
            raiseButton.addEventListener('click', currentActionHandlers.raise, {once: true});
            raiseButton.disabled = false;
        }
    }
    else {
        raiseButton.disabled = true;
        // all in
        currentActionHandlers.call = () => {
            socket.send(JSON.stringify({
                type: "player_action",
                action: "call",
                amount: your_chip_count,
            }));
            buttonsDiv.hidden = true;
        }
        callButton.textContent = `All in (${your_chip_count})`;
        callButton.addEventListener('click', currentActionHandlers.call, {once: true});
    }
}

const clearBetting = () => {
    const roomInfoDiv = document.querySelector(".room-info");
    const actingPlayerInfo = roomInfoDiv.querySelector("#acting-player")
    actingPlayerInfo.textContent = ``;

    const tableDiv = document.getElementById("table");
    for (const seat of tableDiv.children) {
        const betSpan = seat.querySelector(".bet");
        if (betSpan) {
            betSpan.textContent = ``;
        }
    }
}

const playerChecked = (position) => {
    const relativePos = relativePosition(position);
    const seatDiv = document.getElementById(`seat-${relativePos}`);
    if (seatDiv) {
        const betSpan = seatDiv.querySelector(".bet");
        if (betSpan) {
            betSpan.textContent = `Czekam`;
        }
    }
}

const playerFold = (position) => {
    const relativePos = relativePosition(position);
    const seatDiv = document.getElementById(`seat-${relativePos}`);
    if (seatDiv) {
        const betSpan = seatDiv.querySelector(".bet");
        if (betSpan) {
            betSpan.textContent = `Pas`;
        }
    }
}
